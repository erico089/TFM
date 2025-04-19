import asyncio
import httpx
import uuid
import os
from agents.crawler_agent import crawl_convocatoria
from agents.refinement_agent import run_refinement_agent
from tools.vectorial_db_tools import process_temp_pdfs_batch, process_pdfs_to_shared_db
from postgres_manager import insert_into_ayudas_batch

class CrawlingManager:
    def __init__(self, nav_agent_url, crawl_agent_url, refine_agent_url, db_manager_url):
        self.nav_agent_url = nav_agent_url
        self.crawl_agent_url = crawl_agent_url
        self.refine_agent_url = refine_agent_url
        self.db_manager_url = db_manager_url

    async def run_pipeline(self, start_url: str):
        # Paso 1: Llamar al agente de navegación
        nav_response = await self.call_agent(self.nav_agent_url, {"start_url": start_url})
        links = nav_response.get("links", [])

        if not links:
            print("No se encontraron enlaces de convocatorias.")
            return

        # Paso 2: Crawling concurrente
        crawled_results = []
        for url in links:
            result = crawl_convocatoria(url, str(uuid.uuid4()))
            crawled_results.append(result)

        # Refinamiento temporal de los PDFs
        process_temp_pdfs_batch()

        # Paso 3: Refinamiento concurrente
        refined_results = []
        for result in crawled_results:
            json_name = os.path.splitext(os.path.basename(result))[0]
            vector_db_path = f"data/temp_vec_db/{json_name}"
            refined_json_path=  f"data/json/refined/{json_name}.json"
            run_refinement_agent(result, vector_db_path)
            refined_results.append(refined_json_path)

        # Paso 4: Guardado en DB
        insert_into_ayudas_batch()
        process_pdfs_to_shared_db()


if __name__ == "__main__":
    manager = CrawlingManager(
        nav_agent_url="http://localhost:8001/navigate",
        crawl_agent_url="http://localhost:8002/crawl",
        refine_agent_url="http://localhost:8003/refine",
        db_manager_url="http://localhost:8004/store"
    )

    asyncio.run(manager.run_pipeline("https://convocatorias.es"))
