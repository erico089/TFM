from smolagents import CodeAgent, OpenAIServerModel, tool
from dotenv import load_dotenv
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

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

        return simplificar_html(html)  # Limita si es necesario
    except Exception as e:
        return f"Error al obtener HTML con Selenium: {str(e)}"

agent = CodeAgent(
    model=model,
    tools=[fetch_html_tool],
    additional_authorized_imports=['requests', 'selenium']
)

url_objetivo = "https://www.cdti.es/ayudas/proyectos-de-i-d"

prompt = f"""
Dada la siguiente URL: {url_objetivo}

1. Usa la herramienta FetchHTML. Esta debería devolver el HTML de la página.
2. A partir de aqui extrae el nombre de la convocatoria, los beneficiarios de esta y el presupuesto máximo disponible.
"""

result = agent.run(prompt)
print(result)
