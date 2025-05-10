from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import os
import pdfplumber
from langchain_community.docstore.document import Document
from openai import AzureOpenAI
from dotenv import load_dotenv
import time
from tqdm import tqdm  
import uuid

load_dotenv()
api_key = os.environ["AZURE_EMBEDDING_KEY"]
deployment_name = os.environ["AZURE_EMBEDDING_DEPLOYMENT_NAME"]
api_base = os.environ["AZURE_EMBEDDING_ENDPOINT"] 
api_version = os.environ["AZURE_EMBEDDING_API_VERSION"] 

def extract_text_and_tables(pdf_path):
    """
    Extrae texto y tablas de un PDF.
    Retorna una lista de diccionarios {content: str, tipo: 'texto' o 'tabla'}.
    """
    all_chunks = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_chunks.append({"content": text, "tipo": "texto"})

            tables = page.extract_tables()
            for table in tables:
                table_string = "\n".join([" | ".join([str(cell) if cell is not None else "" for cell in row]) for row in table if row])
                all_chunks.append({"content": table_string, "tipo": "tabla"})

    return all_chunks


def save_pdf_at_vec_db(
    pdf_paths: list,
    vectorstore_path: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
    batch_size: int = 50,
    max_retries: int = 5,
    retry_delay: int = 10
):
    """
    Procesa una lista de PDFs y guarda sus embeddings en una base de datos vectorial Chroma,
    manejando automáticamente limitaciones de tasa de Azure OpenAI.
    """
    if not pdf_paths:
        raise ValueError("La lista de pdf_paths está vacía.")

    all_documents = []

    for pdf_path in pdf_paths:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"El archivo {pdf_path} no existe.")

        extracted_chunks = extract_text_and_tables(pdf_path)

        file_name = os.path.splitext(os.path.basename(pdf_path))[0]

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        for idx, chunk in enumerate(extracted_chunks):
            tipo = chunk["tipo"]
            content = chunk["content"]

            if tipo == 'tabla':
                doc = Document(
                    page_content=content,
                    metadata={
                        "id": file_name,
                        "fragment": f"{idx+1}",
                        "tipo": tipo
                    }
                )
                all_documents.append(doc)
            else:
                split_docs = splitter.split_text(content)

                for sub_idx, sub_content in enumerate(split_docs):
                    doc = Document(
                        page_content=sub_content,
                        metadata={
                            "id": file_name,
                            "fragment": f"{idx+1}-{sub_idx+1}",
                            "tipo": tipo
                        }
                    )
                    all_documents.append(doc)

    print(f"Total documentos para indexar: {len(all_documents)}")

    # Conexión manual a Azure OpenAI
    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=api_base,
        api_key=api_key
    )

    print(f"Guardando en base vectorial: {vectorstore_path}")
    db = Chroma(persist_directory=vectorstore_path)

    for i in tqdm(range(0, len(all_documents), batch_size), desc="Indexando documentos"):
        batch = all_documents[i:i + batch_size]

        retries = 0
        while retries <= max_retries:
            try:
                texts_batch = [doc.page_content for doc in batch]
                metadatas_batch = [doc.metadata for doc in batch]

                response = client.embeddings.create(
                    input=texts_batch,
                    model=deployment_name
                )
                embeddings = [r.embedding for r in response.data]

                db._collection.add(
                    embeddings=embeddings,
                    documents=texts_batch,
                    metadatas=metadatas_batch,
                    ids=[str(uuid.uuid4()) for _ in range(len(texts_batch))]
                )


                break
            except Exception as e:
                print(f"Error al indexar batch {i//batch_size + 1}: {str(e)}")
                retries += 1
                if retries > max_retries:
                    print(f"Max reintentos alcanzados para batch {i//batch_size + 1}, continuando con el siguiente.")
                    break
                print(f"Esperando {retry_delay} segundos antes de reintentar...")
                time.sleep(retry_delay)

    db.persist()

    print(f"Base vectorial guardada con {len(all_documents)} documentos.")

