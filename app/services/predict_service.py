from sqlmodel import Session

from app.model_ai.predictor import predict
from app.models.prediction import Prediction


def create_prediction(data, session: Session):

    # Data dari form diubah ke format yang dibutuhkan predictor.py
    user = {
        "Age": data.age,
        "Gender": data.gender,
        "BMI Category": data.bmi_category,
        "Sleep Duration": data.sleep_duration,
        "Physical Activity Level": data.physical_activity,
        "Stress Level": data.stress_level,
        "Heart Rate": data.heart_rate,
        "Daily Steps": data.daily_steps,
        "Systolic": data.systolic,
        "Diastolic": data.diastolic,
    }

    # Jalankan model KNN
    result = predict(user)

    # Buat object database
    prediction = Prediction(
        nama=data.nama,
        age=data.age,
        gender=data.gender,
        bmi_category=data.bmi_category,
        sleep_duration=data.sleep_duration,
        physical_activity=data.physical_activity,
        stress_level=data.stress_level,
        heart_rate=data.heart_rate,
        daily_steps=data.daily_steps,
        systolic=data.systolic,
        diastolic=data.diastolic,

        # Hasil dari KNN
        knn_label=result["prediksi"],
        knn_proba=result["proba"],
    )

    # Simpan ke database
    session.add(prediction)
    session.commit()
    session.refresh(prediction)

    return prediction


def get_by_id(prediction_id: int, session: Session):

    return session.get(Prediction, prediction_id)