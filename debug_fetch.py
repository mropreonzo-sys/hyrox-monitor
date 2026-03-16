import requests, urllib3
urllib3.disable_warnings()

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
r = requests.get("https://hyroxitaly.com/it/event/hyrox-rimini-2/", headers=headers, verify=False, timeout=20)

print("Status code:", r.status_code)
print("Lunghezza risposta:", len(r.text))

# Cerca solo le righe con buy o ticket
for i, line in enumerate(r.text.splitlines()):
    if "buy" in line.lower() or "ticket" in line.lower():
        print(f"Riga {i}: {line.strip()}")
