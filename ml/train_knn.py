# ml/train_knn.py
# Melatih model KNN final (dengan Sleep Duration) dan menyimpannya untuk website.
# Jalankan dari folder utama proyek:  python ml/train_knn.py
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import (GridSearchCV, StratifiedKFold,
                                     train_test_split)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "Sleep_health_and_lifestyle_dataset.csv"
MODEL_PATH = ROOT / "app" / "model_ai" / "knn_sleep_model.joblib"

# 1. LOAD DATA
# keep_default_na=False wajib: supaya label "None" tidak dibaca NaN
df = pd.read_csv(DATA_PATH, keep_default_na=False)
print("Ukuran awal:", df.shape)

# 2. PREPROCESSING
df = df.drop_duplicates(subset=[c for c in df.columns if c != "Person ID"])
print("Setelah hapus duplikat:", df.shape)
df["BMI Category"] = df["BMI Category"].replace({"Normal Weight": "Normal"})
bp = df["Blood Pressure"].str.split("/", expand=True).astype(int)
df["Systolic"], df["Diastolic"] = bp[0], bp[1]

# 3. FITUR DAN TARGET
num_cols = ["Age", "Sleep Duration", "Physical Activity Level", "Stress Level",
            "Heart Rate", "Daily Steps", "Systolic", "Diastolic"]
cat_cols = ["Gender", "BMI Category"]
X = df[num_cols + cat_cols]
y = df["Sleep Disorder"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 4. PIPELINE (scaling wajib untuk KNN karena berbasis jarak)
pipe = Pipeline([
    ("prep", ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ])),
    ("knn", KNeighborsClassifier()),
])

# 5. TUNING
param_grid = {
    "knn__n_neighbors": list(range(3, 22, 2)),
    "knn__weights": ["uniform", "distance"],
    "knn__metric": ["euclidean", "manhattan"],
}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
grid = GridSearchCV(pipe, param_grid, cv=cv, scoring="f1_macro", n_jobs=-1)
grid.fit(X_train, y_train)
print("Parameter terbaik:", grid.best_params_)
print("F1-macro CV:", round(grid.best_score_, 4))

# 6. EVALUASI
best = grid.best_estimator_
y_pred = best.predict(X_test)
print("Akurasi uji:", round(accuracy_score(y_test, y_pred), 4))
print(classification_report(y_test, y_pred))

# 7. SIMPAN MODEL (pipeline utuh: scaler + encoder + KNN)
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(best, MODEL_PATH)
print("Model tersimpan:", MODEL_PATH)
print("Versi scikit-learn:", sklearn.__version__)