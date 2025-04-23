import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def getIdFromFile(file_path: str) -> str:
    """
    Extrae el nombre del archivo sin extensión ni ruta.

    Args:
        file_path (str): Ruta completa o nombre del archivo.

    Returns:
        str: Nombre del archivo sin extensión.
    """
    return os.path.splitext(os.path.basename(file_path))[0]

def getVectorialIdFromFile(file_path: str) -> str:
    """
    Obtiene el ID vectorial desde un path de archivo.
    Si el nombre contiene una o más partes separadas por '_', se sigue esta lógica:
    - Si hay dos partes, devuelve la primera.
    - Si hay tres partes, devuelve la del medio.
    - Si hay una sola parte, devuelve esa.
    - Si hay más de tres, devuelve la segunda como valor representativo.

    Args:
        file_path (str): Ruta completa o nombre del archivo.

    Returns:
        str: ID vectorial basado en la estructura del nombre.
    """
    base_id = getIdFromFile(file_path)
    partes = base_id.split('_')

    if len(partes) == 1:
        return partes[0]
    elif len(partes) == 2:
        return partes[0]
    elif len(partes) == 3:
        return partes[1]
    else:
        return partes[1] 


import os

def listJSONs():
    """
    Busca todos los archivos JSON en el directorio 'data/json' y sus subdirectorios
    (excepto 'refined') y devuelve una lista con las rutas completas de cada uno.

    Returns:
        list[str]: Una lista de rutas completas a los archivos .json encontrados en 'data/json' y sus subdirectorios.
    """
    ruta = 'data/json'
    jsons = []

    for root, dirs, files in os.walk(ruta):
        if 'refined' in dirs:
            dirs.remove('refined')

        if 'reference' in dirs:
            dirs.remove('reference')

        for archivo in files:
            if archivo.endswith('.json'):
                jsons.append(os.path.join(root, archivo))

    return jsons



import tempfile
import shutil

import time
import shutil
import os
import tempfile
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def downloadPDFs(json_file_paths):
    """
    Descarga PDFs desde la propiedad 'Link ficha técnica' en cada JSON usando Selenium.
    El PDF se renombra como <id_unico_extraído_con_GetVectorialLeaderFromFile>.pdf.
    Si ya existe, no se vuelve a descargar.

    Args:
        json_file_paths (list[str]): Lista de rutas completas a archivos JSON.
    """
    destino = 'data/pdf'
    os.makedirs(destino, exist_ok=True)

    carpeta_temp = tempfile.mkdtemp()

    options = Options()
    options.headless = True
    prefs = {
        "download.default_directory": os.path.abspath(carpeta_temp),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
    }
    options.add_experimental_option("prefs", prefs)

    # Configuración para el WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    for json_path in json_file_paths:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                contenido = json.load(f)

            ficha_url = contenido.get('Link ficha técnica')
            if ficha_url and ficha_url.endswith('.pdf'):
                # Usamos solo el ID extraído como nombre final del PDF
                nombre_final = f"{getVectorialIdFromFile(json_path)}.pdf"
                ruta_destino_final = os.path.join(destino, nombre_final)

                if os.path.exists(ruta_destino_final):
                    print(f"🟢 Ya existe: {nombre_final} — no se descarga de nuevo.")
                    continue

                print(f"🟡 Descargando desde: {ficha_url}")
                driver.get(ficha_url)

                # Esperar hasta que el PDF se haya descargado completamente
                nombre_descarga_original = os.path.basename(ficha_url)
                ruta_descargada = os.path.join(carpeta_temp, nombre_descarga_original)
                ruta_descargando = ruta_descargada + ".crdownload"  # Archivo temporal de Chrome

                timeout = 30  # Aumentar el timeout si la descarga es lenta
                start_time = time.time()
                while True:
                    if os.path.exists(ruta_descargada) and not os.path.exists(ruta_descargando):
                        break
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"⏰ Timeout esperando la descarga del PDF desde: {ficha_url}.")
                    time.sleep(1)  # Espera más tiempo entre comprobaciones

                # Renombramos el archivo descargado al nombre final deseado
                shutil.move(ruta_descargada, ruta_destino_final)
                print(f"✅ Descarga completada y guardada como: {nombre_final}")
            else:
                print(f"ℹ️ No hay ficha técnica válida en: {json_path}")
        except Exception as e:
            print(f"❌ Error en {json_path}: {e}")

    driver.quit()




def validate_convocatoria_json(json_path):
    """
    Dado el path de un archivo JSON, esta función verifica si contiene todos los campos
    obligatorios definidos en la estructura de una convocatoria. Si falta alguno, se elimina
    el archivo y se devuelve False. Si están todos los campos, devuelve True.

    Args:
        json_path (str): Ruta al archivo JSON que se quiere validar.

    Returns:
        bool: True si el JSON contiene todos los campos requeridos, False si no.
    """
    required_fields = [
        "Organismo convocante",
        "Nombre de la convocatoria",
        "Linea de la convocatoria",
        "Modalidad o tipo específico",
        "Beneficiarios",
        "Presupuesto mínimo disponible",
        "Presupuesto máximo disponible",
        "Fecha de inicio de la convocatoria",
        "Fecha de fin de la convocatoria",
        "Objetivos de la convocatoria",
        "Tipo de la convocatoria",
        "Área de la convocatoria",
        "Duración mínima",
        "Duración máxima",
        "Tipo de financiación",
        "Forma y plazo de cobro",
        "Minimis",
        "Región de aplicación",
        "Tipo de consorcio",
        "Costes elegibles",
        "Link ficha técnica",
        "Link convocatoria",
        "Link orden de bases"
    ]

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for field in required_fields:
            if field not in data:
                print(f"❌ Campo faltante: '{field}' en {json_path}")
                os.remove(json_path)
                return False

        return True

    except Exception as e:
        print(f"⚠️ Error al procesar {json_path}: {e}")
        return False


def add_missing_keys_to_json(json_file_path):
    """
    Dado un archivo JSON, añade tres claves vacías al JSON y guarda el archivo modificado.
    
    Las claves añadidas son:
    - "año"
    - "intensidad de la subvención"
    - "intensidad del préstamo"
    
    Args:
        json_file_path (str): Ruta completa al archivo JSON que se va a modificar.
    
    Returns:
        None
    """
    try:
        # Cargar el JSON desde el archivo
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Añadir las nuevas claves con valores vacíos
        data['ano'] = ''
        data['Intensidad de la subvención'] = ''
        data['Intensidad del préstamo'] = ''

        # Guardar el archivo modificado
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"El archivo {json_file_path} se ha modificado correctamente.")
    
    except Exception as e:
        print(f"Error al modificar el archivo {json_file_path}: {e}")
