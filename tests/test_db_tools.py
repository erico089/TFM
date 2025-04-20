# test_vectorstore.py
import shutil
shutil.rmtree("db_vectorial", ignore_errors=True)

from langchain_community.embeddings import HuggingFaceEmbeddings
from tools.vectorial_db_tools import (
    procesar_pdf_y_guardar_en_vectorstore,
    buscar_contexto_desde_vectorstore
)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# === Configuración ===
pdf_path = "test.pdf"  # Asegúrate de tener un PDF aquí
vectorstore_path = "db_vectorial"  # Ruta donde se guardará la base vectorial
query = "¿Que son els polígons de thiessen?"

# === 1. Procesar el PDF y guardarlo en la base vectorial ===
print("\n===== INDEXANDO DOCUMENTO =====\n")
procesar_pdf_y_guardar_en_vectorstore(
    pdf_path=pdf_path,
    vectorstore_path=vectorstore_path,
    chunk_size=500,
    chunk_overlap=100
)

# === 2. Hacer una consulta y obtener el contexto ===
print("\n===== HACIENDO CONSULTA =====\n")
contexto = buscar_contexto_desde_vectorstore(
    prompt=query,
    vectorstore_path=vectorstore_path,
    k=3
)

# === Construir el prompt final combinando contexto + pregunta ===
def construir_prompt_final(pregunta: str, contexto: list[str]) -> str:
    prompt = f"Consulta: {pregunta}\n\nSiguiendo el siguiente contexto:\n"
    for i, fragmento in enumerate(contexto, 1):
        prompt += f"[Fragmento {i}]\n{fragmento.strip()}\n\n"
    return prompt

# === Crear el prompt final ===
prompt_final = construir_prompt_final(query, contexto)

# === Mostrar el prompt que se mandaría al modelo ===
print("\n===== PROMPT FINAL PARA EL MODELO =====\n")
print(prompt_final)

