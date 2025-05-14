from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
import requests
from pathlib import Path
import urllib.parse
import re
from re import Match
from typing import Dict
import os

"""
Questo file contiene il codice del server frontend FastAPI che gestisce le richieste HTTP e le pagine web.
Questi sono gli endpoint principali:
1. /search/{search_request}: per cercare film o registi in base a una query specifica.
2. /schema_summary: per ottenere lo schema del database, ovvero i nomi delle tabelle e le colonne di ogni tabella.
3. /add: per aggiungere un nuovo film al database.
"""

app = FastAPI()

# Funziona solo in locale 
#BASE_DIR = Path(__file__).resolve().parent.parent.parent
#templates = Jinja2Templates(directory=BASE_DIR / "templates")

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

@app.get("/search")
def search(request: Request, search_request: str):
    """
    Questa funzione gestisce le richieste (specifiche) di ricerca per film o registi.
    Prende in input una stringa di ricerca, chiama l'API per ottenere i risultati e restituisce la pagina con i risultati in search.html.
    Se si verifica un errore durante la chiamata all'API, restituisce un messaggio di errore.
    """
    print("Search request:", search_request)
    try:
        # Serve per codificare i caratteri speciali nell'URL come ?
        encoded_search_request = urllib.parse.quote(search_request, safe='')    
        response = requests.get(f"{API_BASE_URL}/search/{encoded_search_request}")
        response.raise_for_status()
        search_results = response.json()
        return templates.TemplateResponse("search.html", {"request": request, "search_results": search_results})
    except requests.HTTPError as e:
        # Cattura l'errore HTTP e mostra un messaggio all'utente
        try:
            error_detail = response.json().get("detail", str(e))
        except Exception:
            error_detail = str(e)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Errore nella ricerca: {error_detail}"
        })
    except Exception as e:
        # Qualsiasi altro errore
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Errore inatteso: {e}"
        })

@app.get("/schema_summary")
def schema_summary(request: Request):
    """
    Questa funzione gestisce la richiesta per ottenere lo schema del database.
    Chiama l'API per ottenere i risultati e restituisce la pagina con i risultati in schema_summary.html.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/schema_summary")
        response.raise_for_status()
        schema_summary = response.json()
        return templates.TemplateResponse("schema_summary.html", {"request": request, "schema_summary": schema_summary})
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schema summary: {e}")


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
    print("Add request:", title, director, age, year, genre, platform1, platform2)

    data_line: str = f"{title},{director},{age},{year},{genre},{platform1},{platform2}"
    print("Data line:", data_line)

    # Verifica se l'input è corretto con l'espressione regolare
    pattern: str = r'^([^,]+),([^,]+),(\d{1,3}),(\d{4}),([^,]+),([^,]*),([^,]*)$'
    match: Match[str] = re.fullmatch(pattern, data_line)

    if match:
        print("Match")
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