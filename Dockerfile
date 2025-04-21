FROM python:3.10.16

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos al contenedor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app

# Expón el puerto si tu app lo necesita (opcional)
# EXPOSE 8000

# Comando por defecto (lo puedes overridear con docker-compose)
CMD ["python", "app/main.py"]
