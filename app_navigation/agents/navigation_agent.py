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

output_file = os.path.join(output_dir, "urls_verifyed.txt")

@registry.action(description="Añadir una URL al archivo de URLs verificadas", domains=["*"])
async def add_url_to_file(url: str):
    """
    Esta función añade una URL al final del archivo 'data/nav_urls/urls_verifyed.txt'.
    Si el archivo o directorio no existen, los crea automáticamente.
    """
    os.makedirs(output_dir, exist_ok=True)

    with open(output_file, 'a', encoding='utf-8') as file:
        file.write(f"{url}\n")

    print(f"URL añadida al archivo: {output_file}")

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
    - No debes recoger enlaces a vverify_convosídeos, noticias, eventos, documentos generales u otras secciones que no sean convocatorias.
    3. Para cada convocatoria, obtén el **enlace final completo** que aparece en el navegador cuando pasas el ratón sobre el enlace.
    - No debes recoger simplemente el atributo `href` del HTML.
    - Recoge la URL tal y como la interpreta el navegador, incluyendo el dominio completo si es necesario (por ejemplo: `https://www.cdti.es//node/115`).
    4. Cuando encuentres la pagina con las convocatorias y empiezes a extraer URLs, para cuando tengas todas las URLs de esta pagina.
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

async def verify_convocatoria(url: str):
    """
    Recibe una URL, la carga y verifica si es una página de convocatorias de ayudas.
    Si es válida, guarda la URL en data/nav_urls/urls_verifyed.txt (añadiéndola, no sobrescribiéndola).
    Si no, intenta navegar hasta tres veces para encontrar una página válida.
    """

    os.makedirs("data/nav_urls", exist_ok=True)

    file_path = "data/nav_urls/urls_verifyed.txt"

    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            pass

    browser = Browser()
    task = f"""
    Tu tarea es navegar de forma inteligente a partir de la siguiente URL inicial:

    {url}

    Objetivo:

    - Verificar si la página cargada corresponde a una **convocatoria de ayudas**.

    ¿Cómo debe ser una página de convocatoria?

    - Debe contener información sobre aspectos como: 
    - Nombre de la ayuda
    - Beneficiarios
    - Bases reguladoras
    - Precios o importes de la subvención
    - Ficha técnica
    - Procedimientos de solicitud
    - El contenido debe ser claro y específico sobre una ayuda o subvención.

    Importante: Si no contiene toda la información relevante, la puedes considerar valida. No sera valida cuando solo tenga 1 o 2 campos de información (a no ser que esos dos campos sean el nombre y la ficha tecnica) o sea una mera explicacion de como funciona.
    Pasos a seguir:

    1. **Cargar la página de la URL proporcionada.**

    2. **Verificar si la página cumple los requisitos** de una página de convocatoria de ayudas.

    3. **Si la página es válida**:
    - Añade la URL al fichero `data/nav_urls/urls_verifyed.txt`.
    - Usa el modo "append" (añadir al final, sin sobrescribir el archivo existente).
    - Termina el trabajo.

    4. **Si la página no es válida**:
    - Busca enlaces en la página que parezcan llevar a convocatorias o ayudas. 
    - Algunos ejemplos de enlaces relevantes: "Ver convocatoria", "Bases reguladoras", "Acceder a la ayuda", "Información completa", "Detalles de la convocatoria", etc.
    - Haz clic en uno de esos enlaces relevantes para navegar a otra página.
    - Vuelve al paso 2 y verifica la nueva página.
    - Puedes hacer un máximo de **5 acciones de clic** en total para intentar encontrar una página válida.
    - Ten en cuenta que a veces las paginas pueden derivar a mas de una convocatoria, por lo que añadiras tantas como encuentres.

    5. **Si después de 5 acciones no encuentras una página válida**:
    - No guardes ninguna URL.
    - Termina el trabajo.

    6. **Si antes de 5 acciones encuentras una página válida**:
    - Guarda la URL en el fichero `data/nav_urls/urls_verifyed.txt` y termina el trabajo.

    Reglas adicionales:

    - No recojas enlaces a noticias, comunicados de prensa, eventos, boletines o documentos genéricos.
    - No guardes enlaces que den error o no carguen correctamente.
    - Debes actuar de forma eficiente: no hagas clics innecesarios si ya ves que el enlace no lleva a convocatorias.

    Recuerda: tu tarea principal es **garantizar que solo guardas URLs que verdaderamente correspondan a convocatorias de ayudas**.
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
