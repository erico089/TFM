from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
from tools.utils import getVectorialIdFromFile

local_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


import os

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

        print(f"📄 Cargando PDF desde: {pdf_path}")
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        print(f"✂️ Dividiendo en chunks (chunk_size={chunk_size}, overlap={chunk_overlap}) para {pdf_path}...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = splitter.split_documents(docs)

        # Obtener el id basado en el nombre del archivo (sin extensión)
        file_name = os.path.splitext(os.path.basename(pdf_path))[0]

        print(f"🧩 Añadiendo metadatos (id={file_name}) a {len(chunks)} chunks...")
        for i, chunk in enumerate(chunks, start=1):
            chunk.metadata["id"] = file_name  # <- El id es diferente para cada PDF
            chunk.metadata["fragment"] = i

        all_chunks.extend(chunks)

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print(f"💾 Guardando en la base vectorial en: {vectorstore_path}")
    db = Chroma.from_documents(
        documents=all_chunks,
        embedding=embedding_model,
        persist_directory=vectorstore_path
    )
    db.persist()

    print(f"✅ Proceso completo. Se han guardado {len(all_chunks)} chunks en la base vectorial.")


def search_from_context_vec_db(
    prompt: str,
    vectorstore_path: str,
    embedding_model=None,
    k: int = 5
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
    Procesa todas las carpetas en 'data/pdf/'.
    Para cada carpeta:
        - Junta todos los PDFs.
        - Si no existe una base vectorial en 'data/temp_vec_db/', la crea con todos los PDFs de esa carpeta.

    Así se evita re-procesar carpetas ya convertidas en base vectorial.
    """
    pdf_dir = "data/pdf"
    db_dir = "data/temp_vec_db"

    os.makedirs(db_dir, exist_ok=True)

    for folder_name in os.listdir(pdf_dir):
        carpeta_path = os.path.join(pdf_dir, folder_name)

        if not os.path.isdir(carpeta_path):
            continue  # Saltar si no es una carpeta

        db_path = os.path.join(db_dir, folder_name)

        if os.path.exists(db_path):
            print(f"✅ Skipping carpeta '{folder_name}' (base vectorial ya creada).")
            continue

        # Buscar todos los PDFs dentro de la carpeta
        pdf_paths = [
            os.path.join(carpeta_path, f)
            for f in os.listdir(carpeta_path)
            if f.lower().endswith(".pdf")
        ]

        if not pdf_paths:
            print(f"⚠️ No hay PDFs en la carpeta {folder_name}. Se omite.")
            continue

        print(f"🧩 Procesando carpeta '{folder_name}' con {len(pdf_paths)} PDFs...")
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

    # Recorrer recursivamente todas las carpetas y subcarpetas
    for root, _, files in os.walk(pdf_dir):
        for filename in files:
            if filename.lower().endswith(".pdf"):
                name_without_ext = os.path.splitext(filename)[0]
                marker_path = os.path.join(processed_dir, f"{name_without_ext}.done")

                if os.path.exists(marker_path):
                    print(f"✅ Skipping '{filename}' (already processed).")
                    continue

                pdf_path = os.path.join(root, filename)
                pdf_paths_to_process.append((pdf_path, name_without_ext))

    if not pdf_paths_to_process:
        print("⚠️ No hay nuevos PDFs por procesar.")
        return

    # Procesar todos los PDFs de golpe
    pdf_files = [pdf_path for pdf_path, _ in pdf_paths_to_process]
    save_pdf_at_vec_db(pdf_files, db_dir)

    # Crear archivos de marca para cada PDF procesado
    for _, name_without_ext in pdf_paths_to_process:
        marker_path = os.path.join(processed_dir, f"{name_without_ext}.done")
        with open(marker_path, "w") as f:
            f.write("done")

    print(f"✅ Procesados {len(pdf_paths_to_process)} PDFs.")
