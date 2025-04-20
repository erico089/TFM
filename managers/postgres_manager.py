import psycopg2
import json
from dotenv import load_dotenv
import os
from tools.utils import getIdFromFile, getVectorialIdFromFile

load_dotenv()
postgres_user = os.environ["POSTGRES_USER"]
postgres_password = os.environ["POSTGRES_PASSWORD"]

DB_CONFIG = {
    'dbname': 'ayudas',
    'user': postgres_user,
    'password': postgres_password,
    'host': 'localhost', 
    'port': 5432
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

    for item in data:
        item["id"] = file_id
        item["id_vectorial"] = file_vectorial_id

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
            %(Beneficiarios)s, %(ano)s, %(Área de la convocatoria)s, %(Presupuesto mínimo disponible)s, %(Presupuesto máximo disponible)s, 
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

    print(f"✅ Insertado correctamente: {path_json}")


def insert_into_ayudas_batch():
    """
    Inserta múltiples registros en la tabla 'ayudas' a partir de archivos JSON en un directorio específico.
    """
    directory = "data/json/refined"
    connection = psycopg2.connect(**DB_CONFIG)
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            insert_into_ayudas(file_path, connection)
    connection.close()
