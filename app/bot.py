from datetime import datetime,timedelta
import re
from telegram import InlineKeyboardMarkup,InlineKeyboardButton,Update
from telegram.ext import ApplicationBuilder,CallbackQueryHandler,CommandHandler,ContextTypes
from app.settings import BOT_TOKEN, VAULT_TTL_HOURS
from app.db import init_db, SessionLocal, get_or_create_user
from app.models import EmailVault
from app.email_service import generate_email, inbox as inbox_api, read_message
from app.quotas import reset_if_needed, consume_one
from app.referrals import apply_referral
from app.rate_limit import allow
from app.payments import create_stripe_checkout


MENU=InlineKeyboardMarkup([
    [InlineKeyboardButton("📧 Generate Email",callback_data="gen")],
    [InlineKeyboardButton("📬 Premium Inbox (24h)",callback_data="vault")],
    [InlineKeyboardButton("📥 Check Inbox",callback_data="inbox")],
    [InlineKeyboardButton("💎 Upgrade to Premium",callback_data="upgrade")],
    [InlineKeyboardButton("👥 Referral Program",callback_data="ref")],
    [InlineKeyboardButton("👤 My Account",callback_data="me")],
])

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    db=SessionLocal()
    try:
        user=get_or_create_user(db,update.effective_user.id,update.effective_user.username)
        if context.args and context.args[0].startswith("REF_"):
            ref_id=int(context.args[0].replace("REF_",""))
            apply_referral(db,user,ref_id)
            db.commit()
        await update.message.reply_text("🔥 TempMailPremium",reply_markup=MENU)
    finally:
        db.close()

async def on_gen(update:Update,context:ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    if not allow(f"gen:{q.from_user.id}",10,60):
        return await q.edit_message_text("⏳ Slow down.",reply_markup=MENU)
    db=SessionLocal()
    try:
        user=get_or_create_user(db,q.from_user.id,q.from_user.username)
        reset_if_needed(user)
        if not consume_one(user):
            db.commit()
            return await q.edit_message_text("❌ Daily quota reached.",reply_markup=MENU)
        email=generate_email()
        if user.is_premium:
            exp=datetime.utcnow()+timedelta(hours=VAULT_TTL_HOURS)
            db.add(EmailVault(user_id=user.id,email=email,expires_at=exp))
        db.commit()
        await q.edit_message_text(f"✅ Generated:\n\n{email}",reply_markup=MENU)
    finally:
        db.close()

async def on_vault(update:Update,context:ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    db=SessionLocal()
    try:
        user=get_or_create_user(db,q.from_user.id,q.from_user.username)
        if not user.is_premium:
            return await q.edit_message_text("🔒 Premium only.",reply_markup=MENU)
        rows=db.query(EmailVault).filter(
            EmailVault.user_id==user.id,
            EmailVault.expires_at>datetime.utcnow()
        ).order_by(EmailVault.created_at.desc()).all()
        if not rows:
            return await q.edit_message_text("📭 Vault empty.",reply_markup=MENU)
        txt="📬 Premium Inbox (24h)\n\n"
        for i,r in enumerate(rows,1):
            txt+=f"{i}. {r.email} (expires {r.expires_at:%H:%M UTC})\n"
        await q.edit_message_text(txt[:4000],reply_markup=MENU)
    finally:
        db.close()

async def inbox_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /inbox email@domain")
    email=context.args[0]
    data=inbox_api(email)
    if not data:
        return await update.message.reply_text("📭 Inbox empty.")
    msg="📥 Inbox:\n\n"
    for m in data:
        msg+=f"ID: {m['id']}\nFrom: {m['from']}\nSubject: {m['subject']}\n\n"
    await update.message.reply_text(msg[:4000])

async def read_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if len(context.args)<2:
        return await update.message.reply_text("Usage: /read email@domain id")
    email,mid=context.args[0],int(context.args[1])
    m=read_message(email,mid)
    body=m.get("body","")
    otp=re.findall(r"\b\d{4,8}\b",body)
    out=f"📨 Message:\n\n{body[:3500]}"
    if otp:
        out+=f"\n\n🔐 OTP: {otp[0]}"
    await update.message.reply_text(out)

async def on_upgrade(update:Update,context:ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    url=create_stripe_checkout(5,q.from_user.id)
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("💳 Pay with Card",url=url)]])
    await q.edit_message_text("💎 Upgrade to Premium — $5",reply_markup=kb)

async def on_ref(update:Update,context:ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    link=f"https://t.me/TempMailPremiumBot?start=REF_{q.from_user.id}"
    txt=f"🎁 Referral Program\n\nInvite friends and get +1 daily email per referral.\n\nYour link:\n{link}"
    await q.edit_message_text(txt,reply_markup=MENU)

async def on_me(update:Update,context:ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    db=SessionLocal()
    try:
        u=get_or_create_user(db,q.from_user.id,q.from_user.username)
        reset_if_needed(u); db.commit()
        t="Premium" if u.is_premium else "Free"
        txt=f"👤 Account\n\nPlan: {t}\nDaily quota left: {u.daily_quota}\nReferrals: {u.referrals or 0}"
        await q.edit_message_text(txt,reply_markup=MENU)
    finally:
        db.close()

def main():
    init_db()
    app=ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("inbox",inbox_cmd))
    app.add_handler(CommandHandler("read",read_cmd))
    app.add_handler(CallbackQueryHandler(on_gen,pattern="^gen$"))
    app.add_handler(CallbackQueryHandler(on_vault,pattern="^vault$"))
    app.add_handler(CallbackQueryHandler(on_upgrade,pattern="^upgrade$"))
    app.add_handler(CallbackQueryHandler(on_ref,pattern="^ref$"))
    app.add_handler(CallbackQueryHandler(on_me,pattern="^me$"))
    print("TempMailPremium Bot running…")
    app.run_polling()

if __name__=="__main__":
    main()
