import threading
import time
from agents.orquestation_agent import OrchestrationAgent
from logging_setup import redirect_stdout_to_logger

class OrchestrationManager:
    def __init__(self):
        self.agent = OrchestrationAgent()
        self.context_history = []
        self.response_received = threading.Event()

    def _delayed_processing_message(self):
        """
        Muestra un mensaje de 'Procesando tu consulta...' tras un retraso de 2 segundos si la respuesta no ha llegado aún.
        """
        time.sleep(2)
        if not self.response_received.is_set():
            print("\nProcesando tu consulta (dependiendo de la complejidad, esto puede tardar un poco)...\n")

    def start_chat(self):
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

            with redirect_stdout_to_logger():
                response_obj = self.agent.analyze_prompt(user_input, context)

            self.response_received.set()
            delay_thread.join()

            human_readable_answer = response_obj.get('human_readable_answer', 'Lo siento, no he podido generar respuesta.')
            internal_agent_answer = response_obj.get('internal_agent_answer', '')

            print(f"\nAgente: {human_readable_answer}\n")

            self.context_history.append((user_input, internal_agent_answer))

