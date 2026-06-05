# app/config.py
# Central config — all shared settings in one place.
# If you need to change a path or model name, change it once here only.

from pathlib import Path

BASE_DIR    = Path(__file__).resolve().parent.parent
DATA_DIR    = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
CHROMA_DIR  = BASE_DIR / "chroma_db"

# "all-MiniLM-L6-v2" = small 80MB BERT model, fast and accurate for similarity
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SPACY_MODEL     = "en_core_web_sm"
SKILLS_FILE     = DATA_DIR / "skills_master.csv"