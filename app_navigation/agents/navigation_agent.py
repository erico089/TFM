import os
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

from urllib.parse import urljoin

@registry.action(description="Resuelve un href relativo usando la URL base actual", domains=["*"])
async def resolve_href_url(base_url: str, href: str) -> str:
    """
    Esta función combina la URL base actual con un href (que puede ser relativo o parcial)
    para obtener la URL final completamente resuelta, tal como lo haría un navegador.

    Por ejemplo:
    - base_url: "https://www.sodercan.es/ayudas"
    - href: "/convocatorias/123"

    Resultado: "https://www.sodercan.es/convocatorias/123"
    """
    resolved_url = urljoin(base_url, href)
    print(f"[Resuelto] Base: {base_url} + Href: {href} → {resolved_url}")
    return resolved_url


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

    1. Carga la página web en la URL proporcionada.
    2. Identifica todos los elementos que correspondan a **convocatorias de ayudas**. 
    - Solo debes considerar enlaces que realmente lleven a páginas de convocatorias.
    - Ignora enlaces a vídeos, noticias, documentos generales u otras secciones irrelevantes.
    - Ignora pdfs o documentos, la convocatoria debe ser una url o html.
    3. Para cada convocatoria, obtén el valor del atributo `href`.
    4. Luego, obtén la URL actual de la página (`page.url`) y llama a la herramienta **Resolve Href URL** pasándole ambos valores:
    - `base_url = page.url`
    - `href = valor del enlace encontrado`
    - Esta herramienta te devolverá la URL completamente resuelta (tal como se muestra en el navegador).
    5. No construyas la URL manualmente ni asumas dominios fijos. Usa siempre la herramienta para cada enlace.
    6. Cuando hayas extraído todas las URLs válidas, crea una lista con ellas.
    7. Usa la acción **Save URLs to File** para guardar esta lista.

    Además, se te proporcionan las siguientes instrucciones específicas para navegar por esta web en concreto:

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
    Si no, intenta navegar para encontrar páginas válidas.
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

    Importante: Si no contiene toda la información relevante, la puedes considerar válida. No será válida si solo tiene 1 o 2 campos de información (a no ser que esos campos sean el nombre y la ficha técnica) o si es solo una breve explicación genérica.

    Pasos a seguir:

    1. **Cargar la página de la URL proporcionada.**

    2. **Verificar si la página cumple los requisitos** de una página de convocatoria de ayudas.

    3. **Si la página es válida**:
      - Añade la URL al fichero `data/nav_urls/urls_verifyed.txt` (modo "append", sin sobrescribir).
      - Termina el trabajo.

    4. **Si la página no es válida**:
      - Examina si la página actúa como un "índice de convocatorias" (por ejemplo, lista enlaces a convocatorias de diferentes años).
      - Si detectas este patrón:
        - **Recorre todos los enlaces relevantes** que parezcan llevar a convocatorias específicas.
        - Carga cada enlace individualmente.
        - Aplica la verificación de nuevo en cada uno.
        - Guarda todas las URLs que correspondan a convocatorias válidas.
        - No apliques límite de número de acciones en este caso.
      - Si no detectas un "índice de convocatorias" (es decir, solo ves 1 o 2 enlaces o ninguno relacionado):
        - Busca enlaces relevantes como: "Ver convocatoria", "Bases reguladoras", "Acceder a la ayuda", "Información completa", "Detalles de la convocatoria", etc.
        - Puedes hacer un máximo de **5 acciones de clic** en total para intentar encontrar una página válida.

    5. **Si después de 5 acciones normales no encuentras una página válida**:
      - No guardes ninguna URL.
      - Termina el trabajo.

    Reglas adicionales:

    - No recojas enlaces a noticias, comunicados de prensa, eventos, boletines o documentos genéricos.
    - No guardes enlaces que den error o no carguen correctamente.
    - Actúa de forma eficiente: no hagas clics innecesarios si ya ves que un enlace no lleva a convocatorias.

    Recuerda: tu tarea principal es **garantizar que solo guardas URLs que verdaderamente correspondan a convocatorias de ayudas**.
    """
    agent = Agent(
        task=task,
        llm=llm,
        enable_memory=True,
        browser=browser,
        controller=controller,
    )

    await agent.run(max_steps=25)
    await browser.close()

    print(f"Agent finished processing URL: {url}")

