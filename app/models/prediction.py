from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Numeric, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Prediction(SQLModel, table=True):
    __tablename__ = "predictions"

    id: Optional[int] = Field(default=None, primary_key=True)
    nama: str = Field(max_length=100)

    age: int
    gender: str = Field(max_length=10)
    bmi_category: str = Field(max_length=20)
    physical_activity: int
    stress_level: int
    heart_rate: int
    daily_steps: int
    systolic: int
    diastolic: int

    knn_label: str = Field(max_length=20)
    knn_proba: dict = Field(sa_column=Column(JSONB, nullable=False))
    rf_score: float = Field(sa_column=Column(Numeric(4, 2, asdecimal=False), nullable=False))
    recommendations: list = Field(sa_column=Column(JSONB, nullable=False))

    created_at: Optional[datetime] = Field(
        default=None, sa_column_kwargs={"server_default": func.now()}
    )