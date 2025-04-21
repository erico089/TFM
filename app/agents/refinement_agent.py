import os
import json
from smolagents import CodeAgent, OpenAIServerModel, tool
from dotenv import load_dotenv
from tools.vectorial_db_tools import search_from_context_vec_db
from tools.tools import save_json_tool  # ✅ NUEVO: importamos la herramienta

load_dotenv()
api_key = os.environ["OPENROUTER_API_KEY"]

model = OpenAIServerModel(
    model_id="deepseek/deepseek-chat-v3-0324:free",
    api_key=api_key,
    api_base="https://openrouter.ai/api/v1"
)

# 🔧 Tool modificada para aceptar también el vector_path
def build_context_tool(vector_path):
    @tool
    def get_context_from_vector_db(prompt: str) -> str:
        """
        Recupera contexto desde una base de datos vectorial temporal embebida a partir del PDF de una convocatoria.

        Args:
            prompt (str): Consulta concreta sobre el contenido del PDF.

        Returns:
            str: Fragmento de texto del PDF recuperado por similitud semántica.
        """
        return search_from_context_vec_db(prompt, vectorstore_path=vector_path)
    
    return get_context_from_vector_db


def run_refinement_agent(path_json, vector_path):
    with open(path_json, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # ✅ Creamos la herramienta personalizada con el path
    context_tool = build_context_tool(vector_path)
    nombre_archivo = os.path.basename(path_json)

    agent = CodeAgent(
        model=model,
        tools=[context_tool, save_json_tool],  # ✅ Añadimos la nueva herramienta
        additional_authorized_imports=['json']
    )

    prompt = f"""
Eres un agente especializado en completar datos de convocatorias públicas. Tienes acceso a una herramienta llamada `get_context_from_vector_db(query)` que permite recuperar fragmentos relevantes de un documento PDF (ya embebido) utilizando similitud semántica. El contenido procede exclusivamente del texto original del PDF.

Se te proporciona un JSON con información **parcial** sobre una convocatoria de ayudas. Algunos campos ya tienen valores, que debes **usar únicamente como contexto**. **No debes revisarlos, evaluarlos ni modificarlos**, salvo que contengan errores evidentes. Tu objetivo es **rellenar los campos vacíos** con información textual clara y verificable del PDF.

---

**Objetivo principal:**
Completar exclusivamente los campos que están vacíos, sin alterar los demás. Utiliza el contenido existente como guía para entender el tipo de ayuda, beneficiarios, alcance, etc.

---

**Enfoque prioritario en tres campos clave**:
1. `"ano"`  
   - Extrae el periodo en que está abierta la convocatoria. Ejemplos válidos:  
     - "Convocatoria abierta durante todo 2024"  
     - "Plazo de solicitudes del 15 de marzo al 30 de junio de 2025"

2. `"Intensidad de la subvención"`  
   - Extrae los porcentajes de subvención según el tipo de beneficiario (PYME, gran empresa, etc.) y según el tipo de proyecto (Investigación industrial, Desarrollo experimental), si se especifica.
   - Ten en cuenta también factores como cofinanciación con fondos FEDER o zonas geográficas.
   - Suele presentarse en tablas. **Transforma ese contenido en texto estructurado**.
   - Ejemplo ideal:
     ```
     Hasta 10% para gran empresa; 
     Hasta 17% para PYME; 
     Hasta 30% para PYME cofinanciadas con fondos FEDER en Andalucía, Canarias, Castilla-La Mancha, Ceuta, Extremadura y Melilla;
     Hasta 20% para PYME cofinanciadas en el resto del territorio nacional.
     ```

3. `"Intensidad del préstamo"`  
   - Aplica la misma lógica que para la subvención. Busca condiciones diferenciadas, tramos, tipos de interés, garantías o periodos de amortización.
   - Estructura el contenido en texto claro y detallado.

---

**Uso de `get_context_from_vector_db`**:
- Haz preguntas **concretas y específicas** por cada campo vacío.
- No combines varias preguntas en una sola consulta.
- Ejemplos:
  - Para `"ano"`: *¿Cuál es el periodo de presentación de solicitudes?*
  - Para `"Intensidad de la subvención"`: *¿Qué porcentaje de subvención se ofrece según tipo de empresa o tipo de proyecto?*
  - Para `"Intensidad del préstamo"`: *¿Qué condiciones o porcentajes se aplican al préstamo ofrecido?*

---

**Criterios clave**:
- No inventes información. Solo completa campos vacíos si hay evidencia textual clara.
- Usa el contenido ya presente en el JSON solo como **ayuda contextual**.
- Si no encuentras información fiable para un campo vacío, **déjalo tal como está**.
- No revises ni reescribas campos que ya tienen contenido correcto (excepto si hay errores evidentes).

---

**Formato de salida**:
- Devuelve únicamente el JSON actualizado, sin explicaciones ni comentarios.

---

Una vez hayas completado el JSON, llama a la herramienta `save_json_tool(json_data, filename)` para guardarlo.
- Guardalo con el mismo nombre que tenia el json con el que has trabajado {nombre_archivo} y pero en la carpeta data/json/refined.

---

Empieza ahora con el siguiente JSON:
{json.dumps(json_data, indent=2, ensure_ascii=False)}
"""

    resultado = agent.run(prompt)

    return resultado
