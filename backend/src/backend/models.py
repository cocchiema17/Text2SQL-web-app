from pydantic import BaseModel
from typing import List

"""
Questo file contiene i modelli di dati utilizzati nell'applicazione FastAPI.
I modelli sono definiti utilizzando Pydantic, che fornisce una validazione dei dati e una serializzazione automatica in JSON.
"""

class Property(BaseModel):
    property_name: str
    property_value: str

class SearchRequest(BaseModel):
    question:str
    model:str

class SearchResponse(BaseModel):
    sql:str
    sql_validation:str
    results:List[Property]
    #Campi dell'esonero
    #item_type: str
    #properties: List[Property]

class DatabaseSchemaResponse(BaseModel):
    table_name: str
    table_column: str

class AddRequest(BaseModel):
    data_line: str

class AddResponse(BaseModel):
    status: str