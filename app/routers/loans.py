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
    summary="Mengajukan peminjaman alat",
    responses={
        201: {"description": "Peminjaman berhasil dicatat, available_stock otomatis berkurang."},
        400: {"description": "Bad Request jika quantity dipinjam > available_stock."},
        404: {"description": "Not Found jika item_id tidak ada di database."}
    }
)
def borrow_item(loan_in: LoanCreate, db: Session = Depends(get_db)):
    """
    Acceptance Criteria 1:
    - Mengembalikan 400 Bad Request jika quantity dipinjam > available_stock.
    - Mengembalikan 404 Not Found jika item_id tidak ada di database.
    - Mengembalikan 201 Created jika valid, dan available_stock pada tabel Item otomatis berkurang.
    """
    return loan_service.create_loan(db, loan_in)


@router.put(
    "/{id}/return",
    response_model=LoanResponse,
    status_code=status.HTTP_200_OK,
    summary="Mengembalikan alat yang dipinjam",
    responses={
        200: {"description": "Berhasil, status berubah jadi RETURNED, dan available_stock bertambah kembali."},
        400: {"description": "Bad Request jika status transaksi sudah RETURNED."},
        404: {"description": "Not Found jika transaksi peminjaman tidak ditemukan di database."}
    }
)
def return_item(id: int, db: Session = Depends(get_db)):
    """
    Acceptance Criteria 2:
    - Mengembalikan 400 Bad Request jika status transaksi sudah RETURNED.
    - Mengembalikan 404 Not Found jika transaksi peminjaman tidak ditemukan di database.
    - Mengembalikan 200 OK jika berhasil, status berubah jadi RETURNED,
      dan available_stock pada tabel Item bertambah kembali.
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
