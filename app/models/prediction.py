from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Numeric, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Prediction(SQLModel, table=True):
    __tablename__ = "predictions"

    id: Optional[int] = Field(default=None, primary_key=True)
    nama: str = Field(max_length=100)

    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    bmi_category = Column(String(20), nullable=False)
    physical_activity = Column(Integer, nullable=False)
    stress_level = Column(Integer, nullable=False)
    heart_rate = Column(Integer, nullable=False)
    daily_steps = Column(Integer, nullable=False)
    systolic = Column(Integer, nullable=False)
    diastolic = Column(Integer, nullable=False)

    knn_label = Column(String(20), nullable=False)
    knn_proba = Column(JSONB, nullable=False)
    rf_score = Column(Numeric(4, 2), nullable=False)
    recommendations = Column(JSONB, nullable=False)

    created_at = Column(DateTime, server_default=func.now())