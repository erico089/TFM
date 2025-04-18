import os
import json
from smolagents import CodeAgent, OpenAIServerModel, tool
from dotenv import load_dotenv
from tools.vectorial_db_tools import search_from_context_vec_db

load_dotenv()
api_key = os.environ["OPENROUTER_API_KEY"]

model = OpenAIServerModel(
    model_id="deepseek/deepseek-chat-v3-0324:free",
    api_key=api_key,
    api_base="https://openrouter.ai/api/v1"
)

@tool
def get_context_from_vector_db(prompt: str) -> str:
    """
    Recupera contexto desde una base de datos vectorial temporal embebida a partir del PDF de una convocatoria.

    Parámetros:
    - prompt (str): Consulta concreta relacionada con un campo del JSON de la convocatoria, como "¿Cuál es el presupuesto máximo?" o "¿Quiénes pueden beneficiarse?".

    Retorna:
    - str: Fragmento de texto del PDF que responde (o está relacionado) con la consulta realizada, recuperado por similitud coseno.

    Esta herramienta se usa para extraer información específica desde el contenido textual de un PDF ya embebido en una base de datos vectorial temporal.
    """
    #TODO : Cambiar el path por el dado en la llamada a la función
    search_from_context_vec_db(prompt, vectorstore_path="vectorstore")


agent = CodeAgent(
    model=model,
    tools=[get_context_from_vector_db],
    additional_authorized_imports=['json']
)

def run_refinement_agent(path_json):
    with open(path_json, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    prompt = f"""
Eres un agente especializado en refinar datos de convocatorias. Tienes acceso a una herramienta llamada `get_context_from_vector_db(query)` que te permite recuperar fragmentos relevantes de un documento PDF (previamente embebido) usando similitud coseno. La base de datos solo contiene información textual del PDF original.

Te proporcionamos un JSON que contiene información parcial o posiblemente incorrecta de una convocatoria. Tu tarea es mejorar y completar ese JSON utilizando la herramienta de recuperación de contexto.

Sigue estas instrucciones paso a paso:

1. **Revisión campo por campo**:
   - Para cada campo del JSON, evalúa si la información actual es correcta o sospechosa.
   - Si detectas que algún campo tiene un valor que claramente contradice el contenido del PDF (con alta seguridad), corrígelo.
   - Si un campo está vacío o incompleto, intenta recuperarlo usando la herramienta `get_context_from_vector_db`.

2. **Cómo usar la herramienta**:
   - Haz una consulta específica y concreta para cada campo. No combines varias preguntas en una sola.
   - Ejemplos:
     - Para el campo `presupuesto`, pregunta: *¿Cuál es el presupuesto máximo de esta convocatoria?*
     - Para el campo `fecha_inicio`, pregunta: *¿Cuándo comienza el plazo de solicitud de esta ayuda?*
     - Para el campo `beneficiarios`, pregunta: *¿Quiénes pueden beneficiarse de esta convocatoria?*

3. **Iteración**:
   - Repite el proceso tantas veces como sea necesario para revisar todos los campos importantes.
   - Si no logras encontrar información clara para un campo, déjalo vacío.

4. **Formato final**:
   - Devuelve el JSON actualizado, con la información refinada.
   - No incluyas explicaciones ni comentarios adicionales.
   - Guarda el JSON refinado como archivo en la carpeta `RefinedJson/`, usando el mismo nombre de archivo original.

5. **Importante**:
   - No inventes datos.
   - Solo modifica campos si estás seguro de que la información extraída del PDF lo justifica.
   - Prioriza siempre la precisión frente a la completitud.

Empieza ahora con el siguiente JSON:
{json.dumps(json_data, indent=2, ensure_ascii=False)}
    """

    resultado = agent.run(prompt)

    os.makedirs("data/json/refined", exist_ok=True)

    nombre_archivo = os.path.basename(path_json)
    path_guardado = os.path.join("data/json/refined", nombre_archivo)

    try:
        json_refinado = json.loads(resultado)
        with open(path_guardado, "w", encoding="utf-8") as f:
            json.dump(json_refinado, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON refinado guardado en {path_guardado}")
    except json.JSONDecodeError:
        print("⚠️ No se pudo parsear el resultado como JSON.")
        print("Resultado bruto:")
        print(resultado)

    return resultado
