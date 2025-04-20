# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# import time

# # Configurar navegador sin interfaz
# options = Options()
# options.add_argument("--headless")
# options.add_argument("--disable-gpu")
# options.add_argument("--no-sandbox")

# driver = webdriver.Chrome(options=options)

# try:
#     # 1. Abrir la web
#     driver.get("https://www.playbalatro.com/")
#     time.sleep(3)

#     # 2. Encontrar botón con aria-label "Open Merch"
#     merch_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Open Merch"]')
#     merch_url = merch_button.get_attribute("href")

#     # 3. Ir a la página de merch (tienda externa)
#     driver.get(merch_url)
#     time.sleep(3)

#     # 4. Buscar enlaces a camisetas (shirt)
#     product_links = driver.find_elements(By.CSS_SELECTOR, "a[href]")
#     shirt_url = None
#     for link in product_links:
#         href = link.get_attribute("href")
#         text = link.text.lower()
#         if "shirt" in text or "camiseta" in text:
#             shirt_url = href
#             break

#     # 5. Ir a la URL del producto si se encontró
#     if shirt_url:
#         driver.get(shirt_url)
#         time.sleep(2)
#         print(driver.current_url)
#     else:
#         print("No se encontró camiseta en la tienda.")
# finally:
#     driver.quit()
import os
import sys

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.vectorial_db_tools import search_from_context_vec_db

VECTOR_PATH = "data/temp_vec_db/39cba016-1631-4721-920e-aeb7f20fd524"

def get_context_from_vector_db(prompt: str) -> str:
    """
    Recupera contexto desde una base de datos vectorial temporal embebida a partir del PDF de una convocatoria.

    Esta herramienta se usa para extraer información específica desde el contenido textual de un PDF ya embebido 
    en una base de datos vectorial temporal.

    Args:
        prompt (str): Consulta relacionada con un campo del JSON de la convocatoria, como 
                      "¿Cuál es el presupuesto máximo?" o "¿Quiénes pueden beneficiarse?".

    Returns:
        str: Fragmento de texto del PDF que responde (o está relacionado) con la consulta realizada, 
             recuperado por similitud coseno.
    """
    return search_from_context_vec_db(prompt, vectorstore_path=VECTOR_PATH)

print(get_context_from_vector_db("¿Cuál es el presupuesto máximo de la convocatoria?"))