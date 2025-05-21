import csv
import mariadb
import os
import time

# Configurazione connessione a MariaDB
db_config = {
    "user": os.getenv("MARIADB_USER", "root"),
    "password": os.getenv("MARIADB_PASSWORD", "MySQL"),
    "host": os.getenv("MARIADB_HOST", "localhost"),
    "port": int(os.getenv("MARIADB_PORT", "3306")),
    "database": os.getenv("MARIADB_DB", "movie_catalog")
}

# Prova a connettersi al database
def connect_db(retries=10, delay=3):
    for i in range(retries):
        try:
            conn = mariadb.connect(**db_config)
            return conn
        except mariadb.Error as e:
            print(f"Tentativo {i+1}/{retries}: Errore di connessione a MariaDB: {e}")
            time.sleep(delay)
    return None
    
def get_or_create_director(cursor, name, age):
    # Sto dando per scontato che il nome riconosca il regista, e che l'età sia un campo che può cambiare
    cursor.execute("SELECT id, nome, eta FROM directors WHERE nome = ?", [name])
    director = cursor.fetchone()
    # Se il regista esiste, controlla se l'età è cambiata, e restituisci l'ID
    if director:
        # Se l'età è cambiata, aggiornala
        if director[2] < age:
            cursor.execute("UPDATE directors SET eta = ? WHERE id = ?", [age, director[0]])
        return director[0]
    # Se il regista non esiste, crealo e restituisci l'ID
    else:
        cursor.execute("INSERT INTO directors (nome, eta) VALUES (?, ?)", [name, age])
        return cursor.lastrowid
    
def get_or_create_platform(cursor, name):
    # Sto dando per scontato che il nome riconosca la piattaforma
    cursor.execute("SELECT id FROM platforms WHERE nome = ?", [name])
    platform = cursor.fetchone()
    # Se la piattaforma esiste, restituisci l'ID
    if platform:
        return platform[0]
    # Se la piattaforma non esiste, creala e restituisci l'ID
    else:
        cursor.execute("INSERT INTO platforms (nome) VALUES (?)", [name])
        return cursor.lastrowid
    
def get_or_create_movie(cursor, title, year, genre, id_director, id_platform1, id_platform2):
    # Sto dando per scontato che il titolo riconosca il film, e che l'anno, il genere, il regista e le piattaforme siano campi che possono cambiare
    cursor.execute("SELECT id, titolo, anno, genere, id_director, id_platform1, id_platform2 FROM movies WHERE titolo = ?", [title])
    movie = cursor.fetchone()
    # Se il film esiste, controlla se l'anno, il genere, il regista o le piattaforme sono cambiati e restituisci l'ID
    if movie:
        # Verifica se l'anno è cambiato
        if movie[2] != year:
            cursor.execute("UPDATE movies SET anno = ? WHERE id = ?", [year, movie[0]])
        # Verifica se il genere è cambiato
        if movie[3] != genre:
            cursor.execute("UPDATE movies SET genere = ? WHERE id = ?", [genre, movie[0]])
        # Verifica se il regista è cambiato
        if movie[4] != id_director:
            cursor.execute("UPDATE movies SET id_director = ? WHERE id = ?", [id_director, movie[0]])
        # Verifica se le piattaforma 1 è cambiata
        if movie[5] != id_platform1:
            cursor.execute("UPDATE movies SET id_platform1 = ? WHERE id = ?", [id_platform1, movie[0]])
        # Verifica se le piattaforma 2 è cambiata
        if movie[6] != id_platform2:
            cursor.execute("UPDATE movies SET id_platform2 = ? WHERE id = ?", [id_platform2, movie[0]])
        return movie[0]
    # Se il film non esiste, crealo e restituisci l'ID
    else:
        cursor.execute("INSERT INTO movies (titolo, anno, genere, id_director, id_platform1, id_platform2) VALUES (?, ?, ?, ?, ?, ?)",
                       [title, year, genre, id_director, id_platform1, id_platform2])
        return cursor.lastrowid
    
def main():
    file = "data.tsv"

    conn = connect_db()
    cursor = conn.cursor()

    try:
        with open(file, 'r', encoding='utf-8') as tsvfile:
            reader = csv.reader(tsvfile, delimiter='\t')
            next(reader) # Salta l'intestazione
            for row in reader:
                print(row, flush=True)
                title = row[0].strip()
                director = row[1].strip()
                director_age = int(row[2].strip())
                year = int(row[3].strip())
                genre = row[4].strip()
                platform1 = row[5].strip()
                platform2 = row[6].strip() if len(row) > 6 else None

                id_director = get_or_create_director(cursor, director, director_age)
                id_platform1 = get_or_create_platform(cursor, platform1)
                id_platform2 = get_or_create_platform(cursor, platform2) if platform2 else None

                get_or_create_movie(cursor, title, year, genre, id_director, id_platform1, id_platform2)

        conn.commit()
        print("Dati caricati con successo!")
    
    except Exception as e:
        print(f"Error: {e}")
        print("Rollback delle modifiche.")
        conn.rollback()

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()

