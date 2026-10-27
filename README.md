# HR Assistant

Assistente HR basato su Chainlit che, a partire da una richiesta, cerca il candidato più adatto tra i curriculum.

## Requisiti

- Python 3.13
- Poetry (https://python-poetry.org/)

## Installazione

```powershell
poetry install
copy .env.example .env
```

Inserire la propria chiave OpenAI nel file `.env`: serve per gli embeddings (`text-embedding-3-small`).

Per usare i modelli in locale con Ollama al posto di `gpt-4o-mini`, in `hr_assistant/config.py` sostituire `LLM_MODEL`, `AI_API_URL` e `AI_API_KEY` con i valori indicati nel commento (serve il modello `llama3.2`: `ollama pull llama3.2`).

## Struttura

- `hr_assistant/config.py`: configurazione (cartelle, nomi dei modelli, chiavi lette da `.env`).
- `hr_assistant/document_processor.py`: lettura dei curriculum e divisione in paragrafi.
- `hr_assistant/database.py`: collection ChromaDB persistente in `data/chromadb` con embeddings OpenAI.
- `hr_assistant/utils.py`: chiamate al modello di linguaggio (nome del candidato, prompt, risposta in streaming).
- `hr_assistant/__init__.py`: applicazione Chainlit.

## Come funziona

1. I curriculum in `resumes/` (solo file `.txt`) vengono divisi in paragrafi usando `### ` come separatore.
2. Ogni paragrafo viene trasformato in embedding e salvato in ChromaDB su disco.
3. Alla domanda dell'utente, ChromaDB restituisce il paragrafo più simile e il file da cui proviene.
4. Dalle prime righe di quel file il modello estrae nome e cognome del candidato.
5. Paragrafo, nome del file e nome del candidato vengono inseriti nel prompt e la risposta arriva in streaming nella chat.

## Avvio

```powershell
poetry run chainlit run hr_assistant/__init__.py -w
```

L'applicazione si apre su http://localhost:8000.
