import os
import shutil

def clean_data(root: str):
    """
    Elimina todos los ficheros y el contenido dentro de las carpetas, pero deja vacías las carpetas excluidas.
    
    Args:
    - root (str): La carpeta raíz donde se eliminarán los ficheros y el contenido dentro de las carpetas, 
                  pero sin eliminar las carpetas excluidas.
    """
    excluded_folders = [
        "json", 
        "json/reference", 
        "json/refined", 
        "nav_urls", 
        "pdf", 
        "temp_vec_db"
    ]
    
    if not os.path.isdir(root):
        raise FileNotFoundError(f"La carpeta {root} no existe o no es una carpeta válida.")
    
    for item in os.listdir(root):
        item_path = os.path.join(root, item)

        if os.path.isfile(item_path):
            os.remove(item_path)
        
        elif os.path.isdir(item_path):
            if item not in [os.path.basename(excl) for excl in excluded_folders]:
                shutil.rmtree(item_path)
            else:
                for root_dir, dirs, files in os.walk(item_path, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root_dir, file))
                    for dir in dirs:
                        shutil.rmtree(os.path.join(root_dir, dir))

                print(f"Contenido de {item_path} ha sido eliminado, pero la carpeta se ha conservado.")
    
    print(f"Todos los ficheros y contenidos no excluidos en {root} han sido eliminados.")


