from smolagents import CodeAgent, OpenAIServerModel, tool
from dotenv import load_dotenv
import os
import requests

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
    return response.text


agent = CodeAgent(
    model=model,
    tools=[get_html_from_url],
    additional_authorized_imports=['requests', 'bs4','selenium','json']
)

prompt = """
Quiero que me ayudes a navegar en un sitio web.

1. Usa la herramienta `get_html_from_url` para obtener el HTML de https://www.minecraft.net/es-es
2. Analiza el HTML y dime qué enlaces se pueden clicar para ir a "Tienda" y luego a "Minecraft"
3. Genera código Python usando Selenium que simule esos clics y devuelva la URL final
"""


result = agent.run(prompt)
print(result)