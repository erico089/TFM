import os
import sys
import asyncio
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from browser_use.agent.service import Agent, Controller, Browser

load_dotenv()

azure_openai_api_key = os.getenv('AZURE_OPENAI_KEY')
azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')

if not azure_openai_api_key or not azure_openai_endpoint:
    raise ValueError('AZURE_OPENAI_KEY or AZURE_OPENAI_ENDPOINT is not set')

llm = AzureChatOpenAI(
    model_name='gpt-4.1',
    openai_api_key=azure_openai_api_key,
    azure_endpoint=azure_openai_endpoint, 
    deployment_name='gpt-4.1',
    api_version='2024-12-01-preview',
)

output_dir = "data/nav_urls"
os.makedirs(output_dir, exist_ok=True)

controller = Controller()
registry = controller.registry

# Definimos la acción para guardar las URLs en un fichero
@registry.action(description="Guardar lista de URLs en un archivo", domains=["*"])
async def save_urls_to_file(urls: list):
    """
    Esta función guarda una lista de URLs en un archivo dentro de la carpeta 'data/nav_urls'.
    Cada URL será guardada en una nueva línea y entre comillas.
    """
    output_file = os.path.join(output_dir, "urls.txt")
    
    with open(output_file, 'w') as file:
        for url in urls:
            file.write(f'"{url}"\n')

    print(f"Las URLs se han guardado en el archivo: {output_file}")


async def navigate_convocatoria(url: str, instructions: str):
    """
    Esta función recibe una URL y la utiliza para ejecutar un agente que navegue.
    Se trata de un ejemplo donde el agente interactúa con la URL.
    """

    browser = Browser() 
    task = f"""
    Tu tarea es navegar por la página web de convocatorias de ayudas que se encuentra en la URL proporcionada y extraer los enlaces de las convocatorias disponibles.

    Pasos que debes seguir:

    1. Cargar la página web en la URL proporcionada.
    2. Identificar todos los elementos que correspondan a **convocatorias de ayudas**. 
    - **Importante:** Solo debes considerar enlaces que realmente lleven a páginas de convocatorias de ayudas. 
    - No debes recoger enlaces a vídeos, noticias, eventos, documentos generales u otras secciones que no sean convocatorias.
    3. Para cada convocatoria, obtén el **enlace final completo** que aparece en el navegador cuando pasas el ratón sobre el enlace.
    - No debes recoger simplemente el atributo `href` del HTML.
    - Recoge la URL tal y como la interpreta el navegador, incluyendo el dominio completo si es necesario (por ejemplo: `https://www.cdti.es//node/115`).
    4. Limita el número de convocatorias extraídas a un máximo de 20. Si hay menos de 20 disponibles, guarda todas las que encuentres.
    5. Si encuentras algún enlace roto, vacío o incorrecto, omítelo.
    6. Una vez extraídas las URLs válidas, construye una lista de strings con todas ellas.
    7. Usa la acción **Save URLs to File** para guardar esta lista de URLs extraídas en un fichero.

    Además, se te proporcionan las siguientes instrucciones específicas para poder navegar y consultar las ayudas:

    {instructions}

    URL proporcionada: {url}
    """




    
    agent = Agent(
        task=task,
        llm=llm,
        enable_memory=True,
        browser=browser,
        controller=controller,
    )
    
    await agent.run(max_steps=30)

    await browser.close()

    print(f"Agent finished processing URL: {url}")
