from app_crawler.managers.crawling_manager import CrawlingManager
import os
import pytest
from app_crawler.tests.mock_data_andalucia import mock_data
import json
from app_crawler.agents.test_agent import TestAgent
import shutil

@pytest.fixture(scope="session")
def setup_crawling_manager():
    txt_content = """https://juntadeandalucia.es/servicios/sede/tramites/procedimientos/detalle/25569.html
https://juntadeandalucia.es/servicios/sede/tramites/procedimientos/detalle/25606.html"""

    base_path = 'data_crawl_test'
    nav_urls_path = os.path.join(base_path, 'nav_urls')
    urls_file_path = os.path.join(nav_urls_path, 'urls_verifyed.txt')
    json_folder_base = os.path.join(base_path, 'json')
    pdf_folder_base = os.path.join(base_path, 'pdf')
    db_vec_temp_dir = os.path.join(base_path, 'temp_vec_db')
    db_vec_dir = os.path.join(base_path, 'vec_ayudas_db')
    json_folder_refined = os.path.join(json_folder_base, 'refined')
    json_folder_reference = os.path.join(json_folder_base, 'reference')

    os.makedirs(nav_urls_path, exist_ok=True)
    os.makedirs(json_folder_base, exist_ok=True)
    os.makedirs(json_folder_refined, exist_ok=True)
    os.makedirs(json_folder_reference, exist_ok=True)
    os.makedirs(pdf_folder_base, exist_ok=True)
    os.makedirs(db_vec_temp_dir, exist_ok=True)
    os.makedirs(db_vec_dir, exist_ok=True)

    if os.path.exists(urls_file_path):
        with open(urls_file_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)

    manager = CrawlingManager(
        urls_path=urls_file_path,
        json_folder_base=json_folder_base,
        pdf_folder_base=pdf_folder_base,
        db_vec_temp_dir=db_vec_temp_dir,
        db_vec_dir=db_vec_dir,
        insert=False
    )

    manager.run()
    return manager


def test_pdfs_generated_correctly(setup_crawling_manager):
    pdf_folder_base = setup_crawling_manager.pdf_folder_base
    pdf_folders = [d for d in os.listdir(pdf_folder_base) if os.path.isdir(os.path.join(pdf_folder_base, d))]
    
    print(f"\n[INFO] Carpetas de PDFs encontradas: {len(pdf_folders)}")
    for folder in pdf_folders:
        print(f"- {folder}")
    
    assert len(pdf_folders) == 2, f"Se esperaban 2 carpetas en {pdf_folder_base}, pero hay {len(pdf_folders)}"

    total_pdfs = 0
    for folder in pdf_folders:
        folder_path = os.path.join(pdf_folder_base, folder)
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        num_pdfs = len(pdf_files)
        total_pdfs += num_pdfs
        print(f"[INFO] PDFs encontrados en '{folder}': {num_pdfs}")

    print(f"[INFO] Total de PDFs encontrados: {total_pdfs}")
    
    assert total_pdfs == 4, f"Se esperaban 4 PDFs en total en las carpetas de {pdf_folder_base}, pero hay {total_pdfs}"


def test_jsons_reference_and_refined(setup_crawling_manager):
    json_folder_base = setup_crawling_manager.json_folder_base

    reference_folder = os.path.join(json_folder_base, 'reference')
    refined_folder = os.path.join(json_folder_base, 'refined')

    print(f"\n[INFO] Verificando existencia de carpetas:")
    print(f"- Carpeta de referencia: {reference_folder}")
    print(f"- Carpeta de refinados: {refined_folder}")

    assert os.path.exists(reference_folder), f"[ERROR] No se encontró la carpeta {reference_folder}"
    assert os.path.exists(refined_folder), f"[ERROR] No se encontró la carpeta {refined_folder}"

    reference_jsons = [f for f in os.listdir(reference_folder) if f.lower().endswith('.json')]
    refined_jsons = [f for f in os.listdir(refined_folder) if f.lower().endswith('.json')]

    print(f"\n[INFO] Número de JSONs encontrados:")
    print(f"- En 'reference': {len(reference_jsons)} archivos")
    print(f"- En 'refined': {len(refined_jsons)} archivos")

    assert len(reference_jsons) == 2, f"[ERROR] Se esperaban 2 archivos JSON en {reference_folder}, pero hay {len(reference_jsons)}"
    assert len(refined_jsons) == 2, f"[ERROR] Se esperaban 2 archivos JSON en {refined_folder}, pero hay {len(refined_jsons)}"



def test_json_data_quality_and_extraction(setup_crawling_manager):
    print("\n[INFO] Iniciando extracción de JSONs refinados...")

    json_extraidos = []
    ruta_refined = os.path.join(setup_crawling_manager.json_folder_base, "refined")

    for nombre_json in os.listdir(ruta_refined):
        if nombre_json.endswith('.json'):
            ruta_json = os.path.join(ruta_refined, nombre_json)
            with open(ruta_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            json_extraidos.append(datos.copy())

    print(f"[INFO] Se han cargado {len(json_extraidos)} archivos JSON desde {ruta_refined}")

    total_matches = 0
    convs_to_evaluate = []

    for mock in mock_data:
        for json_item in json_extraidos:
            match_url = mock["identificacion"]["url_convocatoria"] in json_item.get("Link convocatoria", "")
            match_nombre = mock["identificacion"]["nombre"] in json_item.get("Nombre de la convocatoria", "")
            match_linea = mock["identificacion"]["linea"] in json_item.get("Linea de la convocatoria", "")

            if match_url or match_nombre or match_linea:
                convs_to_evaluate.append({
                    "mock": mock["datos_test"],
                    "json_real": json_item
                })
                total_matches += 1
                break

    print(f"[INFO] Total matches encontrados: {total_matches}")

    assert total_matches == 2, f"[ERROR] Se esperaban 2 matches, pero se encontraron {total_matches}."

    aciertos = 0
    fallos = 0
    fallos_list = []
    aciertos_list = []

    print("\n[INFO] Iniciando validación de campos...")

    for pair in convs_to_evaluate:
        mock = pair["mock"]
        json_real = pair["json_real"]

        for campo, expected_value in mock.items():
            real_value = json_real.get(campo, "")

            agent = TestAgent()
            comparison_result = agent.compare(campo, real_value, expected_value)
            print(f"la respuesta del agente es: {comparison_result}")
            if isinstance(comparison_result, bool):
                is_correct = comparison_result
            elif isinstance(comparison_result, str):
                is_correct = comparison_result.strip().lower() == "true"
            else:
                raise ValueError(f"[ERROR] Resultado inesperado del agente para campo '{campo}': {comparison_result}")

            if is_correct:
                aciertos += 1
                aciertos_list.append((campo, expected_value, real_value))
            else:
                fallos += 1
                fallos_list.append((campo, expected_value, real_value))

    print(f"\n[INFO] Resumen de validación:")
    print(f"- Campos correctos: {aciertos}")
    print(f"- Campos incorrectos: {fallos}")

    print("\n[SUCCESS] Detalles de los campos correctos:")
    for campo, expected, real in aciertos_list:
        print(f"- Campo: {campo} | Esperado: '{expected}' | Obtenido: '{real}'")

    if fallos_list:
        print("\n[ERROR] Detalles de los fallos encontrados:")
        for campo, expected, real in fallos_list:
            print(f"- Campo: {campo} | Esperado: '{expected}' | Obtenido: '{real}'")

    assert fallos == 0, f"[ERROR] Hay {fallos} fallos en la validación de campos."



