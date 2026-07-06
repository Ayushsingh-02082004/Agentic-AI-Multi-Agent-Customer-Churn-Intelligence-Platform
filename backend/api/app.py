import os
import uuid
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.orchestrator import WorkflowOrchestrator
from backend.crews.customer_churn_crew import CustomerChurnCrew
from backend.vectorstore.chroma_service import ChromaService
from backend.vectorstore.ingestion_service import IngestionService
from backend.memory.memory_service import MemoryService
from backend.services.pdf_service import PDFService
from backend.services.guardrail_service import GuardrailService, GuardrailException

# Load env vars
import dotenv
dotenv.load_dotenv()

app = FastAPI(
    title="BNP Paribas Churn Intelligence API",
    description="Backend API for AI-driven customer churn analytics, risk prediction, retention recommendation, and validation auditing.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # 1. Run PostgreSQL table migrations
    from database.init_db import init_db
    try:
        print("Running PostgreSQL database table setup...")
        init_db()
    except Exception as e:
        print(f"Startup PostgreSQL setup failed: {e}")
        
    # 2. Automatically ingest ChromaDB vector database if empty
    try:
        print("Checking ChromaDB collection size...")
        db = ChromaService()
        metadatas = db.get_all_metadata()
        if len(metadatas) == 0:
            print("ChromaDB vector store is empty. Starting dataset ingestion...")
            ingestion = IngestionService()
            ingestion.ingest()
        else:
            print(f"ChromaDB vector store is populated with {len(metadatas)} customer profiles.")
    except Exception as e:
        print(f"Startup ChromaDB initialization failed: {e}")

# Request & Response schemas

class WorkflowRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class WorkflowResponse(BaseModel):
    session_id: str
    query_plan: Dict[str, Any]
    retrieval_context: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    prediction: Optional[Dict[str, Any]] = None
    recommendation: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    report: Optional[Dict[str, Any]] = None


@app.post("/api/run", response_model=WorkflowResponse)
def run_workflow(payload: WorkflowRequest):
    """
    Run the complete agentic customer churn analysis workflow.
    Validates input and output guardrails, and stores the execution trace in PostgreSQL.
    """
    query = payload.query
    session_uuid = payload.session_id
    
    # 1. Generate session ID if not provided
    if not session_uuid:
        session_uuid = str(uuid.uuid4())
    else:
        try:
            uuid.UUID(str(session_uuid))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session_id format. Must be a valid UUID.")

    # 2. Input validation guardrails
    try:
        GuardrailService.validate_input(query)
    except GuardrailException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal guardrail validation error: {e}")

    try:
        # 3. Kickoff the Query Understanding agent to build the Query Plan
        inputs = {"user_query": query}
        result = CustomerChurnCrew().crew().kickoff(inputs=inputs)
        plan = result.pydantic
        
        # Enforce that query is part of the plan
        if not hasattr(plan, 'user_query') or not plan.user_query:
            plan.user_query = query
            
        print(f"Executing workflow plan: {plan}")

        # 4. Execute workflow orchestrator
        orchestrator = WorkflowOrchestrator()
        completed = orchestrator.run(plan, session_id=session_uuid)

        # 5. Build and return structured response
        response_data = {
            "session_id": str(session_uuid),
            "query_plan": plan.model_dump(),
            "retrieval_context": completed.get("retrieval_context"),
            "analysis": completed["analysis"].model_dump() if "analysis" in completed else None,
            "prediction": completed["prediction"].model_dump() if "prediction" in completed else None,
            "recommendation": completed["recommendation"].model_dump() if "recommendation" in completed else None,
            "validation": completed["validation"].model_dump() if "validation" in completed else None,
            "report": completed["report"].model_dump() if "report" in completed else None,
        }
        
        return response_data

    except GuardrailException as e:
        # Catch output validation failures
        raise HTTPException(status_code=422, detail=f"Output Guardrail Refusal: {e}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Workflow Execution Failed: {e}")


@app.get("/api/history/{session_id}")
def get_session_history(session_id: str):
    """
    Retrieve past execution traces for a given session ID from PostgreSQL.
    """
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format. Must be UUID.")
        
    memory_service = MemoryService()
    history = memory_service.history(session_id)
    
    if not history:
        raise HTTPException(status_code=404, detail="Session history not found.")
        
    return history


@app.get("/api/statistics")
def get_db_statistics():
    """
    Calculate database statistics and risk distribution directly from ChromaDB.
    """
    try:
        db = ChromaService()
        metadatas = db.get_all_metadata()
        
        total_customers = len(metadatas)
        if total_customers == 0:
            return {
                "total_customers": 0,
                "churned_customers": 0,
                "churn_rate": 0.0,
                "average_age": 0.0,
                "average_tenure": 0.0,
                "risk_distribution": {"Low Risk": 0, "Medium Risk": 0, "High Risk": 0}
            }
            
        churned_customers = sum(1 for m in metadatas if m.get("churn") == 1)
        churn_rate = round((churned_customers / total_customers) * 100, 2)
        average_age = round(sum(m.get("age", 0) for m in metadatas) / total_customers, 2)
        average_tenure = round(sum(m.get("tenure", 0) for m in metadatas) / total_customers, 2)
        
        # Calculate risk class distributions from data rules
        low_count = 0
        med_count = 0
        high_count = 0
        for m in metadatas:
            score = 0
            if int(m.get("support_tickets", 0)) >= 4:
                score += 2
            if m.get("contract") == "Month-to-Month":
                score += 2
            if int(m.get("tenure", 0)) < 12:
                score += 2
                
            if score >= 5:
                high_count += 1
            elif score >= 3:
                med_count += 1
            else:
                low_count += 1
                
        return {
            "total_customers": total_customers,
            "churned_customers": churned_customers,
            "churn_rate": churn_rate,
            "average_age": average_age,
            "average_tenure": average_tenure,
            "risk_distribution": {
                "Low Risk": low_count,
                "Medium Risk": med_count,
                "High Risk": high_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate stats: {e}")


@app.get("/api/customers")
def get_customers(limit: int = Query(default=100, lte=1000)):
    """
    Get all customer metadata records stored in ChromaDB (up to limit).
    """
    try:
        db = ChromaService()
        metadatas = db.get_all_metadata()
        return metadatas[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query customers: {e}")


@app.get("/api/report/pdf/{session_id}")
def download_pdf_report(session_id: str):
    """
    Generate and download the ReportLab PDF report for the given session.
    """
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format.")
        
    memory_service = MemoryService()
    history = memory_service.history(session_id)
    
    if not history:
        raise HTTPException(status_code=404, detail="No execution data found for this session ID.")
        
    # Get latest history entry
    latest_run = history[-1]
    
    # Structure data as expected by PDF service (needs session_id, user_query, report, analysis, prediction, recommendation, validation)
    session_data = {
        "session_id": session_id,
        "user_query": latest_run.get("user_query"),
        "query_plan": latest_run.get("query_plan"),
        "analysis": latest_run.get("analysis"),
        "prediction": latest_run.get("prediction"),
        "recommendation": latest_run.get("recommendation"),
        "validation": latest_run.get("validation"),
        "report": latest_run.get("report")
    }

    # Generate PDF in temp directory
    temp_dir = tempfile.gettempdir()
    pdf_filename = f"bnp_paribas_churn_report_{session_id}.pdf"
    pdf_path = os.path.join(temp_dir, pdf_filename)
    
    try:
        PDFService.generate_report(session_data, pdf_path)
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=pdf_filename
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {e}")


@app.post("/api/ingest")
def trigger_ingestion(background_tasks: BackgroundTasks):
    """
    Asynchronously ingest BNPParibas dataset CSV into ChromaDB.
    """
    try:
        ingestion = IngestionService()
        background_tasks.add_task(ingestion.ingest)
        return {"status": "success", "message": "Dataset ingestion started in background."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger ingestion: {e}")
