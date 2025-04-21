import uuid
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.crawler_agent import crawl_convocatoria
from agents.refinement_agent import run_refinement_agent
from tools.vectorial_db_tools import process_temp_pdfs_batch, process_pdfs_to_shared_db
from managers.postgres_manager import insert_into_ayudas_batch
from tools.utils import downloadPDFs, listJSONs, validate_convocatoria_json, add_missing_keys_to_json, getVectorialIdFromFile

class CrawlingManager:
    def run(self, start_url: str):
        # Paso 1: Llamar al agente de navegación
        # nav_response = await self.call_agent(self.nav_agent_url, {"start_url": start_url})
        # links = nav_response.get("links", [])
        links = ['https://www.cdti.es/ayudas/proyectos-de-i-d']

        if not links:
            print("No se encontraron enlaces de convocatorias.")
            return

        # Paso 2: Crawling concurrente
        for url in links:
            while True:
                current_id = str(uuid.uuid4())  # Generamos un nuevo ID único
                print(f"🔄 Procesando URL {url} con ID {current_id}")

                # Llamamos a crawl_convocatoria, asumiendo que genera los JSON en una carpeta con el id
                crawl_convocatoria(url, current_id)  # Esta función generará los archivos en la carpeta 'data/json/convo_{current_id}'

                # Verificamos los archivos generados en la carpeta correspondiente
                json_folder = f"data/json/convo_{current_id}"

                if not os.path.exists(json_folder):
                    print(f"❌ No se encontró la carpeta {json_folder}, pasando a la siguiente URL.")
                    break

                # Validamos cada archivo JSON en esa carpeta
                all_valid = True
                for filename in os.listdir(json_folder):
                    if filename.endswith(".json"):
                        json_path = os.path.join(json_folder, filename)

                        if not validate_convocatoria_json(json_path):  # Si no es válido
                            all_valid = False

                # Si todos los JSON son válidos, salimos del bucle
                if all_valid:
                    print(f"✅ Todos los archivos JSON para {url} están validados correctamente.")
                    break  # Salimos del while para ir a la siguiente URL
                else:
                    print(f"🔁 Regenerando JSON para {url} (ID anterior: {current_id})...")
                    # No hacemos break, así que el while repite con un nuevo UUID
        
        # Descargar los PDFs
        json_results = listJSONs()
        print(json_results)
        for json_file in json_results:
            add_missing_keys_to_json(json_file)
        downloadPDFs(json_results)

        # Refinamiento temporal de los PDFs
        process_temp_pdfs_batch()

        # Paso 3: Refinamiento concurrente
        refined_results = []
        for result in json_results:
            json_name = os.path.splitext(os.path.basename(result))[0]
            vector_db_path = f"data/temp_vec_db/{getVectorialIdFromFile(json_name)}"
            refined_json_path = f"data/json/refined/{json_name}.json"
            print(result,vector_db_path)
            run_refinement_agent(result, vector_db_path)
            refined_results.append(refined_json_path)



        # Paso 4: Guardado en DB
        insert_into_ayudas_batch()
        process_pdfs_to_shared_db()
