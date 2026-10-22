from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import items_router, loans_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Buat seluruh tabel secara otomatis saat aplikasi mulai jika belum ada
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Lab Equipment Loan System API",
    description="Sistem backend peminjaman alat laboratorium kampus dengan kontrol stok otomatis",
    version="1.0.0",
    lifespan=lifespan
)

# Konfigurasi CORS agar frontend / client web dapat mengakses API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrasi Router
app.include_router(items_router)
app.include_router(loans_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "system": "Lab Equipment Loan System API",
        "status": "online",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
