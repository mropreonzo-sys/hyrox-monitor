import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import hashlib
import json
from datetime import datetime

# --- CONFIG ---
URLS_TO_CHECK = [
    "https://hyroxitaly.com/it/",                        # homepage eventi Italia
    "https://hyroxitaly.com/it/events/",                 # pagina eventi (prova entrambe)
]
KEYWORDS_ALERT = [
    "milano", "milan",
    "iscrizioni aperte", "register now", "iscriviti ora",
    "biglietti", "tickets", "buy now", "acquista"
]
KEYWORDS_IGNORE = ["sold out", "esaurito"]  # opzionale: avvisare anche in caso sold out
EMAIL_TO   = "tua@email.com"     # <-- cambia con la tua email
HASH_FILE  = "last_hash.json"    # salva hash tra un'esecuzione e l'altra

# --- FETCH ---
def fetch_page(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    return r.text

def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(separator=" ").lower()

def get_hash(text):
    return hashlib.md5(text[:8000].encode()).hexdigest()

# --- LOAD/SAVE HASH ---
def load_hashes():
    try:
        with open(HASH_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_hashes(hashes):
    with open(HASH_FILE, "w") as f:
        json.dump(hashes, f)

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
    hashes      = load_hashes()
    alerts      = []
    new_hashes  = {}

    for url in URLS_TO_CHECK:
        print(f"\n🔍 Controllo: {url}")
        try:
            html        = fetch_page(url)
            text        = extract_text(html)
            curr_hash   = get_hash(text)
            prev_hash   = hashes.get(url, "")
            new_hashes[url] = curr_hash

            found_kw    = [kw for kw in KEYWORDS_ALERT if kw in text]
            page_changed = curr_hash != prev_hash

            print(f"   Keywords trovate : {found_kw or 'nessuna'}")
            print(f"   Pagina cambiata  : {'SÌ ⚠️' if page_changed else 'no'}")

            if found_kw or page_changed:
                alerts.append({
                    "url": url,
                    "keywords": found_kw,
                    "changed": page_changed
                })

        except Exception as e:
            print(f"   ❌ Errore: {e}")
            alerts.append({"url": url, "keywords": [], "changed": False, "error": str(e)})

    save_hashes(new_hashes)

    if alerts:
        now  = datetime.now().strftime("%d/%m/%Y %H:%M")
        body = f"🏃 HYROX MILANO MONITOR — {now}\n\n"
        for a in alerts:
            body += f"URL: {a['url']}\n"
            if a.get("error"):
                body += f"⚠️ Errore: {a['error']}\n"
            else:
                body += f"Keywords trovate : {', '.join(a['keywords']) if a['keywords'] else 'nessuna'}\n"
                body += f"Pagina cambiata  : {'SÌ ⚠️' if a['changed'] else 'no'}\n"
            body += "\n"
        body += f"\n👉 Vai a controllare: https://hyroxitaly.com/it/\n"

        send_email("🚨 Hyrox Milano – Controlla le iscrizioni!", body)
    else:
        print("\n✅ Nessuna novità rilevante.")