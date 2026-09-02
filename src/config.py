import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "talktodata")
DB_PASSWORD = os.getenv("DB_PASSWORD", "talktodata123")
DB_NAME = os.getenv("DB_NAME", "talktodata")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-5"
MAX_TOKENS = 300