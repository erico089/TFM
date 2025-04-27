from smolagents import tool

@tool
def get_record_by_id(connection, id):
    """
    Ejecuta una consulta SELECT con JOIN para obtener un registro de la tabla 'ayudas' y 'ayudas_ref' según su ID.

    Args:
        connection (object): Conexión activa a la base de datos.
        id (int): ID del registro que se desea consultar.

    Returns:
        tuple: Tupla con los valores de las columnas del registro encontrado, o None si no existe.
    """

    cur = connection.cursor()
    cur.execute("select * from ayudas inner join ayudas_ref on ayudas.id = ayudas_ref.id where ayudas.id = %s;", (id,))
    result = cur.fetchone()
    cur.close()
    connection.close()
    return result

@tool
def get_record_by_id_vectorial(connection, id_vectorial):
    """
    Ejecuta una consulta SELECT con JOIN para obtener un registro de la tabla 'ayudas' y 'ayudas_ref' según su ID.

    Args:
        connection (object): Conexión activa a la base de datos.
        id_vectorial (int): ID vectorial de los registros que se desean consultar.

    Returns:
        tuple: Tupla con los valores de las columnas del registro encontrado, o None si no existe.
    """

    cur = connection.cursor()
    cur.execute("select * from ayudas inner join ayudas_ref on ayudas.id = ayudas_ref.id where ayudas.id_vectorial = %s;", (id_vectorial,))
    result = cur.fetchone()
    cur.close()
    connection.close()
    return result

@tool
def run_query(connection, query, params=None):
    """
    Ejecuta una consulta SQL personalizada utilizando los parámetros proporcionados,
    siempre y cuando sea una consulta SELECT.

    Args:
        connection (object): Conexión activa a la base de datos.
        query (str): La consulta SQL que se desea ejecutar.
        params (tuple, optional): Parámetros para pasar a la consulta SQL. Defaults to None.

    Returns:
        list: Lista de tuplas con los resultados de la consulta, o lista vacía si no es SELECT.
    """

    # Seguridad: sólo permitir consultas SELECT
    first_word = query.strip().split()[0].lower()
    if first_word != "select":
        # No ejecutar, solo devolver vacío
        cur = connection.cursor()
        cur.close()
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

