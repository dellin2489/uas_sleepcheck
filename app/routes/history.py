from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session
from zoneinfo import ZoneInfo

from app.config import get_session, templates
from app.services import history_service

router = APIRouter()


@router.get("/history")
def history_page(request: Request, session: Session = Depends(get_session)):
    items = history_service.get_all(session)

    wib = ZoneInfo("Asia/Jakarta")

    for item in items:
        if item.created_at is not None:
            item.created_at = item.created_at.astimezone(wib)

    return templates.TemplateResponse(
        request,
        "history.html",
        {"items": items}
    )


@router.post("/history/{prediction_id}/delete")
def delete_history(
    prediction_id: int,
    session: Session = Depends(get_session)
):
    history_service.delete_prediction(session, prediction_id)

    return RedirectResponse(
        url="/history",
        status_code=303
    )