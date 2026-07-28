import os
import pickle
from typing import List, Dict, Any

import faiss
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.groq_client import call_groq


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
                "score": score,
                "source": chunk.get("source"),
                "page": chunk.get("page"),
                "text": chunk.get("text"),
                "full_text": chunk.get("full_text", chunk.get("text")),
                "categoria": chunk.get("categoria"),
                "tema": chunk.get("tema")
            })

        return results

    def build_conversation_context(
        self,
        conversation_history: List[Dict[str, Any]]
        ) -> str:
        if not conversation_history:
            return "No hay mensajes previos en esta conversación."

        lines = []

        for item in conversation_history:
            previous_question = str(item.get("question", "")).strip()
            previous_answer = str(item.get("answer", "")).strip()

            if previous_question:
                lines.append(f"Usuario: {previous_question}")

            if previous_answer:
                # Limita cada respuesta previa para no hacer demasiado pesado el prompt.
                lines.append(f"Capi: {previous_answer[:1200]}")

        return "\n".join(lines)

    def enrich_question_with_context(
        self,
        question: str,
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        if not conversation_history:
            return question

        normalized_question = question.strip().lower()

        # Temas explícitos: indican que el usuario inició o cambió de asunto.
        explicit_topic_markers = [
            "sala",
            "salas",
            "sicc",
            "erpc",
            "recursos humanos",
            "denuncia",
            "denuncias",
            "falla",
            "fallas",
            "soporte",
            "tic",
            "vacaciones",
            "certificado",
            "nómina",
            "nomina",
            "contraseña",
            "contrasena",
            "correo",
            "intranet",
        ]

        # Preguntas que normalmente dependen del tema inmediatamente anterior.
        follow_up_markers = [
            "y cómo",
            "y como",
            "cómo ingreso",
            "como ingreso",
            "dónde ingreso",
            "donde ingreso",
            "y dónde",
            "y donde",
            "y eso",
            "y cuál",
            "y cual",
            "cuál es",
            "cual es",
            "me explicas",
            "explícame",
            "explicame",
            "puedo hacerlo",
            "cómo lo hago",
            "como lo hago",
            "qué necesito",
            "que necesito",
            "para qué sirve",
            "para que sirve",
            "dónde lo hago",
            "donde lo hago",
            "cómo funciona",
            "como funciona",
            "qué debo hacer",
            "que debo hacer",
        ]

        # Si menciona un tema concreto, se trata como una pregunta nueva.
        has_explicit_topic = any(
            marker in normalized_question
            for marker in explicit_topic_markers
        )

        # Solo se usa el historial cuando hay una señal clara de seguimiento
        # y no se identifica un tema nuevo.
        is_follow_up = (
            not has_explicit_topic
            and any(
                marker in normalized_question
                for marker in follow_up_markers
            )
        )

        if not is_follow_up:
            return question

        last_question = str(
            conversation_history[-1].get("question", "")
        ).strip()

        last_answer = str(
            conversation_history[-1].get("answer", "")
        ).strip()

        return f"""
    Pregunta actual: {question}

    Contexto de la conversación anterior:
    Usuario preguntó: {last_question}
    Capi respondió: {last_answer[:1200]}

    Interpreta la pregunta actual teniendo en cuenta el contexto anterior.
    """.strip()

    def build_prompt(
        self,
        question: str,
        contexts: List[Dict[str, Any]],
        conversation_history: List[Dict[str, Any]] | None = None
        ) -> str:
            conversation_history = conversation_history or []

            context_text = ""

            for i, ctx in enumerate(contexts, start=1):
                block = (
                    f"[Fuente {i}] {ctx['source']} | Página {ctx['page']}\n"
                    f"{ctx['text']}\n\n"
                )
                context_text += block

            context_text = context_text[:settings.MAX_CONTEXT_CHARS]

            conversation_text = self.build_conversation_context(
                conversation_history
            )

            prompt = f"""
        Eres Capi, el asistente virtual institucional de la intranet de Canal Capital.

        Responde de forma breve, clara, cordial e institucional.
        Usa únicamente la información recuperada de la base documental y el historial reciente de conversación cuando sea necesario para comprender la pregunta actual.

        No inventes información, procedimientos, enlaces, responsables ni datos institucionales.
        Si no encuentras la respuesta, indica que no está disponible en la documentación y sugiere contactar a Gestión TIC.
        No menciones documentos internos, embeddings, FAISS, Ollama, modelos de lenguaje ni inteligencia artificial.

        Historial reciente de la conversación:
        {conversation_text}

        Contexto documental recuperado:
        {context_text}

        Pregunta actual:
        {question}

        Instrucciones adicionales:
        - Si la pregunta actual es corta o depende de un tema mencionado antes, utiliza el historial para identificar a qué se refiere.
        - Prioriza siempre la información del contexto documental recuperado.
        - Si el historial y el contexto documental no son suficientes, solicita al usuario que reformule su pregunta o contacte a Gestión TIC.

        Respuesta:
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

    def normalize_question_text(self, text: str) -> str:
        replacements = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "ü": "u",
            "ñ": "n"
        }

        normalized = text.lower().strip()

        for original, replacement in replacements.items():
            normalized = normalized.replace(original, replacement)

        return normalized


    def canonicalize_known_question(self, question: str) -> str:
        normalized = self.normalize_question_text(question)

        # SICC - Definición
        if "sicc" in normalized and (
            "que es" in normalized
            or "para que sirve" in normalized
            or "significa" in normalized
            or normalized.strip() in ["sicc", "el sicc"]
        ):
            return (
                "¿Qué es el SICC? ¿Para qué sirve el SICC? "
                "Sistema de Información Canal Capital ambiente de producción gestión documental"
            )

        # SICC - Acceso
        if "sicc" in normalized and (
            "ingreso" in normalized
            or "ingresar" in normalized
            or "entro" in normalized
            or "entrar" in normalized
            or "acceso" in normalized
            or "link" in normalized
            or "enlace" in normalized
            or "usuario" in normalized
            or "contrasena" in normalized
            or "password" in normalized
            or "captcha" in normalized
        ):
            return (
                "¿Cómo ingreso al SICC? enlace SICC usuario contraseña captcha "
                "ambiente de producción Gestión TIC"
            )

        # ERPC - Definición
        if "erpc" in normalized and (
            "que es" in normalized
            or "para que sirve" in normalized
            or "significa" in normalized
            or normalized.strip() in ["erpc", "el erpc"]
        ):
            return (
                "¿Qué es el ERPC? ¿Para qué sirve el ERPC? "
                "entorno de pruebas del SICC ambiente de pruebas software espejo validación"
            )

        # ERPC - Acceso
        if "erpc" in normalized and (
            "ingreso" in normalized
            or "ingresar" in normalized
            or "entro" in normalized
            or "entrar" in normalized
            or "acceso" in normalized
            or "link" in normalized
            or "enlace" in normalized
            or "usuario" in normalized
            or "contrasena" in normalized
            or "password" in normalized
            or "captcha" in normalized
        ):
            return (
                "¿Cómo ingreso al ERPC? enlace ERPC usuario contraseña captcha "
                "ambiente de pruebas Gestión TIC"
            )

        # Salas
        if "sala" in normalized or "salas" in normalized:
            return (
                "¿Cómo solicito una sala? ¿Dónde solicito una sala? "
                "reserva de sala formulario fecha hora propósito reunión"
            )

        # Denuncias
        if "denuncia" in normalized or "denuncias" in normalized:
            return (
                "¿Cómo registro una denuncia pública? Denuncias Públicas formulario "
                "tipo de denuncia evidencias acoso laboral confidencialidad"
            )

        # Recursos Humanos
        if (
            "recursos humanos" in normalized
            or "rrhh" in normalized
            or "rr. hh" in normalized
            or "talento humano" in normalized
        ):
            return (
                "¿Qué contiene Recursos Humanos? bienestar SST inscripción inducción "
                "publicaciones talento humano"
            )

        # Soporte TIC
        if (
            "soporte" in normalized
            or "falla" in normalized
            or "fallas" in normalized
            or "tic" in normalized
            or "mesa de servicios" in normalized
        ):
            return (
                "¿Dónde reporto fallas? soporte TIC mesa de servicios Gestión TIC "
                "correo institucional"
            )

        return question        

    def ask(
        self,
        question: str,
        conversation_history: List[Dict[str, Any]] | None = None
    ) -> Dict[str, Any]:

        conversation_history = conversation_history or []

        canonical_question = self.canonicalize_known_question(question)

        search_question = self.enrich_question_with_context(
            question=canonical_question,
            conversation_history=conversation_history
        )

        contexts = self.retrieve(search_question)

        fallback_answer = (
            "Lo siento, no logro entender tu consulta con la información disponible. "
            "Puedo ayudarte con los siguientes temas:"
        )

        if not contexts:
            return {
                "answer": fallback_answer,
                "source_type": "no_match",
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

        normalized_question = question.lower().strip()

        explicit_topic_keywords = [
            "sicc",
            "erpc",
            "sala",
            "salas",
            "denuncia",
            "denuncias",
            "recursos humanos",
            "rr. hh",
            "rrhh",
            "soporte",
            "tic",
            "intranet"
        ]

        has_explicit_topic = any(
            keyword in normalized_question
            for keyword in explicit_topic_keywords
        )

        required_score = 0.25 if has_explicit_topic else settings.MIN_SIMILARITY_SCORE

        # SI EL SCORE ES BAJO, NO RESPONDE DESDE EL ÍNDICE
        if best_score < required_score:
            conversation_context = self.build_conversation_context(conversation_history)

            groq_answer = call_groq(
                question=question,
                conversation_context=conversation_context
            )

            if groq_answer and len(groq_answer.strip()) >= 20:
                return {
                    "answer": groq_answer,
                    "source_type": "generative_ai",
                    "sources": [],
                    "metrics": {
                        "source_type": "generative_ai",
                        "best_score": best_score,
                        "category": best_context.get("categoria"),
                        "topic": best_context.get("tema"),
                        "used_ollama": False,
                        "used_groq": True,
                        "has_error": False
                    }
                }

            return {
                "answer": fallback_answer,
                "source_type": "no_match",
                "sources": [],
                "metrics": {
                    "source_type": "no_match",
                    "best_score": best_score,
                    "category": best_context.get("categoria"),
                    "topic": best_context.get("tema"),
                    "used_ollama": False,
                    "used_groq": False,
                    "has_error": False
                }
            }

        # RESPUESTA RÁPIDA DESDE JSON / FAISS
        answer_source_text = best_context.get("full_text") or best_context.get("text", "")
        answer = self.extract_direct_answer(answer_source_text)

        # Protección contra respuestas basura o fragmentos demasiado cortos
        if not answer or len(answer.strip()) < 20:
            return {
                "answer": fallback_answer,
                "source_type": "no_match",
                "sources": [],
                "metrics": {
                    "source_type": "no_match",
                    "best_score": best_score,
                    "category": best_context.get("categoria"),
                    "topic": best_context.get("tema"),
                    "used_ollama": False,
                    "has_error": False
                }
            }

        return {
            "answer": answer,
            "source_type": "quick_answer",
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
