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

La chiave OpenAI nel file `.env` serve solo se si usa OpenAI. Con la configurazione predefinita tutto gira in locale: Ollama deve essere attivo con il modello `llama3.2` (`ollama pull llama3.2`).

## Modelli intercambiabili

In `hr_assistant/config.py`:

| `EMBEDDING_PROVIDER` | `MODEL_NAME` | Note |
|---|---|---|
| `local` | `paraphrase-multilingual-mpnet-base-v2` | SentenceTransformer multilingua, adatto ai testi in italiano, scaricato al primo avvio in `modelli/` |
| `ollama` | `nomic-embed-text` | richiede `ollama pull nomic-embed-text` |
| `openai` | `text-embedding-3-small` | richiede la chiave in `.env` |

Per usare OpenAI anche per le risposte, sostituire `LLM_MODEL`, `LLM_MODEL_LOW`, `AI_API_URL` e `AI_API_KEY` con i valori nel commento.

## Struttura

- `hr_assistant/config.py`: configurazione (cartelle, nomi dei modelli, chiavi lette da `.env`).
- `hr_assistant/document_processor.py`: lettura di documenti di diverso formato e sincronizzazione con il database.
- `hr_assistant/semantic_chunking.py`: divisione del testo in frammenti in base al significato.
- `hr_assistant/custom_embedding.py`: embedding con OpenAI, SentenceTransformer oppure Ollama.
- `hr_assistant/database.py`: collection ChromaDB persistente in `data/chromadb`.
- `hr_assistant/utils.py`: chiamate al modello di linguaggio (nome del candidato, prompt, risposta in streaming).
- `hr_assistant/__init__.py`: applicazione Chainlit.

## Come funziona

1. I curriculum in `resumes/` vengono convertiti in testo e divisi in frammenti con il chunking semantico.
2. Ogni frammento viene trasformato in embedding e salvato in ChromaDB su disco, insieme a hash MD5 e data di modifica del file.
3. Alla domanda dell'utente, ChromaDB restituisce il paragrafo più simile e il file da cui proviene.
4. Le prime righe di quel file, che contengono i dati del candidato, vengono aggiunte al contesto: così basta una sola chiamata al modello.
5. La risposta arriva in streaming nella chat e termina con i contatti del candidato e il nome del file.

## Formati supportati

I file vengono convertiti in testo con [MarkItDown](https://github.com/microsoft/markitdown): `.txt`, `.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx`, `.html`, `.htm`, `.csv`, `.json`, `.xml` e `.zip` (vengono letti i file supportati contenuti nell'archivio).

## Chunking semantico

Il testo non viene più tagliato con un separatore fisso:

1. viene diviso in frasi;
2. ogni frase viene unita alle tre precedenti e alle tre successive, per darle contesto;
3. si calcola l'embedding di ogni gruppo e la distanza coseno tra gruppi consecutivi;
4. dove la distanza supera il 65° percentile il significato cambia, e lì inizia un nuovo frammento.

Se si cambia modello di embedding o tecnica di chunking bisogna cancellare `data/chromadb`: i vettori già salvati non sono compatibili e i file non cambiati non verrebbero rielaborati.

## Sincronizzazione dei documenti

A ogni avvio i file in `resumes/` vengono confrontati con quelli tracciati nel database tramite l'hash MD5 del contenuto:

- **file nuovi**: vengono divisi in paragrafi e aggiunti;
- **file modificati** (hash diverso): i vecchi paragrafi vengono rimossi e sostituiti con quelli nuovi;
- **file eliminati**: i loro paragrafi vengono rimossi dal database.

Così vengono elaborati solo i file cambiati e si evitano i duplicati.

## Pulsanti della chat

All'apertura della chat sono disponibili tre pulsanti:

- **Statistiche Database**: descrive collezione, numero di frammenti e numero di file indicizzati.
- **Reindex Database**: rilancia la sincronizzazione senza riavviare l'applicazione, utile dopo aver aggiunto o modificato un curriculum.
- **Svuota completamente il Database**: elimina i frammenti indicizzati, non i file in `resumes/`. Con **Reindex Database** si ricrea tutto.

## Caricamento di file dalla chat

Uno o più file allegati a un messaggio vengono salvati in `resumes/` e indicizzati subito, se il formato è supportato. Un file con lo stesso nome sostituisce quello già presente. Se il messaggio contiene anche una domanda, l'assistente risponde dopo il caricamento.

## Intenzione dell'utente

Prima di rispondere, il modello classifica la domanda:

- **`search_cv`**: l'utente cerca un candidato, quindi si interroga il database e il curriculum trovato resta in memoria nella sessione;
- **`info_cv`**: l'utente chiede altro sul candidato già trovato (per esempio la sua email), quindi si riusa quel curriculum senza una nuova ricerca.

## Personalizzazione grafica

- `public/theme.json`: colori del tema chiaro e scuro (`theme2.json` e `theme3.json` sono varianti: per usarne una, copiarla su `theme.json`).
- `public/app.css`: CSS personalizzato, collegato in `.chainlit/config.toml`.
- `public/logo_light.png`, `public/logo_dark.png`, `public/favicon.png`: logo e icona.
- `public/avatars/`: un'immagine per ogni autore dei messaggi, con il nome di `author`: `hr_assistant` per le risposte, `system_assistant` per i messaggi di sistema.

## Avvio

```powershell
poetry run chainlit run hr_assistant/__init__.py -w
```

L'applicazione si apre su http://localhost:8000.
