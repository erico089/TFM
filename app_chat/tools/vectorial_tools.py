from smolagents import tool
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

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
