import psycopg2
import json
from dotenv import load_dotenv
import os
from tools.utils import getIdFromFile, getVectorialIdFromFile

load_dotenv()

DB_CONFIG = {
    'dbname': 'ayudas',
    'user': os.getenv("POSTGRES_USER", "postgres"),
    'password': os.getenv("POSTGRES_PASSWORD", "postgres"),
    'host': os.getenv("POSTGRES_HOST", "localhost"),
    'port': int(os.getenv("POSTGRES_PORT", 5432)),
}

import json
import psycopg2

def insert_into_ayudas(path_json, conn):
    """
    Inserta los datos del archivo JSON proporcionado en la tabla 'ayudas' de la base de datos.
    
    Args:
        path_json (str): Ruta completa al archivo JSON que contiene la información de la convocatoria.
        conn (psycopg2.connection): Conexión a la base de datos PostgreSQL.
    
    Returns:
        None
    """
    with open(path_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not conn:
        conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print("el path json es:{} con id y vec id respectivamente: {} {}".format(path_json, getIdFromFile(path_json), getVectorialIdFromFile(path_json)))
    file_id = getIdFromFile(path_json)
    file_vectorial_id = getVectorialIdFromFile(path_json)

    if not isinstance(data, list):
        data = [data]

    required_fields = [
    "Organismo convocante", "Nombre de la convocatoria", "Linea de la convocatoria",
    "Fecha de inicio de la convocatoria", "Fecha de fin de la convocatoria",
    "Objetivos de la convocatoria", "Beneficiarios", "Anio",
    "Área de la convocatoria", "Presupuesto mínimo disponible", "Presupuesto máximo disponible",
    "Duración mínima", "Duración máxima", "Intensidad de la subvención", "Intensidad del préstamo",
    "Tipo de financiación", "Forma y plazo de cobro", "Minimis", "Región de aplicación",
    "Tipo de consorcio", "Costes elegibles", "Link ficha técnica", "Link convocatoria",
    "Link orden de bases"
    ]

    for item in data:
        item["id"] = file_id
        item["id_vectorial"] = file_vectorial_id

    print("Item keys:", item.keys())

    for field in required_fields:
            if field not in item:
                print(f"Campo faltante '{field}' en {path_json}. Abortando inserción.")
                cur.close()
                return
            
    query = """
        INSERT INTO ayudas (
            "organismo", "nombre", "linea", 
            "fecha_inicio", "fecha_fin", "objetivo", 
            "beneficiarios", "año", "area", "presupuesto_minimo", "presupuesto_maximo", 
            "duracion_minima", "duracion_maxima", "intensidad_subvencion", "intensidad_prestamo", 
            "tipo_financiacion", "forma_plazo_cobro", "minimis", "region_aplicacion", "tipo_consorcio", 
            "costes_elegibles", "link_ficha_tecnica", "link_convocatoria", "link_orden_bases", 
            id, id_vectorial
        ) VALUES (
            %(Organismo convocante)s, %(Nombre de la convocatoria)s, %(Linea de la convocatoria)s, 
            %(Fecha de inicio de la convocatoria)s, %(Fecha de fin de la convocatoria)s, %(Objetivos de la convocatoria)s, 
            %(Beneficiarios)s, %(Anio)s, %(Área de la convocatoria)s, %(Presupuesto mínimo disponible)s, %(Presupuesto máximo disponible)s, 
            %(Duración mínima)s, %(Duración máxima)s, %(Intensidad de la subvención)s, %(Intensidad del préstamo)s, 
            %(Tipo de financiación)s, %(Forma y plazo de cobro)s, %(Minimis)s, %(Región de aplicación)s, %(Tipo de consorcio)s, 
            %(Costes elegibles)s, %(Link ficha técnica)s, %(Link convocatoria)s, %(Link orden de bases)s, 
            %(id)s, %(id_vectorial)s
        )
    """

    for item in data:
        cur.execute(query, item)

    conn.commit()
    cur.close()

    print(f"Insertado correctamente: {path_json}")

import os
import json

def fix_minimis_in_jsons(carpeta):
    for nombre_archivo in os.listdir(carpeta):
        if nombre_archivo.endswith('.json'):
            ruta_archivo = os.path.join(carpeta, nombre_archivo)
            
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                try:
                    datos = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error al leer {nombre_archivo}, saltando...")
                    continue
            
            if 'Minimis' in datos:
                valor = datos['Minimis']
                if isinstance(valor, str):
                    valor_normalizado = valor.strip().lower()
                    if valor_normalizado == 'true':
                        datos['Minimis'] = True
                    else:
                        datos['Minimis'] = False

            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)


