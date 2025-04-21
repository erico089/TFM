import psycopg2
from dotenv import load_dotenv
import os
from smolagents import tool

load_dotenv()
postgres_user = os.environ["POSTGRES_USER"]
postgres_password = os.environ["POSTGRES_PASSWORD"]

@tool
def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos PostgreSQL.

    Returns:
        psycopg2.extensions.connection: Objeto de conexión que permite interactuar con la base de datos.
    """
    return psycopg2.connect(
        dbname='ayudas',
        user=postgres_user,          
        password=postgres_password, 
        host='localhost',
        port=5432
    )

@tool
def get_record_by_id(record_id):
    """
    Ejecuta una consulta SELECT para obtener un registro de la tabla 'ayudas' según su ID.

    Args:
        record_id (int): ID del registro que se desea consultar.

    Returns:
        tuple: Tupla con los valores de las columnas del registro encontrado, o None si no existe.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ayudas WHERE id = %s;", (record_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result
