from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
import requests
from pathlib import Path
import re
from re import Match
from typing import Dict, List
import os

"""
Questo file contiene il codice del server frontend FastAPI che gestisce le richieste HTTP e le pagine web.
Questi sono gli endpoint principali:
1. /search: per fare una ricerca nel database utilizzando una domanda in linguaggio naturale.
2. /sql_search: per eseguire una query SQL direttamente sul database.
3. /schema_summary: per ottenere lo schema del database, ovvero i nomi delle tabelle e le colonne di ogni tabella.
4. /add: per aggiungere un nuovo film al database.
"""

app = FastAPI()

# Funziona in docker
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:800")

@app.get("/")
def index(request: Request):
    """
    Questa funzione restituisce la pagina principale dell'applicazione dove l'utente può accedere alle varie funzionalità.
    """
    return templates.TemplateResponse("index.html", {"request": request})

# ---------------------------------------------------------- ENDPOINT /search ---------------------------------------------------

@app.post("/search")
def search(request: Request, search_request: str = Form(...), model: str = Form(...)):
    """
    Questa funzione gestisce la richiesta di ricerca nel database.
    Prende in input una domanda in linguaggio naturale e un modello, chiama l'API per ottenere i risultati della ricerca
    """
    print("Search request:", search_request, flush=True)
    print("Model:", model, flush=True)
    data: Dict[str, str] = {
        "question" : search_request,
        "model": model
    }
    try:
        response = requests.post(f"{API_BASE_URL}/search", json=data)
        response.raise_for_status()
        search_results: Dict[str, str] = response.json()
        sql: str = search_results["sql"]
        sql_validation: str = search_results["sql_validation"]
        results: str = search_results["results"]
        print("SQL:", sql, flush=True)
        print("SQL Validation:", sql_validation, flush=True)
        print("Results:", results, flush=True)
        return templates.TemplateResponse("search.html",{"request": request, "sql": sql, "sql_validation": sql_validation, "results": results })
    except requests.HTTPError as e:
        # Cattura l'errore HTTP e mostra un messaggio all'utente
        try:
            error_detail = response.json().get("detail", str(e))
        except Exception:
            error_detail = str(e)
        return templates.TemplateResponse("search.html", {
            "request": request,
            "error": f"Errore nella ricerca: {error_detail}"
        })
    except Exception as e:
        # Qualsiasi altro errore
        return templates.TemplateResponse("search.html", {
            "request": request,
            "error": f"Errore inatteso: {e}"
        })
    
# ---------------------------------------------------------- ENDPOINT /sql_search ---------------------------------------------------

@app.get("/sql_search")
def sql_search_page(request: Request):
    """
    Questa funzione serve per accedere alla pagina web sql_search.html da index.html.
    """
    isfirst_time: bool = True
    return templates.TemplateResponse("sql_search.html", {"request": request, "isfirst_time": isfirst_time})

@app.post("/sql_search")
def sql_search(request: Request, sql_query: str = Form(...), model: str = Form(...)):
    """
    Questa funzione gestisce la richiesta per eseguire una query SQL sul database.
    Prende in input una query SQL e un modello, chiama l'API per ottenere i risultati della ricerca.
    """
    print("SQL Query:", sql_query, flush=True)
    print("Model:", model, flush=True)
    data: Dict[str, str] = {
        "sql_query" : sql_query,
        "model": model
    }
    try:
        response = requests.post(f"{API_BASE_URL}/sql_search", json=data)
        response.raise_for_status()
        sql_search_results: Dict[str, str] = response.json()
        sql_validation: str = sql_search_results["sql_validation"]
        results: str = sql_search_results["results"]
        print("SQL Validation:", sql_validation, flush=True)
        print("Results:", results, flush=True)
        return templates.TemplateResponse("sql_search.html",{"request": request, "sql_validation": sql_validation, "results": results, "isfirst_time": False})
    except requests.HTTPError as e:
        # Cattura l'errore HTTP e mostra un messaggio all'utente
        try:
            error_detail = response.json().get("detail", str(e))
        except Exception:
            error_detail = str(e)
        return templates.TemplateResponse("sql_search.html", {
            "request": request,
            "error": f"Errore nella ricerca sql: {error_detail}"
        })
    except Exception as e:
        # Qualsiasi altro errore
        return templates.TemplateResponse("sql_search.html", {
            "request": request,
            "error": f"Errore inatteso: {e}"
        })

