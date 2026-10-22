from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.item import ItemResponse


class LoanCreate(BaseModel):
    student_id: str = Field(..., min_length=1, description="NIM Mahasiswa peminjam")
    item_id: int = Field(..., gt=0, description="ID alat lab yang dipinjam")
    quantity: int = Field(..., gt=0, description="Jumlah alat yang dipinjam")


class LoanResponse(BaseModel):
    id: int
    student_id: str
    item_id: int
    quantity: int
    status: str
    created_at: datetime
    item: Optional[ItemResponse] = None

    model_config = ConfigDict(from_attributes=True)
