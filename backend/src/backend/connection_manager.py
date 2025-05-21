import mariadb
import os
from typing import List, Tuple
import re
import sqlparse

"""
Questo file contiene la classe ConnectionManager, che gestisce la connessione ed esegue le query al database all'interno di MariaDB.
"""

class ConnectionManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self) -> None:
        """
        Questo metodo stabilisce una connessione al database 'movie_catalog' all'interno di MariaDB utilizzando le credenziali fornite.
        """
        try:
            self.connection = mariadb.connect(
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "MySQL"),
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", 3306)),
                database=os.getenv("DB_NAME", "movie_catalog")
            )
            self.cursor = self.connection.cursor()
            print("Database connection established.", flush=True)
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            raise

    def close(self) -> None:
        """
        Questo metodo chiude la connessione al database e il cursore.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Database connection closed.", flush=True)

# ---------------------------------------------------------- QUERY ENDPOINT /search e /sql_search ---------------------------------------------------

    def clean_sql_output(self, response: str) -> str:
        # Rimuove eventuali blocchi di testo prima/dopo la query
        statements = sqlparse.split(response.strip())
        return statements[0].strip() if statements else ""
    
    
    def sql_validation(self, sql_query: str) -> str:
        """
        Questo metodo esegue una query per validare la sintassi SQL.
        Restituisce: "valid" se la sintassi è corretta, 
                    "unsafe" se contiene comandi di modifica (da evitare),
                    "invalid" se la sintassi è errata.
        """
        self.connect()
        if self.connection and self.cursor:
            #  una regex per controllare se la query inizia con SELECT, ignorando spazi e commenti.
            if re.match(r'^\s*select\b', sql_query, re.IGNORECASE):
                try:
                    # Eseguiamo la query per validare la sintassi SQL
                    self.cursor.execute(sql_query)
                    return "valid"
                except mariadb.Error as e:
                    # Se la sintassi è errata, restituiamo "invalid"
                    print(f"Error executing query: {e}")
                    return "invalid"
                finally:
                    self.close()
            else:
                # Se la query non è una SELECT, restituiamo "unsafe"
                self.close()
                return "unsafe"

            
    def execute_query(self, sql_query: str) -> Tuple[List[str], List[Tuple]]:
        """
        Questo metodo esegue una query SQL e restituisce i risultati e i nomi delle colonne.
        """
        self.connect()
        if self.connection and self.cursor:
            try:
                self.cursor.execute(sql_query)
                columns: List[str] = [description[0] for description in self.cursor.description]
                print("Intestazione della query:", columns, flush=True)
                results: List[Tuple] = self.cursor.fetchall()
                self.connection.commit()
                return (columns, results)
            except mariadb.Error as e:
                self.connection.rollback()
                print(f"Error executing query: {e}")
                raise
            finally:
                self.close()
        else:
            print("Connection not established. Cannot execute query.")
            raise Exception("Connection not established.")


# ---------------------------------------------------------- QUERY ENDPOINT /schema_summary ---------------------------------------------------

    def query_schema_summary(self) -> List[Tuple[str, str]]:
        """
        Questo metodo esegue una query per ottenere un riepilogo dello schema del database.
        Restituisce una lista di tuple contenenti il nome della tabella e il nome della colonna.
        """
        self.connect()
        if self.connection and self.cursor:
            try:
                query = "SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'movie_catalog'"
                self.cursor.execute(query)
                results = self.cursor.fetchall()
                self.connection.commit()
                return results
            except mariadb.Error as e:
                self.connection.rollback()
                print(f"Error executing query: {e}")
                raise
            finally:
                self.close()
        else:
            print("Connection not established. Cannot execute query.")
            raise Exception("Connection not established.")
        
# ---------------------------------------------------------- QUERY ENDPOINT /add ---------------------------------------------------
        
    def get_or_create_director(self, name: str, age: int) -> int:
        """
        Questo metodo esegue una query per ottenere un regista in base al nome fornito.
        Se il regista esiste, restituisce l'ID del regista.
        Se il regista non esiste, lo crea e restituisce l'ID del nuovo regista.
        """
        self.connect()
        if self.connection and self.cursor:
            try:
                self.cursor.execute("SELECT id, nome, eta FROM directors WHERE nome = ?", [name])
                director = self.cursor.fetchone()
                if director:
                    # Se l'età è cambiata, la aggiorna
                    if director[2] < age:
                        self.cursor.execute("UPDATE directors SET eta = ? WHERE id = ?", [age, director[0]])
                        self.connection.commit()
                    return director[0]
                else:
                    self.cursor.execute("INSERT INTO directors (nome, eta) VALUES (?, ?)", [name, age])
                    self.connection.commit()
                    return self.cursor.lastrowid
            except mariadb.Error as e:
                self.connection.rollback()
                print(f"Error executing query: {e}")
                raise
            finally:
                self.close()
        else:
            print("Connection not established. Cannot execute query.")
            raise Exception("Connection not established.")
        
    def get_or_create_platform(self, name: str) -> int:
        """
        Questo metodo esegue una query per ottenere una piattaforma in base al nome fornito.
        Se la piattaforma esiste, restituisce l'ID della piattaforma.
        Se la piattaforma non esiste, la crea e restituisce l'ID della nuova piattaforma.
        """
        self.connect()
        if self.connection and self.cursor:
            try:
                self.cursor.execute("SELECT id FROM platforms WHERE nome = ?", [name])
                platform = self.cursor.fetchone()
                if platform:
                    return platform[0]
                else:
                    self.cursor.execute("INSERT INTO platforms (nome) VALUES (?)", [name])
                    self.connection.commit()
                    return self.cursor.lastrowid
            except mariadb.Error as e:
                self.connection.rollback()
                print(f"Error executing query: {e}")
                raise
            finally:
                self.close()
        else:
            print("Connection not established. Cannot execute query.")
            raise Exception("Connection not established.")
        
    def get_or_create_movie(self, title: str, year: int, genre: str, id_director: int, id_platform1: int = None, id_platform2: int = None) -> int:
        """
        Questo metodo esegue una query per ottenere un film in base al titolo fornito.
        Se il film esiste, restituisce l'ID del film.
        Se il film non esiste, lo crea e restituisce l'ID del nuovo film."""
        self.connect()
        if self.connection and self.cursor:
            try:
                self.cursor.execute("SELECT id, titolo, anno, genere, id_director, id_platform1, id_platform2 FROM movies WHERE titolo = ?", [title])
                movie = self.cursor.fetchone()
                # Se il film esiste, controlla se l'anno, il genere, il regista o le piattaforme sono cambiati e restituisci l'ID
                if movie:
                    # Verifica se l'anno è cambiato
                    if movie[2] != year:
                        self.cursor.execute("UPDATE movies SET anno = ? WHERE id = ?", [year, movie[0]])
                    # Verifica se il genere è cambiato
                    if movie[3] != genre:
                        self.cursor.execute("UPDATE movies SET genere = ? WHERE id = ?", [genre, movie[0]])
                    # Verifica se il regista è cambiato
                    if movie[4] != id_director:
                        self.cursor.execute("UPDATE movies SET id_director = ? WHERE id = ?", [id_director, movie[0]])
                    # Verifica se le piattaforma 1 è cambiata
                    if movie[5] != id_platform1:
                        self.cursor.execute("UPDATE movies SET id_platform1 = ? WHERE id = ?", [id_platform1, movie[0]])
                    # Verifica se le piattaforma 2 è cambiata
                    if movie[6] != id_platform2:
                        self.cursor.execute("UPDATE movies SET id_platform2 = ? WHERE id = ?", [id_platform2, movie[0]])
                    self.connection.commit()
                    return movie[0]
                else:
                    self.cursor.execute("INSERT INTO movies (titolo, anno, genere, id_director, id_platform1, id_platform2) VALUES (?, ?, ?, ?, ?, ?)",
                                       [title, year, genre, id_director, id_platform1, id_platform2])
                    self.connection.commit()
                    return self.cursor.lastrowid
            except mariadb.Error as e:
                self.connection.rollback()
                print(f"Error executing query: {e}")
                raise
            finally:
                self.close()
        else:
            print("Connection not established. Cannot execute query.")
            raise Exception("Connection not established.")
