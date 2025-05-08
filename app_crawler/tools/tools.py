import json
import os
from bs4 import BeautifulSoup, NavigableString, Tag
from selenium.webdriver.chrome.options import Options
from smolagents import tool
from selenium import webdriver
from pypdf import PdfReader
from tools.vectorial_db_tools import search_from_context_vec_db
from urllib.parse import urlparse, urljoin
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
    prompt = "¿Cual es el nombre del organismo o entidad que propone la convocatoria?"
 
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=4)

@tool
def get_beneficiarios_context(vector_path: str) -> str:
    """
    Identifica quiénes pueden solicitar la ayuda (beneficiarios).

    Esta versión mejorada realiza búsquedas con dos formulaciones distintas para obtener
    resultados más completos y variados sobre los beneficiarios.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con los beneficiarios de la convocatoria.
    """
    prompt = "¿Quiénes pueden solicitar la ayuda? ¿Cuáles son los beneficiarios de la convocatoria?"
    
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=4)


@tool
def get_presupuesto_minimo_context(vector_path: str) -> str:
    """
    Obtiene el presupuesto mínimo exigido para acceder a la ayuda.

    Esta versión mejorada realiza búsquedas con tres formulaciones distintas para obtener
    resultados más completos y variados sobre el presupuesto mínimo.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con el presupuesto mínimo exigido.
    """
    prompt = "¿Qué importe mínimo se requiere para participar en la convocatoria?"
    
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=4)



@tool
def get_presupuesto_maximo_context(vector_path: str) -> str:
    """
    Obtiene el presupuesto máximo permitido por la convocatoria.

    Esta versión mejorada realiza búsquedas con tres formulaciones distintas para obtener
    resultados más completos y variados sobre el presupuesto máximo.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con el presupuesto máximo permitido.
    """
    prompt = "¿Qué importe máximo se puede financiar en esta ayuda?"
    
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=4)


@tool
def get_fecha_inicio_context(vector_path: str) -> str:
    """
    Extrae la fecha de apertura del plazo de solicitud.

    Esta versión mejorada realiza búsquedas con tres formulaciones distintas para obtener
    resultados más completos y variados sobre la fecha de inicio del plazo de solicitud.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con la fecha de inicio del plazo de solicitud.
    """
    prompt = "¿Cuándo comienza el plazo de solicitud de la convocatoria?"
    
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=4)


@tool
def get_fecha_fin_context(vector_path: str) -> str:
    """
    Extrae la fecha de cierre del plazo de solicitud.

    Esta versión mejorada realiza búsquedas con tres formulaciones distintas para obtener
    resultados más completos y variados sobre la fecha de cierre del plazo de solicitud.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con la fecha de fin del plazo de solicitud.
    """
    prompt = "¿Cuál es la fecha límite para la presentación de solicitudes?"
    
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=4)


@tool
def get_objetivos_convocatoria_context(vector_path: str) -> str:
    """
    Recupera los objetivos o fines que persigue la convocatoria.

    Esta versión mejorada realiza búsquedas con tres formulaciones distintas para obtener
    resultados más completos y variados sobre los objetivos de la convocatoria.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con los objetivos de la convocatoria.
    """
    prompt = "¿Cuáles son los objetivos y finalidades de la convocatoria?"
    
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=4)


@tool
def get_anio_context(vector_path: str) -> str:
    """
    Identifica el año de publicación o vigencia de la convocatoria.

    Esta versión mejorada realiza búsquedas con tres formulaciones distintas para obtener
    resultados más completos y variados sobre el año de publicación o vigencia de la convocatoria.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con el año de publicación o vigencia.
    """
    prompt = "¿En qué año se publica, abre o cual es la vigencia esta convocatoria?"
    
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=4)


@tool
def get_duracion_minima_context(vector_path: str) -> str:
    """
    Obtiene la duración mínima que deben tener los proyectos subvencionados.

    Esta versión mejorada realiza búsquedas con tres formulaciones distintas para obtener
    resultados más completos y variados sobre la duración mínima exigida para los proyectos.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con la duración mínima permitida.
    """
    prompt = "¿Cuál es la duración mínima exigida para los proyectos?"
    
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=4)


