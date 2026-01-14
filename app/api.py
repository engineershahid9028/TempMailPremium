from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal, init_db
from app.models import User, EmailVault
from datetime import datetime

app=FastAPI(title="TempMailPremium API")

@app.on_event("startup")
def startup():
    init_db()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/user/{user_id}")
def user_info(user_id:int,db:Session=Depends(get_db)):
    u=db.get(User,user_id)
    return u.__dict__ if u else {"error":"not_found"}

@app.get("/vault/{user_id}")
def vault(user_id:int,db:Session=Depends(get_db)):
    rows=db.query(EmailVault).filter(
        EmailVault.user_id==user_id,
        EmailVault.expires_at>datetime.utcnow()
    ).order_by(EmailVault.created_at.desc()).all()
    return [{"email":r.email,"expires_at":r.expires_at} for r in rows]
