# Text2SQL 🧠💬➡️📊

**Text2SQL** è una web app full stack che permette di interrogare un database relazionale utilizzando **domande in linguaggio naturale** o **query SQL dirette**.  
Il progetto integra FastAPI, MariaDB e un modello LLM locale tramite [Ollama](https://ollama.com/), per tradurre automaticamente richieste testuali in query SQL eseguibili.

---

## 🧰 Requisiti

- [Docker](https://www.docker.com/) + [Docker Compose](https://docs.docker.com/compose/)

---

## 🚀 Avvio rapido

1. **Clona il progetto:**

   ```bash
   git clone https://github.com/cocchiema17/Text2SQL-web-app.git
   cd Text2SQL-web-app
   ```

2. **Avvia tutti i servizi con Docker:**
   ```bash
   docker compose up --build
   ```
   ⚠️ Il processo potrebbe richiedere fino a 1-2 minuti al primo avvio.

3. **Apri l'app nel browser all'indirizzo:**
   ```bash
   http://127.0.0.1:8004
   ```
   
🌐 **Funzionalità principali**

🔍 /search – Inserisci una domanda in italiano (es. "Quali film del 2020?"):
→ il backend comunica con Ollama per generare una query SQL, esegue la query e restituisce i risultati.

🧠 /sql_search – Inserisci una query SQL direttamente e visualizza il risultato in formato strutturato.

🧾 /schema_summary – Visualizza la struttura del database (tabelle e colonne).

➕ /add – Inserisci un nuovo film nel database.