@tool
def get_duracion_maxima_context(vector_path: str) -> str:
    """
    Obtiene la duración máxima permitida para los proyectos o ayudas.

    Esta versión mejorada realiza búsquedas con tres formulaciones distintas para obtener
    resultados más completos y variados sobre la duración máxima permitida para los proyectos.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con la duración máxima permitida.
    """
    prompt = "¿Cuál es la duración máxima permitida para los proyectos?"
    
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=4)


@tool
def get_tipo_financiacion_context(vector_path: str) -> str:
    """
    Determina el tipo de financiación ofrecida (subvención, préstamo, etc.).

    Esta versión mejorada realiza búsquedas con tres formulaciones distintas para obtener
    resultados más completos y variados sobre el tipo de financiación ofrecida en la convocatoria.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con el tipo de financiación ofrecida.
    """
    prompt = "¿Qué tipo de financiación ofrece esta convocatoria? ¿Es una subvención, un préstamo u otra modalidad?"
    
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=4)


@tool
def get_forma_plazo_cobro_context(vector_path: str) -> str:
    """
    Recupera la forma de pago y el calendario de cobro de la ayuda.

    Esta versión mejorada realiza búsquedas con tres formulaciones distintas para obtener
    resultados más completos y variados sobre la forma de pago y los plazos de cobro.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes relacionados con la forma y plazos de cobro de la ayuda.
    """
    prompt = "¿Cómo y cuándo se realiza el cobro o desembolso de la ayuda? ¿Cuál es el calendario de pagos?"
    
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=4)


@tool
def get_minimis_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con si la ayuda se considera minimis según la normativa europea.

    Esta versión mejorada realiza búsquedas con tres formulaciones distintas para obtener
    resultados más completos y variados sobre la normativa minimis.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que indican si la ayuda está sujeta al régimen de minimis o si se menciona la normativa correspondiente.
    """
    prompt = "¿La ayuda está sujeta al régimen de minimis según la normativa de la UE? ¿Se menciona que no requiere notificación a la Comisión Europea?"
    
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=4)

@tool
def get_tipo_consorcio_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con el tipo de consorcio requerido o permitido en la convocatoria.

    Este campo recoge información sobre si se exige o favorece la presentación conjunta de proyectos en consorcio,
    qué características debe tener (número de socios, tipo de entidades participantes, condiciones de colaboración, etc.)
    y requisitos específicos sobre su composición.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que describen los requisitos o características del consorcio en la ayuda.
    """
    prompt = "¿Qué requisitos existen sobre la composición del consorcio en esta convocatoria? Número mínimo de socios, tipos de entidades, condiciones de colaboración, etc.¿Qué características deben cumplir los consorcios?"
    
    results = []
    
    results.extend(search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=1, find_table=True))
    results.extend(search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=5))
    
    return results


@tool
def get_region_aplicacion_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con la región o regiones donde aplica la ayuda o convocatoria desde una base de datos vectorial.

    Esta versión mejorada realiza búsquedas con tres formulaciones distintas para obtener
    resultados más completos y variados sobre las zonas geográficas donde aplica la ayuda.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que mencionan zonas geográficas, comunidades autónomas o territorios donde es aplicable la ayuda.
    """
    prompt =  "¿En qué regiones, comunidades autónomas o zonas geográficas aplica esta convocatoria? ¿Dónde es válida la ayuda?"
    
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=4)


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

    prompt = "¿Cuál es el porcentaje de subvención o ayuda a fondo perdido que ofrece la convocatoria? ¿Cuáles son las intensidades de ayuda según tipo de empresa, la región y el tipo de ayuda?"
    
    results = []
    
    results.extend(search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=1, find_table=True))
    results.extend(search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=6))
    
    return results

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
    prompt = "¿Cómo varían las condiciones de devolución del préstamo según el tipo de empresa, región tipo de ayuda?"
        
    results = []
    
    results.extend(search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=1, find_table=True))
    results.extend(search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=6))
    
    return results


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
    prompt = "¿Cuáles son los límites o exclusiones en los tipos de gastos financiables, como sueldos, equipamiento o subcontrataciones?"
    
    results = []
    
    results.extend(search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=1, find_table=True))
    results.extend(search_from_context_vec_db(prompt, vectorstore_path=vector_path, k=6))
    
    return results