def search_from_context_vec_db(
    prompt: str,
    vectorstore_path: str,
    k: int = 3,
    find_table: bool = False,
    max_retries: int = 5,
    retry_delay: int = 10
) -> list:
    """
    Busca documentos relevantes desde una base vectorial en disco, priorizando 80% textos y 20% tablas,
    pero asegurando mínimo 1 tabla si es posible.

    Args:
        prompt (str): Pregunta o input del usuario.
        vectorstore_path (str): Ruta donde está almacenada la base de datos vectorial.
        k (int): Número total de resultados a devolver.
        find_table (bool): Si es True, buscará solo tablas; si es False, buscará tanto tablas como textos.

    Returns:
        list: Lista de documentos más relevantes.
    """

    embedding = None
    retries = 0

    while retries <= max_retries:
        try:
            client = AzureOpenAI(
                azure_endpoint=api_base,
                api_key=api_key,
                api_version=api_version
            )

            response = client.embeddings.create(
                input=[prompt],
                model=deployment_name
            )

            embedding = response.data[0].embedding
            break
        except Exception as e:
            print(f"Error al obtener embedding: {str(e)}")
            retries += 1
            if retries > max_retries:
                raise Exception(f"Error permanente al generar embeddings tras {max_retries} reintentos.")
            print(f"Reintentando en {retry_delay} segundos...")
            time.sleep(retry_delay)

    print(f"Cargando vectorstore desde: {vectorstore_path}")
    db = Chroma(persist_directory=vectorstore_path)

    resultados_generales = db.similarity_search_by_vector(embedding, k=k*2)

    if find_table:
        resultados_finales = [doc for doc in resultados_generales if doc.metadata.get('tipo') == 'tabla']
    else:
        textos = [doc for doc in resultados_generales if doc.metadata.get('tipo') != 'tabla']
        tablas = [doc for doc in resultados_generales if doc.metadata.get('tipo') == 'tabla']

        n_textos = int(k * 0.8)
        n_tablas = k - n_textos

        resultados_finales = textos[:n_textos] + tablas[:n_tablas]

        if len(resultados_finales) < k:
            otros = [doc for doc in resultados_generales if doc not in resultados_finales]
            resultados_finales += otros[:k - len(resultados_finales)]

    print(f"Se han recuperado {len(resultados_finales)} fragmentos.")

    return resultados_finales


def process_temp_pdfs_batch(pdf_dir: str, db_dir: str):
    """
    Procesa todas las carpetas en 'data/pdf/'.
    Junta PDFs y crea base vectorial si no existe.
    """
    os.makedirs(db_dir, exist_ok=True)

    for folder_name in os.listdir(pdf_dir):
        carpeta_path = os.path.join(pdf_dir, folder_name)

        if not os.path.isdir(carpeta_path):
            continue 

        db_path = os.path.join(db_dir, folder_name)

        if os.path.exists(db_path):
            print(f"Skipping carpeta '{folder_name}' (base vectorial ya creada).")
            continue

        pdf_paths = [
            os.path.join(carpeta_path, f)
            for f in os.listdir(carpeta_path)
            if f.lower().endswith(".pdf")
        ]

        if not pdf_paths:
            print(f"No hay PDFs en la carpeta {folder_name}. Se omite.")
            continue

        print(f"Procesando carpeta '{folder_name}' con {len(pdf_paths)} PDFs...")
        save_pdf_at_vec_db(pdf_paths, db_path)


def process_pdfs_to_shared_db(pdf_dir="data/pdf", db_dir="db/vec_ayudas_db"):
    """
    Procesa todos los PDFs en el directorio dado (`pdf_dir`) y sus subdirectorios, 
    y guarda sus vectores en una única base de datos vectorial ubicada en `db_dir`.

    Evita reprocesar PDFs que ya fueron agregados, verificando si un archivo de marca
    existe en una subcarpeta `processed_files` dentro de `db_dir`.
    """
    os.makedirs(db_dir, exist_ok=True)
    processed_dir = os.path.join(db_dir, "processed_files")
    os.makedirs(processed_dir, exist_ok=True)

    pdf_paths_to_process = []

    for root, _, files in os.walk(pdf_dir):
        for filename in files:
            if filename.lower().endswith(".pdf"):
                name_without_ext = os.path.splitext(filename)[0]
                marker_path = os.path.join(processed_dir, f"{name_without_ext}.done")

                if os.path.exists(marker_path):
                    print(f"Skipping '{filename}' (already processed).")
                    continue

                pdf_path = os.path.join(root, filename)
                pdf_paths_to_process.append((pdf_path, name_without_ext))

    if not pdf_paths_to_process:
        print("No hay nuevos PDFs por procesar.")
        return

    pdf_files = [pdf_path for pdf_path, _ in pdf_paths_to_process]
    save_pdf_at_vec_db(pdf_files, db_dir)

    for _, name_without_ext in pdf_paths_to_process:
        marker_path = os.path.join(processed_dir, f"{name_without_ext}.done")
        with open(marker_path, "w") as f:
            f.write("done")

    print(f"Procesados {len(pdf_paths_to_process)} PDFs.")
