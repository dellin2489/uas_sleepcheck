-- Buat database "sleepcheck" dulu di pgAdmin, lalu jalankan file ini di database tersebut.
CREATE TABLE IF NOT EXISTS predictions (
    id                SERIAL PRIMARY KEY,
    nama              VARCHAR(100) NOT NULL,

    -- input user (sama dengan kolom saat training)
    age               INTEGER      NOT NULL,
    gender            VARCHAR(10)  NOT NULL,
    bmi_category      VARCHAR(20)  NOT NULL,
    sleep_duration    NUMERIC(3,1) NOT NULL,   -- jam per hari
    physical_activity INTEGER      NOT NULL,
    stress_level      INTEGER      NOT NULL,
    heart_rate        INTEGER      NOT NULL,
    daily_steps       INTEGER      NOT NULL,
    systolic          INTEGER      NOT NULL,
    diastolic         INTEGER      NOT NULL,

    -- hasil AI (KNN)
    knn_label         VARCHAR(20)  NOT NULL,   -- None / Insomnia / Sleep Apnea
    knn_proba         JSONB        NOT NULL,   -- {"Insomnia": 0.556, ...}

    created_at        TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);