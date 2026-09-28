import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3307))
DB_USER = os.getenv("DB_USER", "talktodata_ro")
DB_PASSWORD = os.getenv("DB_PASSWORD", "readonly123")
DB_NAME = os.getenv("DB_NAME", "talktodata")
QUERY_TIMEOUT_MS = int(os.getenv("QUERY_TIMEOUT_MS", 5000))

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-5"
MAX_TOKENS = 1024