def insert_into_ayudas_batch(base_path: str):
    """
    Inserta múltiples registros en la tabla 'ayudas' a partir de archivos JSON en un directorio específico.
    """
    directory = f"{base_path}/refined"
    connection = psycopg2.connect(**DB_CONFIG)
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            insert_into_ayudas(file_path, connection)
    connection.close()

def insert_into_ayudas_ref_batch(base_path: str):
    """
    Inserta múltiples registros en la tabla 'ayudas_ref' a partir de archivos JSON en el directorio 'data/json/ref'.
    """
    directory = f"{base_path}/reference"
    connection = psycopg2.connect(**DB_CONFIG)
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            insert_into_ayudas_ref(file_path, connection)
    connection.close()

def insert_into_ayudas_ref(path_json, conn):
    """
    Inserta los datos del archivo JSON proporcionado en la tabla 'ayudas_ref' de la base de datos.

    Args:
        path_json (str): Ruta completa al archivo JSON que contiene los fragmentos de referencia.
        conn (psycopg2.connection): Conexión a la base de datos PostgreSQL.

    Returns:
        None
    """
    with open(path_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not conn:
        conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print(f"El path json (ref) es: {path_json} con id y vec id respectivamente: {getIdFromFile(path_json)} {getVectorialIdFromFile(path_json)}")
    file_id = getIdFromFile(path_json)

    if not isinstance(data, list):
        data = [data]

    required_fields = [
        "Organismo convocante_ref", "Fecha de inicio de la convocatoria_ref",
        "Fecha de fin de la convocatoria_ref", "Objetivos de la convocatoria_ref", "Beneficiarios_ref", 
        "Anio_ref", "Presupuesto mínimo disponible_ref", "Presupuesto máximo disponible_ref", 
        "Duración mínima_ref", "Duración máxima_ref", "Tipo de financiación_ref", 
        "Forma y plazo de cobro_ref", "Minimis_ref", "Región de aplicación_ref", 
        "Intensidad de la subvención_ref", "Intensidad del préstamo_ref", "Tipo de consorcio_ref", 
        "Costes elegibles_ref"
    ]

    for item in data:
        item["id"] = file_id

        for key in item.keys():
            if key.endswith('_ref') and item[key] is not None:
                item[key] = json.dumps(item[key], ensure_ascii=False)

        for field in required_fields:
            if field not in item:
                print(f"Campo faltante '{field}' en {path_json}. Creando campo vacío.")
                item[field] = None

    query = """
        INSERT INTO ayudas_ref (
            id,
            organismo_ref,
            fecha_inicio_ref,
            fecha_fin_ref,
            objetivo_ref,
            beneficiarios_ref,
            año_ref,
            presupuesto_minimo_ref,
            presupuesto_maximo_ref,
            duracion_minima_ref,
            duracion_maxima_ref,
            tipo_financiacion_ref,
            forma_plazo_cobro_ref,
            minimis_ref,
            region_aplicacion_ref,
            intensidad_subvencion_ref,
            intensidad_prestamo_ref,
            tipo_consorcio_ref,
            costes_elegibles_ref
        ) VALUES (
            %(id)s,
            %(Organismo convocante_ref)s,
            %(Fecha de inicio de la convocatoria_ref)s,
            %(Fecha de fin de la convocatoria_ref)s,
            %(Objetivos de la convocatoria_ref)s,
            %(Beneficiarios_ref)s,
            %(Anio_ref)s,
            %(Presupuesto mínimo disponible_ref)s,
            %(Presupuesto máximo disponible_ref)s,
            %(Duración mínima_ref)s,
            %(Duración máxima_ref)s,
            %(Tipo de financiación_ref)s,
            %(Forma y plazo de cobro_ref)s,
            %(Minimis_ref)s,
            %(Región de aplicación_ref)s,
            %(Intensidad de la subvención_ref)s,
            %(Intensidad del préstamo_ref)s,
            %(Tipo de consorcio_ref)s,
            %(Costes elegibles_ref)s
        )
    """

    for item in data:
        cur.execute(query, item)

    conn.commit()
    cur.close()

    print(f"Insertado correctamente (ref): {path_json}")

