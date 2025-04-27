class OrchestrationManager:
    def __init__(self):
        pass

    def start_chat(self):
        print("Hola, soy un agente experto en convocatorias.")
        print("Estoy aquí para ayudarte en cualquier consulta que tengas sobre convocatorias, ayudas o subvenciones.")
        print("¡Pregúntame lo que quieras!\n")

        while True:
            user_input = input("Tú: ")

            print(f"Procesando tu consulta (dependiendo de la complejidad, esto puede tardar un poco)...")

            if user_input.lower() in ["salir", "exit", "adiós", "bye"]:
                print("Gracias por usar el agente de convocatorias. ¡Hasta pronto!")
                break
