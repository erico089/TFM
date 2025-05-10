from smolagents import tool
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from openai import AzureOpenAI
import pdfplumber
from langchain_community.docstore.document import Document
import time
from tqdm import tqdm  
import uuid

load_dotenv()
api_key = os.environ["AZURE_EMBEDDING_KEY"]
deployment_name = os.environ["AZURE_EMBEDDING_DEPLOYMENT_NAME"]
api_base = os.environ["AZURE_EMBEDDING_ENDPOINT"] 
api_version = os.environ["AZURE_EMBEDDING_API_VERSION"] 

@tool
def get_context(prompt: str) -> list:
    """
    Busca los documentos más relevantes desde una base vectorial en disco, dada una consulta.
    Se usa una configuración fija para la ruta del vector store y el modelo de embeddings.

    Args:
        prompt (str): Pregunta o input del usuario.

    Returns:
        list[str]: Lista de textos de los documentos más similares (contexto).
    """

    k = 6

    vectorstore_path = "db/vec_ayudas_db"

    load_dotenv()
    if os.getenv("ENVIRONMENT") == "TEST":
        vectorstore_path = "db_test"

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

    db = Chroma(persist_directory=vectorstore_path)

    resultados = db.similarity_search(embedding, k=k)

    contexto = [doc.page_content for doc in resultados]

    return contexto

@tool
def get_context_by_id(prompt: str, doc_id: str) -> list:
    """
    Busca los documentos más relevantes desde una base vectorial en disco, dada una consulta,
    pero solo en los documentos que tienen un ID específico en su metadata.

    Args:
        prompt (str): Pregunta o input del usuario.
        doc_id (str): ID del documento para filtrar los resultados por metadata.

    Returns:
        list[str]: Lista de textos de los documentos más similares (contexto) que coinciden con el ID.
    """

    k = 6

    vectorstore_path = "db/vec_ayudas_db"

    load_dotenv()
    if os.getenv("ENVIRONMENT") == "TEST":
        vectorstore_path = "db_test"

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

    db = Chroma(persist_directory=vectorstore_path)

    return db.similarity_search(embedding, k=k, filter={"id": doc_id})

@tool
def get_context_by_id_and_fragment(prompt: str, doc_id: str, fragment_id: int) -> list:
    """
    Busca los documentos más relevantes desde una base vectorial en disco, dada una consulta,
    pero solo en los documentos que tienen un ID y fragmento específico en su metadata.

    Args:
        prompt (str): Pregunta o input del usuario.
        doc_id (str): ID del documento para filtrar los resultados por metadata.
        fragment_id (int): ID del fragmento para filtrar los resultados por metadata.

    Returns:
        list[str]: Lista de textos de los documentos más similares (contexto) que coinciden con el ID.
    """

    k = 6

    vectorstore_path = "db/vec_ayudas_db"

    load_dotenv()
    if os.getenv("ENVIRONMENT") == "TEST":
        vectorstore_path = "db_test"

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

    db = Chroma(persist_directory=vectorstore_path)

    return db.similarity_search(
        embedding, 
        k=k, 
        filter={
        "$and": [
            {"id": doc_id},
            {"fragment": fragment_id}
        ]
        }
    )

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