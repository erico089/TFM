from smolagents import CodeAgent
from dotenv import load_dotenv
import os
from app_crawler.tools.tools import fetch_html_tool, save_json_tool
from azureOpenAIServerModel import AzureOpenAIServerModel

def crawl_convocatoria(url_objetivo: str, id: str, base_json_path: str):
    load_dotenv()
    api_key = os.environ["AZURE_OPENAI_KEY"]
    deployment_name = os.environ["AZURE_OPENAI_MODEL_ID"]
    api_base = os.environ["AZURE_OPENAI_ENDPOINT"] 
    api_version = os.environ["AZURE_API_VERSION"] 

    model = AzureOpenAIServerModel(
        model_id=deployment_name,
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=api_base
    )

    agent = CodeAgent(
        model=model,
        tools=[fetch_html_tool, save_json_tool],
        additional_authorized_imports=[]
    )

    prompt = f"""
    Dada la siguiente URL: {url_objetivo}

    1. Usa la herramienta FetchHTML para obtener una versión simplificada del HTML. Esta debe devolver solo el texto visible y relevante de la página, conservando los enlaces útiles (por ejemplo, enlaces a documentos o fichas técnicas en PDF).

    2. ATENCIÓN MUY IMPORTANTE: 
    Es absolutamente fundamental detectar y gestionar correctamente las **diferentes líneas, modalidades o subdivisiones** dentro de la convocatoria.  
    Pueden existir múltiples líneas diferenciadas en una misma página, como por ejemplo:
    - Proyectos individuales
    - Proyectos colaborativos
    - Nacional vs Internacional
    - Distintos destinatarios o categorías

    **TU TAREA PRINCIPAL ES**:
    - Detectar **todas las líneas de convocatoria** que existan.
    - Generar un **JSON separado para cada línea o modalidad**.
    - Si hay duda, **prefiere separar en varias** antes que agrupar incorrectamente.
    - Cada JSON debe ser **completo, coherente y autónomo** (no dependiente de otras líneas).

    **Es obligatorio crear bien las líneas**:
    - No debes mezclar información de líneas diferentes en el mismo JSON.
    - No debes inventar líneas inexistentes, pero tampoco debes agrupar dos líneas distintas en uno solo.

    3. Para **cada convocatoria o modalidad identificada**, extrae la siguiente información y estructura el resultado en formato JSON.

    MUY IMPORTANTE:
    - Si la URL redirige a una página sin información relevante, **no generes ningún JSON**.
    - Si detectas una convocatoria válida (aunque falte algún campo), genera el JSON con la información que encuentres.
    - Usa exactamente los nombres de campo listados a continuación, **quitando los paréntesis**.
    - Si un campo no está disponible, déjalo vacío.
    - Siempre que sea aplicable, **indica la unidad de medida** en los valores extraídos (por ejemplo: "10 años", "500.000 €", "3 meses", etc.).

    **TAREA ADICIONAL MUY IMPORTANTE**:
    A pesar de que tienes varias tareas, **lo más importante es extraer los enlaces a la ficha técnica y la orden de bases de la convocatoria**. Estos ficheros suelen estar en formato PDF. La ficha técnica puede aparecer también con nombres como "ficha", "ficha de instrumento" o "convocatoria". La orden de bases también puede ser conocida como "bases" o "ordenes". Asegúrate de extraerlos correctamente, si están disponibles.

    Lista de campos (en el JSON final **no incluyas el texto entre paréntesis**):

        - Organismo convocante (El organismo que lanza la convocatoria)
        - Nombre de la convocatoria
        - Linea de la convocatoria
        - Fecha de inicio de la convocatoria 
        - Fecha de fin de la convocatoria (Si se indica, esta puede estar abierta de forma permanente)
        - Objetivos de la convocatoria
        - Beneficiarios
        - Anio (Se refiere al año de convocatoria o a cuando esta abierta esta)
        - Área de la convocatoria (Elige una de las siguientes opciones o añade otra si es necesario: "I+D", "Innovación", "Inversión", "Internacional")
        - Presupuesto mínimo disponible (El mínimo que se puede solicitar teniendo en cuenta la región y la línea de la convocatoria)
        - Presupuesto máximo disponible (El máximo que se puede solicitar teniendo en cuenta la región y la línea de la convocatoria)
        - Duración mínima (Indica excepciones de duración mínima si las hay)
        - Duración máxima (Indica excepciones de duración máxima si las hay, si se indica que no tiene duración maxima, es decir, permanente, también indicarlo)
        - Tipo de financiación (tipo de ayuda o financiación que se ofrece)
        - Forma y plazo de cobro (explicación de cómo se cobra la ayuda y en qué plazos)
        - Minimis (Indica si la ayuda es minimis o no en formato bool, si no se indica nada, indicar false)
        - Región de aplicación (Dependiendo de la línea de la convocatoria y la convocatoria como tal, a veces se indica una o varias regiones de aplicación)
        - Link ficha técnica (Enlace a la ficha técnica o ficha del instrumento de la convocatoria, si no hay ficha técnica, dejar vacío)
        - Link convocatoria ({url_objetivo} pon siempre esta url, no otra que creeas, tiene que ser esta) 
        - Link orden de bases (Enlace a la orden de bases, si no hay orden de bases, dejar vacío)

    4. Usa la herramienta save_json_tool para guardar cada convocatoria en un archivo separado dentro de la carpeta {base_json_path}/convo_{id}.
    El nombre de cada archivo debe seguir este patrón: {id}_1.json, {id}_2.json, {id}_3.json, etc.

    5. Devuelve una lista con los nombres de los archivos generados, por ejemplo:
    ["{base_json_path}/convo_{id}/{id}_1.json", "{base_json_path}/convo_{id}/{id}_2.json"]
    """


    result = agent.run(prompt)
    print(result)
    return result

