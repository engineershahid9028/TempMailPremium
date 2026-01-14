import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
STRIPE_SECRET = os.getenv("STRIPE_SECRET")
DOMAIN = os.getenv("DOMAIN", "localhost")
ENV = os.getenv("ENV", "dev")

FREE_DAILY = 2
PREMIUM_DAILY = 10
VAULT_TTL_HOURS = 24

TEMP_DOMAINS = [
    "1secmail.com","1secmail.org","1secmail.net",
    "wwjmp.com","esiix.com","xojxe.com","yoggm.com"
]
