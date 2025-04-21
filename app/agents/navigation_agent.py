from smolagents import CodeAgent, OpenAIServerModel, tool
from dotenv import load_dotenv
import os
import requests
import re

load_dotenv()
api_key = os.environ["OPENROUTER_API_KEY"]

model = OpenAIServerModel(
    model_id="deepseek/deepseek-chat-v3-0324:free",
    api_key=api_key,
    api_base="https://openrouter.ai/api/v1"
)

@tool
def get_html_from_url(url: str) -> str:
    """
    Obtiene el contenido HTML completo de una página web.

    Args:
        url (str): La URL del sitio web que quieres visitar.

    Returns:
        str: El contenido HTML de la página.
    """
    response = requests.get(url)
    html = response.text

    # Reemplaza todos los <path ...>...</path> por <path data-simplified="true"/>
    simplified_html = re.sub(
        r'<path[^>]*?d="[^"]+"[^>]*/?>',
        '<path data-simplified="true"/>',
        html,
        flags=re.IGNORECASE
    )

    return simplified_html


agent = CodeAgent(
    model=model,
    tools=[get_html_from_url],
    additional_authorized_imports=['requests', 'bs4','selenium','json']
)

prompt = """
Quiero que me ayudes a navegar en un sitio web.

1. Usa la herramienta `get_html_from_url` para obtener el HTML de https://www.playbalatro.com/
2. Analiza el HTML y genera un codigo de selenium que haga click en el boton merch. Este te redirigira a la pagina de merch.
3. UNa vez aqui, vuelve a usar la herramienta y analiza el HTML de la pagina de merch.
4. Genera un codigo de selenim, junto al que ya tienes para que clicke en el primer producto que sea una camiseta que veas en la pagina de merch.
5. Finalmente ejecuta el codigo y devuelve como respuesta solo la URL del producto que has clickeado.
"""

# prompt = """
# Que es un agente inteligente?
# """


result = agent.run(prompt)
print(result)