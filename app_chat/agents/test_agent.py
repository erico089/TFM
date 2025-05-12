import os
from dotenv import load_dotenv
from app_chat.azureOpenAIServerModel import AzureOpenAIServerModel
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

    def compare(self, response: str, expected_response: str) -> bool:
        task = f"""
        Eres un agente encargado de comparar dos respuestas: una respuesta generada por un sistema y una respuesta esperada.

        Tu tarea consiste en analizar ambas respuestas y decidir si la respuesta generada es aceptable respecto a la respuesta esperada, siguiendo estas instrucciones:

        - Si la respuesta generada transmite una idea similar, compatible o razonablemente alineada con la respuesta esperada, debes devolver **TRUE**.
        - No es necesario que las respuestas coincidan exactamente en palabras o estructura; basta con que el significado principal sea coherente.
        - Si encuentras contradicciones claras o errores de sentido entre la respuesta generada y la esperada, debes devolver **FALSE**.
        - Si la respuesta generada no responde de forma adecuada al objetivo de la respuesta esperada, debes devolver **FALSE**.
        - Si las respuestas son razonablemente similares aunque estén formuladas de manera distinta, debes devolver **TRUE**.

        **Importante:**  
        - Sé flexible con diferencias menores en la redacción.
        - Sé estricto en detectar contradicciones o errores importantes.

        Datos a evaluar:
        - Respuesta generada: "{response}"
        - Respuesta esperada: "{expected_response}"

        Devuelve exclusivamente **TRUE** o **FALSE**, sin ninguna explicación adicional.
        """

        return self.agent.run(task) 

