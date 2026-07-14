import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Asistente Virtual Intranet Canal Capital"

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    VECTORSTORE_DIR: str = os.path.join(BASE_DIR, "vectorstore")

    INDEX_FILE: str = os.path.join(VECTORSTORE_DIR, "index.faiss")
    CHUNKS_FILE: str = os.path.join(VECTORSTORE_DIR, "chunks.pkl")

    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    OLLAMA_URL: str = "http://127.0.0.1:11434/api/generate"
    OLLAMA_MODEL: str = "llama3.2:latest"

    TOP_K: int = 1
    MAX_CONTEXT_CHARS: int = 1200

    USE_OLLAMA: bool = False
    MIN_SIMILARITY_SCORE: float = 0.60


settings = Settings()
