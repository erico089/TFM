import os
import json
from smolagents import CodeAgent, OpenAIServerModel, tool
from dotenv import load_dotenv
from tools.vectorial_db_tools import search_from_context_vec_db
from tools.tools import save_json_tool, get_organismo_context, get_nombre_convocatoria_context, get_beneficiarios_context, get_presupuesto_minimo_context, get_presupuesto_maximo_context, get_fecha_inicio_context, get_fecha_fin_context, get_objetivos_convocatoria_context, get_anio_context, get_duracion_minima_context, get_duracion_maxima_context, get_tipo_financiacion_context, get_forma_plazo_cobro_context, get_minimis_context, get_region_aplicacion_context, get_intensidad_subvencion_context, get_intensidad_prestamo_context, get_tipo_consorcio_context, get_costes_elegibles_context, get_intensidad_subvencion_context, get_intensidad_prestamo_context, get_costes_elegibles_context
from azureOpenAIServerModel import AzureOpenAIServerModel
from tools.utils import getIdFromFile

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

campos_a_revisar = [
    "Organismo convocante",
    "Nombre de la convocatoria",
    "Fecha de inicio de la convocatoria",
    "Fecha de fin de la convocatoria",
    "Objetivos de la convocatoria",
    "Beneficiarios",
    "Anio",
    "Presupuesto mínimo disponible",
    "Presupuesto máximo disponible",
    "Duración mínima",
    "Duración máxima",
    "Tipo de financiación",
    "Forma y plazo de cobro",
    "Minimis",
    "Región de aplicación",
    "Intensidad de la subvención",
    "Intensidad del préstamo",
    "Tipo de consorcio",
    "Costes elegibles"
]

def build_context_tool(vector_path):
    @tool
    def get_context_from_vector_db(prompt: str) -> str:
        """
        Recupera contexto desde una base de datos vectorial temporal embebida a partir del PDF de una convocatoria.

        Args:
            prompt (str): Consulta concreta sobre el contenido del PDF.

        Returns:
            str: Fragmento de texto del PDF recuperado por similitud semántica.
        """
        return search_from_context_vec_db(prompt, vectorstore_path=vector_path)
    
    return get_context_from_vector_db


def run_refinement_agent(path_json, vector_path):
    with open(path_json, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    json_name = getIdFromFile(path_json)
    agent = CodeAgent(
    model=model,
    tools=[
        save_json_tool,
        get_organismo_context,
        get_nombre_convocatoria_context,
        get_beneficiarios_context,
        get_presupuesto_minimo_context,
        get_presupuesto_maximo_context,
        get_fecha_inicio_context,
        get_fecha_fin_context,
        get_objetivos_convocatoria_context,
        get_anio_context,
        get_duracion_minima_context,
        get_duracion_maxima_context,
        get_tipo_financiacion_context,
        get_forma_plazo_cobro_context,
        get_minimis_context,
        get_region_aplicacion_context,
        get_intensidad_subvencion_context,
        get_intensidad_prestamo_context,
        get_costes_elegibles_context,
        get_tipo_consorcio_context
    ],
    additional_authorized_imports=['json']
)


    prompt = f"""Eres un agente especializado en el tratamiento de datos de convocatorias públicas.

    Recibirás un JSON con información de una convocatoria. Este JSON contiene **tanto campos a revisar como campos contextuales**.

    Tu tarea es **revisar únicamente los campos incluidos en la siguiente lista**:

    {campos_a_revisar}

    No debes modificar los campos que no estén en esta lista. **Su función es ayudarte a entender mejor el contexto de la convocatoria**, y deberás tenerlos muy en cuenta a la hora de interpretar los campos que sí debes procesar, en especial el campo "Línea de la convocatoria".

    Para cada uno de los campos a revisar:

    - Si el campo tiene ya un valor, verifícalo y si es necesario, matízalo y expándelo usando la herramienta correspondiente.
    - Si no es correcto, corrígelo con base en el contenido de los fragmentos.
    - Si el campo está vacío y puedes completarlo con los fragmentos proporcionados, hazlo.

    IMPORTANTE: Usa la información de los campos contextuales para interpretar mejor los fragmentos y entender el significado del campo que estás revisando. Por ejemplo, el campo "Línea de la convocatoria" puede darte pistas muy útiles sobre el tipo de beneficiarios o la intensidad de la subvención.

    **Normas adicionales:**

    - Cada campo a revisar tiene una herramienta cuyo nombre es muy similar al del campo.
    - Para usarlas correctamente, pásales el path a la base vectorial con la variable `path` (el valor de `{vector_path}`).
    - Las herramientas devuelven fragmentos con texto y metadatos.
    - Las herramientas tienen descripciones que te ayudarán a entender qué tipo de información puedes esperar de cada una.
    - En cada fragmento, la metadata contiene una propiedad `fragment` y un `id`, que representa el trozo del pdf original y un ID numérico único. Estas propiedades las debes usar para la trazabilidad.
    - Para el campo minimis, si este contiene false, y no se ha encontrado referencia, debes guardar el valor de la referencia {-1}. En caso de que sea true y no hayas encontrado referencia dejalo vacío.

    **Trazabilidad:**

    - Por cada campo que revises, además del valor final, deberás generar un JSON paralelo con el mismo nombre de campo, pero con sufijo `_ref`.
    - En este JSON paralelo, guarda una listas de objetos con `id'` y `fragment` que encontraras en la metadata de los fragmentos.
    Por ejemplo:
    ```json
    "Beneficiarios_ref": [
    {{"id": "ID_ficha", "fragment": 27}},
    {{"id": "ID_bases", "fragment": 32}}
    ]

    ```
    Guardado final:

    Usa la herramienta save_json_tool para guardar:

    El JSON corregido en: data/json/refined/

    El JSON de referencias en: data/json/reference/

    Ambos JSON deben tener el nombre {json_name}.json

    Reglas obligatorias para el JSON Refined:

    El JSON Refined debe incluir todos los campos del JSON de entrada, aunque no se haya modificado o revisado.

    Si un campo no ha sido analizado o completado, debe mantenerse en el JSON Refined con su valor original (aunque esté vacío o nulo).

    No deben faltar campos respecto al JSON inicial

    Por otra parte, el JSON de referencias debe contener únicamente los campos que han sido revisados o completados.

    Objetivo:

    Tu objetivo es asegurar que todos los campos definidos como relevantes estén verificados, corregidos o completados con evidencia. Y cada valor final debe estar claramente justificado por uno o más fragmentos del documento.

    El JSON de entrada es el siguiente: {json.dumps(json_data, indent=2, ensure_ascii=False)} """

    resultado = agent.run(prompt)

    return resultado
