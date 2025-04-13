from smolagents import CodeAgent, OpenAIServerModel, tool
from dotenv import load_dotenv
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import os

load_dotenv()
api_key = os.environ["OPENROUTER_API_KEY"]

model = OpenAIServerModel(
    model_id="deepseek/deepseek-chat-v3-0324:free",
    api_key=api_key,
    api_base="https://openrouter.ai/api/v1"
)

def simplificar_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'form', 'aside']):
        tag.decompose()

    texto_procesado = []

    for h in soup.find_all(['h1', 'h2', 'h3']):
        texto_procesado.append(f"TÍTULO: {h.get_text(strip=True)}")

    for p in soup.find_all('p'):
        texto = p.get_text(strip=True)
        if texto:
            texto_procesado.append(texto)

    for li in soup.find_all('li'):
        texto = li.get_text(strip=True)
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




agent = CodeAgent(
    model=model,
    tools=[fetch_html_tool,save_json_tool],
    additional_authorized_imports=['requests', 'selenium','json']
)

url_objetivo = "https://www.cdti.es/ayudas/proyectos-de-i-d"

# prompt = f"""
# Dada la siguiente URL: {url_objetivo}

# 1. Usa la herramienta FetchHTML. Esta debería devolver una version simplificada de la web, con los textos que hay.
# 2. A partir de aqui extrae los siguientes datos de la convocatoria en formato JSON, si no encuentras un dato, deja el campo vacío:
#         - Organismo convocante
#         - Nombre de la convocatoria
#         - Beneficiarios de la convocatoria
#         - Presupuesto minimo disponible
#         - Presupuesto máximo disponible
#         - Fecha de inicio de la convocatoria (Si no aparece la fecha exacta, pon el rango del plazo de la presentacion de la convocatoria)
#         - Fecha de fin de la convocatoria (Si no aparece la fecha exacta, pon el rango del plazo de la presentacion de la convocatoria)
#         - Objetivos de la convocatoria
#         - Tipo de la convocatoria
#         - Area de la convocatoria (I+D, Innovación, Inversión, Internacional, u otra si no aparece en esta lista)
#         - Duración minima
#         - Duracion máxima
#         - Tipo de financiación 
#         - Forma y plazo de cobro
#         - Minimis (Las ayudas "de minimis" en la Unión Europea son apoyos estatales de pequeña cuantía que no requieren notificación a la Comisión Europea, ya que se consideran demasiado bajas para afectar la competencia o el comercio en el mercado interior.)
#         - Region de aplicación (A veces, si no esta indicado como tal, la pagina web o el organismo ya indica en que region se aplica la ayuda)
#         - Tipo de consorcio
#         - Costes elegibles
#         - link ficha tecnica (o ficha del instrumento que suele ser un PDF)
#         - link convocatoria
#         - link orden de bases
# 3. Usa la herramienta save_json_tool para guardar el JSON resultado, guardalo en la misma carpeta que el script, con el nombre 'convocatoria.json'.
# """


prompt = f"""
Dada la siguiente URL: {url_objetivo}

1. Usa la herramienta FetchHTML para obtener una versión simplificada del HTML. Esta debería devolver el texto visible y relevante de la página.

2. ATENCIÓN: Es posible que en la misma página haya varias convocatorias, diferenciadas por líneas, modalidades u otras divisiones. Por ejemplo, puede haber:
   - Proyectos individuales
   - Proyectos nacionales
   - Proyectos internacionales
   - Modalidades con objetivos o beneficiarios distintos

   Si detectas que hay **más de una convocatoria** claramente diferenciada, **extrae la información separadamente para cada una de ellas**, como si fueran convocatorias distintas.

3. Para **cada convocatoria identificada**, extrae la siguiente información y estructúrala en formato JSON. Si algún campo no está disponible, déjalo vacío:

    - Organismo convocante
    - Nombre de la convocatoria
    - Linea de la convocatoria (la modalidad de la convocatoria que se menciona en el punto 2 del prompt)
    - Modalidad o tipo específico de esta convocatoria (por ejemplo: cooperación nacional, individual, etc.)
    - Beneficiarios de la convocatoria
    - Presupuesto mínimo disponible
    - Presupuesto máximo disponible
    - Fecha de inicio de la convocatoria (o el rango del plazo)
    - Fecha de fin de la convocatoria (o el rango del plazo)
    - Objetivos de la convocatoria
    - Tipo de la convocatoria
    - Área de la convocatoria (I+D, Innovación, Inversión, Internacional, u otra)
    - Duración mínima
    - Duración máxima
    - Tipo de financiación
    - Forma y plazo de cobro
    - Minimis (si aplica o no ,Las ayudas "de minimis" en la Unión Europea son apoyos estatales de pequeña cuantía que no requieren notificación a la Comisión Europea, ya que se consideran demasiado bajas para afectar la competencia o el comercio en el mercado interior.)
    - Región de aplicación
    - Tipo de consorcio
    - Costes elegibles
    - Link ficha técnica (si hay un PDF u otro documento vinculado)
    - Link convocatoria
    - Link orden de bases

4. Usa la herramienta save_json_tool para guardar cada convocatoria encontrada en un archivo separado

   Guarda estos archivos en la misma carpeta donde está el script.
"""



result = agent.run(prompt)
print(result)
