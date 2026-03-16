import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

# --- CONFIG ---
URL = "https://hyroxitaly.com/it/event/hyrox-rimini-2/"
KEYWORD = "buy tickets here"   # esatto — case insensitive
EMAIL_TO = "mropreonzo@gmail.com"

# --- FETCH con headers realistici ---
def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://hyroxitaly.com/it/",
    }
    r = requests.get(url, headers=headers, timeout=20, verify=False)
    r.raise_for_status()
    return r.text

def check_tickets(html):
    return 'Buy Tickets here' in html

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
    html = fetch_page(url=URL)
    print("Lunghezza HTML:", len(html))
    print("'buy tickets here' trovato:", "buy tickets here" in html.lower())
    print("'buy' trovato:", "buy" in html.lower())
    print("'tickets' trovato:", "tickets" in html.lower())

    if check_tickets(html):
        print("🚨 BUY TICKETS HERE trovato! Invio email...")
        send_email(
            subject="🏃 HYROX MILANO — Iscrizioni APERTE!",
            body=f"Il bottone 'BUY TICKETS HERE' è comparso sulla pagina!\n\n👉 {URL}"
        )
    else:
        print("✅ Nessun bottone trovato. Iscrizioni ancora chiuse.")
