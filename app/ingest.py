import os
import json
import pickle
from typing import List, Dict, Any

import faiss
from sentence_transformers import SentenceTransformer

from app.config import settings


def split_text(text: str, chunk_size: int = 900, overlap: int = 120) -> List[str]:
    text = text.replace("\n", " ").strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def load_knowledge_json(json_path: str) -> List[Dict[str, Any]]:
    chunks = []

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"No se encontró la base de conocimiento: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    for item in items:
        categoria = item.get("categoria", "")
        tema = item.get("tema", "")
        preguntas = item.get("preguntas", [])
        respuesta = item.get("respuesta", "")
        fuente = item.get("fuente", "Base de conocimiento Intranet")
        pagina = item.get("pagina", 1)
        palabras_clave = item.get("palabras_clave", [])

        text = f"""
Categoría: {categoria}
Tema: {tema}
Preguntas relacionadas: {' | '.join(preguntas)}
Palabras clave: {' | '.join(palabras_clave)}
Respuesta institucional: {respuesta}
""".strip()

        text_chunks = split_text(text)

        for chunk in text_chunks:
            chunks.append({
                "source": fuente,
                "page": pagina,
                "text": chunk,
                "categoria": categoria,
                "tema": tema
            })

    return chunks


def build_vectorstore(chunks: List[Dict[str, Any]]) -> None:
    if not chunks:
        raise ValueError("No hay información para indexar.")

    os.makedirs(settings.VECTORSTORE_DIR, exist_ok=True)

    print("Cargando modelo de embeddings...")
    embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

    texts = [chunk["text"] for chunk in chunks]

    print(f"Generando embeddings para {len(texts)} fragmentos...")
    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    ).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    faiss.write_index(index, settings.INDEX_FILE)

    with open(settings.CHUNKS_FILE, "wb") as f:
        pickle.dump(chunks, f)

    print("Base vectorial generada correctamente.")
    print(f"Índice FAISS: {settings.INDEX_FILE}")
    print(f"Chunks: {settings.CHUNKS_FILE}")


def main():
    knowledge_file = os.path.join(settings.DATA_DIR, "base_conocimiento_intranet.json")

    print("Procesando base de conocimiento JSON...")
    chunks = load_knowledge_json(knowledge_file)

    print(f"Total de fragmentos generados: {len(chunks)}")

    build_vectorstore(chunks)


if __name__ == "__main__":
    main()