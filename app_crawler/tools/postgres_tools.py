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

