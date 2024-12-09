import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from dotenv import load_dotenv

load_dotenv()
ROUTER_PASSWORD = os.getenv("ROUTER_PASSWORD")
ROUTER_IP = os.getenv("ROUTER_IP", "192.168.100.1")
TESTING = os.getenv("TESTING", "false").lower() == "true"

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
