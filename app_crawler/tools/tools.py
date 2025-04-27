import json
import os
from bs4 import BeautifulSoup, NavigableString, Tag
from selenium.webdriver.chrome.options import Options
from smolagents import tool
from selenium import webdriver
from pypdf import PdfReader
from tools.vectorial_db_tools import search_from_context_vec_db
from urllib.parse import urlparse


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

from urllib.parse import urljoin

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


import os
import json
from typing import List, Dict

@tool
def save_json_tool(carpeta_base: str, datos: Dict, nombre_archivo: str) -> str:
    """
    Esta herramienta guarda un único diccionario como un archivo JSON en una carpeta especificada.

    Args:
        carpeta_base (str): Ruta de la carpeta donde se guardará el archivo JSON.
        datos (Dict): Diccionario que representa los datos a guardar.
        nombre_archivo (str): Nombre del archivo JSON (sin extensión .json).

    Returns:
        str: Mensaje indicando si el archivo fue guardado correctamente o si ocurrió un error.
    """
    try:
        if not isinstance(datos, dict):
            return "Error: 'datos' debe ser un diccionario."

        carpeta_base_abs = os.path.abspath(carpeta_base)
        os.makedirs(carpeta_base_abs, exist_ok=True)

        archivo_json = f"{nombre_archivo}.json"
        ruta_completa = os.path.join(carpeta_base_abs, archivo_json)

        with open(ruta_completa, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

        return f"{archivo_json} guardado correctamente en {carpeta_base_abs}."
    except Exception as e:
        return f"Error al guardar JSON: {str(e)}"

@tool
def get_organismo_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con el organismo convocante desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que contienen información sobre el organismo convocante.
    """

    prompt = (
        "Organismo convocante, entidad organizadora, institución que lanza la convocatoria, "
        "administración responsable, ministerio, agencia pública, autoridad emisora de ayudas, "
        "nombre del organismo público, nombre oficial del ente que convoca"
    )

    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_nombre_convocatoria_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con el nombre de la convocatoria desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que contienen información sobre el nombre de la convocatoria.
    """
    prompt = (
        "Nombre de la convocatoria, título oficial de la convocatoria, denominación de la ayuda, "
        "nombre del programa, título de la línea de ayudas, denominación completa del proyecto."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_beneficiarios_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con "Beneficiarios" desde una base de datos vectorial.
    
    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que contienen información sobre "Beneficiarios".
    """
    prompt = "Empresas, entidades que pueden solicitar la ayuda, sujetos elegibles, destinatarios de la ayuda, tipo de solicitantes permitidos."
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_presupuesto_minimo_context(vector_path: str) -> str:
    """
    Recupera fragmentos sobre el presupuesto mínimo requerido para acceder a la convocatoria desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que contienen información sobre el presupuesto mínimo exigido por la convocatoria.
    """
    prompt = (
        "Presupuesto mínimo exigido, cantidad mínima financiable, umbral mínimo de inversión para participar, "
        "importe mínimo del proyecto."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)


@tool
def get_presupuesto_maximo_context(vector_path: str) -> str:
    """
    Recupera fragmentos sobre el presupuesto máximo permitido por la convocatoria desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que contienen información sobre el presupuesto máximo permitido por la convocatoria.
    """
    prompt = (
        "Presupuesto máximo permitido, importe tope del proyecto, cantidad máxima financiable, "
        "límite superior del presupuesto."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)


@tool
def get_fecha_inicio_context(vector_path: str) -> str:
    """
    Recupera fragmentos con la fecha de inicio de la convocatoria desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que contienen la fecha de apertura de la convocatoria.
    """
    prompt = (
        "Fecha de apertura, inicio del plazo de solicitud, comienzo del periodo de presentación, "
        "fecha inicial de la convocatoria."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)


@tool
def get_fecha_fin_context(vector_path: str) -> str:
    """
    Recupera fragmentos con la fecha de fin de la convocatoria desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que contienen la fecha de cierre de la convocatoria.
    """
    prompt = (
        "Fecha de cierre, fin del plazo de solicitud, término del periodo de presentación, "
        "fecha final de la convocatoria."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_objetivos_convocatoria_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con los objetivos de la convocatoria desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que contienen información sobre los objetivos, fines o propósitos de la convocatoria.
    """
    prompt = (
        "Objetivos de la convocatoria, propósito de la ayuda, finalidad del programa, "
        "qué se busca lograr, metas de los proyectos financiados, qué tipo de actividades se quiere fomentar."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)


@tool
def get_anio_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con el año de publicación o vigencia de la convocatoria desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que contienen información sobre el año en que se publica o está abierta la convocatoria.
    """
    prompt = (
        "Año de la convocatoria, ejercicio de publicación, año natural en el que se publica o abre la ayuda, "
        "vigencia temporal de la convocatoria, fechas relevantes."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)


@tool
def get_duracion_minima_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con la duración mínima permitida de los proyectos o ayudas desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que especifican el tiempo mínimo que deben durar los proyectos financiados.
    """
    prompt = (
        "Duración mínima, mínimo de meses o años del proyecto, duración mínima del proyecto, plazo mínimo del desarrollo, "
        "tiempo mínimo de ejecución exigido."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)


@tool
def get_duracion_maxima_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con la duración máxima permitida de los proyectos o ayudas desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que indican el tiempo máximo permitido para la ejecución de los proyectos.
    """
    prompt = (
        "Duración máxima, máximo de meses o años del proyecto, duración límite del proyecto, "
        "plazo tope de ejecución, restricciones de tiempo."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)


@tool
def get_tipo_financiacion_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con el tipo de financiación o ayuda ofrecida por la convocatoria desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que describen si se trata de subvención, préstamo, ayuda reembolsable, etc.
    """
    prompt = (
        "Tipo de financiación, tipo de ayuda, modalidad de apoyo económico, subvención, préstamo, ayuda reembolsable, "
        "esquema de financiación propuesto."
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)

@tool
def get_forma_plazo_cobro_context(vector_path: str) -> str:
    """
    Recupera fragmentos relacionados con la forma y los plazos en los que se cobra la ayuda desde una base de datos vectorial.

    Args:
        vector_path (str): Ruta a la base de datos vectorial.

    Returns:
        str: Fragmentos relevantes que explican cómo y cuándo se realiza el pago de la ayuda o financiación.
    """
    prompt = (
        "Forma y plazo de cobro, calendario de pagos, modo de desembolso de la ayuda, "
        "momentos en que se recibe la financiación, en qué tramos se entrega el dinero, "
        "cuándo se cobra, distribución temporal del pago."
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
        "Región de aplicación, ámbito territorial de la convocatoria, comunidad autónoma donde aplica la ayuda, "
        "zona geográfica beneficiaria, localización del proyecto, regiones cubiertas por la convocatoria."
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
        "intensidad de la subvención, tramo no reembolsable, tabla de porcentajes, ayuda a fondo perdido, "
        "porcentaje subvencionable, variación por tipo de empresa (pequeña, mediana, grande), "
        "porcentaje no reembolsable según región, condiciones específicas, categoría empresarial, "
        "coste elegible subvencionado, tabla de ayudas, desglose por tipo de beneficiario o actividad, "
        "máximo porcentaje de subvención, intensidad según zona geográfica, condiciones de cofinanciación"
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
        "intensidad del préstamo, tramo reembolsable, porcentaje a devolver, condiciones del préstamo, "
        "ayuda parcialmente reembolsable, tabla de condiciones financieras, interés aplicable, tipo de interés, "
        "duración del préstamo, condiciones de reembolso según tamaño de empresa o región, desglose por categoría, "
        "plazo de amortización, condiciones del tramo reembolsable, préstamo bonificado, devolución del apoyo financiero"
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
        "tipo de consorcio, consorcio obligatorio, participación en agrupación, entidades colaboradoras, "
        "colaboración entre empresas y centros de investigación, consorcio internacional, mínimo de participantes, "
        "proyecto colaborativo, cooperación interregional, requisitos de colaboración, estructura del consorcio, "
        "condiciones de agrupación de entidades, características del consorcio, entidades asociadas"
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
        "costes elegibles, gastos subvencionables, tipos de gasto cubiertos, gastos admitidos, "
        "costes financiables, gastos de personal, subcontratación, costes directos, costes indirectos, "
        "viajes, materiales, equipamiento, partidas aceptadas, presupuesto elegible, conceptos financiables, "
        "limitaciones por categoría de gasto"
    )
    return search_from_context_vec_db(prompt, vectorstore_path=vector_path)
