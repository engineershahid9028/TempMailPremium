import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
STRIPE_SECRET = os.getenv("STRIPE_SECRET")

FREE_DAILY = 2
PREMIUM_DAILY = 10
VAULT_TTL_HOURS = 24