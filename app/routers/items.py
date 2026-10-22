from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.item import ItemCreate, ItemResponse
from app.services import item_service

router = APIRouter(prefix="/items", tags=["Items (Alat Lab)"])


@router.get(
    "",
    response_model=List[ItemResponse],
    status_code=status.HTTP_200_OK,
    summary="Menampilkan daftar alat dan ketersediaan stok"
)
def list_items(db: Session = Depends(get_db)):
    """
    Menampilkan seluruh daftar alat lab beserta kuantitas `available_stock` terkini secara real-time.
    """
    return item_service.get_all_items(db)


@router.post(
    "",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Menambah master data alat baru"
)
def create_item(item_in: ItemCreate, db: Session = Depends(get_db)):
    """
    US-01: Petugas Lab menginput master data alat beserta jumlah stok awalnya.
    """
    return item_service.create_item(db, item_in)
