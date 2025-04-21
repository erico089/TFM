import fitz  # PyMuPDF

def extraer_apartados(pdf_path):
    doc = fitz.open(pdf_path)
    apartados = []
    texto_actual = ""
    apartado_actual = None
    
    for pagina in doc:
        texto = pagina.get_text("text")
        lineas = texto.split("\n")
        
        for linea in lineas:
            # Aquí definimos el patrón para identificar los apartados
            if linea.isupper() and len(linea.split()) < 5:  # Títulos en mayúsculas y pocos términos
                # Si ya hemos empezado un apartado, guardamos el anterior
                if apartado_actual:
                    apartados.append((apartado_actual, texto_actual))
                # Iniciamos el nuevo apartado
                apartado_actual = linea.strip()
                texto_actual = ""
            else:
                texto_actual += linea + "\n"

    # Guardamos el último apartado que puede no haber sido añadido
    if apartado_actual:
        apartados.append((apartado_actual, texto_actual))
    
    return apartados

# Usar el código
pdf_path = "pdf/convocatoria_1.pdf"
apartados = extraer_apartados(pdf_path)

# Ver los apartados extraídos
for apartado, texto in apartados:
    print(f"Apartado: {apartado}")
    print(f"Contenido: {texto[:200]}...")  # Muestra los primeros 200 caracteres de cada apartado
