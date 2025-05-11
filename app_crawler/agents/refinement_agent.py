import os
import json
from smolagents import CodeAgent
from dotenv import load_dotenv
from app_crawler.tools.tools import save_json_field_tool, add_field_ref_json_tool, get_organismo_context, get_beneficiarios_context, get_presupuesto_minimo_context, get_presupuesto_maximo_context, get_fecha_inicio_context, get_fecha_fin_context, get_objetivos_convocatoria_context, get_anio_context, get_duracion_minima_context, get_duracion_maxima_context, get_tipo_financiacion_context, get_forma_plazo_cobro_context, get_minimis_context, get_region_aplicacion_context, get_intensidad_subvencion_context, get_intensidad_prestamo_context, get_tipo_consorcio_context, get_costes_elegibles_context, get_intensidad_subvencion_context, get_intensidad_prestamo_context, get_costes_elegibles_context
from app_crawler.azureOpenAIServerModel import AzureOpenAIServerModel

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

campos_revisar = [
    {
        "field_name": "Organismo convocante",
        "field_ref_name": "Organismo convocante_ref",
        "topic_description": "Organismo o entidad responsable de emitir la convocatoria pública.",
        "context_function": get_organismo_context,
        "max_intentos": 1
    },
    {
        "field_name": "Fecha de inicio de la convocatoria",
        "field_ref_name": "Fecha de inicio de la convocatoria_ref",
        "topic_description": "Fecha en la que comienza el período para presentar solicitudes a la convocatoria.",
        "context_function": get_fecha_inicio_context,
        "max_intentos": 1
    },
    {
        "field_name": "Fecha de fin de la convocatoria",
        "field_ref_name": "Fecha de fin de la convocatoria_ref",
        "topic_description": "Fecha límite para presentar solicitudes a la convocatoria. Si se indica, esta puede estar abierta de forma permanente.",
        "context_function": get_fecha_fin_context,
        "max_intentos": 1
    },
    {
        "field_name": "Objetivos de la convocatoria",
        "field_ref_name": "Objetivos de la convocatoria_ref",
        "topic_description": "Propósitos o metas que busca alcanzar la convocatoria.",
        "context_function": get_objetivos_convocatoria_context,
        "max_intentos": 1
    },
    {
        "field_name": "Beneficiarios",
        "field_ref_name": "Beneficiarios_ref",
        "topic_description": "Personas, empresas o entidades que pueden recibir las ayudas o beneficios de la convocatoria.",
        "context_function": get_beneficiarios_context,
        "max_intentos": 1
    },
    {
        "field_name": "Anio",
        "field_ref_name": "Anio_ref",
        "topic_description": "Año en el que se publica o aplica la convocatoria.",
        "context_function": get_anio_context,
        "max_intentos": 1
    },
    {
        "field_name": "Presupuesto mínimo disponible",
        "field_ref_name": "Presupuesto mínimo disponible_ref",
        "topic_description": "Cantidad mínima de fondos disponibles para ser otorgados en la convocatoria.",
        "context_function": get_presupuesto_minimo_context,
        "max_intentos": 1
    },
    {
        "field_name": "Presupuesto máximo disponible",
        "field_ref_name": "Presupuesto máximo disponible_ref",
        "topic_description": "Cantidad máxima de fondos disponibles para ser otorgados en la convocatoria.",
        "context_function": get_presupuesto_maximo_context,
        "max_intentos": 1
    },
    {
        "field_name": "Duración mínima",
        "field_ref_name": "Duración mínima_ref",
        "topic_description": "Duración mínima de los proyectos o actividades financiadas por la convocatoria.",
        "context_function": get_duracion_minima_context,
        "max_intentos": 1
    },
    {
        "field_name": "Duración máxima",
        "field_ref_name": "Duración máxima_ref",
        "topic_description": "Duración máxima de los proyectos o actividades financiadas por la convocatoria. Si se indica, la duración maxima puede ser permanente",
        "context_function": get_duracion_maxima_context,
        "max_intentos": 1
    },
    {
        "field_name": "Tipo de financiación",
        "field_ref_name": "Tipo de financiación_ref",
        "topic_description": "Modalidad o forma de la ayuda financiera (subvención, préstamo, etc.).",
        "context_function": get_tipo_financiacion_context,
        "max_intentos": 3
    },
    {
        "field_name": "Forma y plazo de cobro",
        "field_ref_name": "Forma y plazo de cobro_ref",
        "topic_description": "Cómo y cuándo se recibe el dinero otorgado en la convocatoria.",
        "context_function": get_forma_plazo_cobro_context,
        "max_intentos": 3
    },
    {
        "field_name": "Minimis",
        "field_ref_name": "Minimis_ref",
        "topic_description": "Indicación de si la ayuda está sujeta a la normativa de ayudas mínimas ('de minimis') según legislación europea.",
        "context_function": get_minimis_context,
        "max_intentos": 2
    },
    {
        "field_name": "Región de aplicación",
        "field_ref_name": "Región de aplicación_ref",
        "topic_description": "Área geográfica donde se aplica o limita la convocatoria.",
        "context_function": get_region_aplicacion_context,
        "max_intentos": 3
    },
    {
        "field_name": "Intensidad de la subvención",
        "field_ref_name": "Intensidad de la subvención_ref",
        "topic_description": "Porcentaje de la subvención respecto al coste total del proyecto. Si la convocatoria de la linea no aplica al ser unicamente prestamo, indicar que no aplica.",
        "context_function": get_intensidad_subvencion_context,
        "max_intentos": 3
    },
    {
        "field_name": "Intensidad del préstamo",
        "field_ref_name": "Intensidad del préstamo_ref",
        "topic_description": "Porcentaje o proporción del préstamo respecto al coste total del proyecto. Si la convocatoria de la linea no aplica al ser unicamente subvencion, indicar que no aplica.",
        "context_function": get_intensidad_prestamo_context,
        "max_intentos": 3
    },
    {
        "field_name": "Tipo de consorcio",
        "field_ref_name": "Tipo de consorcio_ref",
        "topic_description": "Tipo de agrupación de entidades requerida o permitida para acceder a la convocatoria. Si la convocatoria de la linea no aplica consorcio, también se debe indicar.",
        "context_function": get_tipo_consorcio_context,
        "max_intentos": 3
    },
    {
        "field_name": "Costes elegibles",
        "field_ref_name": "Costes elegibles_ref",
        "topic_description": "Gastos o partidas de coste que son admitidos para ser financiados en el proyecto.",
        "context_function": get_costes_elegibles_context,
        "max_intentos": 3
    }
]


