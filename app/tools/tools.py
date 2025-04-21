import json
import os
from bs4 import BeautifulSoup, NavigableString, Tag
from selenium.webdriver.chrome.options import Options
from smolagents import tool
from selenium import webdriver
from pypdf import PdfReader

@tool
def leer_json(file_path: str) -> dict:
    """
    Esta herramienta permite leer y cargar el contenido de un archivo JSON desde una ruta local.

    Es útil para proporcionar al agente datos estructurados previamente extraídos o generados,
    de forma que pueda analizarlos, validarlos o compararlos con otras fuentes de información.

    Args:
        file_path (str): La ruta local al archivo JSON que se desea leer.

    Returns:
        dict: El contenido del JSON parseado como un diccionario de Python.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

@tool
def leer_pdf(file_path: str) -> str:
    """
    Esta herramienta utiliza PyPDF para extraer texto de un archivo PDF.

    Lee las primeras páginas de un archivo PDF y devuelve el contenido textual concatenado,
    permitiendo que el agente lo procese, analice o resuma según se requiera.

    Args:
        file_path (str): La ruta local al archivo PDF que se va a leer.

    Returns:
        str: El texto extraído del PDF, sin formato, para su posterior análisis.
    """
    contenido = ""
    reader = PdfReader(file_path)
    for page in reader.pages[:3]:
        contenido += page.extract_text()
    return contenido

def simplificar_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'form', 'aside']):
        tag.decompose()

    def procesar_nodo(nodo):
        if isinstance(nodo, NavigableString):
            return nodo.strip()
        elif isinstance(nodo, Tag):
            if nodo.name == 'a':
                texto = nodo.get_text(strip=True)
                href = nodo.get('href', '')
                return f"{texto} ({href})" if href else texto
            else:
                contenido = [procesar_nodo(hijo) for hijo in nodo.children]
                return ' '.join(filter(None, contenido))
        return ''

    cuerpo = soup.body or soup
    texto_procesado = procesar_nodo(cuerpo)

    return texto_procesado



@tool
def fetch_html_tool(url: str) -> str:
    """
    Esta herramienta usa Selenium (headless) para obtener el HTML renderizado de una página protegida.

    Args:
        url (str): La URL de la página web que se va a obtener.

    Returns:
        str: Una version simplificada del HTML con la informacion relevante de la pagina web.
    """
    try:
        options = Options()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(15)
        driver.get(url)
        html = driver.page_source
        driver.quit()

        return simplificar_html(html)
    except Exception as e:
        return f"Error al obtener HTML con Selenium: {str(e)}"


import os
import json
from typing import List, Dict

@tool
def save_json_tool(carpeta_base: str, datos: Dict, nombre_archivo: str) -> str:
    """
    Esta herramienta guarda un único diccionario como un archivo JSON en una carpeta especificada.

    Args:
        carpeta_base (str): Ruta de la carpeta donde se guardará el archivo JSON.
        datos (Dict): Diccionario que representa los datos a guardar.
        nombre_archivo (str): Nombre del archivo JSON (sin extensión .json).

    Returns:
        str: Mensaje indicando si el archivo fue guardado correctamente o si ocurrió un error.
    """
    try:
        if not isinstance(datos, dict):
            return "Error: 'datos' debe ser un diccionario."

        carpeta_base_abs = os.path.abspath(carpeta_base)
        os.makedirs(carpeta_base_abs, exist_ok=True)

        archivo_json = f"{nombre_archivo}.json"
        ruta_completa = os.path.join(carpeta_base_abs, archivo_json)

        with open(ruta_completa, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

        return f"{archivo_json} guardado correctamente en {carpeta_base_abs}."
    except Exception as e:
        return f"Error al guardar JSON: {str(e)}"

