import asyncio
from app_navigation.managers.navigation_manager import NavigationManager

def main():
    # url = "https://www.cdti.es/"
    url = "https://www.andaluciatrade.es/"

    # instructions_file_path = "app_navigation/instructions/cdti_instructions.txt" 
    instructions_file_path = "app_navigation/instructions/andalucia_instructions.txt" 
    urls_file_path = "data/nav_urls/urls.txt"

    navigation_manager = NavigationManager()

    asyncio.run(navigation_manager.run(url, instructions_file_path))

    asyncio.run(navigation_manager.process_urls(urls_file_path))

    asyncio.run(navigation_manager.verify_convos())

if __name__ == "__main__":
    main()
