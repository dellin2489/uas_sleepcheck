import json

from fastapi import APIRouter, Request

from app.config import BASE_DIR, templates

router = APIRouter()

META_PATH = BASE_DIR / "model_ai" / "model_meta.json"


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html")


@router.get("/contact")
def contact(request: Request):
    return templates.TemplateResponse(request, "contact.html")


@router.get("/panduan")
def panduan(request: Request):
    return templates.TemplateResponse(request, "panduan.html")


@router.get("/model")
def model_ai(request: Request):
    meta = None
    if META_PATH.exists():
        meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    return templates.TemplateResponse(request, "model.html", {"meta": meta})