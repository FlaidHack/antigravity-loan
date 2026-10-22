from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, description="Nama alat lab")
    total_stock: int = Field(..., ge=0, description="Total jumlah stok awal alat")


class ItemCreate(ItemBase):
    available_stock: Optional[int] = Field(
        None,
        ge=0,
        description="Stok tersedia (default sama dengan total_stock jika tidak diisi)"
    )


class ItemResponse(ItemBase):
    id: int
    available_stock: int

    model_config = ConfigDict(from_attributes=True)
