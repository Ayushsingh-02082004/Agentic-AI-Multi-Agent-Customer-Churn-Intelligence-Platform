from backend.crews.config.database import get_connection
from backend.schemas.memory_record import MemoryRecord
import json


class MemoryService:

    def save(self, record: MemoryRecord):

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO memory
            (
                session_id,
                user_query,
                query_plan,
                retrieval_context,
                analysis_result,
                prediction_result,
                recommendation_result,
                validation_result,
                report_result,
                created_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT(session_id)
            DO UPDATE SET
                query_plan = EXCLUDED.query_plan,
                retrieval_context = EXCLUDED.retrieval_context,
                analysis_result = EXCLUDED.analysis_result,
                prediction_result = EXCLUDED.prediction_result,
                recommendation_result = EXCLUDED.recommendation_result,
                validation_result = EXCLUDED.validation_result,
                report_result = EXCLUDED.report_result
            """,
            (
                str(record.session_id),
                record.user_query,
                json.dumps(record.query_plan),
                json.dumps(record.retrieval_context) if record.retrieval_context else None,
                json.dumps(record.analysis) if record.analysis else None,
                json.dumps(record.prediction) if record.prediction else None,
                json.dumps(record.recommendation) if record.recommendation else None,
                json.dumps(record.validation) if record.validation else None,
                json.dumps(record.report) if record.report else None,
                record.created_at
            )
        )

        conn.commit()

        cur.close()
        conn.close()

    def history(self, session_id: str):

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                user_query,
                query_plan,
                retrieval_context,
                analysis_result,
                prediction_result,
                recommendation_result,
                validation_result,
                report_result,
                created_at
            FROM memory
            WHERE session_id=%s
            ORDER BY created_at
            """,
            (str(session_id),)
        )

        rows = cur.fetchall()

        cur.close()
        conn.close()

        records = []
        for row in rows:
            records.append({
                "user_query": row[0],
                "query_plan": row[1] if isinstance(row[1], dict) else (json.loads(row[1]) if row[1] else {}),
                "retrieval_context": row[2] if isinstance(row[2], dict) else (json.loads(row[2]) if row[2] else {}),
                "analysis": row[3] if isinstance(row[3], dict) else (json.loads(row[3]) if row[3] else {}),
                "prediction": row[4] if isinstance(row[4], dict) else (json.loads(row[4]) if row[4] else {}),
                "recommendation": row[5] if isinstance(row[5], dict) else (json.loads(row[5]) if row[5] else {}),
                "validation": row[6] if isinstance(row[6], dict) else (json.loads(row[6]) if row[6] else {}),
                "report": row[7] if isinstance(row[7], dict) else (json.loads(row[7]) if row[7] else {}),
                "created_at": row[8].isoformat() if hasattr(row[8], "isoformat") else str(row[8])
            })

        return records