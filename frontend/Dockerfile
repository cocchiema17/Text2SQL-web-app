FROM python:3.10-slim

WORKDIR /app

COPY src/frontend /app
COPY templates /app/templates
COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8004

CMD ["uvicorn", "frontend:app", "--host", "0.0.0.0", "--port", "8004"]