from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String, Boolean

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    username = Column(String)
    is_premium = Column(Boolean, default=False)
    daily_quota = Column(Integer, default=2)