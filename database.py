from sqlmodel import create_engine, SQLModel
from sqlmodel.orm import session
from config import settings
DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = session.Session(autocommit=False, autoflush=False, bind=engine)

async def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    db = SessionLocal
    try:
        yield db
    finally:
        db.close()