from fastapi import FastAPI, HTTPException
from typing import List, Tuple
from connection_manager import ConnectionManager
from models import *
import re
from re import Match
import os
from model_controller import ModelController

"""
Questo file contiene il codice del server backend FastAPI che gestisce le richieste HTTP e l''interazione con il database attraverso la 
classe ConnectionManager.
Questi sono gli endpoint principali:
1. /search/{search_request}: per cercare film o registi in base a una query specifica.
2. /schema_summary: per ottenere lo schema del database, ovvero i nomi delle tabelle e le colonne di ogni tabella.
3. /add: per aggiungere un nuovo film al database.
"""

app = FastAPI()
# questa lista serve per il mesaggio di errore quando la search non è valida
search_queries: List[str] = [
    "Elenca i film del <ANNO>.",
    "Quali sono i registi presenti su Netflix?",
    "Elenca tutti i film di fantascienza.",
    "Quali film sono stati fatti da un regista di almeno <ANNI> anni?",
    "Quali registi hanno fatto più di un film?"
]

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")

mc: ModelController = ModelController(OLLAMA_API_URL)
# All'inizio del server, il modello viene caricato
mc.pull_model()

# ---------------------------------------------------------- ENDPOINT /search ---------------------------------------------------
@app.post("/search")
def search(search_request: SearchRequest) -> SearchResponse:
    if not search_request.question or not search_request.model:
        raise HTTPException(status_code=400, detail="Both 'question' and 'model' fields are required.")
    
    cm: ConnectionManager = ConnectionManager()
    schema_summary: List[Tuple[str, str]] = cm.query_schema_summary()

    question: str = search_request.question
    query: str = mc.ask_question(question, schema_summary)
    print(f"Query by model: {query}", flush=True)
    query = cm.clean_query(query)
    print(f"Cleaned query: {query}", flush=True)

    # Verifica se la query è valida
    # fare metodo che prende in input una stringa (una query) e controlla se è "valid", "unsafe" o "invalid" all'interno della classe ConnectionManager
    sql_validation: str = cm.sql_validation(query)

    # se la query è "valid" allora si esegue la query
    # fare metodo che esegue la query e restituisce i risultati
    if sql_validation == "valid":
        results: Tuple[List[str], List[Tuple]] = cm.execute_query(query)
        columns: List[str] = results[0]
        data: List[Tuple[str, str, str]] = results[1]
        print("Columns from DB:", columns, flush=True)
        print("Data from DB:", data, flush=True)

    # fare metodo che restituisce il tipo di oggetto (film, regista o piattaforma) in base alla query
    # item_type: str = cm.get_item_type(query) 

        search_response: SearchResponse = SearchResponse(
            sql=query,
            sql_validation=sql_validation,
            results= [
                SearchResult(
                    item_type="film",   # o "director" o "platform" (da modificare)
                    properties=[
                        Property(property_name=columns[i], property_value=str(row[i]))
                        for i in range(len(columns))
                    ]    
                )
                for row in data
                ]
            )
        return search_response
    
    # se la query è "unsafe" allora si restituisce un errore
    elif sql_validation == "unsafe":
        search_response: SearchResponse = SearchResponse(sql=query, sql_validation=sql_validation, results=None)
        return search_response
    # se la query è "invalid" allora si restituisce un errore
    elif sql_validation == "invalid":
        search_response: SearchResponse = SearchResponse(sql=query, sql_validation=sql_validation, results=None)
        return search_response
    else:
        raise HTTPException(status_code=422, detail="Unknown error. Please check your SQL syntax.")
    
# ---------------------------------------------------------- ENDPOINT /sql_search ---------------------------------------------------

@app.post("/sql_search")
def sql_search(search_request: SQLSearchRequest):
    ##traduzione question to sql
    sql = search_request.sql_query.strip()
    
    #Verifica query valida
    sql_validation,results = sql_validation(sql)

    #mia soluzione
    first_word = sql.split(" ")[0]
    if first_word != "SELECT":
        sql_validation="unsafe"
        return sql_validation,results


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

