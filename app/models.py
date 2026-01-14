from sqlalchemy import Column,Integer,BigInteger,String,Boolean,Date,DateTime,Numeric,ForeignKey,func,Index
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "tm_users"
    id = Column(BigInteger, primary_key=True)
    username = Column(String)
    is_premium = Column(Boolean, default=False)
    daily_quota = Column(Integer, default=0)
    referrals = Column(Integer, default=0)
    referred_by = Column(BigInteger, nullable=True)
    last_reset = Column(Date, nullable=True)

class EmailVault(Base):
    __tablename__ = "tm_email_vault"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("tm_users.id"), index=True)
    email = Column(String, index=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, index=True)
    user = relationship("User")

class Payment(Base):
    __tablename__ = "tm_payments"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, index=True)
    amount = Column(Numeric)
    method = Column(String)
    status = Column(String)
    created_at = Column(DateTime, server_default=func.now())

Index("ix_vault_user_exp", EmailVault.user_id, EmailVault.expires_at)
