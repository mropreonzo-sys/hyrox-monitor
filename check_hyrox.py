import requests
from bs4 import BeautifulSoup
import smtplib
import urllib3
from email.mime.text import MIMEText
import os

# --- CONFIG ---
URL = "https://hyroxitaly.com/it/event/hyrox-rimini-2/"
KEYWORD = "buy tickets here"   # esatto — case insensitive
EMAIL_TO = "mropreonzo@gmail.com"

# --- FETCH con headers realistici ---
def fetch_page(url):
    urllib3.disable_warnings()

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    r = requests.get("https://hyroxitaly.com/it/event/hyrox-rimini-2/", headers=headers, verify=False, timeout=20)

    lines = r.text.splitlines()
    # Cerca solo le righe con buy o ticket
    for i, line in enumerate(lines):
        if "buy tickets here" in line.lower():
            return True
        else:
            return False

def check_tickets(html):
    for line in html.splitlines():
        if "Buy Tickets here" in line:
            return True
    return False

# --- EMAIL ---
def send_email(subject, body):
    sender   = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"]    = sender
    msg["To"]      = EMAIL_TO
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)
    print("✅ Email inviata!")

# --- MAIN ---
if __name__ == "__main__":
    print(f"🔍 Controllo: {URL}")
    if fetch_page(url=URL):
        print("🚨 BUY TICKETS HERE trovato! Invio email...")
        send_email(
            subject="🏃 HYROX MILANO — Iscrizioni APERTE!",
            body=f"Il bottone 'BUY TICKETS HERE' è comparso sulla pagina!\n\n👉 {URL}"
        )
    else:
        print("✅ Nessun bottone trovato. Iscrizioni ancora chiuse.")
