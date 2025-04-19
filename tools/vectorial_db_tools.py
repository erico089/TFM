from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
from tools.utils import getVectorialIdFromFile

local_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

import os

def save_pdf_at_vec_db(
    pdf_path: str,
    vectorstore_path: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
    pdf_id: str = None
):
    """
    Procesa un PDF y guarda sus embeddings en una base de datos vectorial Chroma.

    Args:
        pdf_path (str): Ruta al archivo PDF.
        vectorstore_path (str): Ruta al directorio donde se guardará la base vectorial.
        chunk_size (int): Tamaño de los fragmentos en caracteres.
        chunk_overlap (int): Número de caracteres que se solapan entre chunks.
        pdf_id (str, opcional): Si se proporciona, cada chunk se guarda como un dict con {"text": ..., "id": pdf_id}.
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

    if pdf_id:
        print(f"🆔 Añadiendo ID '{pdf_id}' a cada chunk.")
        for chunk in chunks:
            chunk.metadata["id"] = pdf_id

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print(f"💾 Guardando en la base vectorial en: {vectorstore_path}")
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=vectorstore_path
    )
    db.persist()

    print(f"✅ Proceso completo. Se han guardado {len(chunks)} chunks en la base vectorial.")


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

def process_temp_pdfs_batch():
    """
    Processes all PDFs in the 'data/pdf/' directory. For each PDF:
    
    - Checks if a vector DB already exists in 'data/temp/_bec_db/' with the same name (excluding the .pdf extension).
    - If not, it calls the function `savepdfaddbecdb` to create the DB.

    This avoids reprocessing PDFs that have already been converted into vector DBs.
    """
    pdf_dir = "data/pdf"
    db_dir = "data/temp_vec_db"

    os.makedirs(db_dir, exist_ok=True)

    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith(".pdf"):
            name_without_ext = os.path.splitext(filename)[0]
            db_path = os.path.join(db_dir, name_without_ext)

            if os.path.exists(db_path):
                print(f"✅ Skipping '{filename}' (already processed).")
                continue

            pdf_path = os.path.join(pdf_dir, filename)
            print(f"🧩 Processing '{filename}'...")
            save_pdf_at_vec_db(pdf_path, db_path)


def process_pdfs_to_shared_db(pdf_dir="data/pdf", db_dir="data/vec_ayudas_db"):
    """
    Procesa todos los PDFs en el directorio dado (`pdf_dir`) y guarda sus vectores
    en una única base de datos vectorial ubicada en `db_dir`.

    Evita reprocesar PDFs que ya fueron agregados, verificando si un archivo de marca
    existe en una subcarpeta `processed_files` dentro de `db_dir`.
    """
    os.makedirs(db_dir, exist_ok=True)
    processed_dir = os.path.join(db_dir, "processed_files")
    os.makedirs(processed_dir, exist_ok=True)

    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith(".pdf"):
            name_without_ext = os.path.splitext(filename)[0]
            marker_path = os.path.join(processed_dir, f"{name_without_ext}.done")

            if os.path.exists(marker_path):
                print(f"✅ Skipping '{filename}' (already processed).")
                continue

            pdf_path = os.path.join(pdf_dir, filename)
            print(f"🧩 Processing '{filename}'...")

            save_pdf_at_vec_db(pdf_path, db_dir,pdf_id=getVectorialIdFromFile(filename))

            with open(marker_path, "w") as f:
                f.write("done")