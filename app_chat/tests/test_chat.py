import pytest
import psycopg2
import os
from dotenv import load_dotenv
from app_chat.tests.mock_data import mock_ayudas, mock_ayudas_ref, test_cases
from app_chat.agents.orquestation_agent import OrchestrationAgent
from app_chat.agents.test_agent import TestAgent
import json
from app_chat.logging_setup import redirect_stdout_to_logger
from app_chat.tools.vectorial_tools import save_pdf_at_vec_db
import json
import os
import psycopg2
import unicodedata
import sys
from dotenv import load_dotenv

# --- Función para limpiar cada valor ---
def safe_encode(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')  # Decodifica bytes
    if isinstance(value, str):
        # Normaliza unicode y re-encodea
        value = unicodedata.normalize('NFC', value)
        return value.encode('utf-8', errors='replace').decode('utf-8')
    return value  # Si es otro tipo (int, float...), no tocar

# --- Función para validar todos los datos ---
def validate_data(dataset, dataset_name):
    print(f"\nValidando datos en {dataset_name}...")
    for idx, record in enumerate(dataset):
        for key, value in record.items():
            try:
                safe_encode(value)
            except Exception as e:
                print(f"[ERROR] Problema en registro {idx}, campo '{key}': {repr(value)} -> {e}")
                sys.exit(1)  # Salimos si detectamos un error grave
    print(f"Todos los datos en {dataset_name} son seguros para UTF-8 ✅")

# --- Fixture pytest corregido ---
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    load_dotenv()

    os.environ["ENVIRONMENT"] = "TEST"
    postgres_user = os.environ["POSTGRES_USER"]
    postgres_password = os.environ["POSTGRES_PASSWORD"]

    # --- VALIDAR datasets antes de insertar ---
    validate_data(mock_ayudas, "mock_ayudas")
    validate_data(mock_ayudas_ref, "mock_ayudas_ref")

    connection = psycopg2.connect(
        dbname="ayudas",
        user=postgres_user,
        password=postgres_password,
        host="localhost",
        port=5432,
        options="-c client_encoding=UTF8"
    )
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ayudas_mock (
        minimis TEXT,
        nombre TEXT,
        linea TEXT,
        fecha_inicio TEXT,
        fecha_fin TEXT,
        objetivo TEXT,
        beneficiarios TEXT,
        area TEXT,
        presupuesto_minimo TEXT,
        presupuesto_maximo TEXT,
        duracion_minima TEXT,
        duracion_maxima TEXT,
        intensidad_subvencion TEXT,
        intensidad_prestamo TEXT,
        tipo_financiacion TEXT,
        forma_plazo_cobro TEXT,
        region_aplicacion TEXT,
        tipo_consorcio TEXT,
        costes_elegibles TEXT,
        link_ficha_tecnica TEXT,
        link_orden_bases TEXT,
        link_convocatoria TEXT,
        id_vectorial TEXT,
        id TEXT PRIMARY KEY,
        organismo TEXT,
        año TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ayudas_mock_ref (
        id TEXT PRIMARY KEY,
        organismo_ref TEXT,
        fecha_inicio_ref TEXT,
        fecha_fin_ref TEXT,
        objetivo_ref TEXT,
        beneficiarios_ref TEXT,
        año_ref TEXT,
        presupuesto_minimo_ref TEXT,
        presupuesto_maximo_ref TEXT,
        duracion_minima_ref TEXT,
        duracion_maxima_ref TEXT,
        tipo_financiacion_ref TEXT,
        forma_plazo_cobro_ref TEXT,
        minimis_ref TEXT,
        region_aplicacion_ref TEXT,
        intensidad_subvencion_ref TEXT,
        intensidad_prestamo_ref TEXT,
        tipo_consorcio_ref TEXT,
        costes_elegibles_ref TEXT
    );
    """)

    connection.commit()

    # Limpieza previa
    cursor.execute("DELETE FROM ayudas_mock;")
    cursor.execute("DELETE FROM ayudas_mock_ref;")

    # Insertar datos
    for ayuda in mock_ayudas:
        columns = ayuda.keys()
        values = [
            safe_encode(json.dumps(ayuda[column])) if isinstance(ayuda[column], dict) else safe_encode(ayuda[column])
            for column in columns
        ]
        insert_statement = f"""
        INSERT INTO ayudas_mock ({", ".join(columns)})
        VALUES ({", ".join(["%s"] * len(values))})
        """
        cursor.execute(insert_statement, values)

    for ayuda_ref in mock_ayudas_ref:
        columns = ayuda_ref.keys()
        values = [
            safe_encode(json.dumps(ayuda_ref[column])) if isinstance(ayuda_ref[column], dict) else safe_encode(ayuda_ref[column])
            for column in columns
        ]
        insert_statement = f"""
        INSERT INTO ayudas_mock_ref ({", ".join(columns)})
        VALUES ({", ".join(["%s"] * len(values))})
        """
        cursor.execute(insert_statement, values)

    connection.commit()
    cursor.close()
    connection.close()

    pdf_path = os.path.join(os.getcwd(), "app_chat/tests/id1.pdf")
    vectorstore_path = os.path.join(os.getcwd(), "db_test")

    save_pdf_at_vec_db(
        pdf_paths=[pdf_path],
        vectorstore_path=vectorstore_path,
        chunk_size=500,
        chunk_overlap=100
    )

@pytest.mark.parametrize("query, similar_expected_response", test_cases)
def test_chat_responses(query, similar_expected_response):
    orquestation_agent = OrchestrationAgent()
    
    # with redirect_stdout_to_logger():
    test_agent = TestAgent()
    response = orquestation_agent.analyze_prompt(query)
    result = test_agent.compare(response, similar_expected_response)

    print("\n" + "="*50)
    print(f"Running Test for Query: \n'{query}'\n{'='*50}")
    
    print("Expected Response:")
    print(f"{similar_expected_response}\n")
    
    print("Actual Response:")
    print(f"{response}\n")
    
    print("Test Result:", "PASSED" if result else "FAILED")
    print("="*50)

    assert result
