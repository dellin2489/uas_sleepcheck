# ml/build_model_report.py
# Menghitung metrik, tabel, dan grafik untuk halaman "Model AI".
# Jalankan dari folder utama proyek:  python ml/build_model_report.py
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (accuracy_score, confusion_matrix,
                             precision_recall_fscore_support)
from sklearn.model_selection import (GridSearchCV, RepeatedStratifiedKFold,
                                     StratifiedKFold, cross_val_score,
                                     train_test_split)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "Sleep_health_and_lifestyle_dataset.csv"
META_PATH = ROOT / "app" / "model_ai" / "model_meta.json"
IMG_DIR = ROOT / "app" / "static" / "model"
IMG_DIR.mkdir(parents=True, exist_ok=True)
META_PATH.parent.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------
# 1. DATA (sama persis dengan train_knn.py)
# ---------------------------------------------------------------
raw = pd.read_csv(DATA_PATH, keep_default_na=False)
rows_raw = len(raw)
df = raw.drop_duplicates(subset=[c for c in raw.columns if c != "Person ID"]).copy()
df["BMI Category"] = df["BMI Category"].replace({"Normal Weight": "Normal"})
bp = df["Blood Pressure"].str.split("/", expand=True).astype(int)
df["Systolic"], df["Diastolic"] = bp[0], bp[1]

NUM_A = ["Age", "Sleep Duration", "Physical Activity Level", "Stress Level",
         "Heart Rate", "Daily Steps", "Systolic", "Diastolic"]
NUM_B = [c for c in NUM_A if c != "Sleep Duration"]
CAT = ["Gender", "BMI Category"]
y = df["Sleep Disorder"]
X = df[NUM_A + CAT]

PARAM_GRID = {
    "knn__n_neighbors": list(range(3, 22, 2)),
    "knn__weights": ["uniform", "distance"],
    "knn__metric": ["euclidean", "manhattan"],
}
CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)


def build_pipe(num_cols):
    prep = ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT),
    ])
    return Pipeline([("prep", prep), ("knn", KNeighborsClassifier())])


def scores(y_true, y_pred):
    p, r, f, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0)
    return {"accuracy": accuracy_score(y_true, y_pred),
            "precision": p, "recall": r, "f1": f}


def rnd(d, n=4):
    return {k: round(float(v), n) for k, v in d.items()}


# ---------------------------------------------------------------
# 2. MODEL UTAMA (skenario A: dengan Sleep Duration)
# ---------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

grid = GridSearchCV(build_pipe(NUM_A), PARAM_GRID, cv=CV,
                    scoring="f1_macro", n_jobs=-1)
grid.fit(X_train, y_train)
best = grid.best_estimator_
classes = list(best.classes_)

pred_train = best.predict(X_train)
pred_test = best.predict(X_test)
train_m = scores(y_train, pred_train)
test_m = scores(y_test, pred_test)

base = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
base_m = scores(y_test, base.predict(X_test))

# nested CV (angka evaluasi utama)
outer = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=42)
nested = cross_val_score(
    GridSearchCV(build_pipe(NUM_A), PARAM_GRID, cv=CV, scoring="f1_macro", n_jobs=1),
    X, y, cv=outer, scoring="f1_macro", n_jobs=-1)

# laporan per kelas
p, r, f, s = precision_recall_fscore_support(
    y_test, pred_test, labels=classes, zero_division=0)
report = {c: {"precision": round(float(p[i]), 4), "recall": round(float(r[i]), 4),
              "f1": round(float(f[i]), 4), "support": int(s[i])}
          for i, c in enumerate(classes)}
cm = confusion_matrix(y_test, pred_test, labels=classes)

# 5 percobaan parameter terbaik
res = pd.DataFrame(grid.cv_results_).sort_values(
    ["rank_test_score", "param_knn__n_neighbors"]).reset_index(drop=True)
best_cv = float(res.loc[0, "mean_test_score"])
trials = []
for i in range(5):
    row = res.loc[i]
    trials.append({
        "label": f"Percobaan {i + 1}",
        "n_neighbors": int(row["param_knn__n_neighbors"]),
        "weights": str(row["param_knn__weights"]),
        "metric": str(row["param_knn__metric"]),
        "f1_cv": round(float(row["mean_test_score"]), 4),
        "delta": round(best_cv - float(row["mean_test_score"]), 4),
    })

# ---------------------------------------------------------------
# 3. ANALISIS SLEEP DURATION (dengan vs tanpa)
# ---------------------------------------------------------------
gridB = GridSearchCV(build_pipe(NUM_B), PARAM_GRID, cv=CV,
                     scoring="f1_macro", n_jobs=-1)
gridB.fit(X_train[NUM_B + CAT], y_train)
predB = gridB.best_estimator_.predict(X_test[NUM_B + CAT])
mB = scores(y_test, predB)

sd = df["Sleep Duration"]
grand = sd.mean()
ss_total = float(((sd - grand) ** 2).sum())
ss_between = float(sum(len(g) * (g.mean() - grand) ** 2
                       for _, g in sd.groupby(y)))
eta2 = ss_between / ss_total
means = {c: round(float(sd[y == c].mean()), 2) for c in classes}

