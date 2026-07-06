import re
from typing import Any, Dict, List
from pydantic import BaseModel, ValidationError

class GuardrailException(Exception):
    """Exception raised for guardrail validation failures."""
    pass

class GuardrailService:
    
    @staticmethod
    def validate_input(query: str) -> None:
        """
        Validate the incoming user query.
        Raises GuardrailException if validation fails.
        """
        if not query or not query.strip():
            raise GuardrailException("The user query cannot be empty.")
            
        if len(query) > 1000:
            raise GuardrailException("The query exceeds the maximum allowed length of 1000 characters.")
            
        # SQL Injection patterns
        sql_injection_patterns = [
            r"union\s+select",
            r"drop\s+table",
            r"insert\s+into",
            r"delete\s+from",
            r"update\s+.*\s+set",
            r"or\s+['\"].*['\"]\s*=\s*['\"].*['\"]"
        ]
        
        for pattern in sql_injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                raise GuardrailException("Malicious payload or SQL injection detected in the query.")
                
        # Basic context relevance check
        relevance_keywords = [
            "churn", "customer", "predict", "segment", "retention", "risk", 
            "why", "analyze", "report", "ticket", "tenure", "billing", "monthly", 
            "contract", "payment", "internet", "support", "rate", "bnp", "paribas", "list"
        ]
        
        query_lower = query.lower()
        # If the query is a simple greeting or general help, allow it
        if query_lower in ["hello", "hi", "help", "what can you do?", "explain"]:
            return
            
        # Check if query matches at least one keyword or contains numbers (like customer IDs)
        has_keyword = any(keyword in query_lower for keyword in relevance_keywords)
        has_number = any(c.isdigit() for c in query_lower)
        
        if not (has_keyword or has_number):
            raise GuardrailException(
                "The query is outside the scope of customer churn and bank portfolio analysis. "
                "Please ask a question related to churn analysis, predicting client risk, or retention strategies."
            )

    @staticmethod
    def validate_output(step_name: str, data: BaseModel) -> None:
        """
        Validate the output of a specific agentic pipeline step.
        Raises GuardrailException if constraints are violated.
        """
        try:
            # First, check model constraints
            data_dict = data.model_dump()
        except Exception as e:
            raise GuardrailException(f"Failed to dump Pydantic model for {step_name}: {e}")
            
        # 1. Validate confidence fields
        confidence = None
        if "confidence" in data_dict:
            confidence = data_dict["confidence"]
        elif "overall_confidence" in data_dict:
            confidence = data_dict["overall_confidence"]
            
        if confidence is not None:
            # We accept either 0-1 or 0-100. Let's enforce range 0 to 100.
            if confidence < 0.0 or confidence > 100.0:
                raise GuardrailException(
                    f"Output Validation Error ({step_name}): Confidence score {confidence} is out of bounds (0-100)."
                )

        # 2. Check for empty values or placeholders
        if step_name == "analysis":
            if not data_dict.get("summary") or len(data_dict["summary"].strip()) < 5:
                raise GuardrailException(f"Output Validation Error ({step_name}): Summary is empty or too short.")
                
        elif step_name == "prediction":
            if data_dict.get("customer_id") is None or data_dict["customer_id"] <= 0:
                raise GuardrailException(f"Output Validation Error ({step_name}): Invalid customer_id in prediction.")
            if not data_dict.get("reasons"):
                raise GuardrailException(f"Output Validation Error ({step_name}): Churn prediction must list reasons.")
                
        elif step_name == "recommendation":
            if data_dict.get("customer_id") is None or data_dict["customer_id"] <= 0:
                raise GuardrailException(f"Output Validation Error ({step_name}): Invalid customer_id in recommendation.")
            if not data_dict.get("retention_actions"):
                raise GuardrailException(f"Output Validation Error ({step_name}): Retention actions cannot be empty.")
                
        elif step_name == "validation":
            # Validation step itself
            pass
            
        elif step_name == "report":
            if not data_dict.get("executive_summary") or len(data_dict["executive_summary"].strip()) < 10:
                raise GuardrailException(f"Output Validation Error ({step_name}): Report executive summary is too short.")
            if not data_dict.get("key_findings"):
                raise GuardrailException(f"Output Validation Error ({step_name}): Report must contain key findings.")
                
        # 3. Explainability verification
        # All steps should contain evidence and reasoning
        if step_name in ["analysis", "prediction", "recommendation", "validation", "report"]:
            if "reasoning" in data_dict and (not data_dict["reasoning"] or len(data_dict["reasoning"].strip()) < 5):
                raise GuardrailException(f"Output Validation Error ({step_name}): Explainability reasoning is missing or too short.")
            if "evidence" in data_dict and not data_dict["evidence"]:
                # Validation could verify evidence, let's ensure evidence is populated
                raise GuardrailException(f"Output Validation Error ({step_name}): Explainability evidence is empty.")
