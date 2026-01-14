from datetime import datetime
from app.db import SessionLocal
from app.models import User, EmailVault
from app.quotas import reset_if_needed

def daily_reset():
    db=SessionLocal()
    try:
        for u in db.query(User).all():
            reset_if_needed(u)
        db.commit()
    finally:
        db.close()

def cleanup_vault():
    db=SessionLocal()
    try:
        now=datetime.utcnow()
        db.query(EmailVault).filter(EmailVault.expires_at<now).delete()
        db.commit()
    finally:
        db.close()

if __name__=="__main__":
    daily_reset()
    cleanup_vault()
