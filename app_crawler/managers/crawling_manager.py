import uuid
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.crawler_agent import crawl_convocatoria
from agents.refinement_agent import run_refinement_agent
from tools.vectorial_db_tools import process_temp_pdfs_batch, process_pdfs_to_shared_db
from managers.postgres_manager import insert_into_ayudas_batch, insert_into_ayudas_ref_batch, fix_minimis_in_jsons
from tools.utils import downloadPDFs, listJSONs, validate_convocatoria_json, add_missing_keys_to_json, getVectorialIdFromFile, load_refined_urls, create_json_templates

class CrawlingManager:
    def __init__(
        self,
        urls_path: str = 'data/nav_urls/urls_verifyed.txt',
        json_folder_base: str = 'data/json',
        pdf_folder_base: str = 'data/pdf',
        db_vec_temp_dir: str = 'data/temp_vec_db',
        db_vec_dir: str = 'db/vec_ayudas_db',
        insert: bool = True
    ):
        self.urls_path = urls_path
        self.json_folder_base = json_folder_base
        self.pdf_folder_base = pdf_folder_base
        self.db_vec_temp_dir = db_vec_temp_dir
        self.db_vec_dir = db_vec_dir
        self.insert = insert

    
    def run(self):
        links = load_refined_urls(self.urls_path) 

        if not links:
            print("Faltan los enlaces de convocatorias.")
            return

        self.crawl_urls(links)
        json_results = listJSONs(self.json_folder_base)
        for json in json_results:
            add_missing_keys_to_json(json)
        downloadPDFs(json_results, self.pdf_folder_base)
        create_json_templates(json_results, self.json_folder_base)
        process_temp_pdfs_batch(self.pdf_folder_base, self.db_vec_temp_dir)

        self.run_refinement_agents(json_results)

        fix_minimis_in_jsons(f"{self.json_folder_base}/refined")

        if (self.insert):
            insert_into_ayudas_batch(self.json_folder_base)
            insert_into_ayudas_ref_batch(self.json_folder_base)
            process_pdfs_to_shared_db(self.pdf_folder_base, self.db_vec_dir)

    def crawl_urls(self, links):

        for link in links:
            self.crawl_process_single_url(link)

    def crawl_process_single_url(self, url):
        """Método privado que procesa una sola URL: crawl + validar"""
        while True:
            current_id = str(uuid.uuid4())
            print(f"Procesando URL {url} con ID {current_id}")

            crawl_convocatoria(url, current_id, self.json_folder_base)

            json_folder = f"{self.json_folder_base}/convo_{current_id}"

            if not os.path.exists(json_folder):
                print(f"No se encontró la carpeta {json_folder}, pasando a la siguiente URL.")
                break

            all_valid = True
            for filename in os.listdir(json_folder):
                if filename.endswith(".json"):
                    json_path = os.path.join(json_folder, filename)
                    if not validate_convocatoria_json(json_path):
                        all_valid = False

            if all_valid:
                print(f"Todos los archivos JSON para {url} están validados correctamente.")
                break
            else:
                print(f"Regenerando JSON para {url} (ID anterior: {current_id})...")

    def run_refinement_agents(self, json_results):
        def refine_single_json(result):
            json_name = os.path.splitext(os.path.basename(result))[0]
            vector_db_path = f"{self.db_vec_temp_dir}/{getVectorialIdFromFile(json_name)}"
            run_refinement_agent(result, vector_db_path, self.json_folder_base)

        for json in json_results:
            refine_single_json(json);