import os

from dotenv import load_dotenv

load_dotenv(".env")


class Config:
    DOCUMENTS_DIR = "resumes"
    COLLECTION_NAME = "CVs"
    PERSISTENT_DIR = "data/chromadb"

    MODEL_NAME = "text-embedding-3-small"
    OPENAI_KEY = os.environ["OPENAI_API_KEY"]

    # Ollama in locale
    # LLM_MODEL = "llama3.2"
    # AI_API_URL = "http://localhost:11434/v1"
    # AI_API_KEY = "ollama"

    LLM_MODEL = "gpt-4o-mini"
    AI_API_URL = "https://api.openai.com/v1/"
    AI_API_KEY = os.environ["OPENAI_API_KEY"]
