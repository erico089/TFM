# navigation_manager.py

from agents.navigation_agent import navigate_convocatoria

class NavigationManager:
    def __init__(self):
        pass

    def run(self, url: str, instructions_file_path: str):
        """
        La función principal que se ejecuta. Recibe la URL de la página web y el path al archivo de instrucciones.
        """
        with open(instructions_file_path, 'r') as file:
            instructions = file.read()

        navigate_convocatoria(url, instructions)
