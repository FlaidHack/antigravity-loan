import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# In-memory SQLite untuk isolasi test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# =========================================================================
# Acceptance Criteria 1: POST /loans
# =========================================================================

def test_post_loans_success_201_reduces_stock(client):
    """AC 1: Mengembalikan 201 Created jika valid, dan available_stock pada tabel Item otomatis berkurang."""
    item_res = client.post("/items", json={"name": "Multimeter Digital", "total_stock": 5})
    assert item_res.status_code == 201
    item_id = item_res.json()["id"]

    # Ajukan peminjaman 2 unit
    loan_payload = {"student_id": "MHS001", "item_id": item_id, "quantity": 2}
    loan_res = client.post("/loans", json=loan_payload)
    assert loan_res.status_code == 201
    data = loan_res.json()
    assert data["student_id"] == "MHS001"
    assert data["quantity"] == 2
    assert data["status"] == "BORROWED"

    # Verifikasi available_stock berkurang dari 5 menjadi 3
    items = client.get("/items").json()
    assert items[0]["available_stock"] == 3


def test_post_loans_400_when_quantity_exceeds_stock(client):
    """AC 1: Mengembalikan 400 Bad Request jika quantity dipinjam > available_stock."""
    item_res = client.post("/items", json={"name": "Osiloskop", "total_stock": 2})
    item_id = item_res.json()["id"]

    # Coba pinjam 3 unit (stok hanya 2)
    loan_payload = {"student_id": "MHS002", "item_id": item_id, "quantity": 3}
    loan_res = client.post("/loans", json=loan_payload)
    assert loan_res.status_code == 400
    assert "melebihi" in loan_res.json()["detail"].lower()

    # Stok tidak boleh berubah
    items = client.get("/items").json()
    assert items[0]["available_stock"] == 2


def test_post_loans_400_when_quantity_zero_or_negative(client):
    """AC 1: Mengembalikan 400 Bad Request jika quantity dipinjam <= 0."""
    item_res = client.post("/items", json={"name": "Power Supply", "total_stock": 5})
    item_id = item_res.json()["id"]

    # Pinjam 0 unit
    loan_res = client.post("/loans", json={"student_id": "MHS003", "item_id": item_id, "quantity": 0})
    assert loan_res.status_code == 400

    # Pinjam minus unit
    loan_res_neg = client.post("/loans", json={"student_id": "MHS003", "item_id": item_id, "quantity": -2})
    assert loan_res_neg.status_code == 400


def test_post_loans_404_when_item_not_found(client):
    """AC 1: Mengembalikan 404 Not Found jika item_id tidak ada di database."""
    loan_payload = {"student_id": "MHS004", "item_id": 99999, "quantity": 1}
    loan_res = client.post("/loans", json=loan_payload)
    assert loan_res.status_code == 404
    assert "tidak ada di database" in loan_res.json()["detail"].lower()


# =========================================================================
# Acceptance Criteria 2: PUT /loans/{id}/return
# =========================================================================

def test_put_return_success_200_restores_stock(client):
    """AC 2: Mengembalikan 200 OK jika berhasil, status berubah jadi RETURNED, dan available_stock bertambah kembali."""
    item_res = client.post("/items", json={"name": "Mikroskop", "total_stock": 4})
    item_id = item_res.json()["id"]

    # Pinjam 3 unit -> sisa stok 1
    loan_res = client.post("/loans", json={"student_id": "MHS005", "item_id": item_id, "quantity": 3})
    assert loan_res.status_code == 201
    loan_id = loan_res.json()["id"]

    assert client.get("/items").json()[0]["available_stock"] == 1

    # Kembalikan alat
    return_res = client.put(f"/loans/{loan_id}/return")
    assert return_res.status_code == 200
    assert return_res.json()["status"] == "RETURNED"

    # Stok kembali penuh ke 4
    assert client.get("/items").json()[0]["available_stock"] == 4


def test_put_return_400_when_already_returned(client):
    """AC 2: Mengembalikan 400 Bad Request jika status transaksi sudah RETURNED."""
    item_res = client.post("/items", json={"name": "Solder Listrik", "total_stock": 5})
    item_id = item_res.json()["id"]

    loan_res = client.post("/loans", json={"student_id": "MHS006", "item_id": item_id, "quantity": 1})
    loan_id = loan_res.json()["id"]

    # Pengembalian ke-1: Sukses
    res1 = client.put(f"/loans/{loan_id}/return")
    assert res1.status_code == 200

    # Pengembalian ke-2: Ditolak 400 Bad Request karena sudah RETURNED
    res2 = client.put(f"/loans/{loan_id}/return")
    assert res2.status_code == 400
    assert "returned" in res2.json()["detail"].lower()


def test_put_return_404_when_loan_id_not_found(client):
    """AC 2: Mengembalikan 404 Not Found jika id transaksi peminjaman tidak ada."""
    return_res = client.put("/loans/99999/return")
    assert return_res.status_code == 404
    assert "tidak ditemukan" in return_res.json()["detail"].lower()


# =========================================================================
# Acceptance Criteria 3 & US-04
# =========================================================================

def test_get_items_realtime(client):
    """AC 3: Respon JSON GET /items harus menampilkan jumlah stok terupdate secara realtime."""
    client.post("/items", json={"name": "Test Item", "total_stock": 10})
    res = client.get("/items")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1
    assert items[0]["available_stock"] == 10


def test_get_loans_by_student(client):
    """US-04: Menampilkan riwayat peminjaman berdasarkan NIM."""
    item_res = client.post("/items", json={"name": "Kabel Jumper", "total_stock": 50})
    item_id = item_res.json()["id"]

    client.post("/loans", json={"student_id": "NIM111", "item_id": item_id, "quantity": 5})
    client.post("/loans", json={"student_id": "NIM222", "item_id": item_id, "quantity": 3})

    res = client.get("/loans/student/NIM111")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["student_id"] == "NIM111"
