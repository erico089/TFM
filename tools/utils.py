import os

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
    Si el nombre contiene un '_', se toma solo la parte antes del guion bajo.

    Args:
        file_path (str): Ruta completa o nombre del archivo.

    Returns:
        str: ID vectorial base (antes del '_', si lo hay).
    """
    base_id = getIdFromFile(file_path)
    return base_id.split('_')[0] if '_' in base_id else base_id
