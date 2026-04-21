import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
EXTEND_API_KEY = os.getenv("EXTEND_API_KEY")
EXTEND_EXTRACTOR_ID = os.getenv("EXTEND_EXTRACTOR_ID")

BACKEND_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BACKEND_DIR / "data" / "buchungsstapel.csv"
EXTEND_EXTRACTOR_CONFIG_PATH = BACKEND_DIR / "extend_invoice_extractor_config.json"

MAX_PDF_BYTES = 5 * 1024 * 1024
