from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./lab_loan.db"

# connect_args={"check_same_thread": False} diperlukan untuk SQLite pada FastAPI/multithreading
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency injection untuk sesi database per HTTP request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
