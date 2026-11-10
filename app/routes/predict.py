from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.config import get_session, templates
from app.schemas.prediction import PredictionCreate
from app.services.predict_service import (
    create_prediction,
    get_by_id,
)

router = APIRouter()


@router.get("/predict")
def predict_page(request: Request):
    return templates.TemplateResponse(
        request,
        "predict.html",
        {
            "errors": [],
            "values": {},
        },
    )


@router.post("/predict")
def create_predict(
    request: Request,

    nama: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    bmi_category: str = Form(...),
    sleep_duration: float = Form(...),
    physical_activity: int = Form(...),
    stress_level: int = Form(...),
    heart_rate: int = Form(...),
    daily_steps: int = Form(...),
    systolic: int = Form(...),
    diastolic: int = Form(...),

    session: Session = Depends(get_session),
):

    values = {
        "nama": nama,
        "age": age,
        "gender": gender,
        "bmi_category": bmi_category,
        "sleep_duration": sleep_duration,
        "physical_activity": physical_activity,
        "stress_level": stress_level,
        "heart_rate": heart_rate,
        "daily_steps": daily_steps,
        "systolic": systolic,
        "diastolic": diastolic,
    }

    # Validasi backend
    try:
        data = PredictionCreate(**values)

    except Exception as e:
        return templates.TemplateResponse(
            request,
            "predict.html",
            {
                "errors": [str(e)],
                "values": values,
            },
            status_code=422,
        )

    # Jalankan AI dan simpan hasilnya
    prediction = create_prediction(
        data,
        session,
    )

    # Setelah berhasil, menuju halaman hasil
    return RedirectResponse(
        url=f"/history/{prediction.id}",
        status_code=303,
    )


@router.get("/history/{prediction_id}")
def prediction_result(
    request: Request,
    prediction_id: int,
    session: Session = Depends(get_session),
):

    item = get_by_id(
        prediction_id,
        session,
    )

    if item is None:
        return templates.TemplateResponse(
            request,
            "result.html",
            {
                "item": None,
                "error": "Data prediksi tidak ditemukan.",
            },
            status_code=404,
        )

    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "item": item,
            "error": None,
        },
    )