def verificar_campo(path_json, field_name_ref):
    """Verifica si el campo field_name_ref existe en el JSON."""
    with open(path_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    return field_name_ref in data and data[field_name_ref] not in [None, "", []]

def run_refinement_agent(path_json: str, vector_path: str, output_base_path: str):
    for campo in campos_revisar:
        field_name = campo["field_name"]
        field_name_ref = campo["field_ref_name"]
        topic_description = campo["topic_description"]
        context_function = campo["context_function"]
        max_intentos = campo["max_intentos"]

        intento = 0
        exito = False

        while intento < max_intentos and not exito:
            context = context_function(vector_path, intento)

            run_mini_agent(
                path_json=path_json,
                field_name=field_name,
                field_name_ref=field_name_ref,
                topic_description=topic_description,
                context=context,
                output_base_path=output_base_path
            )
            
            exito = verificar_campo(path_json, field_name_ref)
            intento += 1


def run_mini_agent(
    path_json: str,
    field_name: str,
    field_name_ref: str,
    topic_description: str,
    context: str,
    output_base_path: str
):
    with open(path_json, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    agent = CodeAgent(
        model=model,
        tools=[
            save_json_field_tool,
            add_field_ref_json_tool
        ]
    )

    refined_dir = os.path.join(output_base_path, "refined")
    reference_dir = os.path.join(output_base_path, "reference")
    os.makedirs(refined_dir, exist_ok=True)
    os.makedirs(reference_dir, exist_ok=True)

    file_name = os.path.basename(path_json)
    output_path_refined = os.path.join(refined_dir, file_name)
    output_path_reference = os.path.join(reference_dir, file_name)

    prompt = f"""
    Eres un agente especializado en extraer el campo {field_name} relacionado con {topic_description} de convocatorias públicas.

    Tienes acceso a:
    - El campo extraído de una convocatoria (o no, porque a veces vendrá vacío).
    - Una herramienta para guardar tu resultado (`save_json_field_tool`).
    - Una herramienta para añadir una referencia al campo (`add_field_ref_json_tool`).

    **Tu tarea**:

    - Dado el contexto y la información de la línea y el nombre de la convocatoria, tendrás que:

    1. Si el valor dado está vacío, intentar rellenarlo con la información del contexto.
    2. Si no está vacío, corroborar la información, incluso modificarla o extenderla con la información del contexto.
    3. A excepción de cuando dejes el campo vacío, tendrás que generar un objeto referencia, indicando en qué fragmentos y con qué id's del contexto has encontrado o corroborado la información.
    4. Usar la herramienta save_json_field_tool una vez, para guardar el dato que has conseguido.
    5. Usar la herramienta add_field_ref_json_tool, tantas veces como sea necesario para añadir referencias que respalden la validez de los datos en el campo.
    6. Pero cuidado, si no has podido verificar el valor o no has conseguido referencias, no uses la herramienta add_field_ref_json_tool.

    Un ejemplo de uso de la herramienta save_json_field_tool sería:

    Dado que se ha concluido que el valor obtenido de {field_name} es ejemplo1, usarás save_json_field_tool({output_path_refined}, {field_name}, ejemplo1)

    Un ejemplo de uso de la herramienta add_field_ref_json_tool sería:

    Dadas las partes de los fragmentos que te han ayudado a obtener o verificar el valor:

    {{texto: "....", fragment: "fragmento_ejemplo_1", id: "id_ejemplo"}}
    {{texto: "....", fragment: "fragmento_ejemplo_2", id: "id_ejemplo"}}

    Dados los fragmentos fragmento_ejemplo_1 y fragmento_ejemplo_2 con id_ejemplo que respaldan los datos encontrados, usarás add_field_ref_json_tool({output_path_reference}, {field_name_ref}, id_ejemplo, [fragmento_ejemplo_1,fragmento_ejemplo_2])

    Es importante que para ambas funciones, siempre uses los mismos valores de {output_path_refined}, {output_path_reference}, {field_name} y {field_name_ref}, tal y como se muestran en los ejemplos, y solo varíen el valor, el id y los fragmentos en base a tus resultados.

    **Información inicial**:

    - El campo {field_name} de entrada contiene actualmente:
    
    ```json
    {json.dumps(json_data.get(field_name, ''), indent=2, ensure_ascii=False)}
    ```
    
    El nombre y línea de la convocatoria son:

    ```json
    {json.dumps(json_data.get('Nombre de la convocatoria', ''), indent=2, ensure_ascii=False)}
    {json.dumps(json_data.get('Linea de la convocatoria', ''), indent=2, ensure_ascii=False)}
    ```

    Y por último, el contexto para extraer la información es:

    {context}
    """

    resultado = agent.run(prompt)

    return resultado
