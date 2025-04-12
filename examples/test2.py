from smolagents import CodeAgent, DuckDuckGoSearchTool, OpenAIServerModel, tool
from smolagents.tools import Tool
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ---------- Configuración del agente ----------
load_dotenv()
api_key = os.environ["OPENROUTER_API_KEY"]

model = OpenAIServerModel(
    model_id="deepseek/deepseek-chat-v3-0324:free",
    api_key=api_key,
    api_base="https://openrouter.ai/api/v1"
)

@tool
def fetch_html_tool(url: str) -> str:
    """
    Esta herramienta usa Selenium (headless) para obtener el HTML renderizado de una página protegida.

    Args:
        url (str): La URL de la página web que se va a obtener.

    Returns:
        str: El HTML completo de la página obtenida.
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

        return html[:100000]  # Limita si es necesario
    except Exception as e:
        return f"Error al obtener HTML con Selenium: {str(e)}"
    

agent = CodeAgent(
    model=model,
    tools=[
        DuckDuckGoSearchTool(),
        fetch_html_tool
    ],
    additional_authorized_imports=['requests', 'beautifulsoup4','bs4','BeautifulSoup','selenium']
)

# ---------- Instrucción para generar el scraper ----------
url_objetivo = "https://www.cdti.es/ayudas/proyectos-de-i-d"  # ← Cambia por la URL real de una convocatoria

prompt = f"""
Dada la siguiente URL: {url_objetivo}

1. Usa la herramienta FetchHTML para descargar y obtener el HTML dada la URL.
2. Analiza el contendio del HTML y indentifica el titulo de la convocatoria, el presupuesto de la convocatoria y la fecha de la convocatoria.
3. A partir de ese HTML, genera un script de python que scrapee el título, presupuesto y fecha de la convocatoria.

Muestra solo el código final en tu respuesta.
"""

# ---------- Ejecutar agente ----------
result = agent.run(prompt)
print(result)
