from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
import pdfplumber
from langchain_community.docstore.document import Document

local_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


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
    chunk_overlap: int = 100
):
    """
    Procesa una lista de PDFs y guarda sus embeddings en una base de datos vectorial Chroma.
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

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print(f"Guardando en base vectorial: {vectorstore_path}")
    db = Chroma.from_documents(
        documents=all_documents,
        embedding=embedding_model,
        persist_directory=vectorstore_path
    )
    db.persist()

    print(f"Base vectorial guardada con {len(all_documents)} documentos.")


def search_from_context_vec_db(
    prompt: str,
    vectorstore_path: str,
    embedding_model=None,
    k: int = 5
) -> list:
    """
    Busca documentos relevantes desde una base vectorial en disco, priorizando 80% textos y 20% tablas,
    pero asegurando mínimo 1 tabla si es posible.

    Args:
        prompt (str): Pregunta o input del usuario.
        vectorstore_path (str): Ruta donde está almacenada la base de datos vectorial.
        embedding_model: Instancia de un modelo de embeddings compatible con LangChain.
        k (int): Número total de resultados a devolver.

    Returns:
        list[str]: Lista de textos de los documentos más relevantes.
    """

    if embedding_model is None:
        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print(f"Cargando vectorstore desde: {vectorstore_path}")
    db = Chroma(
        persist_directory=vectorstore_path,
        embedding_function=embedding_model
    )

    num_tables = max(1, round(0.2 * k))
    num_texts = k - num_tables

    print(f"Buscando {num_texts} textos y {num_tables} tablas más relevantes...")

    resultados_texto = db.similarity_search(
        prompt, 
        k=num_texts * 2
    )
    textos_filtrados = [doc for doc in resultados_texto if doc.metadata.get('type') != 'table']

    resultados_tabla = db.similarity_search(
        prompt,
        k=num_tables * 2
    )
    tablas_filtradas = [doc for doc in resultados_tabla if doc.metadata.get('type') == 'table']

    textos_final = textos_filtrados[:num_texts]
    tablas_final = tablas_filtradas[:num_tables]

    resultados_finales = textos_final + tablas_final

    if len(resultados_finales) < k:
        print("No se encontraron suficientes documentos del tipo esperado. Rellenando...")
        otros = [
            doc for doc in (resultados_texto + resultados_tabla)
            if doc not in resultados_finales
        ]
        resultados_finales += otros[:k - len(resultados_finales)]

    print(f"Se han recuperado {len(resultados_finales)} fragmentos (textos + tablas).")

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
