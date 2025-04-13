import pdfplumber
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
api_key = os.environ["OPENROUTER_API_KEY"]

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def extraer_texto_pdf(pdf_path):
    texto_completo = ""
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text()
    print("\n--- Texto extraído del PDF (preview) ---\n")
    print(texto_completo[:2000]) 
    return texto_completo

def obtener_apartados(texto_pdf):
    prompt = f"Extrae los apartados principales de este texto:\n\n{texto_pdf}"
    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324:free",
        messages=[
            {"role": "system", "content": "Eres un asistente que identifica y lista los apartados de documentos."},
            {"role": "user", "content": prompt}
        ],
        extra_headers={
            "HTTP-Referer": "https://tuweb.com", 
            "X-Title": "ResumenPDF",             
        }
    )
    respuesta = completion.choices[0].message.content.strip()
    print("\n--- Apartados detectados por el modelo ---\n")
    print(respuesta)
    apartados = [a.strip() for a in respuesta.split("\n") if a.strip()]
    return apartados

def resumir_apartado(apartado):
    prompt = f"Resume el siguiente apartado:\n\n{apartado}"
    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324:free",
        messages=[
            {"role": "system", "content": "Eres un asistente experto en resumir textos técnicos de forma clara y concisa."},
            {"role": "user", "content": prompt}
        ],
        extra_headers={
            "HTTP-Referer": "https://tuweb.com",
            "X-Title": "ResumenPDF",
        }
    )
    resumen = completion.choices[0].message.content.strip()
    print(f"\n--- Resumen del apartado '{apartado}' ---\n")
    print(resumen)
    return resumen

def guardar_txt(apartados_resumenes, output_txt):
    with open(output_txt, 'w', encoding='utf-8') as f:
        for apartado, resumen in apartados_resumenes:
            f.write(f"{apartado}\n{resumen}\n\n")
    print(f"\n✅ Archivo guardado como: {output_txt}")

def procesar_pdf(pdf_path, output_txt):
    texto_pdf = extraer_texto_pdf(pdf_path)
    apartados = obtener_apartados(texto_pdf)

    apartados_resumenes = []
    for apartado in apartados:
        resumen = resumir_apartado(apartado)
        apartados_resumenes.append((apartado, resumen))

    guardar_txt(apartados_resumenes, output_txt)


pdf_path = "pdf/convocatoria_1.pdf" 
output_pdf = "txt/convocatoria_1_resumen.txt" 

procesar_pdf(pdf_path, output_pdf)
