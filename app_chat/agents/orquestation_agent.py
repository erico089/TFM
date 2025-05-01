from smolagents import CodeAgent, tool, DuckDuckGoSearchTool
from dotenv import load_dotenv
import os
import psycopg2
from azureOpenAIServerModel import AzureOpenAIServerModel
from app_chat.agents.vectorial_agent import VectorialAgent
from app_chat.agents.postgres_agent import PostgresAgent

class OrchestrationAgent:
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
            port=5432
        )

        self.vectorial_agent = VectorialAgent()
        self.postgres_agent = PostgresAgent()

        @tool
        def ask_vectorial_agent(prompt):
            """
            Envía un prompt al agente vectorial para su análisis.

            Args:
                prompt (str): El texto o consulta que se desea analizar mediante el agente vectorial.

            Returns:
                Resultado del análisis del agente vectorial.
            """
            return self.vectorial_agent.analyze_prompt(prompt)

        @tool
        def ask_postgres_agent(prompt):
            """
            Envía un prompt al agente de PostgreSQL para su análisis.

            Args:
                prompt (str): El texto o consulta que se desea analizar mediante el agente de PostgreSQL.

            Returns:
                Resultado del análisis del agente de PostgreSQL.
            """
            return self.postgres_agent.analyze_prompt(prompt)

        @tool
        def extract_from_id_if_present( id):
            """
            Ejecuta una consulta SELECT con JOIN para obtener un registro de la tabla 'ayudas' y 'ayudas_ref' según su ID.

            Args:
                id (int): ID del registro que se desea consultar.

            Returns:
                tuple: Tupla con los valores de las columnas del registro encontrado, o None si no existe. Algunas columnas tendran otras con el mismo nombre _ref, si estas tienen valor, aseguran la calidad de los datos.
            """

            cur = self.connection.cursor()
            cur.execute("select * from ayudas inner join ayudas_ref on ayudas.id = ayudas_ref.id where ayudas.id = %s;", (id,))
            result = cur.fetchone()
            cur.close()
            self.connection.close()
            return result

        model = AzureOpenAIServerModel(
            model_id = deployment_name,
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=api_base
        )

        self.agent = CodeAgent(
            model=model,
            tools=[ask_vectorial_agent, ask_postgres_agent, DuckDuckGoSearchTool(), extract_from_id_if_present],
        )


    def analyze_prompt(self, prompt, context=None):
        print(f"Analizando el prompt recibido: '{prompt}'")
        if context is None:
            context = []

        orchestration_prompt = f"""
        Eres un agente de orquestación especializado en encontrar información sobre convocatorias (ayudas, subvenciones, programas, etc.). Dispones de las siguientes herramientas:

        1. **extract_from_id_if_present**: Extrae directamente toda la información de una convocatoria dado su ID. Úsala inmediatamente si dispones de un ID claro relacionado con una convocatoria. Debes priorizar esta herramienta si el ID está presente en el contexto o en el prompt. Esta herramienta es la más rápida y directa para obtener información específica de una convocatoria. 

        2. **ask_postgres_agent**: Accede a una base de datos estructurada que contiene convocatorias. Devuelve:
        - El ID de la fila (row) donde está almacenada la convocatoria.
        - El ID del fichero relacionado en la base vectorial.
        - Todos los datos de convocatorias que hayas pedido.

        Debes priorizar el uso de ask_postgres_agent cuando la consulta esté relacionada con alguno de los siguientes campos:
        - Nombre de la convocatoria
        - Linea de la convocatoria
        - Duración mínima
        - Duración máxima
        - Organismo convocante
        - Fecha de inicio de la convocatoria
        - Fecha de fin de la convocatoria
        - Objetivos de la convocatoria
        - Beneficiarios
        - Anio
        - Área de la convocatoria
        - Presupuesto mínimo disponible
        - Presupuesto máximo disponible
        - Tipo de financiación
        - Forma y plazo de cobro
        - Minimis
        - Región de aplicación
        - Link ficha técnica
        - Link convocatoria
        - Link orden de bases
        - Intensidad de la subvención
        - Intensidad del préstamo
        - Tipo de consorcio
        - Costes elegibles

        3. **ask_vectorial_agent**: Consulta una base vectorial más flexible y semántica. Úsala si:
        - Postgres no puede resolver completamente.
        - Postgres devuelve un ID de fichero y necesitas más detalles.
        - Necesitas información adicional o especifica que no está en la base de datos estructurada.
        - Siempre que uses ask_vectorial_agent y dispongas de un ID de fichero, pásalo para enfocar la búsqueda de forma precisa.

        4. **DuckDuckGoSearchTool**: Realiza búsquedas generales en Internet. Úsala si:
        - La pregunta es sobre conceptos generales, definiciones o historia de convocatorias.
        - No obtienes suficiente información de las bases de datos anteriores.

        Normas de actuación:
        - **Prioriza el uso de extract_from_id_if_present si tienes un ID claro** en el contexto o en el prompt.
        - **Luego intenta resolver con Postgres** usando los campos relevantes.
        - **Si Postgres no puede** o **devuelve un ID de fichero**, usa ask_vectorial_agent para buscar detalles, pasando siempre ese ID de fichero.
        - **En último caso, usa DuckDuckGo** si es necesario.
        - Cuando debas listar varias convocatorias como respuesta, **asegúrate de que cada convocatoria esté claramente identificada**, proporcionando como mínimo:
        - El **nombre completo** de la convocatoria.

        Esto facilitará que si el usuario dice "me interesa la primera" o "quiero más información sobre la segunda", puedas rastrear exactamente a qué convocatoria se refiere.

        **Importante**:
        - **No inventes datos**. Si no encuentras la información, explica claramente qué herramientas usaste y que no has podido encontrar una respuesta completa.
        - **Responde de forma precisa, estructurada y comprensible** para el usuario.

        Contexto de conversación anterior (últimos mensajes relevantes):
        {context}

        Nueva pregunta del usuario:
        {prompt}

        Ahora, actúa siguiendo estrictamente las instrucciones anteriores.
        """

        return self.agent.run(orchestration_prompt)
