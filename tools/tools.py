import json
import os
from bs4 import BeautifulSoup
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

    texto_procesado = []

    def extraer_texto_con_links(tag):
        for a in tag.find_all('a'):
            texto = a.get_text(strip=True)
            href = a.get('href', '')
            if href:
                a.replace_with(f"{texto} ({href})")
        return tag.get_text(strip=True)

    for h in soup.find_all(['h1', 'h2', 'h3']):
        texto = extraer_texto_con_links(h)
        if texto:
            texto_procesado.append(f"TÍTULO: {texto}")

    for p in soup.find_all('p'):
        texto = extraer_texto_con_links(p)
        if texto:
            texto_procesado.append(texto)

    for li in soup.find_all('li'):
        texto = extraer_texto_con_links(li)
        if texto:
            texto_procesado.append(f"- {texto}")

    return "\n".join(texto_procesado)


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


@tool
def save_json_tool(nombre_base: str, datos: list[dict]) -> str:
    """
    Esta herramienta guarda una lista de diccionarios como múltiples archivos JSON 
    en la misma carpeta que el script. Cada archivo se nombra con un índice incremental.

    Args:
        nombre_base (str): El nombre base para los archivos JSON (ej. 'convocatoria').
        datos (list[dict]): Lista de convocatorias a guardar. Cada una será un archivo JSON.

    Returns:
        str: Mensaje indicando si los archivos fueron guardados correctamente o si ocurrió un error.
    """
    try:
        if not isinstance(datos, list):
            return "Error: 'datos' debe ser una lista de diccionarios."

        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        mensajes = []

        for i, item in enumerate(datos, start=1):
            if not isinstance(item, dict):
                mensajes.append(f"Elemento {i} ignorado: no es un diccionario.")
                continue

            nombre_archivo = f"{nombre_base}_{i}.json"
            ruta_completa = os.path.join(ruta_actual, nombre_archivo)

            with open(ruta_completa, 'w', encoding='utf-8') as f:
                json.dump(item, f, indent=4, ensure_ascii=False)

            mensajes.append(f"Archivo {nombre_archivo} guardado correctamente.")

        return "\n".join(mensajes)
    except Exception as e:
        return f"Error al guardar JSONs: {str(e)}"
