from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate


def get_all_items(db: Session) -> List[Item]:
    """Mengambil seluruh master data alat beserta stok terkini secara real-time."""
    return db.query(Item).order_by(Item.id.asc()).all()


def get_item_by_id(db: Session, item_id: int) -> Optional[Item]:
    """Mengambil satu data alat berdasarkan item_id."""
    return db.query(Item).filter(Item.id == item_id).first()


def create_item(db: Session, item_in: ItemCreate) -> Item:
    """
    Menambahkan master data alat baru.
    Jika available_stock tidak diisi, otomatis disamakan dengan total_stock.
    """
    available_stock = (
        item_in.available_stock
        if item_in.available_stock is not None
        else item_in.total_stock
    )
    db_item = Item(
        name=item_in.name,
        total_stock=item_in.total_stock,
        available_stock=available_stock
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
