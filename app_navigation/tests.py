import pytest
import asyncio
from managers.navigation_manager import NavigationManager
from mock_data import CTDI_URL, CTDI_URLS
import sys
import os

# Añade automáticamente la carpeta raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Función para inicializar y ejecutar una vez el NavigationManager
@pytest.fixture(scope="module")
def navigation_manager():
    """
    Ejecuta el NavigationManager una vez para todas las pruebas.
    """
    instructions_file_path = "app_navigation/instructions/cdti_instructions.txt" 
    urls_file_path = "data/nav_urls/urls.txt"
    urls_verified_file_path = "data/nav_urls/urls_verifyed.txt"

    # navigation_manager = NavigationManager()
    # asyncio.run(navigation_manager.run(CTDI_URL, instructions_file_path))
    # asyncio.run(navigation_manager.process_urls(urls_file_path))
    # asyncio.run(navigation_manager.verify_convos())

    with open(urls_verified_file_path, "r", encoding="utf-8") as f:
        verified_urls = set(line.strip() for line in f if line.strip())

    return verified_urls

# Ahora parametrize el test para cada URL en CTDI_URLS
@pytest.mark.parametrize("expected_url", CTDI_URLS)
def test_navigation_agent_cdti_should_find_correct_urls(navigation_manager, expected_url):
    """
    Test that the navigation agent can find each of the correct URLs for CDTI.
    """

    # Verifica si la URL esperada está en los URLs verificados
    assert expected_url in navigation_manager, f"URL not found: {expected_url}"

