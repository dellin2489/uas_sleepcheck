from sqlalchemy import Column, DateTime, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB

from app.config import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)

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