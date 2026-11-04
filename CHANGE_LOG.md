## 03

- Sync Documenti

## 04

- tasti db info e db reindex

## 05

- Semantic Chunking

## 06

- Refactoring Semantic Chunking

## 06.1 Sentence Transformer

- Uso di modelli di embedding in locale con SentenceTransformer
- Uso di modelli di embedding in locale con ollama
- Refactoring per uso dei vari tipi di modelli in modo intercambiabile

## 06.2 User intent

- Capire se l'utente sta cercando un CV o vuole sapere altre info su un cv già restituito

## 07

- lettura di file di tipo diverso con https://github.com/microsoft/markitdown
- in semantic chunking aggiunta funzione _split_into_sentences per evitare che un file riporti una singola frase

## 08 - Upload file da interfaccia

- possibilita' di aggiungere uno o piu' file in resumes da interfaccia, e all'aggiunta, lanciare l'aggiornamento del database degli embeddings
- nuova action per azzerare il database
