# Lab Equipment Loan System - Backend API

Sistem backend RESTful API untuk mengelola peminjaman dan pengembalian alat laboratorium kampus oleh mahasiswa dengan mekanisme kontrol ketersediaan stok otomatis (`available_stock`) dan integritas status transaksi.

Dibangun berdasarkan spesifikasi teknis pada [requirement.md](file:///c:/Users/Hype%20G12/Documents/FADIL/KULIAH/SEM5/lab-loan-system/requirement.md) dan aturan bisnis pada [prd.md](file:///c:/Users/Hype%20G12/Documents/FADIL/KULIAH/SEM5/lab-loan-system/prd.md).

---

## 🛠️ Tech Stack
- **Bahasa**: Python 3.11+
- **Framework Web**: FastAPI
- **Database**: SQLite (Relational DB)
- **ORM**: SQLAlchemy
- **Data Validation & Serialization**: Pydantic v2
- **Testing**: Pytest & HTTPX

---

## 📁 Struktur Proyek
```
lab-loan-system/
├── app/
│   ├── __init__.py
│   ├── main.py            # Entry point FastAPI, CORS, lifespans, router registration
│   ├── database.py        # Konfigurasi SQLAlchemy engine, session maker, get_db dependency
│   ├── models/            # SQLAlchemy ORM Models (Relasional)
│   │   ├── __init__.py
│   │   ├── item.py        # Model Item (id, name, total_stock, available_stock)
│   │   └── loan.py        # Model Loan (id, student_id, item_id, quantity, status, created_at)
│   ├── schemas/           # Skema validasi Pydantic v2
│   │   ├── __init__.py
│   │   ├── item.py        # ItemCreate, ItemResponse
│   │   └── loan.py        # LoanCreate, LoanResponse
│   ├── services/          # Business Logic & Logika Pengurangan/Pemulihan Stok Otomatis
│   │   ├── __init__.py
│   │   ├── item_service.py
│   │   └── loan_service.py
│   └── routers/           # API Endpoints (Controllers)
│       ├── __init__.py
│       ├── items.py       # GET /items, POST /items
│       └── loans.py       # POST /loans, PUT /loans/{id}/return, GET /loans/student/{student_id}
├── tests/
│   ├── __init__.py
│   └── test_api.py        # Suite pengujian otomatis (7 skenario acceptance criteria)
├── seed.py                # Seeder database dengan data awal alat laboratorium
├── requirements.txt       # Daftar pustaka & dependensi
├── requirement.md         # Software Requirement Specification (SRS)
├── prd.md                 # Product Requirement Document (PRD)
└── README.md              # Dokumentasi teknis proyek
```

---

## 🚀 Panduan Menjalankan Sistem

### 1. Instalasi Dependensi
Pastikan Python 3 sudah terpasang, lalu jalankan:
```bash
pip install -r requirements.txt
```

### 2. (Opsional) Mengisi Data Awal Alat Lab (Seeder)
Untuk mengisi database dengan beberapa contoh alat lab:
```bash
python seed.py
```

### 3. Menjalankan Server Backend
Jalankan server menggunakan Uvicorn:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Server akan aktif di `http://127.0.0.1:8000`.

### 4. Dokumentasi API Interaktif (Swagger UI)
Buka browser dan akses:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Menjalankan Pengujian Otomatis (Test Suite)
Jalankan perintah berikut untuk menguji seluruh Acceptance Criteria dan aturan bisnis:
```bash
python -m pytest tests/test_api.py -v
```

---

## 📌 Ringkasan API Endpoints

| Metode | Endpoint | Deskripsi | Status Code Sukses |
|---|---|---|---|
| `GET` | `/items` | Menampilkan seluruh alat & `available_stock` real-time | `200 OK` |
| `POST` | `/items` | Menambahkan master data alat baru (US-01) | `201 Created` |
| `POST` | `/loans` | Mengajukan peminjaman & mengurangi stok otomatis (US-02) | `201 Created` |
| `PUT` | `/loans/{id}/return` | Mengembalikan alat & memulihkan stok otomatis (US-03) | `200 OK` |
| `GET` | `/loans/student/{student_id}` | Melihat riwayat peminjaman mahasiswa berdasarkan NIM (US-04) | `200 OK` |

---

## ⚖️ Aturan Bisnis & Validasi yang Diterapkan

1. **Pengurangan Stok Otomatis (`POST /loans`)**:
   - Jika `item_id` tidak terdaftar $\rightarrow$ Mengembalikan `404 Not Found`.
   - Jika `quantity > available_stock` $\rightarrow$ Mengembalikan `400 Bad Request`.
   - Jika valid $\rightarrow$ `available_stock` berkurang otomatis dan peminjaman dicatat dengan status `BORROWED`.

2. **Pemulihan Stok Otomatis (`PUT /loans/{id}/return`)**:
   - Jika transaksi tidak ditemukan $\rightarrow$ Mengembalikan `404 Not Found`.
   - Jika status peminjaman sudah `RETURNED` $\rightarrow$ Mengembalikan `400 Bad Request` (mencegah duplikasi pemulihan stok).
   - Jika valid $\rightarrow$ `available_stock` pada alat lab bertambah kembali sesuai `quantity` dan status berubah jadi `RETURNED`.
