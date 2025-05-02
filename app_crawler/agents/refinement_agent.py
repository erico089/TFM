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


    prompt = f"""
    Eres un agente especializado en el tratamiento de datos de convocatorias públicas.

    Recibirás un JSON que contiene:
    - **Campos a revisar** (que deberás procesar)
    - **Campos contextuales** (que solo sirven para entender mejor el contexto)

    ---

    **Tu tarea**:

    - **Revisar exclusivamente** los campos incluidos en la siguiente lista:
    
    {campos_a_revisar}

    - **No modificar** los campos que no estén en esta lista.
    - Su función es ayudarte a interpretar mejor el contenido, especialmente el campo "Línea de la convocatoria".

    ---

    **Para cada campo a revisar**:

    1. **Si ya tiene un valor**:
    - Verifica su exactitud.
    - Si es necesario, matízalo o expándelo utilizando la herramienta correspondiente.

    2. **Si el valor es incorrecto**:
    - Corrígelo basándote en los fragmentos proporcionados.

    3. **Si el campo está vacío**:
    - Complétalo, siempre que sea posible, usando la información de los fragmentos.

    **Uso de campos contextuales**:

    - Siempre debes usar los campos contextuales como apoyo para interpretar correctamente los fragmentos.
    - **Ejemplo**: El campo "Línea de la convocatoria" puede ser clave para entender mejor a los beneficiarios o el tipo de subvención.

    **Normas sobre herramientas**:

    - Cada campo a revisar tiene una herramienta asociada, con un nombre similar al del campo.
    - Para usar las herramientas:
    - Pásales el path de la base vectorial usando la variable `path` (valor: `{vector_path}`).
    - Las herramientas devuelven fragmentos con:
    - Texto
    - Metadatos (incluyen `fragment` y `id`, donde `id` es un número único que identifica el fragmento del PDF original).
    - Deberas usar estos fragmentos e id para generar el json de referencia explicado más abajo.

    **Trazabilidad obligatoria**:

    - Por cada campo revisado, genera un campo paralelo en un JSON de referencias:
    - Nombre del campo: igual al original, pero añadiendo el sufijo `_ref`.
    - Formato del contenido:

    ```json
    "Beneficiarios_ref": [
    {{"id": "ID_ficha", "fragment": 27}},
    {{"id": "ID_bases", "fragment": 32}}
    ]

        ```

    **Caso especial — Campo "minimis"**:

    - Si el valor es `false` y no encuentras referencia, guarda la referencia como `{-1}`.
    - Si el valor es `true` y no encuentras referencia, déjalo vacío.

    Reglas para el JSON refinado:

    Debe incluir todos los campos del JSON de entrada (aunque no se hayan modificado o completado).

    Si un campo no ha sido revisado o completado, debe mantenerse con su valor original (aunque sea vacío o nulo).

    No debe faltar ningún campo respecto al JSON inicial.

    Reglas para el JSON de referencias:

    Solo debe contener los campos de la lista de campos a revisar.

    Todos esos campos deben aparecer, incluso si no se encontró referencia.

    Objetivo final:

    Asegurar que todos los campos relevantes están:

    Verificados, Corregidos, Parcialmente Completados

    Cada valor final debe estar respaldado por fragmentos del documento cuando sea posible.

    Guardado final:

    Usa la herramienta save_json_tool para guardar:

    El JSON corregido en: data/json/refined/

    El JSON de referencias en: data/json/reference/

    Ambos deben llamarse {json_name}.json

    El JSON de entrada es:

    {json.dumps(json_data, indent=2, ensure_ascii=False)} """

    resultado = agent.run(prompt)

    return resultado
