import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Gunakan in-memory SQLite untuk pengujian terisolasi
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


def test_create_and_get_items(client):
    """Test US-01 & GET /items"""
    # 1. Tambah alat baru
    payload = {"name": "Osiloskop Digital", "total_stock": 5}
    response = client.post("/items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Osiloskop Digital"
    assert data["total_stock"] == 5
    assert data["available_stock"] == 5
    item_id = data["id"]

    # 2. Get items realtime
    get_res = client.get("/items")
    assert get_res.status_code == 200
    items = get_res.json()
    assert len(items) == 1
    assert items[0]["id"] == item_id
    assert items[0]["available_stock"] == 5


def test_loan_success_reduces_stock(client):
    """Test POST /loans berhasil dan mengurangi available_stock otomatis"""
    # Siapkan item dengan stok 3
    item_res = client.post("/items", json={"name": "Multimeter", "total_stock": 3})
    item_id = item_res.json()["id"]

    # Pinjam 2 unit
    loan_payload = {
        "student_id": "2100018001",
        "item_id": item_id,
        "quantity": 2
    }
    loan_res = client.post("/loans", json=loan_payload)
    assert loan_res.status_code == 201
    loan_data = loan_res.json()
    assert loan_data["student_id"] == "2100018001"
    assert loan_data["status"] == "BORROWED"
    assert loan_data["quantity"] == 2

    # Verifikasi stok item berkurang jadi 1
    items_res = client.get("/items")
    assert items_res.json()[0]["available_stock"] == 1


def test_loan_rejected_insufficient_stock(client):
    """Test POST /loans ditolak 400 jika pinjam > available_stock"""
    item_res = client.post("/items", json={"name": "Generator Sinyal", "total_stock": 2})
    item_id = item_res.json()["id"]

    # Coba pinjam 3 unit (stok hanya 2)
    loan_payload = {
        "student_id": "2100018002",
        "item_id": item_id,
        "quantity": 3
    }
    loan_res = client.post("/loans", json=loan_payload)
    assert loan_res.status_code == 400
    assert "melebihi stok" in loan_res.json()["detail"].lower()

    # Pastikan stok tidak berubah
    items_res = client.get("/items")
    assert items_res.json()[0]["available_stock"] == 2


def test_loan_rejected_item_not_found(client):
    """Test POST /loans ditolak 404 jika item_id tidak terdaftar"""
    loan_payload = {
        "student_id": "2100018003",
        "item_id": 9999,
        "quantity": 1
    }
    loan_res = client.post("/loans", json=loan_payload)
    assert loan_res.status_code == 404
    assert "tidak ditemukan" in loan_res.json()["detail"].lower()


def test_return_loan_success_restores_stock(client):
    """Test PUT /loans/{id}/return mengembalikan alat dan memulihkan available_stock"""
    item_res = client.post("/items", json={"name": "Solder Listrik", "total_stock": 5})
    item_id = item_res.json()["id"]

    # Pinjam 2
    loan_res = client.post("/loans", json={"student_id": "2100018004", "item_id": item_id, "quantity": 2})
    loan_id = loan_res.json()["id"]

    # Stok tersisa 3
    items_res = client.get("/items")
    assert items_res.json()[0]["available_stock"] == 3

    # Kembalikan pinjaman
    return_res = client.put(f"/loans/{loan_id}/return")
    assert return_res.status_code == 200
    assert return_res.json()["status"] == "RETURNED"

    # Stok lab pulih kembali menjadi 5
    items_res2 = client.get("/items")
    assert items_res2.json()[0]["available_stock"] == 5


def test_return_already_returned_rejected(client):
    """Test PUT /loans/{id}/return ditolak 400 jika sudah berstatus RETURNED"""
    item_res = client.post("/items", json={"name": "Mikroskop", "total_stock": 2})
    item_id = item_res.json()["id"]

    loan_res = client.post("/loans", json={"student_id": "2100018005", "item_id": item_id, "quantity": 1})
    loan_id = loan_res.json()["id"]

    # Pengembalian pertama berhasil
    res1 = client.put(f"/loans/{loan_id}/return")
    assert res1.status_code == 200

    # Pengembalian kedua harus ditolak 400
    res2 = client.put(f"/loans/{loan_id}/return")
    assert res2.status_code == 400
    assert "sudah berstatus returned" in res2.json()["detail"].lower()

    # Stok tidak boleh bertambah ganda
    items_res = client.get("/items")
    assert items_res.json()[0]["available_stock"] == 2


def test_get_loans_by_student(client):
    """Test US-04: GET /loans/student/{student_id}"""
    item_res = client.post("/items", json={"name": "Tang Krimping", "total_stock": 10})
    item_id = item_res.json()["id"]

    # Mahasiswa A pinjam 2 transaksi berbeda
    client.post("/loans", json={"student_id": "NIM1001", "item_id": item_id, "quantity": 1})
    client.post("/loans", json={"student_id": "NIM1001", "item_id": item_id, "quantity": 2})

    # Mahasiswa B pinjam 1 transaksi
    client.post("/loans", json={"student_id": "NIM1002", "item_id": item_id, "quantity": 3})

    # Cek transaksi NIM1001
    res_a = client.get("/loans/student/NIM1001")
    assert res_a.status_code == 200
    loans_a = res_a.json()
    assert len(loans_a) == 2
    for l in loans_a:
        assert l["student_id"] == "NIM1001"

    # Cek transaksi NIM1002
    res_b = client.get("/loans/student/NIM1002")
    assert res_b.status_code == 200
    loans_b = res_b.json()
    assert len(loans_b) == 1
    assert loans_b[0]["student_id"] == "NIM1002"