# ---------------------------------------------------------- ENDPOINT /schema_summary ---------------------------------------------------

@app.get("/schema_summary")
def schema_summary(request: Request):
    """
    Questa funzione gestisce la richiesta per ottenere lo schema del database.
    Chiama l'API per ottenere i risultati e restituisce la pagina con i risultati in schema_summary.html.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/schema_summary")
        response.raise_for_status()
        schema_summary_response: List[Dict[str, str]] = response.json()
        schema_summary: Dict[str, List[str]] = {}
        for item in schema_summary_response:
            table_name: str = item["table_name"]
            table_column: str = item["table_column"]
            if table_name not in schema_summary:
                schema_summary[table_name] = []
            schema_summary[table_name].append(table_column)
        print("Schema Summary:", schema_summary, flush=True)
        return templates.TemplateResponse("schema_summary.html", {"request": request, "schema_summary": schema_summary})
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schema summary: {e}")

# ---------------------------------------------------------- ENDPOINT /add ---------------------------------------------------

@app.get("/add")
def add_page(request: Request):
    """
    Questa funzione serve per accedere alla pagina web add.html da index.html.
    """
    return templates.TemplateResponse("add.html", {"request": request})


@app.post("/add")
def add(request: Request, title: str = Form(...), director: str = Form(...), age: int = Form(...), year: int = Form(...), genre: str = Form(...), platform1: str = Form(...), platform2: str = Form(...)):
    """
    Questa funzione gestisce la richiesta per aggiungere un nuovo film al database.
    Prende in input una serie di dati, li sistema nel formato corretto e chiama l'API per aggiungere il film.
    Se si verifica un errore durante la chiamata all'API, restituisce un messaggio di errore.
    """
    print("Add request:", title, director, age, year, genre, platform1, platform2, flush=True)

    data_line: str = f"{title},{director},{age},{year},{genre},{platform1},{platform2}"
    print("Data line:", data_line, flush=True)

    # Verifica se l'input è corretto con l'espressione regolare
    pattern: str = r'^([^,]+),([^,]+),(\d{1,3}),(\d{4}),([^,]+),([^,]*),([^,]*)$'
    match: Match[str] = re.fullmatch(pattern, data_line)

    if match:
        print("Match", flush=True)
        data: Dict[str, str] = {
            "data_line": data_line
        }
        try:
            response = requests.post(f"{API_BASE_URL}/add", json=data)
            response.raise_for_status()
            add_response: Dict[str, str] = response.json()
            status: str = add_response["status"]

            return templates.TemplateResponse("index.html", {
                "request": request,
                "status": status
            })
    
        except requests.HTTPError as e:
            # Cattura l'errore HTTP e mostra un messaggio all'utente
            try:
                error_detail = response.json().get("detail", str(e))
            except Exception:
                error_detail = str(e)
            return templates.TemplateResponse("add.html", {
                "request": request,
                "error": f"Errore nell'inserimento dei dati': {error_detail}"
            })
        except Exception as e:
            # Qualsiasi altro errore
            return templates.TemplateResponse("add.html", {
                "request": request,
                "error": f"Errore inatteso: {e}"
            })
    else:
        return templates.TemplateResponse("add.html", {
            "request": request,
            "error": "Si è verificato un errore nell'inserimento dei dati. Assicurati che i dati siano inseriti correttamente."
        })