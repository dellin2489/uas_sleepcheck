from pydantic import BaseModel, Field

class PredictionCreate(BaseModel):
    nama: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=10, le=100)
    gender: str = Field(max_length=10)
    bmi_category: str = Field(
        pattern="^(Normal|Overweight|Obese)$"
    )
    sleep_duration: float = Field(ge=1, le=24)
    physical_activity: int = Field(ge=0, le=300)
    stress_level: int = Field(ge=1, le=10)
    heart_rate: int = Field(ge=40, le=200)
    daily_steps: int = Field(ge=0, le=50000)
    systolic: int = Field(ge=70, le=220)
    diastolic: int = Field(ge=40, le=140)