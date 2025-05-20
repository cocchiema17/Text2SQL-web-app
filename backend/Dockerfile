FROM python:3.10-slim

WORKDIR /app

# Installa dipendenze di sistema necessarie per mariadb client
RUN apt-get update && apt-get install -y gcc g++ libmariadb-dev

# Installa dipendenze di sistema necessarie per testare l'avvio del backend
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*


COPY text_to_sql/src /app
COPY text_to_sql/requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/src/backend /app
COPY backend/requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8003

CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8003"]