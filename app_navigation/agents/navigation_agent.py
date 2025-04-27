import os
import sys
import asyncio

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from browser_use import Agent

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

async def navigate_convocatoria(url: str, instructions: str):
    """
    Esta función recibe una URL y la utiliza para ejecutar un agente que navegue.
    Se trata de un ejemplo donde el agente interactúa con la URL.
    """

    task = f"""
    Tu tarea es navegar por la página web de convocatorias de ayudas que se encuentra en la URL proporcionada y extraer todas las URLs de las convocatorias disponibles.

    Pasos que debes seguir:
    1. Cargar la página web en la URL proporcionada.
    2. Buscar todas las convocatorias de ayudas listadas en la página. Generalmente, las convocatorias pueden estar en una lista o tabla, por lo que tendrás que identificar correctamente los elementos relevantes (como los enlaces o botones de convocatoria).
    3. Extraer el enlace (URL) de cada convocatoria. Las URLs deben ser válidas y deben llevar a una página con más detalles sobre la convocatoria.
    4. Limita el número de URLs que extraes a un máximo de 10 (esto se puede ajustar si es necesario).
    5. Si encuentras algún error o si una URL no funciona correctamente, omítela.
    6. Devuelve una lista con las URLs de las convocatorias extraídas.

    Además, se te proporcionan las siguientes instrucciones para poder navegar y consultar diferentes ayudas:

    {instructions}

    URL proporcionada: {url}
    """
    
    agent = Agent(
        task=task,
        llm=llm,
        enable_memory=True,
    )
    
    await agent.run(max_steps=30)

    print(f"Agent finished processing URL: {url}")
