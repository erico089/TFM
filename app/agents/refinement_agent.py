import os
import json
from smolagents import CodeAgent, OpenAIServerModel, tool
from dotenv import load_dotenv
from tools.vectorial_db_tools import search_from_context_vec_db
from tools.tools import save_json_tool 
from azureOpenAIServerModel import AzureOpenAIServerModel

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
    "Modalidad o tipo específico",
    "Beneficiarios",
    "Presupuesto mínimo disponible",
    "Presupuesto máximo disponible",
    "Fecha de inicio de la convocatoria",
    "Fecha de fin de la convocatoria",
    "Objetivos de la convocatoria",
    "Tipo de la convocatoria",
    "Área de la convocatoria",
    "Duración mínima",
    "Duración máxima",
    "Tipo de financiación",
    "Forma y plazo de cobro",
    "Minimis",
    "Región de aplicación",
    "Costes elegibles",
    "Intensidad de la subvención",
    "Intensidad del préstamo"
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

    context_tool = build_context_tool(vector_path)

    agent = CodeAgent(
        model=model,
        tools=[context_tool, save_json_tool],
        additional_authorized_imports=['json']
    )

    prompt = f"""Eres un agente especializado en el tratamiento de datos de convocatorias públicas.

📥 Recibirás un JSON con información de una convocatoria. Este JSON contiene **tanto campos a revisar como campos contextuales**.

🔎 Tu tarea es **revisar únicamente los campos incluidos en la siguiente lista**:

{campos_a_revisar}

No debes modificar los campos que no estén en esta lista. **Su función es ayudarte a entender mejor el contexto de la convocatoria**, y deberás tenerlos muy en cuenta a la hora de interpretar los campos que sí debes procesar.

---

Para cada uno de los campos a revisar:

- Si el campo tiene ya un valor, verifícalo usando la herramienta correspondiente.
- Si no es correcto, corrígelo con base en el contenido de los fragmentos.
- Si el campo está vacío y puedes completarlo con los fragmentos proporcionados, hazlo.

IMPORTANTE: Usa la información de los campos contextuales para interpretar mejor los fragmentos y entender el significado del campo que estás revisando. Por ejemplo, el campo "Línea de la convocatoria" puede darte pistas muy útiles sobre el tipo de beneficiarios o la intensidad de la subvención.

---

Herramientas:

- Cada campo a revisar tiene una herramienta cuyo nombre es muy similar al del campo.
- Para usarlas correctamente, pásales el path a la base vectorial con la variable `path` (el valor de `{vector_path}`).
- Las herramientas devuelven fragmentos con texto y metadatos.

En cada fragmento, la metadata contiene una propiedad `fragment`, que es un ID numérico único. Esa es la propiedad que debes usar para la trazabilidad.

---

Trazabilidad:

- Por cada campo que revises, además del valor final, deberás generar un JSON paralelo con el mismo nombre de campo, pero con sufijo `_ref`.
- En este JSON paralelo, guarda una lista de los valores `fragment` de los fragmentos que sustentan el valor del campo.
  Por ejemplo:
  ```json
  "Beneficiarios": [27, 32, 54]
    ```
    Guardado final:

    Usa la herramienta SaveJSONTool para guardar:

    El JSON corregido en: data/json/refined/

    El JSON de referencias en: data/json/reference/

    Objetivo:

    Tu objetivo es asegurar que todos los campos definidos como relevantes estén verificados, corregidos o completados con evidencia. Y cada valor final debe estar claramente justificado por uno o más fragmentos del documento.

    El JSON de entrada es el siguiente: {json.dumps(json_data, indent=2, ensure_ascii=False)} """

    resultado = agent.run(prompt)

    return resultado
