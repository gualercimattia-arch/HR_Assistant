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

Il nome del candidato e la risposta vengono generati in locale con Ollama, quindi deve essere attivo con il modello `llama3.2`:

```powershell
ollama pull llama3.2
```

## Come funziona

1. I curriculum in `resumes/` (solo file `.txt`) vengono divisi in paragrafi usando `### ` come separatore.
2. Ogni paragrafo viene trasformato in embedding e salvato in una collection ChromaDB in memoria.
3. Alla domanda dell'utente, ChromaDB restituisce il paragrafo più simile e il file da cui proviene.
4. Dalle prime righe di quel file `llama3.2` estrae nome e cognome del candidato.
5. Paragrafo, nome del file e nome del candidato vengono inseriti nel prompt e la risposta arriva in streaming nella chat.

## Avvio

```powershell
poetry run chainlit run hr_assistant/__init__.py -w
```

L'applicazione si apre su http://localhost:8000.
