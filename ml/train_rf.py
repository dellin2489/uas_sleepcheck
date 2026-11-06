# ml/train_rf.py
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import (
    GridSearchCV, 
    KFold, cross_val_score,
    train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent / "data" / "Sleep_health_and_lifestyle_dataset.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

# 1. LOAD & PREPROCESSING (sama seperti KNN)
df = pd.read_csv(DATA_PATH, keep_default_na=False)
df = df.drop_duplicates(subset=[c for c in df.columns if c != "Person ID"])
df["BMI Category"] = df["BMI Category"].replace({"Normal Weight": "Normal"})
bp = df["Blood Pressure"].str.split("/", expand=True).astype(int)
df["Systolic"], df["Diastolic"] = bp[0], bp[1]

# 2. FITUR & TARGET (tanpa Sleep Duration)
num_cols = ["Age", "Physical Activity Level", "Stress Level",
            "Heart Rate", "Daily Steps", "Systolic", "Diastolic"]
cat_cols = ["Gender", "BMI Category"]
X = df[num_cols + cat_cols]
y = df["Quality of Sleep"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 3. PIPELINE (RF tidak butuh scaling)
prep = ColumnTransformer(
    [("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)],
    remainder="passthrough",
)
pipe = Pipeline([
    ("prep", prep),
    ("rf", RandomForestRegressor(random_state=42)),
])

param_grid = {
    "rf__n_estimators": [100, 300],
    "rf__max_depth": [None, 5, 10],
    "rf__min_samples_leaf": [1, 2, 4],
}
cv = KFold(n_splits=5, shuffle=True, random_state=42)
grid = GridSearchCV(pipe, param_grid, cv=cv,
                    scoring="neg_mean_absolute_error", n_jobs=-1)
grid.fit(X_train, y_train)
best = grid.best_estimator_
print("Parameter terbaik:", grid.best_params_)

# 4. EVALUASI
pred = best.predict(X_test)
print("MAE test :", round(mean_absolute_error(y_test, pred), 3))
print("R2 test  :", round(r2_score(y_test, pred), 3))
cv_r2 = cross_val_score(best, X, y, cv=cv, scoring="r2")
print("R2 CV    :", round(cv_r2.mean(), 3), "+/-", round(cv_r2.std(), 3))

# 5. FEATURE IMPORTANCE
names = best.named_steps["prep"].get_feature_names_out()
names = [n.split("__")[-1] for n in names]
imp = pd.Series(best.named_steps["rf"].feature_importances_, index=names)
imp = imp.sort_values()
print("\nFeature importance:\n", imp.sort_values(ascending=False).round(3))

imp.plot(kind="barh", figsize=(7, 5))
plt.title("Feature Importance Random Forest (Quality of Sleep)")
plt.tight_layout()
plt.savefig(MODEL_DIR / "rf_feature_importance.png", dpi=150)
plt.close()

# 6. SIMPAN MODEL
joblib.dump(best, MODEL_DIR / "rf_sleep_quality.joblib")
print("Model tersimpan: rf_sleep_quality.joblib")