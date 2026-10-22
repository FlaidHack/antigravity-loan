from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.item import Item
from app.models.loan import Loan
from app.schemas.loan import LoanCreate


def create_loan(db: Session, loan_in: LoanCreate) -> Loan:
    """
    Mengajukan peminjaman alat lab:
    - 404 Not Found jika item_id tidak terdaftar di database.
    - 400 Bad Request jika quantity yang dipinjam > available_stock.
    - 201 Created jika berhasil, available_stock otomatis berkurang, status='BORROWED'.
    """
    # 1. Validasi keberadaan item
    item = db.query(Item).filter(Item.id == loan_in.item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item dengan id {loan_in.item_id} tidak ditemukan di database."
        )

    # 2. Validasi ketersediaan stok
    if loan_in.quantity > item.available_stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Jumlah pinjam ({loan_in.quantity}) melebihi stok yang tersedia "
                f"({item.available_stock}). Peminjaman ditolak."
            )
        )

    # 3. Pengurangan available_stock secara otomatis
    item.available_stock -= loan_in.quantity

    # 4. Simpan transaksi peminjaman
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
    Pengembalian alat yang dipinjam:
    - 404 Not Found jika transaksi pinjaman tidak ditemukan.
    - 400 Bad Request jika status transaksi sudah RETURNED.
    - 200 OK jika berhasil, status berubah jadi RETURNED, dan available_stock bertambah kembali.
    """
    # 1. Cari transaksi peminjaman
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaksi peminjaman dengan id {loan_id} tidak ditemukan."
        )

    # 2. Cek status: transaksi yang sudah RETURNED tidak boleh dikembalikan ulang
    if loan.status == "RETURNED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaksi peminjaman sudah berstatus RETURNED, tidak boleh dikembalikan ulang."
        )

    # 3. Pulihkan available_stock pada tabel Item sesuai jumlah yang dipinjam
    item = db.query(Item).filter(Item.id == loan.item_id).first()
    if item:
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
