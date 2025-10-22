# 🎯 Talent Match Intelligence System

## Overview

Aplikasi Streamlit ini mengimplementasikan sistem cerdas untuk membantu manajer HR mengidentifikasi talenta internal yang cocok untuk suksesi atau peran baru. Aplikasi ini menggunakan data historis karyawan, hasil asesmen, dan profil kinerja untuk mencocokkan karyawan dengan profil *benchmark* yang ditentukan melalui REST API Supabase. Fitur utamanya meliputi:

* Perhitungan skor kecocokan (*match rate*) dinamis berdasarkan *benchmark* yang dipilih, dengan penanganan inverse scale dan data completeness.
* Pembuatan profil pekerjaan (deskripsi, kualifikasi, kompetensi) otomatis menggunakan AI (Groq API).
* Visualisasi interaktif untuk analisis hasil pencocokan, termasuk histogram, bar chart, dan radar chart dengan range dinamis.
* Fitur tambahan seperti chatbot AI untuk analisis hasil, input validation, error handling, dan indikator kualitas data.
* Logging untuk tracing error dan proses.

## Installation

1.  **Clone repositori:**
    ```bash
    git clone https://www.andarepository.com/
    cd talent-match-intelligence
    ```
2.  **Buat & Aktifkan Virtual Environment:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Siapkan Environment Variables:**
    * Salin file `.env.example` menjadi `.env`.
    * Isi file `.env` dengan kredensial Supabase (SUPABASE_URL, SUPABASE_KEY) dan Groq API Key (GROQ_API_KEY).

## Usage Guide

1.  **Jalankan Aplikasi:**
    ```bash
    streamlit run app.py
    ```
2.  **Buka Aplikasi:** Buka URL yang ditampilkan di terminal (biasanya `http://localhost:8501`).
3.  **Konfigurasi di Sidebar:**
    * Pilih atau masukkan Nama Peran (support peran baru dengan opsi "[New Role]").
    * Pilih Level Jabatan dan masukkan Tujuan Peran.
    * Pilih minimal 1 Karyawan Benchmark (rekomendasi 3-5 untuk akurasi).
4.  **Klik Tombol:** Tekan "Generate Profile & Match".
5.  **Lihat Hasil:** Hasil akan muncul di tab-tab seperti AI Profile, Ranking (dengan filter dan download CSV), Dashboard (visualisasi), Comparison (radar chart), dan Ask AI (chatbot untuk analisis).

Catatan: Aplikasi akan validasi input dan tampilkan warning jika data tidak lengkap. Cek file `app.log` untuk detail logging jika ada error.

## Project Structure
```bash
Case-Study/
│
├── 📄 README.md
├── 📄 requirements.txt
├── 📄 .env
├── 📄 .env.example
├── 📄 .gitignore
│
├── 📂 sql/                   <-- Folder untuk SQL
│   ├── 📄 talent_matching_query.sql  <-- Script SQL Utama Case 2
│   └── 📄 ...                        <-- (file SQL pendukung lainnya)
│
├── 📂 src/                   <-- Folder untuk Kode Python Aplikasi
│   ├── 📄 __init__.py
│   ├── 📄 config.py          <-- Konfigurasi sentral
│   ├── 📄 database.py        <-- Logika akses data via REST API Supabase
│   ├── 📄 ai_generator.py    <-- Logika API Groq untuk generate profil
│   ├── 📄 visualizations.py  <-- Fungsi visualisasi Plotly
│   ├── 📄 utils.py           <-- Fungsi utilitas (validasi, data quality, dll.)
│   └── 📄 components.py      <-- Komponen UI modular
│
├── 📂 notebooks/             <-- Folder Analisis Case 1
│   └── 📄 analysis.ipynb
│
├── 📂 venv/                  <-- Folder Virtual Environment
│
├── 📄 app.py                 <-- Aplikasi Utama Streamlit Case 3
│
├── 📄 dim_talent_mapping_rows.csv   <-- File Mapping 
├── 📄 Supabase Snippet Consolidated employee score set.csv <-- File Hasil Ekspor 
└── 📄 app.log                <-- File logging
```