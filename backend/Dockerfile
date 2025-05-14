FROM python:3.10-slim

WORKDIR /app

# Installa dipendenze di sistema necessarie per mariadb client
RUN apt-get update && apt-get install -y gcc g++ libmariadb-dev

# Installa dipendenze di sistema necessarie per testare l'avvio del backend
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*


COPY src/backend /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8003

CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8003"]