import os
from crewai import LLM
from pathlib import Path
import dotenv


ROOT = Path(__file__).resolve().parents[3]
dotenv.load_dotenv(ROOT / ".env")

# print("ROOT:", ROOT)
# print("ENV EXISTS:", (ROOT / ".env").exists())
# print("OLLAMA_API_KEY:", os.getenv("OLLAMA_API_KEY"))

llm = LLM(
    model="gemma4:31b-cloud",
    base_url="https://ollama.com/v1",
    api_key=os.getenv("OLLAMA_API_KEY"),
)