from agents.navigation_agent import navigate_convocatoria, verify_convocatoria
from playwright.async_api import async_playwright
import os

class NavigationManager:
    def __init__(self):
        pass

    async def run(self, url: str, instructions_file_path: str):
        """
        La función principal que se ejecuta. Recibe la URL de la página web y el path al archivo de instrucciones.
        """
        with open(instructions_file_path, 'r', encoding='utf-8') as file:
            instructions = file.read()

        await navigate_convocatoria(url, instructions)


class NavigationManager:
    def __init__(self):
        pass

    async def run(self, url: str, instructions_file_path: str):
        """
        La función principal que se ejecuta. Recibe la URL de la página web y el path al archivo de instrucciones.
        """
        with open(instructions_file_path, 'r', encoding='utf-8') as file:
            instructions = file.read()

        await navigate_convocatoria(url, instructions)

    async def process_urls(self, urls_file_path: str):
        """
        Lee las URLs del archivo especificado, abre cada una usando Playwright,
        obtiene la URL final (después de posibles redirecciones) y la guarda en un nuevo archivo '_refined'.
        """
        refined_urls = []

        if not os.path.exists(urls_file_path):
            raise FileNotFoundError(f"El archivo {urls_file_path} no existe.")

        with open(urls_file_path, 'r', encoding='utf-8') as file:
            urls = [line.strip().strip('"') for line in file if line.strip()]


        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            for index, url in enumerate(urls):
                try:
                    await page.goto(url, timeout=15000)
                    final_url = page.url
                    refined_urls.append(final_url)
                    print(f"[{index+1}/{len(urls)}] Procesada: {final_url}")
                except Exception as e:
                    print(f"Error accediendo a {url}: {e}")

            await browser.close()

        base, ext = os.path.splitext(urls_file_path)
        refined_file_path = f"{base}_refined{ext}"

        os.makedirs(os.path.dirname(refined_file_path), exist_ok=True)
        with open(refined_file_path, 'w', encoding='utf-8') as file:
            for url in refined_urls:
                file.write(url + "\n")

        print(f"Archivo refinado guardado en: {refined_file_path}")

    async def verify_convos(self):
        """
        Esta función lee URLs desde 'data/nav_urls/urls_refined.txt' y
        para cada URL llama a 'verify_convocatoria'.
        """

        urls_file = "data/nav_urls/urls_refined.txt"

        if not os.path.exists(urls_file):
            print(f"El archivo {urls_file} no existe.")
            return

        with open(urls_file, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]

        if not urls:
            print("No se encontraron URLs en el archivo.")
            return

        for url in urls:
            print(f"Procesando URL: {url}")
            try:
                await verify_convocatoria(url)
            except Exception as e:
                print(f"Error procesando {url}: {str(e)}")

