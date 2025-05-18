import json
import os
from bs4 import BeautifulSoup, NavigableString, Tag
from selenium.webdriver.chrome.options import Options
from smolagents import tool
from selenium import webdriver
from pypdf import PdfReader
from app_crawler.tools.vectorial_db_tools import search_from_context_vec_db
from urllib.parse import urlparse, urljoin
from typing import Dict
import time

@tool
def leer_json(file_path: str) -> dict:
    """
    Esta herramienta permite leer y cargar el contenido de un archivo JSON desde una ruta local.

    Es útil para proporcionar al agente datos estructurados previamente extraídos o generados,
    de forma que pueda analizarlos, validarlos o compararlos con otras fuentes de información.

    Args:
        file_path (str): La ruta local al archivo JSON que se desea leer.

    Returns:
        dict: El contenido del JSON parseado como un diccionario de Python.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

@tool
def leer_pdf(file_path: str) -> str:
    """
    Esta herramienta utiliza PyPDF para extraer texto de un archivo PDF.

    Lee las primeras páginas de un archivo PDF y devuelve el contenido textual concatenado,
    permitiendo que el agente lo procese, analice o resuma según se requiera.

    Args:
        file_path (str): La ruta local al archivo PDF que se va a leer.

    Returns:
        str: El texto extraído del PDF, sin formato, para su posterior análisis.
    """
    contenido = ""
    reader = PdfReader(file_path)
    for page in reader.pages[:3]:
        contenido += page.extract_text()
    return contenido

def simplificar_html(html: str, base_url: str) -> str:
    """
    Función para simplificar el HTML, extrayendo solo el contenido relevante,
    y construyendo URLs absolutas a partir de URLs relativas.

    Args:
        html (str): El HTML de la página que se va a procesar.
        base_url (str): La URL base para resolver URLs relativas.

    Returns:
        str: El HTML simplificado con URLs completas.
    """
    soup = BeautifulSoup(html, 'html.parser')

    for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'form', 'aside']):
        tag.decompose()

    def procesar_nodo(nodo):
        if isinstance(nodo, NavigableString):
            return nodo.strip()
        elif isinstance(nodo, Tag):
            if nodo.name == 'a':
                texto = nodo.get_text(strip=True)
                href = nodo.get('href', '')

                if href.startswith('//'):
                    href = 'https:' + href  
                elif href.startswith('/'):
                    href = urljoin(base_url, href) 

                return f"{texto} ({href})" if href else texto
            else:
                contenido = [procesar_nodo(hijo) for hijo in nodo.children]
                return ' '.join(filter(None, contenido))
        return ''

    cuerpo = soup.body or soup
    texto_procesado = procesar_nodo(cuerpo)

    return texto_procesado

@tool
def fetch_html_tool(url: str) -> str:
    """
    Esta herramienta usa Selenium (headless) para obtener el HTML renderizado de una página protegida.

    Args:
        url (str): La URL de la página web que se va a obtener.

    Returns:
        str: Una version simplificada del HTML con la informacion relevante de la pagina web.
    """
    try:
        options = Options()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(20)
        driver.get(url)

        time.sleep(5)
        html = driver.page_source
        driver.quit()

        parsed = urlparse(html)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        return simplificar_html(html,base_url)
    except Exception as e:
        return f"Error al obtener HTML con Selenium: {str(e)}"

@tool
def save_json_field_tool(path_json: str, field_name: str, value: str) -> str:
    """
    Guarda o actualiza el valor de un campo específico en un archivo JSON. 
    Si el archivo no existe, lo crea.

    Args:
        path_json (str): Ruta al archivo JSON.
        field_name (str): Nombre del campo a guardar o actualizar.
        value (str): Valor que se asignará al campo.

    Returns:
        str: Mensaje de confirmación o de error.
    """
    try:
        if not os.path.exists(path_json):
            data = {}
        else:
            with open(path_json, "r", encoding="utf-8") as f:
                data = json.load(f)

        data[field_name] = value

        with open(path_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return f"Campo '{field_name}' guardado correctamente en {path_json}."
    except Exception as e:
        return f"Error al guardar el campo '{field_name}' en {path_json}: {str(e)}"


@tool
def add_field_ref_json_tool(path_json: str, field_name_ref: str, id_doc: str, fragments: list) -> str:
    """
    Añade referencias a un campo de referencias en un archivo JSON. 
    Si el archivo no existe, lo crea.

    Args:
        path_json (str): Ruta al archivo JSON.
        field_name_ref (str): Nombre del campo de referencias a actualizar o crear.
        id_doc (str): ID del documento de origen de los fragmentos.
        fragments (list): Lista de fragmentos a añadir.

    Returns:
        str: Mensaje de confirmación o de error.
    """
    try:
        if not os.path.exists(path_json):
            data = {}
        else:
            with open(path_json, "r", encoding="utf-8") as f:
                data = json.load(f)

        if field_name_ref not in data:
            data[field_name_ref] = []

        for fragment in fragments:
            data[field_name_ref].append({
                "id": id_doc,
                "fragment": fragment
            })

        with open(path_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return f"Referencias añadidas correctamente al campo '{field_name_ref}' en {path_json}."
    except Exception as e:
        return f"Error al añadir referencias en el campo '{field_name_ref}' en {path_json}: {str(e)}"

@tool
def save_json_tool(carpeta_base: str, datos: Dict, nombre_archivo: str) -> str:
    """
    Guarda un diccionario como archivo JSON en una carpeta especificada.

    Si el nombre del archivo no termina en '.json', se añade automáticamente.

    Args:
        carpeta_base (str): Ruta de la carpeta donde se guardará el archivo JSON.
        datos (Dict): Diccionario que representa los datos a guardar.
        nombre_archivo (str): Nombre del archivo JSON (con o sin extensión .json).

    Returns:
        str: Mensaje indicando si el archivo fue guardado correctamente o si ocurrió un error.
    """
    try:
        if not isinstance(datos, dict):
            return "Error: 'datos' debe ser un diccionario."

        carpeta_base_abs = os.path.abspath(carpeta_base)
        os.makedirs(carpeta_base_abs, exist_ok=True)

        if not nombre_archivo.lower().endswith('.json'):
            nombre_archivo += '.json'

        ruta_completa = os.path.join(carpeta_base_abs, nombre_archivo)

        with open(ruta_completa, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

        return f"{nombre_archivo} guardado correctamente en {carpeta_base_abs}."
    except Exception as e:
        return f"Error al guardar JSON: {str(e)}"


def get_organismo_context(vector_path: str, idx: int) -> str:
    """
    Extrae información sobre el organismo que convoca la ayuda.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con el organismo convocante.
    """
    prompts = ["¿Cual es el nombre del organismo o entidad que propone la convocatoria?",
               "¿Quién es el responsable de emitir esta convocatoria pública?"]
 
    return search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=4)

def get_beneficiarios_context(vector_path: str, idx: int) -> str:
    """
    Identifica quiénes pueden solicitar la ayuda (beneficiarios).
    
    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes relacionados con los beneficiarios de la convocatoria.
    """
    prompts = [
        "¿Quiénes pueden solicitar la ayuda? ¿Cuáles son los beneficiarios de la convocatoria?",
        "¿A qué personas, empresas o entidades está dirigida esta convocatoria?"
    ]
    return search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=4)

def get_presupuesto_minimo_context(vector_path: str, idx: int) -> str:
    """
    Obtiene el presupuesto mínimo exigido para acceder a la ayuda.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes relacionados con el presupuesto mínimo exigido.
    """
    prompts = [
        "¿Qué importe mínimo se requiere para participar en la convocatoria?",
        "¿Cuál es la cantidad mínima de fondos que se pueden solicitar en esta ayuda?"
    ]
    return search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=4)

def get_presupuesto_maximo_context(vector_path: str, idx: int) -> str:
    """
    Obtiene el presupuesto máximo permitido por la convocatoria.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes relacionados con el presupuesto máximo permitido.
    """
    prompts = [
        "¿Qué importe máximo se puede financiar en esta ayuda?",
        "¿Cuál es la cantidad máxima de fondos que se pueden otorgar en esta convocatoria?"
    ]
    return search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=4)


def get_fecha_inicio_context(vector_path: str, idx: int) -> str:
    """
    Extrae la fecha de apertura del plazo de solicitud.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes relacionados con la fecha de inicio del plazo de solicitud.
    """
    prompts = [
        "¿Cuándo comienza el plazo de solicitud de la convocatoria?",
        "¿A partir de qué fecha se pueden presentar solicitudes para esta convocatoria?"
    ]
    return search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=4)

def get_fecha_fin_context(vector_path: str, idx: int) -> str:
    """
    Extrae la fecha de cierre del plazo de solicitud.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes relacionados con la fecha de fin del plazo de solicitud.
    """
    prompts = [
        "¿Cuál es la fecha límite para la presentación de solicitudes?",
        "¿Hasta qué día se pueden presentar solicitudes para esta convocatoria?"
    ]
    return search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=4)

def get_objetivos_convocatoria_context(vector_path: str, idx: int) -> str:
    """
    Recupera los objetivos o fines que persigue la convocatoria.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes relacionados con los objetivos de la convocatoria.
    """
    prompts = [
        "¿Cuáles son los objetivos y finalidades de la convocatoria?",
        "¿Qué pretende conseguir esta convocatoria? ¿Cuáles son sus principales metas?"
    ]
    return search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=4)



def get_anio_context(vector_path: str, idx: int) -> str:
    """
    Identifica el año de publicación o vigencia de la convocatoria.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes relacionados con el año de publicación o vigencia.
    """
    prompts = [
        "¿En qué año se publica, abre o cuál es la vigencia de esta convocatoria?",
        "¿A qué año corresponde esta convocatoria?"
    ]
    return search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=4)

def get_duracion_minima_context(vector_path: str, idx: int) -> str:
    """
    Obtiene la duración mínima que deben tener los proyectos subvencionados.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes relacionados con la duración mínima permitida.
    """
    prompts = [
        "¿Cuál es la duración mínima exigida para los proyectos?",
        "¿Qué duración mínima deben cumplir los proyectos financiados?"
    ]
    return search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=4)

def get_duracion_maxima_context(vector_path: str, idx: int) -> str:
    """
    Obtiene la duración máxima permitida para los proyectos o ayudas.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes relacionados con la duración máxima permitida.
    """
    prompts = [
        "¿Cuál es la duración máxima permitida para los proyectos?",
        "¿Qué duración máxima pueden tener los proyectos subvencionados?"
    ]
    return search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=4)


def get_tipo_financiacion_context(vector_path: str, idx: int) -> str:
    """
    Determina el tipo de financiación ofrecida (subvención, préstamo, etc.).

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes relacionados con el tipo de financiación ofrecida.
    """
    prompts = [
        "¿Qué tipo de financiación ofrece esta convocatoria? ¿Es una subvención, un préstamo u otra modalidad?",
        "¿Se trata de una ayuda económica directa, un crédito, o un incentivo fiscal?",
        "¿Qué modalidad de financiación está prevista en esta convocatoria?",
        "¿Se especifica si la ayuda es reembolsable o no reembolsable?"
    ]
    return search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=4)


def get_forma_plazo_cobro_context(vector_path: str, idx: int) -> str:
    """
    Recupera la forma de pago y el calendario de cobro de la ayuda.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes relacionados con la forma y plazos de cobro de la ayuda.
    """
    prompts = [
        "¿Cómo y cuándo se realiza el cobro o desembolso de la ayuda? ¿Cuál es el calendario de pagos?",
        "¿En qué plazos y de qué forma se recibe el dinero de la convocatoria?",
        "¿Cuál es el procedimiento de pago establecido para las ayudas?",
        "¿Se anticipa el pago total, se realiza en varios tramos o depende de hitos?"
    ]
    return search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=4)


def get_minimis_context(vector_path: str, idx: int) -> str:
    """
    Recupera fragmentos relacionados con si la ayuda se considera minimis según la normativa europea.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes sobre si la ayuda está sujeta al régimen de minimis.
    """
    prompts = [
        "¿La ayuda está sujeta al régimen de minimis según la normativa de la UE?",
        "¿Se menciona que la ayuda se acoge a la normativa europea de minimis?",
        "¿La ayuda requiere notificación previa a la Comisión Europea o está exenta?",
        "¿Se especifica el cumplimiento de los límites establecidos para ayudas de minimis?"
    ]
    return search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=4)


def get_tipo_consorcio_context(vector_path: str, idx: int) -> str:
    """
    Recupera fragmentos relacionados con el tipo de consorcio requerido o permitido en la convocatoria.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes que describen los requisitos o características del consorcio en la ayuda.
    """
    prompts = [
        "¿Qué requisitos existen sobre la composición del consorcio en esta convocatoria? Número mínimo de socios, tipos de entidades, condiciones de colaboración, etc.",
        "¿Se exige participación en consorcio? ¿Qué características deben tener los consorcios?",
        "¿Cuántos participantes debe tener el consorcio y qué tipo de entidades deben formar parte?",
        "¿Qué condiciones específicas deben cumplir los consorcios en esta convocatoria?"
    ]

    results = []
    
    results.extend(search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=1, find_table=True))
    results.extend(search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=5))
    
    return results


def get_region_aplicacion_context(vector_path: str, idx: int) -> str:
    """
    Recupera fragmentos relacionados con la región o regiones donde aplica la ayuda o convocatoria.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes que mencionan zonas geográficas donde es aplicable la ayuda.
    """
    prompts = [
        "¿En qué regiones, comunidades autónomas o zonas geográficas aplica esta convocatoria? ¿Dónde es válida la ayuda?",
        "¿A qué territorios se dirige esta convocatoria?",
        "¿La ayuda está limitada a una región específica o es de ámbito nacional?",
        "¿Qué áreas geográficas cubre la ayuda ofrecida en esta convocatoria?"
    ]
    return search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=4)


def get_intensidad_subvencion_context(vector_path: str, idx: int) -> str:
    """
    Recupera fragmentos relacionados con la intensidad de la subvención (o tramo no reembolsable) desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes que incluyen tablas, porcentajes u otras estructuras que describen la parte no reembolsable de la ayuda.
    """
    prompts = [
        "¿Cuál es el porcentaje máximo de ayuda a fondo perdido que ofrece la convocatoria? Detallar diferencias según tipo de empresa, región o categoría del proyecto.",
        "¿Qué intensidades de ayuda aplican dependiendo de si se trata de investigación industrial, desarrollo experimental o innovación?",
        "¿Cómo varía el porcentaje de subvención según el tamaño de la empresa (pequeña, mediana, grande) y la localización geográfica?",
        "¿Qué condiciones específicas afectan la intensidad de la subvención? ¿Hay incrementos por colaboración en consorcio o participación de pymes?"
    ]
    
    results = []
    results.extend(search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=1, find_table=True))
    results.extend(search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=6))
    
    return results


def get_intensidad_prestamo_context(vector_path: str, idx: int) -> str:
    """
    Recupera fragmentos relacionados con la intensidad del préstamo (o tramo reembolsable) desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.
        idx (int): Índice del intento para variar el prompt.

    Returns:
        str: Fragmentos relevantes que incluyen información estructurada sobre las condiciones de devolución del préstamo.
    """
    prompts = [
        "¿Qué porcentaje del proyecto es financiado mediante préstamo reembolsable? Indicar variaciones por tipo de actividad y tamaño de empresa.",
        "¿Cómo se estructura el tramo reembolsable frente al tramo no reembolsable en la convocatoria?",
        "¿Qué condiciones específicas (plazos, tipos de interés, carencia) regulan el tramo de préstamo en esta ayuda?",
        "¿Existen diferencias en el préstamo otorgado según localización territorial, sector o tamaño de la empresa?"
    ]
    
    results = []
    results.extend(search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=1, find_table=True))
    results.extend(search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=6))
    
    return results


def get_costes_elegibles_context(vector_path: str, idx: int) -> str:
    """
    Recupera información sobre los costes elegibles dentro de una convocatoria, es decir, aquellos gastos que son financiables.

    Este campo incluye detalles sobre los tipos de gasto que pueden ser cubiertos por la subvención, tales como sueldos, equipamiento,
    costes indirectos, viajes, y subcontrataciones. Las convocatorias a menudo definen categorías específicas de gasto financiables
    y pueden imponer límites o restricciones a ciertos tipos de costos o beneficiarios.

    Args:
        vector_path (str): Ruta al archivo de la base de datos vectorial.
        idx (int): Índice para variar las consultas sobre costes elegibles.

    Returns:
        str: Fragmentos relevantes sobre los tipos de gastos financiables y las condiciones que los acompañan.
    """
    prompts = [
        "¿Qué tipos de gasto están considerados elegibles para esta convocatoria? ¿Hay limitaciones en los tipos de gasto financiables?",
        "¿Cuáles son los gastos que pueden ser financiados por la ayuda? ¿Incluye costes indirectos, equipamiento o subcontrataciones?",
        "¿Qué restricciones existen en relación con los gastos financiables? ¿Cuáles son los límites en cada categoría de gasto?",
        "¿Cuáles son las condiciones de elegibilidad de los costes para la ayuda? ¿Se aplican exclusiones para ciertos tipos de gasto?"
    ]
    
    results = []
    
    results.extend(search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=1, find_table=True))
    results.extend(search_from_context_vec_db(prompts[idx], vectorstore_path=vector_path, k=6))
    
    return results

