from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import HuggingFaceEmbeddings

local_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def save_pdf_at_vec_db(
    pdf_path: str,
    vectorstore_path: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
):
    """
    Procesa un PDF y guarda sus embeddings en una base de datos vectorial Chroma.

    Args:
        pdf_path (str): Ruta al archivo PDF.
        vectorstore_path (str): Ruta al directorio donde se guardará la base vectorial.
        chunk_size (int): Tamaño de los fragmentos en caracteres.
        chunk_overlap (int): Número de caracteres que se solapan entre chunks.
    """

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"El archivo {pdf_path} no existe.")

    print(f"📄 Cargando PDF desde: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    print(f"✂️ Dividiendo en chunks (chunk_size={chunk_size}, overlap={chunk_overlap})...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(docs)

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print(f"💾 Guardando en la base vectorial en: {vectorstore_path}")
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=vectorstore_path
    )
    db.persist()

    print(f"✅ Proceso completo. Se han guardado {len(chunks)} chunks en la base vectorial.")

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings 

def search_from_context_vec_db(
    prompt: str,
    vectorstore_path: str,
    embedding_model=None,
    k: int = 4
) -> list:
    """
    Busca los documentos más relevantes desde una base vectorial en disco, dada una consulta.

    Args:
        prompt (str): Pregunta o input del usuario.
        vectorstore_path (str): Ruta donde está almacenada la base de datos vectorial.
        embedding_model: Instancia de un modelo de embeddings compatible con LangChain.
        k (int): Número de resultados más similares a devolver.

    Returns:
        list[str]: Lista de textos de los documentos más similares (contexto).
    """

    if embedding_model is None:
        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print(f"🔍 Cargando vectorstore desde: {vectorstore_path}")
    db = Chroma(
        persist_directory=vectorstore_path,
        embedding_function=embedding_model
    )

    print(f"🧠 Buscando los {k} documentos más similares...")
    resultados = db.similarity_search(prompt, k=k)

    contexto = [doc.page_content for doc in resultados]
    print(f"✅ Se han recuperado {len(contexto)} fragmentos de contexto.")

    return contexto

