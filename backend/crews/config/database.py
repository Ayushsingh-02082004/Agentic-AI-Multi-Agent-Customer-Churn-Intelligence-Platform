import os
import psycopg
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]

load_dotenv(ROOT / ".env")

def get_connection():
    return psycopg.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        dbname=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
    )


# print("HOST:", os.getenv("DATABASE_HOST"))
# print("DB:", os.getenv("DATABASE_NAME"))
# print("USER:", os.getenv("DATABASE_USER"))