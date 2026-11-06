# Proyek UAS - Sleep Check App

Aplikasi web klasifikasi kualitas tidur menggunakan FastAPI, Machine Learning, dan PostgreSQL.

## Cara Menjalankan Proyek (Setup Awal)

1. **Clone Repository**

   ```bash
   git clone https://github.com/dellin2489/uas_sleepcheck.git
   cd uas_sleepcheck
   ```

2. **Buat Virtual Environment & Install Dependency**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Konfigurasi Database (.env)**

   * Salin file `.env.example` menjadi `.env`:

     ```bash
     copy .env.example .env
     ```

   * Buka file `.env`, lalu isi `DB_PASSWORD` sesuai dengan password PostgreSQL di komputermu.

   * Buat database baru bernama `sleepcheck` di pgAdmin / PostgreSQL lokalmu.

4. **Jalankan Aplikasi**

   ```bash
   uvicorn app.main:app --reload
   ```

   Buka browser di `http://127.0.0.1:8000`.

## Alur Kerja Git (Aturan Anggota Kelompok)

1. **Ambil update terbaru dari branch `main`:**

   ```bash
   git pull origin main
   ```

2. **Buat branch baru untuk pengerjaan fiturmu:**

   ```bash
   git checkout -b nama-branch-kamu
   ```

   *(Contoh usulan nama branch: `anggota1-ai`, `anggota2-backend`, `anggota3-frontend`, `anggota4-fitur`)*

3. **Simpan dan unggah perubahan:**

   ```bash
   git add .
   git commit -m "Deskripsi pekerjaan"
   git push -u origin nama-branch-kamu
   ```

4. **Buat Pull Request (PR) di GitHub:**

   * Buka repositori di GitHub (`https://github.com/dellin2489/uas_sleepcheck`), klik tombol **Compare & pull request**.

   * Minta ketua/anggota lain untuk review dan merge ke `main`.