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
    - Si la convocatoria no es válida o no existe, **la URL debe redirigir a una página sin información relevante**. En este caso, no se debe generar ningún archivo JSON.
    - Si la convocatoria es válida y contiene la información requerida (algunos campos almenos), sigue el siguiente formato y asegúrate de extraer los datos correctamente.

    - Usa exactamente los nombres de campo listados a continuación, **quitando los paréntesis**.
    - Los paréntesis solo sirven como aclaración para que entiendas qué va en cada campo.
    - Si un campo no está disponible, déjalo vacío.
    - Asegúrate de indicar siempre **la unidad de medida** en los valores cuando corresponda (por ejemplo: "10 años", "500.000 €", "3 meses", etc.).

    Lista de campos (en el JSON final **no incluyas el texto entre paréntesis**):

        - Organismo convocante (El organismo que lanza la convocatoria)
        - Nombre de la convocatoria 
        - Linea de la convocatoria 
        - Fecha de inicio de la convocatoria
        - Fecha de fin de la convocatoria
        - Objetivos de la convocatoria
        - Beneficiarios
        - Anio (Se refiere al año de convocatoria o a cuando esta abierta esta)
        - Área de la convocatoria (Elige una de las siguientes opciones o añádela tú si no crees que cuadre: "I+D", "Innovación", "Inversión", "Internacional")
        - Presupuesto mínimo disponible (El mínimo que se puede solicitar teniendo en cuenta la región y la línea de la convocatoria)
        - Presupuesto máximo disponible (El máximo que se puede solicitar teniendo en cuenta la región y la línea de la convocatoria)
        - Duración mínima (Indica excepciones de duración mínima si las hay)
        - Duración máxima (Indica excepciones de duración máxima si las hay)
        - Tipo de financiación (tipo de ayuda o financiación que se ofrece)
        - Forma y plazo de cobro (explicación de cómo se cobra la ayuda y en qué plazos)
        - Minimis (Indica si la ayuda es minimis o no en formato bool, si no se indica nada, indicar false)
        - Región de aplicación (Dependiendo de la línea de la convocatoria y la convocatoria como tal, a veces se indica una o varias regiones de aplicación)
        - Link ficha técnica (Enlace a la ficha técnica o ficha del instrumento de la convocatoria, si no hay ficha técnica, dejar vacío)
        - Link convocatoria (Enlace con el que estás trabajando)
        - Link orden de bases (Enlace a la orden de bases, si no hay orden de bases, dejar vacío)

    4. Usa la herramienta save_json_tool para guardar cada convocatoria en un archivo separado dentro de la carpeta de data/json/convo_{id}. El nombre de cada archivo debe contener el ID proporcionado ({id}), por ejemplo: {id}_1.json

    5. Devuelve una lista con los nombres de los archivos generados, por ejemplo, siguiendo el mismo formato de carpeta:
    ["data\\json\\convo_{id}\\{id}_1.json", "data\\json\\convo_{id}\\{id}_2.json"]
    """

    result = agent.run(prompt)
    print(result)
    return result
