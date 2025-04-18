from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Configurar navegador sin interfaz
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

try:
    # 1. Abrir la web
    driver.get("https://www.playbalatro.com/")
    time.sleep(3)

    # 2. Encontrar botón con aria-label "Open Merch"
    merch_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Open Merch"]')
    merch_url = merch_button.get_attribute("href")

    # 3. Ir a la página de merch (tienda externa)
    driver.get(merch_url)
    time.sleep(3)

    # 4. Buscar enlaces a camisetas (shirt)
    product_links = driver.find_elements(By.CSS_SELECTOR, "a[href]")
    shirt_url = None
    for link in product_links:
        href = link.get_attribute("href")
        text = link.text.lower()
        if "shirt" in text or "camiseta" in text:
            shirt_url = href
            break

    # 5. Ir a la URL del producto si se encontró
    if shirt_url:
        driver.get(shirt_url)
        time.sleep(2)
        print(driver.current_url)
    else:
        print("No se encontró camiseta en la tienda.")
finally:
    driver.quit()
