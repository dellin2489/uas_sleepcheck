from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent / "knn_sleep_A_semua_fitur.joblib"
_knn = joblib.load(MODEL_PATH)


def predict(user: dict) -> dict:
    """
    user: Age, Gender, BMI Category, Sleep Duration, Physical Activity Level,
          Stress Level, Heart Rate, Daily Steps, Systolic, Diastolic
    """
    df = pd.DataFrame([user])
    label = str(_knn.predict(df)[0])
    proba = dict(zip(_knn.classes_, _knn.predict_proba(df)[0].round(3)))
    return {
        "prediksi": label,
        "proba": {k: float(v) for k, v in proba.items()},
    }


if __name__ == "__main__":
    contoh = {"Age": 35, "Gender": "Male", "BMI Category": "Overweight",
              "Sleep Duration": 6.2, "Physical Activity Level": 30,
              "Stress Level": 8, "Heart Rate": 80, "Daily Steps": 4000,
              "Systolic": 130, "Diastolic": 85}
    print(predict(contoh))