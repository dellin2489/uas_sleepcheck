# ml/recommend.py
from itertools import product
from pathlib import Path

import joblib
import pandas as pd

MODEL_DIR = Path(__file__).resolve().parent
_rf = joblib.load(MODEL_DIR / "rf_sleep_quality.joblib")
_knn = joblib.load(MODEL_DIR / "knn_sleep_B_tanpa_sleep_duration.joblib")

# Opsi perubahan yang realistis (hanya faktor gaya hidup)
STEP_OPTIONS = [0, 1000, 2000, 3000]    # tambahan langkah/hari
ACTIVITY_OPTIONS = [0, 10, 20, 30]      # tambahan menit aktivitas/hari
STRESS_OPTIONS = [0, 1, 2, 3]           # penurunan skala stres

JENIS = {
    "stres": "Kelola stres",
    "langkah": "Perbanyak langkah harian",
    "aktivitas": "Tambah aktivitas fisik",
    "kombinasi": "Kombinasi beberapa kebiasaan",
}


def _knn_label(user: dict):
    """Prediksi gangguan tidur + probabilitas per kelas."""
    df = pd.DataFrame([user])
    label = str(_knn.predict(df)[0])
    proba = dict(zip(_knn.classes_, _knn.predict_proba(df)[0].round(3)))
    return label, {k: float(v) for k, v in proba.items()}


def _jenis(d_steps, d_act, d_stress):
    aktif = [n for n, d in (("langkah", d_steps), ("aktivitas", d_act),
                            ("stres", d_stress)) if d > 0]
    return aktif[0] if len(aktif) == 1 else "kombinasi"


def _deskripsi(d_steps, d_act, d_stress):
    bagian = []
    if d_steps:
        bagian.append(f"tambah {d_steps:,} langkah/hari".replace(",", "."))
    if d_act:
        bagian.append(f"tambah {d_act} menit aktivitas fisik/hari")
    if d_stress:
        bagian.append(f"turunkan tingkat stres sebanyak {d_stress} poin")
    return ", ".join(bagian)


def analyze(user: dict):
    """
    user: dict dengan kolom yang sama seperti saat training
    (Age, Gender, BMI Category, Physical Activity Level, Stress Level,
     Heart Rate, Daily Steps, Systolic, Diastolic).
    """
    base_score = float(_rf.predict(pd.DataFrame([user]))[0])
    base_label, base_proba = _knn_label(user)

    # 1. buat semua skenario
    skenario = []
    for d_steps, d_act, d_stress in product(STEP_OPTIONS, ACTIVITY_OPTIONS,
                                            STRESS_OPTIONS):
        if d_steps == d_act == d_stress == 0:
            continue
        new = dict(user)
        new["Daily Steps"] = user["Daily Steps"] + d_steps
        new["Physical Activity Level"] = user["Physical Activity Level"] + d_act
        new["Stress Level"] = max(user["Stress Level"] - d_stress, 1)
        # kalau stres sudah mendekati 1, penurunan nyata bisa lebih kecil
        real_stress = user["Stress Level"] - new["Stress Level"]
        skenario.append((d_steps, d_act, real_stress, new))

    scores = _rf.predict(pd.DataFrame([s[3] for s in skenario]))

    kandidat = []
    for (d_steps, d_act, d_stress, new), s in zip(skenario, scores):
        gain = float(s) - base_score
        if gain <= 0:
            continue
        effort = d_steps / 1000 + d_act / 10 + d_stress
        if effort == 0:
            continue
        kandidat.append({
            "jenis": _jenis(d_steps, d_act, d_stress),
            "deskripsi": _deskripsi(d_steps, d_act, d_stress),
            "skor_baru": round(float(s), 2),
            "kenaikan": round(gain, 2),
            "efisiensi": gain / effort,
            "_new": new,
        })

    # 2. ambil SATU terbaik per jenis supaya tampilan bervariasi
    #    - stres/langkah/aktivitas: paling efisien (kenaikan per usaha)
    #    - kombinasi: kenaikan terbesar
    hasil = []
    for jenis in ("stres", "langkah", "aktivitas", "kombinasi"):
        grup = [k for k in kandidat if k["jenis"] == jenis]
        if not grup:
            continue
        kunci = "kenaikan" if jenis == "kombinasi" else "efisiensi"
        best = max(grup, key=lambda k: k[kunci])
        label, proba = _knn_label(best.pop("_new"))
        best.pop("efisiensi")
        best["judul"] = JENIS[jenis]
        best["prediksi_knn"] = label
        best["proba_knn"] = proba
        hasil.append(best)

    hasil.sort(key=lambda r: r["kenaikan"], reverse=True)
    return {
        "skor_saat_ini": round(base_score, 2),
        "prediksi_knn": base_label,
        "proba_knn": base_proba,
        "rekomendasi": hasil,
    }


if __name__ == "__main__":
    contoh = {"Age": 35, "Gender": "Male", "BMI Category": "Overweight",
              "Physical Activity Level": 30, "Stress Level": 8,
              "Heart Rate": 80, "Daily Steps": 4000,
              "Systolic": 130, "Diastolic": 85}
    out = analyze(contoh)
    print("Skor saat ini :", out["skor_saat_ini"])
    print("Prediksi KNN  :", out["prediksi_knn"], out["proba_knn"])
    for r in out["rekomendasi"]:
        print(f"\n[{r['judul']}] {r['deskripsi']}")
        print(f"  skor {out['skor_saat_ini']} -> {r['skor_baru']} "
              f"(+{r['kenaikan']}), KNN: {r['prediksi_knn']}")