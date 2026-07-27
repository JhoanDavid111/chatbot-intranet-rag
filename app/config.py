import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "Asistente Virtual Intranet Canal Capital"

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    VECTORSTORE_DIR: str = os.path.join(BASE_DIR, "vectorstore")

    INDEX_FILE: str = os.path.join(VECTORSTORE_DIR, "index.faiss")
    CHUNKS_FILE: str = os.path.join(VECTORSTORE_DIR, "chunks.pkl")

    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # =========================
    # Ollama local
    # =========================
    OLLAMA_URL: str = "http://127.0.0.1:11434/api/generate"
    OLLAMA_MODEL: str = "llama3.2:latest"
    USE_OLLAMA: bool = False

    # =========================
    # GroqCloud API
    # =========================
    USE_GROQ: bool = False
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # =========================
    # RAG / FAISS
    # =========================
    TOP_K: int = 1
    MAX_CONTEXT_CHARS: int = 1200
    MIN_SIMILARITY_SCORE: float = 0.60


settings = Settings()
