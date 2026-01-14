from datetime import date
from .settings import FREE_DAILY, PREMIUM_DAILY

def reset_if_needed(user):
    today = date.today()
    if user.last_reset != today:
        base = PREMIUM_DAILY if user.is_premium else FREE_DAILY
        user.daily_quota = base + (user.referrals or 0)
        user.last_reset = today

def consume_one(user):
    if user.daily_quota <= 0:
        return False
    user.daily_quota -= 1
    return True
