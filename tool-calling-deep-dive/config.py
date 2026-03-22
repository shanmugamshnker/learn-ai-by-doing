"""
Central configuration — all settings in one place.
Every exercise imports from here.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- LLM Settings ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MODEL = "openai/gpt-oss-120b"

# --- LLM Client ---
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url=GROQ_BASE_URL,
)

# --- Database Settings ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "catalog_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "catalog_pass")
DB_NAME = os.getenv("DB_NAME", "catalog_db")
