from pydantic import BaseModel
from typing import List, Optional

"""
Questo file contiene i modelli di dati utilizzati nell'applicazione FastAPI.
I modelli sono definiti utilizzando Pydantic, che fornisce una validazione dei dati e una serializzazione automatica in JSON.
"""

# ---------------------------------------------------------- MODELLI ENDPOINT /search ---------------------------------------------------

class Property(BaseModel):
    property_name: str
    property_value: str

class SearchResult(BaseModel):
    item_type: str
    properties: List[Property]

class SearchRequest(BaseModel):
    question: str
    model: str

class SearchResponse(BaseModel):
    sql: str
    sql_validation: str
    results: Optional[List[SearchResult]]
  

# ---------------------------------------------------------- MODELLI ENDPOINT /sql_search ---------------------------------------------------

class SQLSearchRequest(BaseModel):
    sql_query: str
    model: Optional[str] = None

class SQLSearchResponse(BaseModel):
    sql_validation: str
    results: Optional[List[SearchResult]]

# ---------------------------------------------------------- MODELLI ENDPOINT /schema_summary ---------------------------------------------------

class DatabaseSchemaResponse(BaseModel):
    table_name: str
    table_column: str

# ---------------------------------------------------------- MODELLI ENDPOINT /add ---------------------------------------------------

class AddRequest(BaseModel):
    data_line: str

class AddResponse(BaseModel):
    status: str

# ---------------------------------------------------------- MODELLI PER OLLAMA ---------------------------------------------------

class Question(BaseModel):
    role: str
    content: str

class ModelPullRequest(BaseModel):
    model: str

class ModelRequest(BaseModel):
    model: str
    messages: List[Question]
    stream: bool

class ModelResponse(BaseModel):
    model: str
    created_at: str
    message: Question
    done_reason: str
    done: bool
    total_duration: int
    load_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int