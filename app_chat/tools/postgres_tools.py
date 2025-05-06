from smolagents import tool
from psycopg2.extensions import connection as PsycopgConnection
import psycopg2
import os
from dotenv import load_dotenv

@tool
def get_record_by_id(id: int) -> tuple:
    """
    Ejecuta una consulta SELECT con JOIN para obtener un registro de la tabla 'ayudas' y 'ayudas_ref' según su ID.

    Args:
        id (int): ID del registro que se desea consultar.

    Returns:
        tuple: Tupla con los valores de las columnas del registro encontrado, o None si no existe.
    """

    load_dotenv()
    DB_CONFIG = {
        "dbname": "ayudas",
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
        "host": "localhost",
        "port": 5432
    }

    connection = psycopg2.connect(
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],          
        password=DB_CONFIG["password"], 
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        options="-c client_encoding=UTF8"
    )
    
    cur = connection.cursor()
    cur.execute(
        "SELECT * FROM ayudas INNER JOIN ayudas_ref ON ayudas.id = ayudas_ref.id WHERE ayudas.id = %s;",
        (id,)
    )
    result = cur.fetchone()
    cur.close()
    connection.close()
    return result

@tool
def get_record_by_id_vectorial(id_vectorial: int) -> tuple:
    """
    Ejecuta una consulta SELECT con JOIN para obtener un registro de la tabla 'ayudas' y 'ayudas_ref' según su ID vectorial.

    Args:
        id_vectorial (int): ID vectorial de los registros que se desean consultar.

    Returns:
        tuple: Tupla con los valores de las columnas del registro encontrado, o None si no existe.
    """

    load_dotenv()
    DB_CONFIG = {
        "dbname": "ayudas",
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
        "host": "localhost",
        "port": 5432
    }

    connection = psycopg2.connect(
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],          
        password=DB_CONFIG["password"], 
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        options="-c client_encoding=UTF8"
    )
    
    cur = connection.cursor()
    cur.execute(
        "SELECT * FROM ayudas INNER JOIN ayudas_ref ON ayudas.id = ayudas_ref.id WHERE ayudas.id_vectorial = %s;",
        (id_vectorial,)
    )
    result = cur.fetchone()
    cur.close()
    connection.close()
    return result

@tool
def run_query(query: str, params: tuple = None) -> list:
    """
    Ejecuta una consulta SQL personalizada en la base de datos PostgreSQL.

    Solo se permiten consultas que comiencen con SELECT para proteger la integridad de los datos.

    Args:
        query (str): La consulta SQL que se desea ejecutar. Debe ser una sentencia SELECT.
        params (tuple, optional): Parámetros que se desean pasar de forma segura a la consulta SQL. Defaults to None.

    Returns:
        list: Una lista de tuplas que representa las filas devueltas por la consulta.
              Si la consulta no es un SELECT o si falla, se devuelve una lista vacía.
    """

    load_dotenv()
    DB_CONFIG = {
        "dbname": "ayudas",
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
        "host": "localhost",
        "port": 5432
    }

    connection = psycopg2.connect(
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],          
        password=DB_CONFIG["password"], 
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        options="-c client_encoding=UTF8"
    )

    first_word = query.strip().split()[0].lower()
    if first_word != "select":
        connection.close()
        return []

    cur = connection.cursor()

    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        results = cur.fetchall()
    finally:
        cur.close()
        connection.close()

    return results

@tool
def extract_from_id_if_present(id: int) -> list:
    """
    Ejecuta una consulta SELECT con JOIN para obtener un registro de la tabla 'ayudas' y 'ayudas_ref' según su ID.
    
    Devuelve los valores de las columnas del registro encontrado como una lista de tuplas. Si no se encuentra el registro, 
    devuelve una lista vacía.
    
    Args:
        id (int): ID del registro que se desea consultar.
    
    Returns:
        list: Lista con los valores de las columnas del registro encontrado, o una lista vacía si no existe.
    """

    load_dotenv()
    DB_CONFIG = {
        "dbname": "ayudas",
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
        "host": "localhost",
        "port": 5432
    }

    connection = psycopg2.connect(
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],          
        password=DB_CONFIG["password"], 
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        options="-c client_encoding=UTF8"
    )

    cur = connection.cursor()
    cur.execute("SELECT * FROM ayudas INNER JOIN ayudas_ref ON ayudas.id = ayudas_ref.id WHERE ayudas.id = %s;", (id,))
    result = cur.fetchone()
    cur.close()
    connection.close()

    if result is None:
        return []

    return [result]
