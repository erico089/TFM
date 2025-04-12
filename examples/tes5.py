from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

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

def fetch_html_tool(url: str) -> str:
    """
    Esta herramienta usa Selenium (headless) para obtener el HTML renderizado de una página.
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

# URL de prueba
url = "https://www.cdti.es/ayudas/proyectos-de-i-d"

# Ejecutar
resultado = fetch_html_tool(url)
print("\n--- CONTENIDO EXTRAÍDO Y SIMPLIFICADO ---\n")
print(resultado)
