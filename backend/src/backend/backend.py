from fastapi import FastAPI, HTTPException
from typing import List, Tuple
from connection_manager import ConnectionManager
from models import *
import re
from re import Match
import os
from model_controller import ModelController

"""
Questo file contiene il codice del server backend FastAPI che gestisce le richieste HTTP, l'interazione con il database attraverso la 
classe ConnectionManager e gestisce e comunica con il modello di IA di Ollama attraverso la classe ModelController.
Questi sono gli endpoint principali:
1. /search: richiedere informazioni sui film, registi e piattaforme.
2. /sql_search: per eseguire query SQL dirette sul database.
3. /schema_summary: per ottenere lo schema del database, ovvero i nomi delle tabelle e le colonne di ogni tabella.
4. /add: per aggiungere un nuovo film al database.
"""

app = FastAPI()

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")

mc: ModelController = ModelController(OLLAMA_API_URL)
# All'inizio del server, il modello viene caricato
is_model_loaded: bool = mc.pull_model()
if not is_model_loaded:
    raise HTTPException(status_code=500, detail="Failed to load the model. Please check the OLLAMA API URL or the model name.")

# ---------------------------------------------------------- ENDPOINT /search ---------------------------------------------------

@app.post("/search")
def search(search_request: SearchRequest) -> SearchResponse:
    """
    Questo metodo prende in input una stringa di ricerca e la passa al modello di IA per generare una query SQL.
    Se la query è valida, viene eseguita sul database e restituisce i risultati.
    Se la query è "unsafe" o "invalid", lo segnala.
    """
    if not search_request.question:
        raise HTTPException(status_code=422, detail="'question' is a necessary field.")
    
    cm: ConnectionManager = ConnectionManager()
    schema_summary: List[Tuple[str, str]] = cm.query_schema_summary()

    question: str = search_request.question
    query: str = mc.ask_question(question, schema_summary)
    print(f"Query by model: {query}", flush=True)
    query = cm.clean_sql_output(query)
    print(f"Cleaned query: {query}", flush=True)

    sql_validation: str = cm.sql_validation(query)

    # se la query è "valid" allora si esegue la query
    if sql_validation == "valid":
        results: Tuple[List[str], List[Tuple]] = cm.execute_query(query)
        columns: List[str] = results[0]
        data: List[Tuple[str, str, str]] = results[1]
        print("Columns from DB:", columns, flush=True)
        print("Data from DB:", data, flush=True)

        search_response: SearchResponse = SearchResponse(
            sql=query,
            sql_validation=sql_validation,
            results= [
                SearchResult(
                    item_type="film",
                    properties=[
                        Property(property_name="name" if columns[i] == "titolo" else columns[i],
                                 property_value=str(row[i]))
                        for i in range(len(columns))
                    ]    
                )
                for row in data
                ]
            )
        return search_response
    
    # se la query è "unsafe"
    elif sql_validation == "unsafe":
        search_response: SearchResponse = SearchResponse(sql=query, sql_validation=sql_validation, results=None)
        return search_response
    # se la query è "invalid"
    elif sql_validation == "invalid":
        search_response: SearchResponse = SearchResponse(sql=query, sql_validation=sql_validation, results=None)
        return search_response
    else:
        raise HTTPException(status_code=422, detail="Unknown error. Please check your SQL syntax.")
    
# ---------------------------------------------------------- ENDPOINT /sql_search ---------------------------------------------------

