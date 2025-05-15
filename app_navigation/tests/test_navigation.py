import pytest
import asyncio
from app_navigation.managers.navigation_manager import NavigationManager
from app_navigation.tests.mock_data import CTDI_URL, CTDI_URLS, SODERCAN_URLS, SODERCAN_URL, ANDALUCIA_URL, ANDALUCIA_URLS
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

@pytest.mark.asyncio
async def test_navigation_agent_cdti_complete_flow():
    """
    Ejecuta todo el flujo de navegación y verifica que se encuentran todas las URLs esperadas.
    """

    clean_txt("data/nav_urls/urls.txt")
    clean_txt("data/nav_urls/urls_refined.txt")
    clean_txt("data/nav_urls/urls_verifyed.txt")

    instructions_file_path = "app_navigation/instructions/cdti_instructions.txt"
    urls_file_path = "data/nav_urls/urls.txt"
    urls_verified_file_path = "data/nav_urls/urls_verifyed.txt"

    navigation_manager = NavigationManager()
    await navigation_manager.run(CTDI_URL, instructions_file_path)
    await navigation_manager.process_urls(urls_file_path)
    await navigation_manager.verify_convos()

    with open(urls_verified_file_path, "r", encoding="utf-8") as f:
        verified_urls = set(line.strip() for line in f if line.strip())

    total = len(CTDI_URLS)
    fallidas = [url for url in CTDI_URLS if url not in verified_urls]

    print(f"\nFallaron {len(fallidas)} de {total} URLs.")

    for url in fallidas:
        print(f"URL no encontrada: {url}")

    assert not fallidas, "Algunas URLs no fueron encontradas."

        
@pytest.mark.asyncio
async def test_navigation_agent_sodercan_complete_flow():
    """
    Ejecuta todo el flujo de navegación y verifica que se encuentran todas las URLs esperadas.
    """

    clean_txt("data/nav_urls/urls.txt")
    clean_txt("data/nav_urls/urls_refined.txt")
    clean_txt("data/nav_urls/urls_verifyed.txt")

    instructions_file_path = "app_navigation/instructions/sodercan_instructions.txt"
    urls_file_path = "data/nav_urls/urls.txt"
    urls_verified_file_path = "data/nav_urls/urls_verifyed.txt"

    navigation_manager = NavigationManager()
    await navigation_manager.run(SODERCAN_URL, instructions_file_path)
    await navigation_manager.process_urls(urls_file_path)
    await navigation_manager.verify_convos()

    with open(urls_verified_file_path, "r", encoding="utf-8") as f:
        verified_urls = set(line.strip() for line in f if line.strip())

    total = len(SODERCAN_URLS)
    fallidas = [url for url in SODERCAN_URLS if url not in verified_urls]

    print(f"\nFallaron {len(fallidas)} de {total} URLs.")

    for url in fallidas:
        print(f"URL no encontrada: {url}")

    assert not fallidas, "Algunas URLs no fueron encontradas."


def clean_txt(ruta_archivo):
    with open(ruta_archivo, 'w') as archivo:
        pass

@pytest.mark.asyncio
async def test_navigation_agent_andalucia_complete_flow():
    """
    Ejecuta todo el flujo de navegación y verifica que se encuentran todas las URLs esperadas.
    """

    clean_txt("data/nav_urls/urls.txt")
    clean_txt("data/nav_urls/urls_refined.txt")
    clean_txt("data/nav_urls/urls_verifyed.txt")

    instructions_file_path = "app_navigation/instructions/andalucia_instructions.txt"
    urls_file_path = "data/nav_urls/urls.txt"
    urls_verified_file_path = "data/nav_urls/urls_verifyed.txt"

    navigation_manager = NavigationManager()
    await navigation_manager.run(ANDALUCIA_URL, instructions_file_path)
    await navigation_manager.process_urls(urls_file_path)
    await navigation_manager.verify_convos()

    with open(urls_verified_file_path, "r", encoding="utf-8") as f:
        verified_urls = set(line.strip() for line in f if line.strip())

    total = len(ANDALUCIA_URLS)
    fallidas = [url for url in ANDALUCIA_URLS if url not in verified_urls]

    print(f"\nFallaron {len(fallidas)} de {total} URLs.")

    for url in fallidas:
        print(f"URL no encontrada: {url}")

    assert not fallidas, "Algunas URLs no fueron encontradas."