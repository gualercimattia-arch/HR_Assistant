import os

import ollama
from chromadb.api.types import EmbeddingFunction
from chromadb.utils import embedding_functions
from config import Config
from sentence_transformers import SentenceTransformer


class CustomEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        self.provider = Config.EMBEDDING_PROVIDER
        self.model_name = Config.MODEL_NAME
        self.model_path = Config.MODEL_PATH

        if self.provider == "openai":
            self._setup_openai()
        elif self.provider == "local":
            self._setup_local_model()
        elif self.provider == "ollama":
            self._setup_ollama()
        else:
            raise ValueError(f"EMBEDDING_PROVIDER '{self.provider}' non supportato")

    def _setup_openai(self):
        print(f"Uso OpenAI Embeddings: {self.model_name}")
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=Config.OPENAI_EMBEDDINGS_KEY, model_name=self.model_name
        )

    def _setup_local_model(self):
        if os.path.exists(self.model_path):
            print(f"Modello locale '{self.model_name}' trovato, caricamento in corso")
            self.embedding_function = SentenceTransformer(self.model_path)
        else:
            print(f"Scaricamento di '{self.model_name}' in corso")
            self.embedding_function = SentenceTransformer(self.model_name)
            self.embedding_function.save(self.model_path)
            print(f"Modello salvato in '{self.model_path}'")

    def _setup_ollama(self):
        print(f"Uso modello Ollama: {self.model_name}")

    def __call__(self, input):
        if self.provider == "openai":
            return self.embedding_function(input)

        if self.provider == "local":
            return self.embedding_function.encode(input).tolist()

        if self.provider == "ollama":
            return [
                ollama.embeddings(model=self.model_name, prompt=text)["embedding"]
                for text in input
            ]
