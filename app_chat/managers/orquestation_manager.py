import threading
import time
from app_chat.agents.orquestation_agent import OrchestrationAgent
from app_chat.logging_setup import redirect_stdout_to_logger
import os
import psycopg2
from dotenv import load_dotenv
import zipfile
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class OrchestrationManager:
    def __init__(self):
        self.agent = OrchestrationAgent()
        self.context_history = []
        self.response_received = threading.Event()

        load_dotenv()

        if os.getenv("USE_BACKUP_DATA", "FALSE").upper() == "TRUE":
            self.load_buckup_data()

    def _delayed_processing_message(self):
        """
        Muestra un mensaje de 'Procesando tu consulta...' tras un retraso de 2 segundos si la respuesta no ha llegado aún.
        """
        time.sleep(2)
        if not self.response_received.is_set():
            print("\nProcesando tu consulta (dependiendo de la complejidad, esto puede tardar un poco)...\n")

    def start_chat(self):
        print("\n\n############\n\n")
        print("Hola, soy un agente experto en convocatorias.\n")
        print("Estoy aquí para ayudarte en cualquier consulta que tengas sobre convocatorias, ayudas o subvenciones.\n")
        print("¡Pregúntame lo que quieras!\n")

        while True:
            user_input = input("\nTú: ")

            if user_input.lower() in ["salir", "exit", "adiós", "bye"]:
                print("\nGracias por usar el agente de convocatorias. ¡Hasta pronto!\n")
                break

            context = ""
            for user, agent_internal in self.context_history[-3:]:
                context += f"Tú: {user}\n\nAgente: {agent_internal}\n\n"

            self.response_received.clear()
            delay_thread = threading.Thread(target=self._delayed_processing_message)
            delay_thread.start()

            # with redirect_stdout_to_logger():
            response_obj = self.agent.analyze_prompt(user_input, context)

            self.response_received.set()
            delay_thread.join()

            human_readable_answer = response_obj.get('human_readable_answer', 'Lo siento, no he podido generar respuesta.')
            internal_agent_answer = response_obj.get('internal_agent_answer', '')

            print(f"\nAgente: {human_readable_answer}\n")

            self.context_history.append((user_input, internal_agent_answer))

    def load_buckup_data(self):
        load_dotenv()

        if os.getenv("ENVIRONMENT") == "TEST":
            return
        
        print("\nInsertando datos...")
        postgres_user = os.environ["POSTGRES_USER"]
        postgres_password = os.environ["POSTGRES_PASSWORD"]

        AYUDAS_PATH = BASE_DIR / "./data_backup/postgres/ayudas.sql"
        AYUDAS_REF_PATH = BASE_DIR / "./data_backup/postgres/ayudas_ref.sql"

        VECTORIAL_ZIP_PATH = BASE_DIR / "./data_backup/vector/vec_ayudas_db.zip"
        VECTORIAL_EXTRACT_PATH = BASE_DIR / "./db/"

        try:
            conn = psycopg2.connect(
                dbname= 'ayudas',
                user=postgres_user,          
                password=postgres_password, 
                host='localhost',
                port=5432
            )
            conn.autocommit = True

            cursor = conn.cursor()

            with open(AYUDAS_PATH, 'r', encoding='utf-8') as f:
                sql = f.read()

            cursor.execute(sql)

            with open(AYUDAS_REF_PATH, 'r', encoding='utf-8') as f:
                sql = f.read()

            cursor.execute(sql)

            print("\nDatos insertados correctamente en postgres")

            if os.path.exists(VECTORIAL_ZIP_PATH):
                if os.path.exists(VECTORIAL_EXTRACT_PATH):
                    shutil.rmtree(VECTORIAL_EXTRACT_PATH)
                    print(f"Carpeta {VECTORIAL_EXTRACT_PATH} eliminada para limpieza.")

                os.makedirs(VECTORIAL_EXTRACT_PATH, exist_ok=True)

                with zipfile.ZipFile(VECTORIAL_ZIP_PATH, 'r') as zip_ref:
                    zip_ref.extractall(VECTORIAL_EXTRACT_PATH)
                    print(f"Vectorial database extraída en {VECTORIAL_EXTRACT_PATH}.\n")
            else:
                print(f"No se encontró el ZIP de la base de datos vectorial en {VECTORIAL_ZIP_PATH}.\n")


        except Exception as e:
            print(f"Error: {e}") 

        finally:
            if conn:
                cursor.close()
                conn.close()

