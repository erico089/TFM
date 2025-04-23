FROM python:3.10.16

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app

CMD ["tail", "-f", "/dev/null"]
