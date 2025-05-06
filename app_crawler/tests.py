from managers.crawling_manager import CrawlingManager
import os
import pytest
from mock_data import mock_data
import json
from agents.test_agent import TestAgent

@pytest.fixture(scope="session")
def setup_crawling_manager():
    txt_content = """https://www.cdti.es/ayudas/programa-tecnologico-espacial-pte
https://www.cdti.es/ayudas/proyectos-de-i-d
https://www.cdti.es/ayudas/innterconecta-step"""

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

    if not os.path.exists(urls_file_path):
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
    assert len(pdf_folders) == 3, f"Se esperaban 3 carpetas en {pdf_folder_base}, pero hay {len(pdf_folders)}"

    total_pdfs = 0
    for folder in pdf_folders:
        folder_path = os.path.join(pdf_folder_base, folder)
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        total_pdfs += len(pdf_files)

    assert total_pdfs == 4, f"Se esperaban 4 PDFs en total en las carpetas de {pdf_folder_base}, pero hay {total_pdfs}"

def test_jsons_reference_and_refined(setup_crawling_manager):
    json_folder_base = setup_crawling_manager.json_folder_base

    reference_folder = os.path.join(json_folder_base, 'reference')
    refined_folder = os.path.join(json_folder_base, 'refined')

    assert os.path.exists(reference_folder), f"No se encontró la carpeta {reference_folder}"
    assert os.path.exists(refined_folder), f"No se encontró la carpeta {refined_folder}"

    reference_jsons = [f for f in os.listdir(reference_folder) if f.lower().endswith('.json')]
    assert len(reference_jsons) == 10, f"Se esperaban 10 archivos JSON en {reference_folder}, pero hay {len(reference_jsons)}"

    refined_jsons = [f for f in os.listdir(refined_folder) if f.lower().endswith('.json')]
    assert len(refined_jsons) == 10, f"Se esperaban 10 archivos JSON en {refined_folder}, pero hay {len(refined_jsons)}"


def test_json_data_quality_and_extraction(setup_crawling_manager, capsys):
    json_extraidos = []

    ruta_refined = os.path.join(setup_crawling_manager.json_folder_base, "refined")

    for nombre_json in os.listdir(ruta_refined):
        if not nombre_json.endswith('.json'):
            continue

        ruta_json = os.path.join(ruta_refined, nombre_json)
        with open(ruta_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)

        json_extraidos.append(datos.copy())

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

    assert total_matches == 3, f"Se esperaban 3 matches, pero se encontraron {total_matches}."

    aciertos = 0
    fallos = 0
    fallos_list = []
    agent = TestAgent()

    for pair in convs_to_evaluate:
        mock = pair["mock"]
        json_real = pair["json_real"]

        for campo, expected_value in mock.items():
            real_value = json_real.get(campo, "")

            if agent.compare(campo, real_value, expected_value):
                aciertos += 1
            else:
                fallos += 1
                fallos_list.append((campo, expected_value, real_value))

    print(f"\nResumen: {aciertos} campos correctos, {fallos} campos incorrectos.")

    if fallos_list:
        print("\nDetalles de los fallos encontrados:")
        for fallo in fallos_list:
            print(f"- [{fallo['mock_name']}] Campo: {fallo['campo']} | Esperado: '{fallo['expected']}' | Obtenido: '{fallo['real']}'")

    assert fallos == 0, f"Hay {fallos} fallos en la validación de campos."

    captured = capsys.readouterr()
    print("Salida capturada:")
    print(captured.out)


