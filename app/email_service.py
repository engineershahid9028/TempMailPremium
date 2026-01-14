import random,string,requests
from .settings import TEMP_DOMAINS

def generate_email():
    name = "".join(random.choices(string.ascii_lowercase+string.digits,k=10))
    domain = random.choice(TEMP_DOMAINS)
    return f"{name}@{domain}"

def inbox(email:str):
    login,domain=email.split("@")
    url=f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
    return requests.get(url,timeout=20).json()

def read_message(email:str,mail_id:int):
    login,domain=email.split("@")
    url=f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={mail_id}"
    return requests.get(url,timeout=20).json()
