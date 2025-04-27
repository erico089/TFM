# main.py

from managers.navigation_manager import NavigationManager

def main():
    url = "https://www.ejemplo.com/convocatorias"

    instructions_file_path = "path/to/instructions.txt" 

    navigation_manager = NavigationManager()

    navigation_manager.run(url, instructions_file_path)

if __name__ == "__main__":
    main()
