import requests
from models import Question, ModelRequest, ModelResponse, ModelPullRequest
from typing import List, Tuple

"""
Questo file contiene la classe ModelController che gestisce l'interazione con il modello di intelligenza artificiale.
La classe consente di caricare un modello specifico e di inviare domande al modello per ottenere risposte in formato SQL.
"""

class ModelController:
    def __init__(self, api_url: str):
        self.api_url: str = api_url
        self.model: str = "gemma3:1b-it-qat"  # Default model
        self.is_model_loaded: bool = False 

    def pull_model(self) -> bool:
        """
        Questa funzione invia una richiesta al server per caricare il modello specificato.
        Restituisce True se il modello è stato caricato con successo, altrimenti False.
        """
        print(f"Pulling model {self.model} from {self.api_url}", flush=True)
        try:
            response = requests.post(f"{self.api_url}/api/pull", json=ModelPullRequest(model=self.model).model_dump())
            response.raise_for_status()
            if response.status_code == 200:
                self.is_model_loaded = True
                print(f"Model {self.model} pulled successfully", flush=True)
                return True
            else:
                print(f"Failed to pull model {self.model}: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Pull failed: {e}")
            return False

    def ask_question(self, question: str, schema_summary: List[Tuple[str, str]]) -> str:
        """
        Questa funzione invia una domanda al modello e restituisce la risposta in formato SQL.
        Prende in input una domanda in linguaggio naturale e lo schema del database.
        Prepara una richiesta al modello per far si che quest'ultimo generi una query SQL.
        Restituisce la query SQL generata dal modello.
        """
        print(f"Received question from backend: {question}", flush=True)
        print(f"Schema summary: {schema_summary}", flush=True)

        schema_summary_str = "\n".join([f"{table_name}: {columns}" for table_name, columns in schema_summary])
        print(f"Schema summary string: {schema_summary_str}", flush=True)

        final_question: str = (
            "Sei un assistente che trasforma domande in linguaggio naturale in query SQL valide per un database relazionale.\n\n"
            "Schema del database:\n"
            f"{schema_summary_str}\n\n"
            "Relazioni:\n"
            "id_directors è chiave esterna da directors(id)\n"
            "id_platform1 è chiave esterna da platform(id)\n"
            "id_platform2 è chiave esterna da platform(id)\n\n"
            f"Domanda: {question}\n\n"
            "Genera **solo** la query SQL, **senza spiegazioni, testo aggiuntivo o formattazione extra**."
        )

        model_request: ModelRequest = ModelRequest(
            model=self.model,
            messages=[
                Question(role="user", content=final_question)
            ],
            stream=False
        )
        print(f"Model request: {model_request}", flush=True)

        try:
            response = requests.post(f"{self.api_url}/api/chat", json=model_request.model_dump())
            response.raise_for_status()

            model_response: ModelResponse = ModelResponse(**response.json())
            print(f"Model response: {model_response}", flush=True)

            if not model_response.done:
                print("Model response not done yet")
                return ""

            answer:str = model_response.message.content
            return answer
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return ""
