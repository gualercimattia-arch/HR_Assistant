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
- `hr_assistant/document_processor.py`: lettura dei curriculum, divisione in paragrafi e sincronizzazione con il database.
- `hr_assistant/database.py`: collection ChromaDB persistente in `data/chromadb` con embeddings OpenAI.
- `hr_assistant/utils.py`: chiamate al modello di linguaggio (nome del candidato, prompt, risposta in streaming).
- `hr_assistant/__init__.py`: applicazione Chainlit.

## Come funziona

1. I curriculum in `resumes/` (solo file `.txt`) vengono divisi in paragrafi usando `### ` come separatore.
2. Ogni paragrafo viene trasformato in embedding e salvato in ChromaDB su disco, insieme a hash MD5 e data di modifica del file.
3. Alla domanda dell'utente, ChromaDB restituisce il paragrafo più simile e il file da cui proviene.
4. Le prime righe di quel file, che contengono i dati del candidato, vengono aggiunte al contesto: così basta una sola chiamata al modello.
5. La risposta arriva in streaming nella chat e termina con i contatti del candidato e il nome del file.

## Sincronizzazione dei documenti

A ogni avvio i file in `resumes/` vengono confrontati con quelli tracciati nel database tramite l'hash MD5 del contenuto:

- **file nuovi**: vengono divisi in paragrafi e aggiunti;
- **file modificati** (hash diverso): i vecchi paragrafi vengono rimossi e sostituiti con quelli nuovi;
- **file eliminati**: i loro paragrafi vengono rimossi dal database.

Così vengono elaborati solo i file cambiati e si evitano i duplicati.

## Pulsanti della chat

All'apertura della chat sono disponibili due pulsanti:

- **Statistiche Database**: descrive collezione, numero di frammenti e numero di file indicizzati.
- **Reindex Database**: rilancia la sincronizzazione senza riavviare l'applicazione, utile dopo aver aggiunto o modificato un curriculum.

## Avvio

```powershell
poetry run chainlit run hr_assistant/__init__.py -w
```

L'applicazione si apre su http://localhost:8000.
