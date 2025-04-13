import asyncio
from typing import List
import httpx
import uuid
import os
from agents.crawler_agent import crawl_convocatoria

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

        
        # Paso 3: Refinamiento concurrente
        refine_tasks = []
        for result in crawled_results:
            if result.get("status") == "ok":
                json_data = result["data"]
                pdf_path = result["pdf_path"]
                refine_tasks.append(
                    self.call_agent(self.refine_agent_url, {"json_data": json_data, "pdf_path": pdf_path})
                )

        refined_results = await asyncio.gather(*refine_tasks)

        # Paso 4: Guardado en DB
        for refined in refined_results:
            if refined.get("status") == "ok":
                await self.call_agent(self.db_manager_url, {
                    "json_data": refined["data"],
                    "pdf_path": refined["pdf_path"]
                })

    async def call_agent(self, url, payload):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)
                return response.json()
            except Exception as e:
                print(f"Error al llamar a {url}: {e}")
                return {}



if __name__ == "__main__":
    manager = CrawlingManager(
        nav_agent_url="http://localhost:8001/navigate",
        crawl_agent_url="http://localhost:8002/crawl",
        refine_agent_url="http://localhost:8003/refine",
        db_manager_url="http://localhost:8004/store"
    )

    asyncio.run(manager.run_pipeline("https://convocatorias.es"))
