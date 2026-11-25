import os

from dotenv import load_dotenv

load_dotenv()

# MySQL connection
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "jarvis_db")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# AI brain (Anthropic Claude API). Leave blank to run in offline demo mode.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "claude-sonnet-5-5")

SYSTEM_PROMPT = (
    "You are JARVIS, a smart, polite and slightly witty personal AI assistant. "
    "Keep answers short and clear, because they may be spoken aloud. "
    "Use the user's saved notes if they are relevant."
)

# How many past messages are sent to the AI for context
HISTORY_LIMIT = 20
