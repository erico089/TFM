import os
from dotenv import load_dotenv
from app_chat.azureOpenAIServerModel import AzureOpenAIServerModel
from smolagents import CodeAgent, tool
from app_chat.tools.vectorial_tools import get_context, get_context_by_id, get_context_by_id_and_fragment

class VectorialAgent:
    def __init__(self):
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

        self.agent = CodeAgent(
            model=model,
            tools=[get_context, get_context_by_id, get_context_by_id_and_fragment],
        )

    def analyze_prompt(self, prompt: str) -> str:
        task = f"""
        Eres un agente especializado en consultar una base de datos vectorial de fragmentos de documentos.

        Dispones de tres herramientas principales:

        1. get_context_by_id(query, id):
        - Sirve para buscar información específica dentro de un documento concreto (identificado por su id).

        2. get_context_by_id_and_fragment(query, id, fragment):
        - Sirve para buscar información todavía más concreta, limitándote a un fragmento particular dentro de un documento.

        3. get_context(query):
        - Sirve para buscar información general en toda la base de datos vectorial, sin limitarte a un documento o fragmento concreto.

        Funcionamiento esperado:

        - Si el prompt del usuario especifica un id o id + fragment, utiliza las herramientas especializadas correspondientes.
        - Si no se especifica nada concreto, utiliza la búsqueda general.
        - Es muy importante que no te inventes datos ni des respuestas basadas en suposiciones.
        - Siempre analiza cuidadosamente los fragmentos devueltos antes de construir una respuesta.
        - Si la información encontrada responde claramente a la pregunta, genera una respuesta precisa.
        - Si la información encontrada es parcial o incompleta, indícalo de forma explícita.
        - Si no encuentras información relevante, indica que no has encontrado información suficiente para responder.

        Tu objetivo es responder al siguiente prompt del usuario de la forma más precisa, honesta y útil posible, basándote únicamente en la información obtenida mediante tus herramientas.

        Prompt del usuario: {prompt}

        Sigue todas las instrucciones anteriores y responde en consecuencia.
        """
        return self.agent.run(task)

@tool
def ask_vectorial_agent(prompt: str) -> str:
    """
    Envía un prompt al agente vectorial para su análisis.

    Args:
        prompt (str): El texto o consulta que se desea analizar mediante el agente vectorial.

    Returns:
        str: Resultado del análisis del agente vectorial.
    """
    vectorial_agent = VectorialAgent()
    return vectorial_agent.analyze_prompt(prompt)