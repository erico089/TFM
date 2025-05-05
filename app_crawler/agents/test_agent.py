import os
from dotenv import load_dotenv
from azureOpenAIServerModel import AzureOpenAIServerModel
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
        )

    def compare(self, field: str, response: str, expected_response: str) -> bool:
        task = f"""
        Eres un agente encargado de comparar dos respuestas relacionadas con un campo específico de datos.

        Recibirás:
        - El nombre del campo a evaluar.
        - Una respuesta generada por un sistema.
        - Una respuesta esperada.

        Tu tarea consiste en analizar ambas respuestas y decidir si la respuesta generada es aceptable respecto a la respuesta esperada, siguiendo estrictamente estas instrucciones:

        - Entiende bien qué tipo de información representa el campo recibido.
        - Si la respuesta generada y la esperada son compatibles, coherentes y no presentan ninguna contradicción importante, debes devolver **TRUE**.
        - Si hay **cualquier contradicción** o **error relevante** entre la respuesta generada y la respuesta esperada, debes devolver **FALSE**.
        - Diferencias menores de redacción, cambios no críticos en la información, o detalles adicionales que no contradigan el sentido general son aceptables.
        - Si la respuesta generada omite datos secundarios pero mantiene la esencia correcta respecto a la esperada, debes devolver **TRUE**.
        - Si falta información crítica o se agregan datos que cambian el significado esperado, debes devolver **FALSE**.

        **Importante:**
        - La presencia de cualquier contradicción implica **obligatoriamente** devolver **FALSE**.
        - No devuelvas ninguna explicación ni comentario adicional, solo responde con **TRUE** o **FALSE**.

        Datos a evaluar:
        - Campo: "{field}"
        - Respuesta generada: "{response}"
        - Respuesta esperada: "{expected_response}"

        Recuerda: SOLO devuelve **TRUE** o **FALSE**.
        """

        return self.agent.run(task) 

