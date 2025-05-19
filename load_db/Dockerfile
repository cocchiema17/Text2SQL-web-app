FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ libmariadb-dev

COPY load_db.py /app/
COPY data.tsv /app/

RUN pip install --no-cache-dir mariadb

CMD ["python", "load_db.py"]
