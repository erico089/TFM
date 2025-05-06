import json
import os
from bs4 import BeautifulSoup, NavigableString, Tag
from selenium.webdriver.chrome.options import Options
from smolagents import tool
from selenium import webdriver
from pypdf import PdfReader
from tools.vectorial_db_tools import search_from_context_vec_db
from urllib.parse import urlparse
from typing import Dict

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
        driver.set_page_load_timeout(15)
        driver.get(url)
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


@tool
def get_organismo_context(vector_path: str) -> str:
    """
    Extrae información sobre el organismo que convoca la ayuda.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con el organismo convocante.
    """
    prompt = (
        "Organismo convocante, entidad organizadora, administración responsable, "
        "nombre de la institución o agencia pública que publica la convocatoria."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_beneficiarios_context(vector_path: str) -> str:
    """
    Identifica quiénes pueden solicitar la ayuda (beneficiarios).

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con los beneficiarios de la convocatoria.
    """
    prompt = (
        "Beneficiarios, entidades elegibles, tipo de solicitantes permitidos, destinatarios de la convocatoria."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_presupuesto_minimo_context(vector_path: str) -> str:
    """
    Obtiene el presupuesto mínimo exigido para acceder a la ayuda.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con el presupuesto mínimo exigido.
    """
    prompt = (
        "Presupuesto mínimo exigido, importe mínimo financiable, umbral mínimo de inversión para participar."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_presupuesto_maximo_context(vector_path: str) -> str:
    """
    Obtiene el presupuesto máximo permitido por la convocatoria.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con el presupuesto máximo permitido.
    """
    prompt = (
        "Presupuesto máximo permitido, importe tope del proyecto, cantidad máxima financiable, "
        "límite superior del presupuesto."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_fecha_inicio_context(vector_path: str) -> str:
    """
    Extrae la fecha de apertura del plazo de solicitud.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con la fecha de inicio del plazo de solicitud.
    """
    prompt = (
        "Fecha de apertura, inicio del plazo de solicitud, fecha inicial de la convocatoria."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_fecha_fin_context(vector_path: str) -> str:
    """
    Extrae la fecha de cierre del plazo de solicitud.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con la fecha de fin del plazo de solicitud.
    """
    prompt = (
        "Fecha de cierre, fin del plazo de solicitud, término del periodo de presentación, fecha límite."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_objetivos_convocatoria_context(vector_path: str) -> str:
    """
    Recupera los objetivos o fines que persigue la convocatoria.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con los objetivos de la convocatoria.
    """
    prompt = (
        "Objetivos de la convocatoria, propósito de la ayuda, finalidad del programa, "
        "metas de los proyectos financiados, actividades que se quieren fomentar."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_anio_context(vector_path: str) -> str:
    """
    Identifica el año de publicación o vigencia de la convocatoria.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con el año de publicación o vigencia.
    """
    prompt = (
        "Año de la convocatoria, ejercicio de publicación, año natural en el que se publica o abre la ayuda, "
        "vigencia temporal."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_duracion_minima_context(vector_path: str) -> str:
    """
    Obtiene la duración mínima que deben tener los proyectos subvencionados.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con la duración mínima permitida.
    """
    prompt = (
        "Duración mínima exigida, mínimo de meses o años del proyecto, plazo mínimo de ejecución."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_duracion_maxima_context(vector_path: str) -> str:
    """
    Obtiene la duración máxima permitida para los proyectos o ayudas.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con la duración máxima permitida.
    """
    prompt = (
        "Duración máxima permitida, máximo de meses o años del proyecto, plazo límite de ejecución."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_tipo_financiacion_context(vector_path: str) -> str:
    """
    Determina el tipo de financiación ofrecida (subvención, préstamo, etc.).

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con el tipo de financiación ofrecida.
    """
    prompt = (
        "Tipo de financiación, modalidad de ayuda, subvención, préstamo, ayuda reembolsable, esquema de apoyo financiero."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_forma_plazo_cobro_context(vector_path: str) -> str:
    """
    Recupera la forma de pago y el calendario de cobro de la ayuda.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con la forma y plazos de cobro de la ayuda.
    """
    prompt = (
        "Forma y plazo de cobro, calendario de pagos, modo de desembolso de la ayuda, "
        "cuándo se recibe el dinero, en qué tramos o momentos se entrega la financiación."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)


@tool
def get_minimis_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con si la ayuda se considera minimis según la normativa europea.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que indican si la ayuda está sujeta al régimen de minimis o si se menciona la normativa correspondiente.
    """
    prompt = (
        "Minimis, ayuda de minimis, reglamento de la Unión Europea sobre ayudas de pequeña cuantía, "
        "si la ayuda queda dentro de los límites de minimis, mención a que no requiere notificación a la Comisión Europea."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)


@tool
def get_region_aplicacion_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con la región o regiones donde aplica la ayuda o convocatoria desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que mencionan zonas geográficas, comunidades autónomas o territorios donde es aplicable la ayuda.
    """
    prompt = (
    "¿En qué regiones, comunidades autónomas o zonas geográficas aplica esta convocatoria? "
    "Busca cualquier referencia a territorio beneficiario, ubicación del proyecto o ámbito territorial de la ayuda."
    )

    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_intensidad_subvencion_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con la intensidad de la subvención (o tramo no reembolsable) desde una base de datos vectorial.

    Este campo representa el porcentaje de la ayuda que no debe devolverse y suele depender de factores como el tipo de empresa,
    la región, la modalidad del proyecto o el tipo de investigación. Esta información generalmente se presenta en forma de tabla
    con categorías como "pequeña empresa", "mediana empresa", "gran empresa", e incluye porcentajes y condiciones específicas.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que incluyen tablas, porcentajes u otras estructuras que describan la parte no reembolsable de la ayuda.
    """
    prompt = (
    "¿Cuál es el porcentaje de subvención o ayuda a fondo perdido que ofrece la convocatoria? "
    "Busca datos que indiquen intensidades máximas de ayuda según tipo de empresa, región o categoría de beneficiario, "
    "especialmente en forma de tablas o porcentajes."
    )

    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_intensidad_prestamo_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con la intensidad del préstamo (o tramo reembolsable) desde una base de datos vectorial.

    Este campo representa la parte de la ayuda que debe devolverse, normalmente bajo condiciones definidas según el tipo de empresa,
    la región, el tipo de proyecto o el marco normativo. La información suele aparecer en tablas que detallan porcentajes, plazos,
    y categorías de beneficiarios.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que incluyen información estructurada (como tablas o porcentajes) sobre las condiciones de devolución del préstamo.
    """
    prompt = (
    "¿Qué condiciones de préstamo o tramo reembolsable establece la convocatoria? "
    "Busca fragmentos que describan porcentaje a devolver, interés aplicado, plazos de amortización o condiciones de reembolso, "
    "especialmente si aparecen tablas o desgloses por tipo de beneficiario."
    )

    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_tipo_consorcio_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con el tipo de consorcio requerido o permitido por la convocatoria desde una base de datos vectorial.

    Este campo describe la estructura de colaboración esperada entre entidades (empresas, universidades, centros tecnológicos, etc.),
    incluyendo si es obligatorio o no formar un consorcio, el tipo de entidades que deben participar y las condiciones específicas
    de esta colaboración.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que mencionan requisitos de consorcio, colaboración entre entidades o características del grupo participante.
    """
    prompt = (
    "¿Es obligatorio formar un consorcio para participar en esta convocatoria? "
    "Busca información sobre tipos de consorcio permitidos, número mínimo de participantes o características de la colaboración entre entidades."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_costes_elegibles_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con los costes elegibles de una convocatoria desde una base de datos vectorial.

    Este campo especifica qué tipos de gasto están permitidos o cubiertos por la ayuda: sueldos, material, subcontrataciones,
    viajes, equipamiento, costes indirectos, etc. También puede incluir límites por categoría, condiciones específicas o
    exclusiones.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que mencionan categorías de gasto financiables o condiciones de elegibilidad del presupuesto.
    """
    prompt = (
    "¿Qué tipos de costes son elegibles o financiables en esta convocatoria? "
    "Busca descripciones de gastos subvencionables, como personal, equipamiento, subcontrataciones, viajes, materiales u otros conceptos aceptados."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)
