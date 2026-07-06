import os
import psycopg
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

def get_postgres_connection():
    # Connect to default postgres DB first to create our app DB if it doesn't exist
    return psycopg.connect(
        host=os.getenv("DATABASE_HOST", "localhost"),
        port=os.getenv("DATABASE_PORT", "5432"),
        dbname="postgres",
        user=os.getenv("DATABASE_USER", "postgres"),
        password=os.getenv("DATABASE_PASSWORD", "postgres"),
        autocommit=True
    )

def get_app_connection():
    return psycopg.connect(
        host=os.getenv("DATABASE_HOST", "localhost"),
        port=os.getenv("DATABASE_PORT", "5432"),
        dbname=os.getenv("DATABASE_NAME", "customer_churn_ai"),
        user=os.getenv("DATABASE_USER", "postgres"),
        password=os.getenv("DATABASE_PASSWORD", "postgres"),
        autocommit=True
    )

def init_db():
    db_name = os.getenv("DATABASE_NAME", "customer_churn_ai")
    print(f"Connecting to Postgres to verify DB '{db_name}' exists...")
    
    # 1. Create DB if not exists
    try:
        conn = get_postgres_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone()
        
        if not exists:
            print(f"Database '{db_name}' does not exist. Creating...")
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Database '{db_name}' exists.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to check/create database using postgres connection: {e}")
        print("Will attempt direct connection to the application database.")

    # 2. Connect to the application database and create the table
    print("Initializing tables...")
    app_conn = get_app_connection()
    app_cur = app_conn.cursor()
    
    # We create the memory table with columns for every step including explainability and validation.
    app_cur.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            session_id UUID PRIMARY KEY,
            user_query TEXT,
            query_plan JSONB,
            retrieval_context JSONB,
            analysis_result JSONB,
            prediction_result JSONB,
            recommendation_result JSONB,
            validation_result JSONB,
            report_result JSONB,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    print("Table 'memory' verified/created successfully.")
    app_cur.close()
    app_conn.close()

if __name__ == "__main__":
    init_db()
