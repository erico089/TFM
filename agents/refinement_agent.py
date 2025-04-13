from smolagents import CodeAgent, OpenAIServerModel, tool
from dotenv import load_dotenv
import os
from tools.tools import leer_pdf, leer_json

load_dotenv()
api_key = os.environ["OPENROUTER_API_KEY"]

model = OpenAIServerModel(
    model_id="deepseek/deepseek-chat-v3-0324:free",
    api_key=api_key,
    api_base="https://openrouter.ai/api/v1"
)

agent = CodeAgent(
    model=model,
    tools=[leer_pdf, leer_json],
    additional_authorized_imports=['json']
)

pdf_path = "pdf/convocatoria_1.pdf"
json_path = "convocatorias/convocatoria_1.json"

prompt = f"""
Vas a recibir dos entradas:

1. Una ruta de pdf con la ficha tecnica de una convocatoria extraída previamente desde la web {pdf_path}.
2. Una ruta de JSON con información estructurada extraída previamente desde la web {json_path}.

Tu tarea es la siguiente:

**PASO 1:** Lee cuidadosamente el contenido del PDF. Extrae toda la información relevante de la ficha técnica de la convocatoria.

**PASO 2:** Compara los datos encontrados en el PDF con los que ya existen en el JSON proporcionado.

**PASO 3:** Realiza las siguientes acciones:

    - Si un campo del JSON está vacío o incompleto, complétalo usando la información que encuentres en el PDF.
    - Si un campo ya tiene información, pero en el PDF aparece algo diferente, **corrige el valor y usa la información del PDF como fuente válida**.
    - Si algún campo no puede ser extraído de forma clara, déjalo vacío.

**PASO 4:** Devuelve un nuevo JSON **completamente corregido y validado**.

**Importante:** Sé riguroso, no inventes datos. Si el PDF no tiene un campo claro, déjalo vacío. Prioriza siempre la información del PDF frente a la del JSON si hay contradicción.
"""

result = agent.run(prompt)
print(result)