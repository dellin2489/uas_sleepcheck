# ml/train_knn.py
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score,
                             classification_report, confusion_matrix)
from sklearn.model_selection import (GridSearchCV, RepeatedStratifiedKFold,
                                     StratifiedKFold, cross_val_score,
                                     train_test_split)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ---------------------------------------------------------------
# 0. PATH (script ini ada di ml/, dataset di data/)
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent / "data" / "Sleep_health_and_lifestyle_dataset.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------
# 1. LOAD DATA
# keep_default_na=False wajib: supaya label "None" tidak dibaca NaN
# ---------------------------------------------------------------
df = pd.read_csv(DATA_PATH, keep_default_na=False)
print("Ukuran awal:", df.shape)

# ---------------------------------------------------------------
# 2. PREPROCESSING
# ---------------------------------------------------------------
# a. buang duplikat (kalau tidak, baris kembar bisa bocor ke test set)
df = df.drop_duplicates(subset=[c for c in df.columns if c != "Person ID"])
print("Setelah hapus duplikat:", df.shape)
print(df["Sleep Disorder"].value_counts(), "\n")

# b. samakan kategori BMI
df["BMI Category"] = df["BMI Category"].replace({"Normal Weight": "Normal"})

# c. pecah tekanan darah "126/83" jadi dua kolom numerik
bp = df["Blood Pressure"].str.split("/", expand=True).astype(int)
df["Systolic"], df["Diastolic"] = bp[0], bp[1]

# ---------------------------------------------------------------
# 3. DEFINISI SKENARIO FITUR
# ---------------------------------------------------------------
CAT_COLS = ["Gender", "BMI Category"]

SCENARIOS = {
    "A_semua_fitur": [
        "Age", "Sleep Duration", "Physical Activity Level", "Stress Level",
        "Heart Rate", "Daily Steps", "Systolic", "Diastolic",
    ],
    "B_tanpa_sleep_duration": [
        "Age", "Physical Activity Level", "Stress Level",
        "Heart Rate", "Daily Steps", "Systolic", "Diastolic",
    ],
}

y = df["Sleep Disorder"]  # None / Insomnia / Sleep Apnea

param_grid = {
    "knn__n_neighbors": list(range(3, 22, 2)),
    "knn__weights": ["uniform", "distance"],
    "knn__metric": ["euclidean", "manhattan"],
}


def build_pipeline(num_cols):
    preprocess = ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
    ])
    return Pipeline([
        ("prep", preprocess),
        ("knn", KNeighborsClassifier()),
    ])


# ---------------------------------------------------------------
# 4. LATIH & EVALUASI TIAP SKENARIO
# ---------------------------------------------------------------
summary = []

for name, num_cols in SCENARIOS.items():
    print("=" * 60)
    print("SKENARIO:", name)
    print("=" * 60)

    X = df[num_cols + CAT_COLS]

    # --- 4a. Nested CV (angka evaluasi utama untuk laporan) ---
    inner_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    outer_cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=42)

    grid_for_cv = GridSearchCV(build_pipeline(num_cols), param_grid,
                               cv=inner_cv, scoring="f1_macro", n_jobs=1)
    nested_scores = cross_val_score(grid_for_cv, X, y, cv=outer_cv,
                                    scoring="f1_macro", n_jobs=-1)
    nested_mean, nested_std = nested_scores.mean(), nested_scores.std()
    print(f"F1-macro nested CV: {nested_mean:.4f} +/- {nested_std:.4f}")

    # --- 4b. Train/test split (hasil pelengkap + model final) ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    grid = GridSearchCV(build_pipeline(num_cols), param_grid,
                        cv=inner_cv, scoring="f1_macro", n_jobs=-1)
    grid.fit(X_train, y_train)
    print("Parameter terbaik:", grid.best_params_)
    print("F1-macro CV (train):", round(grid.best_score_, 4))

    best = grid.best_estimator_
    y_pred = best.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print("Akurasi test:", round(acc, 4))
    print(classification_report(y_test, y_pred))

    # --- 4c. Confusion matrix ---
    cm = confusion_matrix(y_test, y_pred, labels=best.classes_)
    disp = ConfusionMatrixDisplay(cm, display_labels=best.classes_)
    disp.plot(cmap="Blues")
    plt.title(f"Confusion Matrix KNN - {name}")
    plt.savefig(MODEL_DIR / f"confusion_matrix_{name}.png",
                dpi=150, bbox_inches="tight")
    plt.close()

    # --- 4d. Simpan model (pipeline utuh: scaler + encoder + KNN) ---
    model_path = MODEL_DIR / f"knn_sleep_{name}.joblib"
    joblib.dump(best, model_path)
    print("Model tersimpan:", model_path, "\n")

    summary.append({
        "Skenario": name,
        "F1-macro nested CV": round(nested_mean, 4),
        "Std": round(nested_std, 4),
        "Akurasi test": round(acc, 4),
        "Parameter": grid.best_params_,
    })

# ---------------------------------------------------------------
# 5. RINGKASAN PERBANDINGAN (untuk laporan poin 4a)
# ---------------------------------------------------------------
print("=" * 60)
print("RINGKASAN PERBANDINGAN")
print("=" * 60)
print(pd.DataFrame(summary).to_string(index=False))