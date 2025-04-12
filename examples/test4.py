from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Configurar Selenium en modo headless
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

# Acceder a la web y obtener el HTML renderizado
driver.get("https://www.cdti.es/ayudas/proyectos-de-i-d")
html = driver.page_source
driver.quit()

# Extraer el texto (puedes afinar esto más según lo que quieras)
soup = BeautifulSoup(html, 'html.parser')
texto = soup.get_text()

# Ahora sí, pásale ese texto al agente
prompt = f"""
A continuación se muestra el contenido de una página web sobre una ayuda pública.

{texto}

Extrae y lista: 
1. El título de la ayuda.
2. La fecha límite para solicitarla.
3. El presupuesto máximo disponible.
"""
result = agent.run(prompt)
print(result)
