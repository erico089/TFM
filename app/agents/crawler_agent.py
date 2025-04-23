from smolagents import CodeAgent, OpenAIServerModel
from dotenv import load_dotenv
import os
from tools.tools import fetch_html_tool, save_json_tool
from azureOpenAIServerModel import AzureOpenAIServerModel

def crawl_convocatoria(url_objetivo: str, id: str):
    load_dotenv()
    api_key = os.environ["AZURE_OPENAI_KEY"]
    deployment_name = os.environ["AZURE_OPENAI_MODEL_ID"]
    api_base = os.environ["AZURE_OPENAI_ENDPOINT"] 
    api_version = os.environ["AZURE_API_VERSION"] 

    model = AzureOpenAIServerModel(
        model_id = deployment_name,
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=api_base
    )

    agent = CodeAgent(
        model=model,
        tools=[fetch_html_tool, save_json_tool],
        additional_authorized_imports=['requests', 'selenium', 'json']
    )

    prompt = f"""
    Dada la siguiente URL: {url_objetivo}

    1. Usa la herramienta FetchHTML para obtener una versión simplificada del HTML. Esta debe devolver solo el texto visible y relevante de la página, conservando los enlaces útiles (por ejemplo, enlaces a documentos o fichas técnicas en PDF).

    2. ATENCIÓN: Es posible que en la misma página haya varias convocatorias claramente diferenciadas, por líneas, modalidades, objetivos u otras divisiones. Por ejemplo:
    - Proyectos individuales
    - Proyectos nacionales
    - Proyectos internacionales
    - Diferentes modalidades para distintos tipos de beneficiarios

    Si detectas más de una convocatoria, **extrae la información por separado para cada una de ellas**, tratándolas como convocatorias distintas.

    3. Para **cada convocatoria identificada**, extrae la siguiente información y estructura el resultado en formato JSON.

    MUY IMPORTANTE:
    - Usa exactamente los nombres de campo listados a continuación, **quitando los paréntesis**.
    - Los paréntesis solo sirven como aclaración para que entiendas qué va en cada campo.
    - Si un campo no está disponible, déjalo vacío.
    - Asegúrate de indicar siempre **la unidad de medida** en los valores cuando corresponda (por ejemplo: "10 años", "500.000 €", "3 meses", etc.).

    Lista de campos (en el JSON final **no incluyas el texto entre paréntesis**):

        - Organismo convocante
        - Nombre de la convocatoria
        - Linea de la convocatoria
        - Modalidad o tipo específico
        - Beneficiarios
        - Presupuesto mínimo disponible
        - Presupuesto máximo disponible
        - Fecha de inicio de la convocatoria
        - Fecha de fin de la convocatoria
        - Objetivos de la convocatoria
        - Tipo de la convocatoria
        - Área de la convocatoria
        - Duración mínima
        - Duración máxima
        - Tipo de financiación
        - Forma y plazo de cobro
        - Minimis
        - Región de aplicación
        - Tipo de consorcio
        - Costes elegibles
        - Link ficha técnica
        - Link convocatoria
        - Link orden de bases

    4. Usa la herramienta save_json_tool para guardar cada convocatoria en un archivo separado dentro de la carpeta de data/json/convo_{id}. El nombre de cada archivo debe contener el ID proporcionado ({id}), por ejemplo: {id}_1.json

    5. Devuelve una lista con los nombres de los archivos generados, por ejemplo, siguiendo el mismo formato de carpeta:
    ["data\\json\\convo_{id}\\{id}_1.json", "data\\json\\convo_{id}\\{id}_2.json"]
    """

    result = agent.run(prompt)
    print(result)
    return result