sleep_analysis = {
    "eta_squared": round(eta2, 4),
    "means": means,
    "dengan": {"cv_f1": round(float(grid.best_score_), 4),
               "test_accuracy": round(test_m["accuracy"], 4),
               "test_f1": round(test_m["f1"], 4)},
    "tanpa": {"cv_f1": round(float(gridB.best_score_), 4),
              "test_accuracy": round(mB["accuracy"], 4),
              "test_f1": round(mB["f1"], 4)},
}

# ---------------------------------------------------------------
# 4. GRAFIK
# ---------------------------------------------------------------
plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False})
COLORS = {"None": "#2a7f8e", "Insomnia": "#e08a3c", "Sleep Apnea": "#8a5fbf"}


def save(name):
    plt.tight_layout()
    plt.savefig(IMG_DIR / name, dpi=130, bbox_inches="tight")
    plt.close()


# a. pie distribusi kelas
counts = y.value_counts().reindex(["None", "Insomnia", "Sleep Apnea"])
plt.figure(figsize=(5.5, 5))
plt.pie(counts.values, labels=[f"{k} ({v})" for k, v in counts.items()],
        colors=[COLORS[k] for k in counts.index], autopct="%1.1f%%",
        startangle=90, wedgeprops={"edgecolor": "white"})
plt.title("Distribusi kelas Sleep Disorder")
save("pie_kelas.png")

# b. heatmap korelasi
corr = df[NUM_A].corr()
plt.figure(figsize=(7.5, 6.2))
im = plt.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
plt.colorbar(im, fraction=0.046)
plt.xticks(range(len(NUM_A)), NUM_A, rotation=45, ha="right")
plt.yticks(range(len(NUM_A)), NUM_A)
for i in range(len(NUM_A)):
    for j in range(len(NUM_A)):
        plt.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center",
                 fontsize=8, color="white" if abs(corr.values[i, j]) > 0.6 else "black")
plt.title("Korelasi antar fitur numerik")
save("korelasi.png")

# c. confusion matrix
plt.figure(figsize=(5.2, 4.6))
plt.imshow(cm, cmap="Blues")
plt.xticks(range(len(classes)), classes)
plt.yticks(range(len(classes)), classes)
for i in range(len(classes)):
    for j in range(len(classes)):
        plt.text(j, i, int(cm[i, j]), ha="center", va="center",
                 color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=13)
plt.xlabel("Prediksi")
plt.ylabel("Aktual")
plt.title("Confusion matrix (data uji)")
save("confusion_matrix.png")

# d. line plot: pengaruh k terhadap F1-macro CV
plt.figure(figsize=(7, 4.2))
for metric, color in (("manhattan", "#2a7f8e"), ("euclidean", "#e08a3c")):
    sub = res[res["param_knn__metric"] == metric]
    line = sub.groupby("param_knn__n_neighbors")["mean_test_score"].max()
    plt.plot(line.index, line.values, marker="o", color=color, label=metric)
plt.axvline(grid.best_params_["knn__n_neighbors"], color="gray", linestyle="--",
            linewidth=1)
plt.xlabel("Jumlah tetangga (k)")
plt.ylabel("F1-macro CV (5-fold)")
plt.title("Pengaruh nilai k terhadap F1-macro")
plt.xticks(sorted(res["param_knn__n_neighbors"].unique()))
plt.legend(title="Jarak")
plt.grid(alpha=0.25)
save("k_vs_f1.png")

# e. boxplot durasi tidur per kelas
order = ["None", "Insomnia", "Sleep Apnea"]
plt.figure(figsize=(6, 4.2))
bp_ = plt.boxplot([sd[y == c] for c in order], tick_labels=order, patch_artist=True,
                  medianprops={"color": "black"})
for patch, c in zip(bp_["boxes"], order):
    patch.set_facecolor(COLORS[c])
    patch.set_alpha(0.8)
plt.ylabel("Durasi tidur (jam)")
plt.title("Durasi tidur menurut kelas")
plt.grid(axis="y", alpha=0.25)
save("boxplot_durasi.png")

# ---------------------------------------------------------------
# 5. SIMPAN META
# ---------------------------------------------------------------
meta = {
    "dataset": {
        "rows_raw": rows_raw,
        "rows_clean": int(len(df)),
        "class_counts": {k: int(v) for k, v in counts.items()},
        "features": NUM_A + CAT,
    },
    "train_rows": int(len(X_train)),
    "test_rows": int(len(X_test)),
    "classes": classes,
    "best_params": {
        "n_neighbors": int(grid.best_params_["knn__n_neighbors"]),
        "weights": grid.best_params_["knn__weights"],
        "metric": grid.best_params_["knn__metric"],
    },
    "cv_f1": round(float(grid.best_score_), 4),
    "nested_cv": {"mean": round(float(nested.mean()), 4),
                  "std": round(float(nested.std()), 4)},
    "train_metrics": rnd(train_m),
    "test_metrics": rnd(test_m),
    "baseline_metrics": rnd(base_m),
    "report": report,
    "confusion": {"labels": classes, "matrix": cm.tolist()},
    "trials": trials,
    "total_trials": int(len(res)),
    "sleep_analysis": sleep_analysis,
}
META_PATH.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
print("Selesai.")
print("Meta  :", META_PATH)
print("Grafik:", IMG_DIR)
print("Params:", meta["best_params"], "| F1 CV:", meta["cv_f1"],
      "| nested:", meta["nested_cv"])
print("Test  :", meta["test_metrics"])