from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
    STATIC_DIR,
)

# TODO: Sesuaikan dengan nama router di folder app/routes/
# from app.routes.sleep_route import router as sleep_router 

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

app.add_middleware(
    SessionMiddleware,
    secret_key="secret123",
)

# Menghubungkan folder static (CSS/JS)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Hubungkan router jika file router sudah dibuat:
# app.include_router(sleep_router)

@app.get("/")
def home():
    return {"message": "Server UAS Sleep Check Berhasil Jalan!"}