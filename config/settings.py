from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

load_dotenv()

DB_URL = "sqlite:///content.db"

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

logger.info(f'LANGSMITH_TRACING: {os.environ.get("LANGSMITH_TRACING")}')
logger.info(f'LANGSMITH_API_KEY is set: {"Yes" if os.environ.get("LANGSMITH_API_KEY") else "No"}')