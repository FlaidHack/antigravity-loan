from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.loan import LoanCreate, LoanResponse
from app.services import loan_service

router = APIRouter(prefix="/loans", tags=["Loans (Peminjaman Alat)"])


@router.post(
    "",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Mengajukan peminjaman alat"
)
def borrow_item(loan_in: LoanCreate, db: Session = Depends(get_db)):
    """
    US-02 & Kriteria Keberhasilan:
    - Mengurangi `available_stock` otomatis.
    - Mengembalikan `400 Bad Request` jika quantity > available_stock.
    - Mengembalikan `404 Not Found` jika item_id tidak ada di database.
    - Mengembalikan `201 Created` jika peminjaman valid.
    """
    return loan_service.create_loan(db, loan_in)


@router.put(
    "/{id}/return",
    response_model=LoanResponse,
    status_code=status.HTTP_200_OK,
    summary="Mengembalikan alat yang dipinjam"
)
def return_item(id: int, db: Session = Depends(get_db)):
    """
    US-03 & Kriteria Keberhasilan:
    - Mengembalikan `400 Bad Request` jika status transaksi sudah RETURNED.
    - Mengembalikan `404 Not Found` jika ID transaksi tidak ditemukan.
    - Mengembalikan `200 OK` jika berhasil, status berubah jadi RETURNED,
      dan `available_stock` pada tabel Item bertambah kembali.
    """
    return loan_service.return_loan(db, id)


@router.get(
    "/student/{student_id}",
    response_model=List[LoanResponse],
    status_code=status.HTTP_200_OK,
    summary="Menampilkan riwayat peminjaman berdasarkan NIM"
)
def get_student_loans(student_id: str, db: Session = Depends(get_db)):
    """
    US-04: Petugas Lab mengecek daftar transaksi peminjaman milik mahasiswa tertentu (NIM).
    """
    return loan_service.get_loans_by_student(db, student_id)
