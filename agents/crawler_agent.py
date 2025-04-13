from smolagents import CodeAgent, OpenAIServerModel
from dotenv import load_dotenv
import os
from tools.tools import fetch_html_tool, save_json_tool

def crawl_convocatoria(url_objetivo: str, id: str):
    load_dotenv()
    api_key = os.environ["OPENROUTER_API_KEY"]

    model = OpenAIServerModel(
        model_id="deepseek/deepseek-chat-v3-0324:free",
        api_key=api_key,
        api_base="https://openrouter.ai/api/v1"
    )

    agent = CodeAgent(
        model=model,
        tools=[fetch_html_tool, save_json_tool],
        additional_authorized_imports=['requests', 'selenium', 'json']
    )

    prompt = f"""
    Dada la siguiente URL: {url_objetivo}

    1. Usa la herramienta FetchHTML para obtener una versión simplificada del HTML. Esta debería devolver el texto visible y relevante de la página.

    2. ATENCIÓN: Es posible que en la misma página haya varias convocatorias, diferenciadas por líneas, modalidades u otras divisiones. Por ejemplo, puede haber:
    - Proyectos individuales
    - Proyectos nacionales
    - Proyectos internacionales
    - Modalidades con objetivos o beneficiarios distintos

    Si detectas que hay **más de una convocatoria** claramente diferenciada, **extrae la información separadamente para cada una de ellas**, como si fueran convocatorias distintas.

    3. Para **cada convocatoria identificada**, extrae la siguiente información y estructúrala en formato JSON. Si algún campo no está disponible, déjalo vacío:

        - Organismo convocante
        - Nombre de la convocatoria
        - Linea de la convocatoria (la modalidad de la convocatoria que se menciona en el punto 2 del prompt)
        - Modalidad o tipo específico de esta convocatoria (por ejemplo: cooperación nacional, individual, etc.)
        - Beneficiarios de la convocatoria
        - Presupuesto mínimo disponible
        - Presupuesto máximo disponible
        - Fecha de inicio de la convocatoria (o el rango del plazo)
        - Fecha de fin de la convocatoria (o el rango del plazo)
        - Objetivos de la convocatoria
        - Tipo de la convocatoria
        - Área de la convocatoria (I+D, Innovación, Inversión, Internacional, u otra)
        - Duración mínima
        - Duración máxima
        - Tipo de financiación
        - Forma y plazo de cobro
        - Minimis (si aplica o no)
        - Región de aplicación
        - Tipo de consorcio
        - Costes elegibles
        - Link ficha técnica (si hay un PDF u otro documento vinculado)
        - Link convocatoria
        - Link orden de bases

    4. Usa la herramienta save_json_tool para guardar cada convocatoria encontrada en un archivo separado en la carpeta de convocatorias. Los JSON que guardes deben tener el {id} en el nombre del archivo y deben ser guardados. Tal que convo_{id}_1.json
    5. Devuelve una lista con el nombre de los archivos generados. Por ejemplo: ["convocatorias\convo_{id}_1.json", "convocatorias\convo_{id}_2.json", "convocatorias\convo_{id}_3.json"]
    """

    result = agent.run(prompt)
    print(result)
    return result
