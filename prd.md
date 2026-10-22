# Product Requirement Document (PRD) - Lab Equipment Loan System
## 1. Business Logic & Constraints
- Stok alat berkurang otomatis saat peminjaman berhasil dicatat.
- Peminjaman harus ditolak jika jumlah pinjam memproyeksikan available_stock menjadi kurang dari 0.
- Pengembalian alat memulihkan available_stock sesuai jumlah yang dipinjam dan mengubah status transaksi menjadi RETURNED.
- Transaksi yang sudah berstatus RETURNED tidak boleh dikembalikan ulang.
## 2. User Stories
- US-01: Sebagai Petugas Lab, saya ingin menginput master data alat beserta jumlah stok awalnya.
- US-02: Sebagai Mahasiswa, saya ingin mengajukan peminjaman alat menggunakan NIM dan jumlah yang dibutuhkan.
- US-03: Sebagai Mahasiswa, saya ingin mengembalikan alat yang dipinjam agar stok lab terisi kembali.
- US-04: Sebagai Petugas Lab, saya ingin mengecek daftar transaksi peminjaman milik mahasiswa tertentu.
## 3. Acceptance Criteria (Kriteria Keberhasilan)
1. Aturan Transaksi Peminjaman (POST /loans):
   - Mengembalikan 400 Bad Request jika quantity dipinjam > available_stock.
   - Mengembalikan 404 Not Found jika item_id tidak ada di database.
   - Mengembalikan 201 Created jika valid, dan available_stock pada tabel Item otomatis berkurang.
2. Aturan Pengembalian (PUT /loans/{id}/return):
   - Mengembalikan 400 Bad Request jika status transaksi sudah RETURNED.
   - Mengembalikan 200 OK jika berhasil, status berubah jadi RETURNED, dan available_stock pada tabel Item bertambah kembali.
3. Penyajian Data:
   - Respon JSON GET /items harus menampilkan jumlah stok terupdate secara realtime.