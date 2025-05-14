import mariadb
import os
from typing import List, Tuple

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
            print("Database connection established.")
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
            print("Database connection closed.")

# ---------------------------------------------------------- QUERY ENDPOINT /search ---------------------------------------------------

    def query_list_movies_by_year(self, year: int) -> Tuple[List[str], List[Tuple[str, str, str]]]:
        """
        Questo metodo esegue una query per ottenere un elenco di film in base all'anno fornito.
        Restituisce una tupla contenente l'intestazione della query e i risultati.
        """
        self.connect()
        if self.connection and self.cursor:
            try:
                query: str = "SELECT id, title as name, year FROM movies WHERE year = ?"
                self.cursor.execute(query, [year])
                # Ciclo per ottenere l'intestazione della query
                columns: List[str] = [description[0] for description in self.cursor.description]
                print("Intestazione della query:", columns)
                results: List[Tuple[str, str, str]] = self.cursor.fetchall()
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
        
    def query_list_directors_by_platform(self, platform: str = 'Netflix') -> Tuple[List[str], List[Tuple[str, str, str]]]:
        """
        Questo metodo esegue una query per ottenere un elenco di registi in base alla piattaforma fornita, 'Netflix' di default.
        Restituisce una tupla contenente l'intestazione della query e i risultati.
        """
        self.connect()
        if self.connection and self.cursor:
            try:
                query: str = """
                SELECT DISTINCT d.id, d.name, p.name 
                FROM movies m JOIN directors d ON m.id_director = d.id JOIN platforms p ON p.id IN (m.id_platform1, m.id_platform2)
                WHERE p.name = ?
                """
                self.cursor.execute(query, [platform])
                columns: List[str] = [description[0] for description in self.cursor.description]
                print("Intestazione della query:", columns)
                results: List[Tuple[str, str, str]] = self.cursor.fetchall()
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
        
    def query_list_movies_by_genre(self, genre: str = 'Fantascienza') -> Tuple[List[str], List[Tuple[str, str, str, str]]]:
        """
        Questo metodo esegue una query per ottenere un elenco di film in base al genere fornito, 'Fantascienza' di default.
        Restituisce una tupla contenente l'intestazione della query e i risultati.
        """
        self.connect()
        if self.connection and self.cursor:
            try:
                query: str = """
                SELECT DISTINCT id, title as name, year, genre
                FROM movies
                WHERE genre = ?
                """
                self.cursor.execute(query, [genre])
                columns: List[str] = [description[0] for description in self.cursor.description]
                print("Intestazione della query:", columns)
                results: List[Tuple[str, str, str, str]] = self.cursor.fetchall()
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
        
    def query_list_movies_by_director_age(self, age: int) -> Tuple[List[str], List[Tuple[str, str, str]]]:
        """
        Questo metodo esegue una query per ottenere un elenco di film in base all'età del regista fornita.
        Restituisce una tupla contenente l'intestazione della query e i risultati.
        """
        self.connect()
        if self.connection and self.cursor:
            try:
                query: str = """
                SELECT DISTINCT m.title as name, d.name, d.age
                FROM movies m JOIN directors d ON m.id_director = d.id
                WHERE d.age >= ?
                """
                self.cursor.execute(query, [age])
                columns: List[str] = [description[0] for description in self.cursor.description]
                print("Intestazione della query:", columns)
                results: List[Tuple[str, str, str]] = self.cursor.fetchall()
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
        
    def query_list_directors_with_films(self) -> Tuple[List[str], List[Tuple[str, str, str]]]:
        """
        Questo metodo esegue una query per ottenere un elenco di registi con più di un film.
        Restituisce una tupla contenente l'intestazione della query e i risultati.
        """
        self.connect()
        if self.connection and self.cursor:
            try:
                query: str = """
                SELECT d.id, d.name, COUNT(*) num_movies
                FROM movies m JOIN directors d ON m.id_director = d.id
                GROUP BY d.id, d.name
                HAVING COUNT(*) > 1
                """
                self.cursor.execute(query)
                columns: List[str] = [description[0] for description in self.cursor.description]
                print("Intestazione della query:", columns)
                results: List[Tuple[str, str, str]] = self.cursor.fetchall()
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
                self.cursor.execute("SELECT id, name, age FROM directors WHERE name = ?", [name])
                director = self.cursor.fetchone()
                if director:
                    # Se l'età è cambiata, la aggiorna
                    if director[2] < age:
                        self.cursor.execute("UPDATE directors SET age = ? WHERE id = ?", [age, director[0]])
                        self.connection.commit()
                    return director[0]
                else:
                    self.cursor.execute("INSERT INTO directors (name, age) VALUES (?, ?)", [name, age])
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
                self.cursor.execute("SELECT id FROM platforms WHERE name = ?", [name])
                platform = self.cursor.fetchone()
                if platform:
                    return platform[0]
                else:
                    self.cursor.execute("INSERT INTO platforms (name) VALUES (?)", [name])
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
                self.cursor.execute("SELECT id, title, year, genre, id_director, id_platform1, id_platform2 FROM movies WHERE title = ?", [title])
                movie = self.cursor.fetchone()
                # Se il film esiste, controlla se l'anno, il genere, il regista o le piattaforme sono cambiati e restituisci l'ID
                if movie:
                    # Verifica se l'anno è cambiato
                    if movie[2] != year:
                        self.cursor.execute("UPDATE movies SET year = ? WHERE id = ?", [year, movie[0]])
                    # Verifica se il genere è cambiato
                    if movie[3] != genre:
                        self.cursor.execute("UPDATE movies SET genre = ? WHERE id = ?", [genre, movie[0]])
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
                    self.cursor.execute("INSERT INTO movies (title, year, genre, id_director, id_platform1, id_platform2) VALUES (?, ?, ?, ?, ?, ?)",
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
