# main.py
from app_chat.managers.orquestation_manager import OrchestrationManager

def main():
    manager = OrchestrationManager()
    manager.start_chat()

if __name__ == "__main__":
    main()
