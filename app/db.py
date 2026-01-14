from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import DATABASE_URL
from .models import Base, User, EmailVault, Payment

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_or_create_user(db, user_id: int, username: str | None):
    u = db.get(User, user_id)
    if not u:
        u = User(id=user_id, username=username or "")
        db.add(u)
        db.commit()
        db.refresh(u)
    return u
