from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import APP_DESCRIPTION, APP_NAME, APP_VERSION, STATIC_DIR
from app.routes import history, pages, predict

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(pages.router)
app.include_router(predict.router)
app.include_router(history.router)