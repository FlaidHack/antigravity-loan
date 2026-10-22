"""
Script Seeder untuk menginisialisasi database dengan data awal alat laboratorium.
Dijalankan dengan: python seed.py
"""
from app.database import Base, SessionLocal, engine
from app.models.item import Item
from app.models.loan import Loan


def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Item).count() == 0:
            initial_items = [
                Item(name="Osiloskop Digital 100MHz", total_stock=5, available_stock=5),
                Item(name="Multimeter Digital True-RMS", total_stock=10, available_stock=10),
                Item(name="Function Generator FG-100", total_stock=4, available_stock=4),
                Item(name="Power Supply DC Variable 30V/5A", total_stock=8, available_stock=8),
                Item(name="Mikroskop Binokuler Lab", total_stock=6, available_stock=6),
            ]
            db.add_all(initial_items)
            db.commit()
            print("Berhasil memasukkan data awal alat laboratorium.")
        else:
            print("Database sudah memiliki data alat lab.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
