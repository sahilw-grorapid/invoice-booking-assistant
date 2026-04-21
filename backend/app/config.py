import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

BACKEND_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BACKEND_DIR / "data" / "buchungsstapel.csv"

MAX_PDF_BYTES = 5 * 1024 * 1024
