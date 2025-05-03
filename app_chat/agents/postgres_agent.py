import os
import psycopg2
from dotenv import load_dotenv
from azureOpenAIServerModel import AzureOpenAIServerModel
from smolagents import CodeAgent, tool
from tools.postgres_tools import get_record_by_id, get_record_by_id_vectorial, run_query

class PostgresAgent:
    def __init__(self):
        
        load_dotenv()

        postgres_user = os.environ["POSTGRES_USER"]
        postgres_password = os.environ["POSTGRES_PASSWORD"]
        api_key = os.environ["AZURE_OPENAI_KEY"]
        deployment_name = os.environ["AZURE_OPENAI_MODEL_ID"]
        api_base = os.environ["AZURE_OPENAI_ENDPOINT"] 
        api_version = os.environ["AZURE_API_VERSION"] 

        self.connection = psycopg2.connect(
            dbname='ayudas',
            user=postgres_user,          
            password=postgres_password, 
            host='localhost',
            port=5432,
            options="-c client_encoding=UTF8"
        )

        model = AzureOpenAIServerModel(
            model_id = deployment_name,
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=api_base
        )

        self.agent = CodeAgent(
            model=model,
            tools=[run_query, get_record_by_id, get_record_by_id_vectorial],
        )

    def analyze_prompt(self, prompt) -> str:
        task = f"""
        Dispones de una conexión a una base de datos PostgreSQL que contiene información sobre ayudas.

        Dado el siguiente prompt de usuario: "{prompt}", tu tarea es:
        - Utilizar las herramientas disponibles para consultar la base de datos y obtener toda la información necesaria.
        - Siempre que uses una herramienta, debes pasarle la conexión: por ejemplo, `run_query(self.connection, "SELECT * FROM ayudas")`.
        - Dispones de las siguientes herramientas:
            - `run_query`: para ejecutar consultas SQL personalizadas (principalmente sobre la tabla "ayudas"). Ten en cuenta que todos los campos a exepcion de ambas tablas son de tipo text.
            - `get_record_by_id` y `get_record_by_id_vectorial`: para recuperar registros específicos a partir del ID o ID vectorial.

        Instrucciones importantes:
        - Cuando la tarea esté enfocada en una ayuda concreta (es decir, cuando dispongas de un ID o un ID vectorial), **debes preferir** usar `get_record_by_id` o `get_record_by_id_vectorial`.
        - En la respuesta que generes para el usuario, **siempre debes incluir explícitamente** el **ID** y el **ID vectorial** de cada ayuda referenciada.

        Información crítica sobre los resultados:
        - Las herramientas `get_record_by_id` y `get_record_by_id_vectorial` también devuelven algunos campos adicionales que tienen el mismo nombre que los originales, pero terminados en "_ref" (por ejemplo: `fecha_inicio` y `fecha_inicio_ref`).
        - Estos campos "_ref" indican el **nivel de fiabilidad** del valor original:
            - Si un campo "_ref" tiene un valor válido (normalmente un número o identificador), significa que el dato correspondiente es **altamente fiable**.
            - Si el campo "_ref" está vacío o nulo, significa que el dato es **menos fiable** y deberías advertir al usuario en tu respuesta. Puedes usar frases como:
                - "Este dato debería validarse."
                - "Existe cierta incertidumbre sobre esta información."
        - Si un campo no tiene un correspondiente campo "_ref", se puede considerar fiable de forma normal.

        Recuerda ser preciso, utilizar las herramientas de forma eficiente y construir una respuesta clara, completa y transparente para el usuario.
        """

        return self.agent.run(task)

@tool
def ask_postgres_agent(prompt: str) -> str:
    """
    Envía un prompt al agente de PostgreSQL para su análisis.

    Args:
        prompt (str): El texto o consulta que se desea analizar mediante el agente de PostgreSQL.

    Returns:
        str: Resultado del análisis del agente de PostgreSQL.
    """
    postgres_agent = PostgresAgent()
    return postgres_agent.analyze_prompt(prompt)