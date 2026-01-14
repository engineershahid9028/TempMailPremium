def apply_referral(db, new_user, referrer_id: int):
    if new_user.referred_by:
        return
    ref = db.get(type(new_user), referrer_id)
    if not ref:
        return
    new_user.referred_by = referrer_id
    ref.referrals = (ref.referrals or 0) + 1
