from smolagents import tool
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

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

    k = 10

    vectorstore_path = "db/vec_ayudas_db"

    load_dotenv()
    if os.getenv("ENVIRONMENT") == "TEST":
        vectorstore_path = "db_test"

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = Chroma(
        persist_directory=vectorstore_path,
        embedding_function=embedding_model
    )

    resultados = db.similarity_search(prompt, k=k)

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

    k = 10

    vectorstore_path = "db/vec_ayudas_db"

    load_dotenv()
    if os.getenv("ENVIRONMENT") == "TEST":
        vectorstore_path = "db_test"

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = Chroma(
        persist_directory=vectorstore_path,
        embedding_function=embedding_model
    )

    return db.similarity_search(prompt, k=k, filter={"id": doc_id})

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

    k = 10

    vectorstore_path = "db/vec_ayudas_db"

    load_dotenv()
    if os.getenv("ENVIRONMENT") == "TEST":
        vectorstore_path = "db_test"

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = Chroma(
        persist_directory=vectorstore_path,
        embedding_function=embedding_model
    )

    return db.similarity_search(
        prompt, 
        k=k, 
        filter={
        "$and": [
            {"id": doc_id},
            {"fragment": fragment_id}
        ]
        }
    )

local_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def save_pdf_at_vec_db(
    pdf_paths: list,
    vectorstore_path: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
):
    """
    Procesa una lista de PDFs y guarda sus embeddings en una base de datos vectorial Chroma.

    Args:
        pdf_paths (list): Lista de rutas de archivos PDF.
        vectorstore_path (str): Ruta al directorio donde se guardará la base vectorial.
        chunk_size (int): Tamaño de los fragmentos en caracteres.
        chunk_overlap (int): Número de caracteres que se solapan entre chunks.
    """

    if not pdf_paths:
        raise ValueError("La lista de pdf_paths está vacía.")

    all_chunks = []

    for pdf_path in pdf_paths:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"El archivo {pdf_path} no existe.")

        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = splitter.split_documents(docs)

        file_name = os.path.splitext(os.path.basename(pdf_path))[0]

        for i, chunk in enumerate(chunks, start=1):
            chunk.metadata["id"] = file_name
            chunk.metadata["fragment"] = i

        all_chunks.extend(chunks)

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print(f"Guardando en la base vectorial en: {vectorstore_path}")
    db = Chroma.from_documents(
        documents=all_chunks,
        embedding=embedding_model,
        persist_directory=vectorstore_path
    )
    db.persist()

    print(f"✅ Proceso completo. Se han guardado {len(all_chunks)} chunks en la base vectorial.")