# Software Requirement Specification (SRS) - Lab Equipment Loan System 
## 1. Overview Sistem
Informasi backend untuk mengelola peminjaman alat/fasilitas laboratorium kampus oleh mahasiswa dengan kontrol stok otomatis dan verifikasi status peminjaman. 
## 2. Tech Stack & Environment
 - Language: Python 3.x 
 - Framework: FastAPI / Flask 
 - Database: SQLite (Relational DB) 
 - Data Interchange: JSON 
## 3. Data Model & Database Schema 
1. Item (Alat Lab): - id (Integer, Primary Key) - name (String, Required) - total_stock (Integer) - available_stock (Integer) 
2. Loan (Transaksi Peminjaman): - id (Integer, Primary Key) - student_id (String, NIM Mahasiswa) - item_id (Integer, Foreign Key -> Item.id) - quantity (Integer) - status (String: BORROWED, RETURNED, CANCELLED) - created_at (Timestamp) 
## 4. API Endpoints 
- GET /items : Menampilkan daftar alat dan ketersediaan stok. 
- POST /items: Menambah master data alat baru. 
- POST /loans : Mengajukan peminjaman alat (mengurangi available_stock). 
- PUT /loans/{id}/return : Mengembalikan alat yang dipinjam (menambah kembali available_stock). 
- GET /loans/student/{student_id} : Menampilkan riwayat peminjaman berdasarkan NIM.