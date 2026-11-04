import os

from dotenv import load_dotenv

load_dotenv(".env")


class Config:
    DOCUMENTS_DIR = "resumes"
    COLLECTION_NAME = "CVs"
    PERSISTENT_DIR = "data/chromadb"

    # Provider degli embedding: "openai", "local" oppure "ollama"
    EMBEDDING_PROVIDER = "local"

    # "text-embedding-3-small" per OpenAI, "nomic-embed-text" per Ollama
    MODEL_NAME = "all-mpnet-base-v2"
    MODEL_PATH = "modelli/mio_modello"
    OPENAI_EMBEDDINGS_KEY = os.environ.get("OPENAI_API_KEY", "")

    LLM_MODEL = "llama3.2"
    LLM_MODEL_LOW = "llama3.2"
    AI_API_URL = "http://localhost:11434/v1"
    AI_API_KEY = "ollama"

    # OpenAI
    # LLM_MODEL = "gpt-4o"
    # LLM_MODEL_LOW = "gpt-4o-mini"
    # AI_API_URL = "https://api.openai.com/v1/"
    # AI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
