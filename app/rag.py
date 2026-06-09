import os
import pickle
from typing import List, Dict, Any

import faiss
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

from app.config import settings


class RAGService:
    def __init__(self):
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.index = None
        self.chunks = []
        self.load_vectorstore()

    def load_vectorstore(self):
        if not os.path.exists(settings.INDEX_FILE) or not os.path.exists(settings.CHUNKS_FILE):
            raise FileNotFoundError(
                "No existe el índice vectorial. Ejecuta primero: python app/ingest.py"
            )

        self.index = faiss.read_index(settings.INDEX_FILE)

        with open(settings.CHUNKS_FILE, "rb") as f:
            self.chunks = pickle.load(f)

    def extract_direct_answer(self, text: str) -> str:
        marker = "Respuesta institucional:"

        if marker in text:
            return text.split(marker, 1)[1].strip()

        marker_alt = "Respuesta:"

        if marker_alt in text:
            return text.split(marker_alt, 1)[1].strip()

        return text.strip()

    def retrieve(self, question: str, top_k: int = None) -> List[Dict[str, Any]]:
        top_k = top_k or settings.TOP_K

        query_embedding = self.embedding_model.encode(
            [question],
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype("float32")

        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            chunk = self.chunks[idx]
            results.append({
                "score": float(score),
                "source": chunk.get("source"),
                "page": chunk.get("page"),
                "text": chunk.get("text"),
                "categoria": chunk.get("categoria"),
                "tema": chunk.get("tema")
            })

        return results

    def build_prompt(self, question: str, contexts: List[Dict[str, Any]]) -> str:
        context_text = ""

        for i, ctx in enumerate(contexts, start=1):
            block = (
                f"[Fuente {i}] {ctx['source']} | Página {ctx['page']}\n"
                f"{ctx['text']}\n\n"
            )
            context_text += block

        context_text = context_text[:settings.MAX_CONTEXT_CHARS]

        prompt = f"""
    Eres el asistente virtual de la intranet de Canal Capital.

    Responde de forma breve, clara e institucional.
    Usa únicamente el contexto documental.
    Si no encuentras la respuesta, indica que no está en la documentación disponible y sugiere contactar a Gestión TIC.
    No inventes información.

    Contexto:
    {context_text}

    Pregunta:
    {question}

    Respuesta breve:
    """
        return prompt.strip()

    def call_ollama(self, prompt: str) -> str:
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.8,
                "num_predict": 100,
                "num_ctx": 1024,
                "repeat_penalty": 1.1
            }
        }

        try:
            response = requests.post(
                settings.OLLAMA_URL,
                json=payload,
                timeout=240
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

        except requests.exceptions.ConnectionError:
            return (
                "No fue posible conectarse con Ollama. "
                "Verifica que Ollama esté instalado y ejecutándose en http://localhost:11434."
            )

        except requests.exceptions.Timeout:
            return (
                "La respuesta del modelo tardó demasiado. "
                "Prueba con un modelo más liviano como phi3 o reduce el contexto documental."
            )

        except Exception as e:
            return f"Ocurrió un error al consultar el modelo local: {str(e)}"

    def ask(self, question: str) -> Dict[str, Any]:
        contexts = self.retrieve(question)

        if not contexts:
            answer = (
                "Por ahora no tengo una respuesta precisa sobre ese tema en mi base de conocimiento. "
                "Puedes reformular la pregunta o consultar con Gestión TIC si se trata de un caso específico."
            )

            return {
                "answer": answer,
                "sources": [],
                "metrics": {
                    "source_type": "no_match",
                    "best_score": None,
                    "category": None,
                    "topic": None,
                    "used_ollama": False,
                    "has_error": False
                }
            }

        best_context = contexts[0]
        best_score = best_context["score"]

        print(f"Mejor score recuperado: {best_score}")

        # RESPUESTA RÁPIDA DESDE JSON
        if best_score >= 0.30:
            answer = self.extract_direct_answer(best_context["text"])

            return {
                "answer": answer,
                "sources": [],
                "metrics": {
                    "source_type": "quick_answer",
                    "best_score": best_score,
                    "category": best_context.get("categoria"),
                    "topic": best_context.get("tema"),
                    "used_ollama": False,
                    "has_error": False
                }
            }

        # IA GENERATIVA / OLLAMA
        prompt = self.build_prompt(question, contexts)
        answer = self.call_ollama(prompt)

        has_error = (
            "No fue posible conectarse con Ollama" in answer
            or "Ocurrió un error" in answer
            or "tardó demasiado" in answer
            or "no pudo procesar" in answer
        )

        return {
            "answer": answer,
            "sources": [],
            "metrics": {
                "source_type": "generative_ai",
                "best_score": best_score,
                "category": best_context.get("categoria"),
                "topic": best_context.get("tema"),
                "used_ollama": True,
                "has_error": has_error
            }
        }