@app.post("/sql_search")
def sql_search(search_request: SQLSearchRequest) -> SQLSearchResponse:
    """
    Questo metodo prende in input una stringa che rappresenta una query SQL e la passa alla classe ConnectionManager per eseguire la query sul database.
    Se la query è valida, viene eseguita sul database e restituisce i risultati.
    Se la query è "unsafe" o "invalid", lo segnala.
    """
    if not search_request.sql_query:
        raise HTTPException(status_code=422, detail="'sql_query' is a necessary field.")
    
    query: str = search_request.sql_query
    
    
    cm: ConnectionManager = ConnectionManager()
    query = cm.clean_sql_output(query)
    print(f"Cleaned query: {query}", flush=True)
   
    sql_validation: str = cm.sql_validation(query)
    print(f"SQL Validation: {sql_validation}", flush=True)

    # se la query è "valid" allora si esegue la query
    if sql_validation == "valid":
        results: Tuple[List[str], List[Tuple]] = cm.execute_query(query)
        columns: List[str] = results[0]
        data: List[Tuple[str, str, str]] = results[1]
        print("Columns from DB:", columns, flush=True)
        print("Data from DB:", data, flush=True)

        search_response: SQLSearchResponse = SQLSearchResponse(
            sql_validation=sql_validation,
            results= [SearchResult(
                    item_type="film",
                    properties=[
                        Property(property_name="name" if columns[i] == "titolo" else columns[i],
                                 property_value=str(row[i]))
                        for i in range(len(columns))
                    ]    
                )
                for row in data
                ]
            )
        return search_response
    
     # se la query è "unsafe"
    elif sql_validation == "unsafe":
        search_response: SQLSearchResponse = SQLSearchResponse(sql_validation=sql_validation, results=None)
        print(f"Response unsafe: {search_response}", flush=True)
        return search_response
    # se la query è "invalid"
    elif sql_validation == "invalid":
        search_response: SQLSearchResponse = SQLSearchResponse(sql_validation=sql_validation, results=None)
        print(f"Response invalid: {search_response}", flush=True)
        return search_response
    else:
        raise HTTPException(status_code=422, detail="Unknown error. Please check your SQL syntax.")


# ---------------------------------------------------------- ENDPOINT /schema_summary ---------------------------------------------------

@app.get("/schema_summary") 
def schema_summary() -> List[DatabaseSchemaResponse]:
    """
    Questo metodo richima il metodo appropriato della classe ConnectionManager per eseguire la query sul database.
    In output restituisce lo schema del database, ovvero i nomi delle tabelle e le colonne di ogni tabella.
    """
    cm: ConnectionManager = ConnectionManager()

    try:
        results: List[Tuple[str, str]] = cm.query_schema_summary()
        schema_summary: List[DatabaseSchemaResponse] = [
            DatabaseSchemaResponse(table_name=row[0], table_column=row[1]) for row in results
        ]
        return schema_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schema summary: {e}")


#---------------------------------------------------------- ENDPOINT /add ---------------------------------------------------


@app.post("/add")
def add(add_request: AddRequest) -> AddResponse:
    """
    Questo metodo si aspetta una stringa in input con il formato: Titolo*,Regista*,Età_autore*,Anno*,Genere*,Piattaforma1,Piataforma2 (* = obbligatorio)
    Verifica se l'input è corretto con l'espressione regolare.
    Se l'input è corretto, chiama il metodo appropriato della classe ConnectionManager per eseguire la query sul database.
    Restituisce un oggetto AddResponse con lo status "ok" se la query è andata a buon fine.
    Se l'input non è come se l'aspetta, lancia un'eccezione 422 con un messaggio di errore.
    """
    data_line: str = add_request.data_line
    print(f"Dataline:", data_line, flush=True)

    cm: ConnectionManager = ConnectionManager()

    # Verifica se l'input è corretto con l'espressione regolare
    pattern: str = r'^([^,]+),([^,]+),(\d{1,3}),(\d{4}),([^,]+),([^,]*),([^,]*)$'
    match: Match[str] = re.fullmatch(pattern, data_line)

    if match:
        split_data: List[str] = data_line.split(",")
        print("Split data:", split_data, flush=True)

        title: str = split_data[0]
        director: str = split_data[1]
        age: int = int(split_data[2])
        year: int = int(split_data[3])
        genre: str = split_data[4]
        platform1: str = split_data[5] if split_data[5] != "" else None
        platform2: str = split_data[6] if split_data[6] != "" else None
        print(f"Title: {title}, Director: {director}, Age: {age}, Year: {year}, Genre: {genre}, Platform1: {platform1}, Platform2: {platform2}", flush=True)

        
        id_director: int = cm.get_or_create_director(director, age)
        print(f"ID Director: {id_director}", flush=True)
        id_platform1: int = cm.get_or_create_platform(platform1) if platform1 else None
        print(f"ID Platform1: {id_platform1}", flush=True)
        id_platform2: int = cm.get_or_create_platform(platform2) if platform2 else None
        print(f"ID Platform2: {id_platform2}", flush=True)

        id_movie: int = cm.get_or_create_movie(title, year, genre, id_director, id_platform1, id_platform2) 
        print(f"ID Movie: {id_movie}")
    

        return AddResponse(status="ok")

    else:
        raise HTTPException(
            status_code=422,
            detail="Invalid input format. Expected format: 'Title,Director,Age,Year,Genre,Platform1,Platform2'"
        )

