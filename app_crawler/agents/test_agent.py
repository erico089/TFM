import os
from dotenv import load_dotenv
from app_crawler.azureOpenAIServerModel import AzureOpenAIServerModel
from smolagents import CodeAgent

class TestAgent:
    def __init__(self):
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

        self.agent = CodeAgent(
            model=model,
            tools=[], 
            max_steps=1
        )

    def compare(self, field: str, response: str, expected_response: str) -> bool:
        task = f"""
Eres un agente encargado de comparar dos respuestas relacionadas con un campo específico de datos.

Recibirás:
- El nombre del campo a evaluar.
- Una respuesta generada por un sistema.
- Una respuesta esperada.

Tu tarea consiste en analizar ambas respuestas y decidir si la respuesta generada es aceptable respecto a la respuesta esperada, siguiendo estas instrucciones estrictas pero permisivas:

- Entiende bien qué tipo de información representa el campo recibido.
- Para que la respuesta generada sea aceptable (**TRUE**), debe cumplir dos condiciones:
    1. **La información esperada debe estar incluida, explícita o implícitamente**, en la respuesta generada, aunque se exprese con otras palabras o falten siglas, referencias administrativas o detalles que no afecten al significado principal.
    2. **No debe existir ninguna contradicción importante** entre la información generada y la información esperada.
- La respuesta generada puede contener información adicional, menos detalles o formulaciones alternativas. Esto es aceptable siempre que:
    - No contradiga la respuesta esperada.
    - No omita ningún aspecto crítico para entender o aplicar correctamente la información del campo.
- Diferencias en formato, estilo, redacción, o referencias administrativas no consideradas esenciales (ejemplo: siglas o nombres de organismos) **no invalidan** la respuesta.
- Fechas o plazos expresados en términos relativos o con condiciones equivalentes serán considerados válidos, salvo que contradigan claramente la fecha fija esperada.
- Información extra, irrelevante o más completa **no es motivo** para rechazar la respuesta.
- Solo si falta información crítica o existe alguna contradicción relevante y sustancial, debes devolver **FALSE**.
- En casos de duda razonable por omisión menor o diferencia de nivel de detalle, considera **TRUE**.
- Cuando el mensaje esperado sea vacío o indique “no se especifica”, también darás por válidas respuestas vacías o no detalladas.

**Importante:**
- La mera presencia de más datos o explicaciones NO implica error.
- Solo responde **TRUE** o **FALSE**, sin ningún comentario adicional.

Datos a evaluar:
- Campo: "{field}"
- Respuesta generada: "{response}"
- Respuesta esperada: "{expected_response}"

Recuerda: SOLO devuelve **TRUE** o **FALSE**.
"""



        return self.agent.run(task) 

