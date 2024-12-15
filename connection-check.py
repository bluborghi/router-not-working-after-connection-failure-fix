import os
import subprocess
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

load_dotenv()
TESTING = os.getenv("TESTING", "false").lower() == "true"
REBOOT_INTERVAL = int(os.getenv("REBOOT_SCRIPT_INTERVAL", 300))  # Default 5 minuti
PING_SITES = os.getenv("PING_SITES", "8.8.8.8,1.1.1.1,www.google.com").split(',') if not TESTING else ["error.invalid.site.aaa"]
REBOOT_SCRIPT_PATH = "./router-reboot.py"  # Sostituisci con il percorso corretto
ROUTER_PASSWORD = os.getenv("ROUTER_PASSWORD")
ROUTER_IP = os.getenv("ROUTER_IP", "192.168.100.1")

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
        # Configura il driver di Selenium
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Esegui il browser in modalità headless
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=options)

        try:
            # Passo 1: Accedi alla pagina del router
            router_url = f"http://{ROUTER_IP}"
            driver.get(router_url)

            # Passo 2: Inserisci la password e premi il pulsante di login
            password_field = driver.find_element(By.ID, "pc-login-password")
            password_field.send_keys(ROUTER_PASSWORD)  # Sostituisci con la tua password

            login_button = driver.find_element(By.ID, "pc-login-btn")
            login_button.click()


            # Passo 2.1: Controlla se compare il dialog per il login forzato
            time.sleep(1)  # Aspetta un momento per il dialog
            try:
                force_login_dialog = driver.find_element(By.ID, "alert-container")
                if force_login_dialog.is_displayed():
                    print("Dialog 'Only one device' rilevato, premendo 'Log in'...")
                    force_login_button = driver.find_element(By.ID, "confirm-yes")
                    force_login_button.click()
                    time.sleep(2)  # Attendi che il dialogo si chiuda
            except Exception:
                print("Nessun dialog di login forzato rilevato.")


            # Attendi che il login sia completato (modifica se necessario)
            time.sleep(10)

            # Passo 3: Premi il pulsante "Reboot"
            reboot_button = driver.find_element(By.ID, "topReboot")
            reboot_button.click()

            # Attendi che appaia il dialog di conferma
            time.sleep(2)

            # Passo 4: Conferma il reboot cliccando su "Yes"
            if TESTING:
                print("Modalità di test attiva, non confermo il reboot.")
                confirm_button = driver.find_element(By.CLASS_NAME, "btn-msg-no")  # btn-msg-ok or btn-msg-no
                confirm_button.click()
            else:
                print("Confermo il reboot...")
                confirm_button = driver.find_element(By.CLASS_NAME, "btn-msg-ok")  # btn-msg-ok or btn-msg-no
                confirm_button.click()

            print("Reboot richiesto con successo!")
        finally:
            driver.quit()
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
