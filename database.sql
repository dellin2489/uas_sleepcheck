
CREATE TABLE IF NOT EXISTS predictions (
    id                SERIAL PRIMARY KEY,
    nama              VARCHAR(100) NOT NULL,

    -- input user (sama persis dengan kolom saat training)
    age               INTEGER      NOT NULL,
    gender            VARCHAR(10)  NOT NULL,
    bmi_category      VARCHAR(20)  NOT NULL,
    physical_activity INTEGER      NOT NULL,
    stress_level      INTEGER      NOT NULL,
    heart_rate        INTEGER      NOT NULL,
    daily_steps       INTEGER      NOT NULL,
    systolic          INTEGER      NOT NULL,
    diastolic         INTEGER      NOT NULL,

    -- hasil AI
    knn_label         VARCHAR(20)  NOT NULL,   -- None / Insomnia / Sleep Apnea
    knn_proba         JSONB        NOT NULL,   -- {"Insomnia": 0.556, ...}
    rf_score          NUMERIC(4,2) NOT NULL,   -- estimasi kualitas tidur
    recommendations   JSONB        NOT NULL,   -- daftar kartu rekomendasi

    created_at        TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);