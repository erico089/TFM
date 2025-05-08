import os
import json
import shutil
import requests
import concurrent.futures

def getIdFromFile(file_path: str) -> str:
    """
    Extrae el nombre del archivo sin extensión (quitando repeticiones de extensiones comunes como .json, .txt, etc.).
    
    Args:
        file_path (str): Ruta completa o nombre del archivo.

    Returns:
        str: Nombre del archivo sin extensiones.
    """
    filename = os.path.basename(file_path)

    while filename.endswith('.json') or filename.endswith('.txt') or filename.endswith('.pdf'):
        filename = filename.rsplit('.', 1)[0]
    
    return filename

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


def listJSONs(path: str):
    f"""
    Busca todos los archivos JSON en el directorio {path} y sus subdirectorios
    (excepto 'refined') y devuelve una lista con las rutas completas de cada uno.

    Returns:
        list[str]: Una lista de rutas completas a los archivos .json encontrados en {path} y sus subdirectorios.
    """
    jsons = []

    for root, dirs, files in os.walk(path):
        if 'refined' in dirs:
            dirs.remove('refined')

        if 'reference' in dirs:
            dirs.remove('reference')

        for archivo in files:
            if archivo.endswith('.json'):
                jsons.append(os.path.join(root, archivo))

    return jsons

def create_json_templates(jsons: list[str], base_path: str, max_workers=10):
    """
    Crea copias de los JSONs en una carpeta 'refined' dentro de base_path.

    Args:
        jsons (list[str]): Lista de rutas de archivos JSON a copiar.
        base_path (str): Ruta base donde crear la carpeta 'refined'.

    Returns:
        None
    """
    refined_folder = os.path.join(base_path, "refined")
    os.makedirs(refined_folder, exist_ok=True)

    def copy_single_json(json_path):
        if os.path.exists(json_path):
            filename = os.path.basename(json_path)
            destination = os.path.join(refined_folder, filename)
            shutil.copy(json_path, destination)
        else:
            print(f"Advertencia: El archivo {json_path} no existe y no se ha copiado.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(copy_single_json, jsons)


def downloadPDFs(json_file_paths, pdf_dest_path, max_workers=10):
    """
    Descarga PDFs desde 'Link ficha técnica' y 'Link orden de bases' en cada JSON.
    Crea una carpeta por ID y guarda los PDFs como <id>_ficha.pdf y <id>_bases.pdf.
    Si ya existen, no se vuelven a descargar.
    """
    os.makedirs(pdf_dest_path, exist_ok=True)

    def process_single_json(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                contenido = json.load(f)

            id_convocatoria = getVectorialIdFromFile(json_path)
            carpeta_id = os.path.join(pdf_dest_path, id_convocatoria)
            os.makedirs(carpeta_id, exist_ok=True)

            ficha_url = contenido.get('Link ficha técnica')
            if ficha_url and ficha_url.endswith('.pdf'):
                nombre_ficha = f"{id_convocatoria}_ficha.pdf"
                ruta_ficha = os.path.join(carpeta_id, nombre_ficha)

                if not os.path.exists(ruta_ficha):
                    print(f"Descargando ficha técnica desde: {ficha_url}")
                    descargar_pdf(ficha_url, ruta_ficha)
                else:
                    print(f"Ficha técnica ya existe: {nombre_ficha}")
            else:
                print(f"No hay ficha técnica válida en: {json_path}")

            bases_url = contenido.get('Link orden de bases')
            if bases_url and bases_url.endswith('.pdf'):
                nombre_bases = f"{id_convocatoria}_bases.pdf"
                ruta_bases = os.path.join(carpeta_id, nombre_bases)

                if not os.path.exists(ruta_bases):
                    print(f"Descargando orden de bases desde: {bases_url}")
                    descargar_pdf(bases_url, ruta_bases)
                else:
                    print(f"Orden de bases ya existe: {nombre_bases}")
            else:
                print(f"No hay orden de bases válida en: {json_path}")

        except Exception as e:
            print(f"Error procesando {json_path}: {e}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(process_single_json, json_file_paths)


def descargar_pdf(url, ruta_destino):
    """Descarga un PDF usando requests con reintentos."""
    intentos = 0
    exito = False

    while intentos < 3 and not exito:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/90.0.4430.85 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
                with open(ruta_destino, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Descarga completada y guardada en: {ruta_destino}")
                exito = True
            else:
                raise Exception(f"Respuesta inesperada. Status: {response.status_code}, Content-Type: {response.headers.get('Content-Type')}")
        except Exception as e:
            intentos += 1
            print(f"Error al descargar {url} (intento {intentos}/3): {e}")
            if intentos >= 3:
                print(f"Fallo definitivo al descargar {url}. Se omite este archivo.")


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
        "Fecha de inicio de la convocatoria",
        "Fecha de fin de la convocatoria",
        "Objetivos de la convocatoria",
        "Beneficiarios",
        "Anio",
        "Área de la convocatoria",
        "Presupuesto mínimo disponible",
        "Presupuesto máximo disponible",
        "Duración mínima",
        "Duración máxima",
        "Tipo de financiación",
        "Forma y plazo de cobro",
        "Minimis",
        "Región de aplicación",
        "Link ficha técnica",
        "Link convocatoria",
        "Link orden de bases"
    ]

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for field in required_fields:
            if field not in data:
                print(f"Campo faltante: '{field}' en {json_path}")
                os.remove(json_path)
                return False

        return True

    except Exception as e:
        print(f"Error al procesar {json_path}: {e}")
        return False


def add_missing_keys_to_json(json_file_path):
    """
    Dado un archivo JSON, añade tres claves vacías al JSON y guarda el archivo modificado.
    
    Las claves añadidas son:
    - "intensidad de la subvención"
    - "intensidad del préstamo"
    - "tipo de consorcio"
    - "costes elegibles"
    
    Args:
        json_file_path (str): Ruta completa al archivo JSON que se va a modificar.
    
    Returns:
        None
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        data['Intensidad de la subvención'] = ''
        data['Intensidad del préstamo'] = ''
        data['Tipo de consorcio'] = ''
        data['Costes elegibles'] = ''

        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"El archivo {json_file_path} se ha modificado correctamente.")
    
    except Exception as e:
        print(f"Error al modificar el archivo {json_file_path}: {e}")


def load_refined_urls(path: str) -> list:
    """
    Carga todas las URLs del archivo de texto proporcionado.
    
    Args:
    - path (str): La ruta completa del archivo .txt.
    
    Returns:
    - list: Una lista con todas las URLs encontradas en el archivo.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"El archivo '{path}' no existe.")

    with open(path, 'r', encoding='utf-8') as file:
        links = [line.strip() for line in file if line.strip()]

    return links

