from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.item import Item
from app.models.loan import Loan
from app.schemas.loan import LoanCreate


def create_loan(db: Session, loan_in: LoanCreate) -> Loan:
    """
    Mengajukan peminjaman alat lab sesuai Acceptance Criteria PRD Nomor 1:
    - Mengembalikan 404 Not Found jika item_id tidak ada di database.
    - Mengembalikan 400 Bad Request jika quantity dipinjam > available_stock (atau <= 0).
    - Mengembalikan 201 Created jika valid, dan available_stock pada tabel Item otomatis berkurang.
    """
    # 1. Validasi keberadaan item di database
    item = db.query(Item).filter(Item.id == loan_in.item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item dengan id {loan_in.item_id} tidak ada di database."
        )

    # 2. Validasi kuantitas pinjam
    if loan_in.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quantity dipinjam ({loan_in.quantity}) harus lebih dari 0."
        )

    # 3. Validasi stok: jika quantity dipinjam > available_stock
    if loan_in.quantity > item.available_stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Quantity dipinjam ({loan_in.quantity}) melebihi "
                f"available_stock ({item.available_stock}). Peminjaman ditolak."
            )
        )

    # 4. Pengurangan available_stock secara otomatis
    item.available_stock -= loan_in.quantity

    # 5. Catat transaksi peminjaman (status awal: BORROWED)
    loan = Loan(
        student_id=loan_in.student_id,
        item_id=loan_in.item_id,
        quantity=loan_in.quantity,
        status="BORROWED"
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def return_loan(db: Session, loan_id: int) -> Loan:
    """
    Pengembalian alat yang dipinjam sesuai Acceptance Criteria PRD Nomor 2:
    - Mengembalikan 404 Not Found jika transaksi peminjaman tidak ditemukan di database.
    - Mengembalikan 400 Bad Request jika status transaksi sudah RETURNED.
    - Mengembalikan 200 OK jika berhasil, status berubah jadi RETURNED,
      dan available_stock pada tabel Item bertambah kembali.
    """
    # 1. Validasi keberadaan transaksi peminjaman
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaksi peminjaman dengan id {loan_id} tidak ditemukan."
        )

    # 2. Validasi status: transaksi yang sudah RETURNED tidak boleh dikembalikan ulang
    if loan.status == "RETURNED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status transaksi sudah RETURNED, tidak boleh dikembalikan ulang."
        )

    # 3. Pulihkan available_stock pada tabel Item sesuai jumlah yang dipinjam
    item = db.query(Item).filter(Item.id == loan.item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item relasi dengan id {loan.item_id} tidak ditemukan di database."
        )

    item.available_stock += loan.quantity

    # 4. Ubah status transaksi menjadi RETURNED
    loan.status = "RETURNED"
    db.commit()
    db.refresh(loan)
    return loan


def get_loans_by_student(db: Session, student_id: str) -> List[Loan]:
    """
    Menampilkan seluruh riwayat transaksi peminjaman milik mahasiswa berdasarkan NIM.
    """
    return (
        db.query(Loan)
        .filter(Loan.student_id == student_id)
        .order_by(Loan.created_at.desc())
        .all()
    )
