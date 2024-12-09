import os
import subprocess
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
TESTING = os.getenv("TESTING", "false").lower() == "true"
REBOOT_INTERVAL = int(os.getenv("REBOOT_SCRIPT_INTERVAL", 300))  # Default 5 minuti
PING_SITES = os.getenv("PING_SITES", "8.8.8.8,1.1.1.1,www.google.com").split(',') if not TESTING else ["error.invalid.site.aaa"]
REBOOT_SCRIPT_PATH = "./router-reboot.py"  # Sostituisci con il percorso corretto

last_reboot_time = datetime.min  # Timestamp dell'ultimo riavvio


def is_site_reachable(site):
    """Controlla se un sito è raggiungibile con il ping."""
    try:
        print(f"ping di {site} ...")
        subprocess.run(
            ["ping", "-c", "1", "-w", "10", site],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        print(f"{site} OK")
        return True
    except Exception:
        print(f"{site} unreachable")
        return False


def is_internet_available():
    """Controlla se almeno uno dei siti della lista è raggiungibile."""
    for site in PING_SITES:
        if is_site_reachable(site):
            return True
    return False


def reboot_router():
    """Riavvia il router eseguendo lo script di riavvio."""
    global last_reboot_time
    now = datetime.now()
    if now - last_reboot_time >= timedelta(seconds=REBOOT_INTERVAL):
        print(f"{now}: Connessione assente. Riavvio il router...")
        os.system(f"python3 {REBOOT_SCRIPT_PATH}")  # Esegui lo script di riavvio
        last_reboot_time = now
    else:
        print(f"{now}: Connessione assente, ma in attesa del prossimo intervallo di riavvio.")


def main():
    """Ciclo principale di monitoraggio."""
    while True:
        if is_internet_available():
            print(f"{datetime.now()}: Connessione Internet OK.")
        else:
            reboot_router()
        time.sleep(60)  # Controlla la connessione ogni 60 secondi


if __name__ == "__main__":
    main()
