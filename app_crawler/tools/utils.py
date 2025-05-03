import os
import json
import shutil
import tempfile
import requests


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

import os
import json
import shutil
import tempfile
from playwright.sync_api import sync_playwright

def downloadPDFs(json_file_paths):
    """
    Descarga PDFs desde 'Link ficha técnica' y 'Link orden de bases' en cada JSON.
    Crea una carpeta por ID y guarda los PDFs como <id>_ficha.pdf y <id>_bases.pdf.
    Si ya existen, no se vuelven a descargar.
    """
    destino = 'data/pdf'
    os.makedirs(destino, exist_ok=True)

    for json_path in json_file_paths:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                contenido = json.load(f)

            id_convocatoria = getVectorialIdFromFile(json_path)
            carpeta_id = os.path.join(destino, id_convocatoria)
            os.makedirs(carpeta_id, exist_ok=True)

            # --- Descarga ficha técnica ---
            ficha_url = contenido.get('Link ficha técnica')
            if ficha_url and ficha_url.endswith('.pdf'):
                nombre_ficha = f"{id_convocatoria}_ficha.pdf"
                ruta_ficha = os.path.join(carpeta_id, nombre_ficha)

                if not os.path.exists(ruta_ficha):
                    print(f"🟡 Descargando ficha técnica desde: {ficha_url}")
                    descargar_pdf(ficha_url, ruta_ficha)
                else:
                    print(f"🟢 Ficha técnica ya existe: {nombre_ficha}")
            else:
                print(f"ℹ️ No hay ficha técnica válida en: {json_path}")

            # --- Descarga orden de bases (opcional) ---
            bases_url = contenido.get('Link orden de bases')
            if bases_url and bases_url.endswith('.pdf'):
                nombre_bases = f"{id_convocatoria}_bases.pdf"
                ruta_bases = os.path.join(carpeta_id, nombre_bases)

                if not os.path.exists(ruta_bases):
                    print(f"🟡 Descargando orden de bases desde: {bases_url}")
                    descargar_pdf(bases_url, ruta_bases)
                else:
                    print(f"🟢 Orden de bases ya existe: {nombre_bases}")
            else:
                print(f"ℹ️ No hay orden de bases válida en: {json_path}")

        except Exception as e:
            print(f"❌ Error procesando {json_path}: {e}")

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
            print(f"⚠️ Error al descargar {url} (intento {intentos}/3): {e}")
            if intentos >= 3:
                print(f"❌ Fallo definitivo al descargar {url}. Se omite este archivo.")


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
        # Cargar el JSON desde el archivo
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Añadir las nuevas claves con valores vacíos
        data['Intensidad de la subvención'] = ''
        data['Intensidad del préstamo'] = ''
        data['Tipo de consorcio'] = ''
        data['Costes elegibles'] = ''

        # Guardar el archivo modificado
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"El archivo {json_file_path} se ha modificado correctamente.")
    
    except Exception as e:
        print(f"Error al modificar el archivo {json_file_path}: {e}")


def load_refined_urls(path: str) -> list:
    """
    Carga todas las URLs de los archivos '_verifyed.txt' en la carpeta indicada.
    
    Args:
    - carpeta (str): La ruta donde se encuentran los archivos '_verifyed.txt'.
    
    Returns:
    - list: Una lista con todas las URLs encontradas en el archivo '_verifyed.txt'.
    """
    archivo_refinado = None
    for archivo in os.listdir(path):
        if archivo.endswith('_verifyed.txt'):
            archivo_refinado = os.path.join(path, archivo)
            break

    if archivo_refinado is None:
        raise FileNotFoundError("No se encontró ningún archivo que termine en '_verifyed.txt' en la carpeta.")

    links = []
    with open(archivo_refinado, 'r', encoding='utf-8') as file:
        links = [line.strip() for line in file if line.strip()]  # Filtra las líneas vacías

    return links
