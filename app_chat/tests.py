import pytest
import psycopg2
import os
from dotenv import load_dotenv
from mock_data import mock_ayudas, mock_ayudas_ref, test_cases
from agents.orquestation_agent import OrchestrationAgent
from agents.test_agent import TestAgent
import json
from logging_setup import redirect_stdout_to_logger

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    load_dotenv()

    os.environ["ENVIRONMENT"] = "TEST"
    postgres_user = os.environ["POSTGRES_USER"]
    postgres_password = os.environ["POSTGRES_PASSWORD"]

    connection = psycopg2.connect(
        dbname="ayudas",
        user=postgres_user,
        password=postgres_password,
        host="localhost",
        port=5432,
        options="-c client_encoding=UTF8"
    )
    cursor = connection.cursor()

   # Crear tablas si no existen
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

    cursor.execute("DELETE FROM ayudas_mock;")
    cursor.execute("DELETE FROM ayudas_mock_ref;")

    for ayuda in mock_ayudas:
        columns = ayuda.keys()
        values = [json.dumps(ayuda[column]) if isinstance(ayuda[column], dict) else ayuda[column] for column in columns]
        insert_statement = f"""
        INSERT INTO ayudas_mock ({", ".join(columns)})
        VALUES ({", ".join(["%s"] * len(values))})
        """
        cursor.execute(insert_statement, values)

    for ayuda_ref in mock_ayudas_ref:
        columns = ayuda_ref.keys()
        values = [json.dumps(ayuda_ref[column]) if isinstance(ayuda_ref[column], dict) else ayuda_ref[column] for column in columns]
        insert_statement = f"""
        INSERT INTO ayudas_mock_ref ({", ".join(columns)})
        VALUES ({", ".join(["%s"] * len(values))})
        """
        cursor.execute(insert_statement, values)


    connection.commit()
    cursor.close()
    connection.close()
    
    from tools.vectorial_tools import save_pdf_at_vec_db

    pdf_path = os.path.join(os.getcwd(), "app_chat/id1.pdf")
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
    
    with redirect_stdout_to_logger():
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
