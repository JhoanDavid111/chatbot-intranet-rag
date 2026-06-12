import os
import time
import csv
import io

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.rag import RAGService
from app.metrics import (
    init_metrics_db,
    save_chat_log,
    get_summary_metrics,
    get_all_logs
)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://intranet.canalcapital.gov.co",
        "http://intranet.canalcapital.gov.co",
        "http://192.168.0.14:8000",
        "http://192.168.0.14"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Inicializa la base de datos de métricas
init_metrics_db()

# Inicializa el servicio RAG
rag_service = RAGService()


from typing import Optional

class QuestionRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None


@app.get("/")
def home():
    index_path = os.path.join(STATIC_DIR, "index.html")
    return FileResponse(index_path)


@app.post("/ask")
def ask_question(request_data: QuestionRequest, request: Request):
    start_time = time.time()

    result = rag_service.ask(request_data.question)

    response_time_ms = int((time.time() - start_time) * 1000)

    metrics = result.get("metrics", {})

    save_chat_log(
        conversation_id=request_data.conversation_id,
        question=request_data.question,
        answer=result.get("answer", ""),
        response_time_ms=response_time_ms,
        source_type=metrics.get("source_type", "unknown"),
        best_score=metrics.get("best_score"),
        category=metrics.get("category"),
        topic=metrics.get("topic"),
        used_ollama=metrics.get("used_ollama", False),
        has_error=metrics.get("has_error", False),
        user_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    # No enviamos las métricas internas al frontend del usuario final
    result.pop("metrics", None)

    return result


@app.get("/admin")
def admin_panel():
    admin_path = os.path.join(STATIC_DIR, "admin.html")
    return FileResponse(admin_path)


@app.get("/admin/metrics")
def admin_metrics(
    date_from: str = "",
    date_to: str = ""
):
    return get_summary_metrics(
        date_from=date_from,
        date_to=date_to
    )


@app.get("/admin/logs")
def admin_logs(
    search: str = "",
    conversation_id: str = "",
    source_type: str = "",
    date_from: str = "",
    date_to: str = ""
):
    return get_all_logs(
        search=search,
        conversation_id=conversation_id,
        source_type=source_type,
        date_from=date_from,
        date_to=date_to
    )


@app.get("/admin/reports/chatlogs.csv")
def download_chatlogs_csv(
    search: str = "",
    conversation_id: str = "",
    source_type: str = "",
    date_from: str = "",
    date_to: str = ""
):
    logs = get_all_logs(
        search=search,
        conversation_id=conversation_id,
        source_type=source_type,
        date_from=date_from,
        date_to=date_to
    )

    output = io.StringIO()

    # BOM para que Excel abra correctamente tildes y caracteres especiales
    output.write("\ufeff")

    fieldnames = [
        "ID",
        "ID Conversación",
        "Fecha y hora",
        "Pregunta",
        "Respuesta",
        "Tiempo de respuesta (ms)",
        "Origen de respuesta",
        "Score",
        "Categoría",
        "Tema",
        "Usó IA generativa",
        "Presentó error",
        "IP usuario",
        "Navegador / User Agent"
    ]

    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        delimiter=";",
        quoting=csv.QUOTE_ALL
    )

    writer.writeheader()

    def format_source_type(value):
        if value in ["quick_answer", "json_direct"]:
            return "Respuesta rápida"
        if value in ["generative_ai", "ollama"]:
            return "IA generativa"
        if value == "no_match":
            return "Sin coincidencia"
        if value == "unknown" or not value:
            return "No clasificado"
        return value

    def yes_no(value):
        return "Sí" if value in [1, True, "1", "true", "True"] else "No"

    for row in logs:
        writer.writerow({
            "ID": row.get("id", ""),
            "ID Conversación": row.get("conversation_id", ""),
            "Fecha y hora": row.get("created_at", ""),
            "Pregunta": row.get("question", ""),
            "Respuesta": row.get("answer", ""),
            "Tiempo de respuesta (ms)": row.get("response_time_ms", ""),
            "Origen de respuesta": format_source_type(row.get("source_type")),
            "Score": row.get("best_score", ""),
            "Categoría": row.get("category", ""),
            "Tema": row.get("topic", ""),
            "Usó IA generativa": yes_no(row.get("used_ollama")),
            "Presentó error": yes_no(row.get("has_error")),
            "IP usuario": row.get("user_ip", ""),
            "Navegador / User Agent": row.get("user_agent", "")
        })

    output.seek(0)

    filename = "reporte_capi_interacciones.csv"

    return StreamingResponse(
        output,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )