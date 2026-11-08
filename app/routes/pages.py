from fastapi import APIRouter, Request

from app.config import templates

router = APIRouter()


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html")


@router.get("/contact")
def contact(request: Request):
    return templates.TemplateResponse(request, "contact.html")