from fastapi import FastAPI, HTTPException
from typing import List, Tuple
from connection_manager import ConnectionManager
from models import Property,SQLSearchRequest,SearchResponse, DatabaseSchemaResponse, AddRequest, AddResponse,SearchRequest
import re
from re import Match

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

# ---------------------------------------------------------- ENDPOINT /search ---------------------------------------------------
#BASE_MODEL="gemma3:1b-it-qat"
@app.post("/search")
def search(search_request: SearchRequest) -> List[SearchResponse]:
    if not search_request.question or not search_request.model:
        raise HTTPException(status_code=400, detail="Both 'question' and 'model' fields are required.")
    
    #implementazione di un sistema textToSql
    #sql = textToSql( )


    #Dobbiamo permettere solo richieste SELECT
    #first_word = sql.split(" ")[0]
    #if first_word != "SELECT":
    #   raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
    
    #dopo la select sql_validation è per forza valid
    #invalid se non è stato possibile eseguirlo con succeso
    pass


def sql_validation(sql:str)->(str,Optional[List[Any]]):
    first_word= sql.split(" ").strip()
    if first_word != "SELECT":
        pass

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



@app.get("/search/{search_request}")   
def search(search_request: str) -> List[SearchResponse]:
    """
    Questo metodo si aspetta delle stringhe esatte ossia:
    Elenca i film del <ANNO>.
    Quali sono i registi presenti su Netflix?
    Elenca tutti i film di fantascienza.
    Quali film sono stati fatti da un regista di almeno <ANNI> anni?
    Quali registi hanno fatto più di un film?

    Fa il parsing di <ANNO> e <ANNI> e fa il controllo che siano numeri interi, <ANNO> con 4 cifre e <ANNI> con 1-3 cifre.
    Il parsing delle stringhe è fatto con le espressioni regolari.
    Se l'input è corretto, chiama il metodo appropriato della classe ConnectionManager per eseguire la query sul database.
    Restituisce una lista di oggetti SearchResponse, che contengono le proprietà dei film o dei registi trovati.
    Se l'input non è come se l'aspetta, lancia un'eccezione 422 con un messaggio di errore.
    """
    query: str = search_request
    print("Query:", query, flush=True)
    cm: ConnectionManager = ConnectionManager()

    # Caso query 1 Elenca i film del <ANNO>.
    match: Match[str] = re.fullmatch(r"Elenca i film del (\d{4})\.", query)
    if match:
        year: int = int(match.group(1))
        try:
            results: Tuple[List[str], List[Tuple[str, str, str]]] = cm.query_list_movies_by_year(year)
            columns: List[str] = results[0]
            data: List[Tuple[str, str, str]] = results[1]
            print("Columns from DB:", columns, flush=True)
            print("Data from DB:", data, flush=True)
            search_response: List[SearchResponse] = [
                SearchResponse(
                    item_type="film",
                    properties=[
                        Property(property_name=columns[i], property_value=str(row[i]))
                        for i in range(len(columns))
                    ]
                ) for row in data
            ]
            return search_response
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching movies by year: {e}")
        
    # Caso query 2 Quali sono i registi presenti su Netflix?
    elif query == "Quali sono i registi presenti su Netflix?":
        try:
            results: Tuple[List[str], List[Tuple[str, str, str]]] = cm.query_list_directors_by_platform()
            columns: List[str] = results[0]
            data: List[Tuple[str, str, str]] = results[1]
            print("Columns from DB:", columns, flush=True)
            print("Data from DB:", data, flush=True)
            search_response: List[SearchResponse] = [
                SearchResponse(
                    item_type="director",
                    properties=[
                        Property(property_name=columns[i], property_value=str(row[i]))
                        for i in range(len(columns))
                    ]
                ) for row in data
            ]
            return search_response
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching directors: {e}")
        
    # Caso query 3 Elenca tutti i film di fantascienza.
    elif query == "Elenca tutti i film di fantascienza.":
        try:
            results: Tuple[List[str], List[Tuple[str, str, str]]] = cm.query_list_movies_by_genre()
            columns: List[str] = results[0]
            data: List[Tuple[str, str, str, str]] = results[1]
            print("Columns from DB:", columns, flush=True)
            print("Data from DB:", data, flush=True)
            search_response: List[SearchResponse] = [
                SearchResponse(
                    item_type="film",
                    properties=[
                        Property(property_name=columns[i], property_value=str(row[i]))
                        for i in range(len(columns))
                    ]
                ) for row in data
            ]
            return search_response
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching directors: {e}")
        
    # Caso query 4 Quali film sono stati fatti da un regista di almeno <ANNI> anni?
    match: Match[str] = re.fullmatch(r"Quali film sono stati fatti da un regista di almeno (\d{1,3}) anni\?", query)
    if match:
        age: int = int(match.group(1))
        print("Age:", age)
        try:
            results: Tuple[List[str], List[Tuple[str, str, str]]] = cm.query_list_movies_by_director_age(age)
            columns: List[str] = results[0]
            data: List[Tuple[str, str, str]] = results[1]
            print("Columns from DB:", columns, flush=True)
            print("Data from DB:", data, flush=True)
            search_response: List[SearchResponse] = [
                SearchResponse(
                    item_type="film",
                    properties=[
                        Property(property_name=columns[i], property_value=str(row[i]))
                        for i in range(len(columns))
                    ]
                ) for row in data
            ]
            return search_response
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching movies by year: {e}")
        
    # Caso query 5 Quali registi hanno fatto più di un film?
    elif query == "Quali registi hanno fatto più di un film?":
        try:
            results: Tuple[List[str], List[Tuple[str, str, str]]] = cm.query_list_directors_with_films()
            columns: List[str] = results[0]
            data: List[Tuple[str, str, str]] = results[1]
            print("Columns from DB:", columns, flush=True)
            print("Data from DB:", data, flush=True)
            search_response: List[SearchResponse] = [
                SearchResponse(
                    item_type="director",
                    properties=[
                        Property(property_name=columns[i], property_value=str(row[i]))
                        for i in range(len(columns))
                    ]
                ) for row in data
            ]
            return search_response
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching directors: {e}")

    else:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid query format. Expected one of this format: {search_queries}"
        )

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

