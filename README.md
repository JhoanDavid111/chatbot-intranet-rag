# Asistente Virtual RAG - Intranet Canal Capital

Proyecto local en Python para crear un asistente virtual con arquitectura RAG sobre documentos institucionales de la intranet, SICC y ERPC.

## 1. Requisitos

- Python 3.10 o superior
- Ollama instalado
- Modelo local descargado, por ejemplo:

```bash
ollama pull llama3.1
```

También puedes usar:

```bash
ollama pull mistral
ollama pull qwen2.5
```

## 2. Crear entorno virtual

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 4. Ubicar documentos

El manual inicial debe estar en:

```text
data/manual_intranet.pdf
```

Puedes agregar más documentos PDF dentro de la carpeta `data/`.

## 5. Crear índice vectorial

```bash
python app/ingest.py
```

Esto genera:

```text
vectorstore/index.faiss
vectorstore/chunks.pkl
```

## 6. Ejecutar API local

```bash
uvicorn app.main:app --reload
```

La API quedará disponible en:

```text
http://127.0.0.1:8000
```

## 7. Abrir el chat

Abre en el navegador:

```text
http://127.0.0.1:8000
```

## 8. Probar por API

```bash
curl -X POST http://127.0.0.1:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"¿Qué es el SICC?\"}"
```

En Linux/Mac:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"¿Qué es el SICC?"}'
```

## 9. Variables de configuración

Puedes modificar el archivo `app/config.py`.

Variables principales:

- `OLLAMA_MODEL`: modelo local usado por Ollama.
- `TOP_K`: cantidad de fragmentos recuperados.
- `CHUNK_SIZE`: tamaño de fragmentos.
- `CHUNK_OVERLAP`: solapamiento entre fragmentos.

## 10. Producción futura

Para producción en la intranet se recomienda:

- Exponer FastAPI detrás de Nginx o Apache reverse proxy.
- Proteger el endpoint con autenticación institucional.
- Guardar logs de preguntas/respuestas.
- Crear proceso de actualización automática de documentos.
- Migrar FAISS local a Azure AI Search si se requiere escalabilidad.
- Desplegar en Docker, VM institucional, Azure Container Apps o AKS.
