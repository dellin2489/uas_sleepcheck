import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, SQLModel, create_engine

# --- Informasi Aplikasi (Dipanggil di main.py) ---
APP_NAME = "Sleep Check API"
APP_DESCRIPTION = "Aplikasi Web Klasifikasi Kualitas Tidur - UAS"
APP_VERSION = "1.0.0"

# --- Path Folder Template & Static ---
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "template"
STATIC_DIR = BASE_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# --- Memuat Kredensial Database dari File .env ---
load_dotenv(BASE_DIR.parent / ".env")

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "sleepcheck")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# --- Engine SQLModel ---
engine = create_engine(DATABASE_URL, echo=True)


# --- Dependency Injection Sesi Database ---
def get_session():
    with Session(engine) as session:
        yield session