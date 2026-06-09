import os
import sqlite3
import math
from collections import Counter
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.config import settings


DB_FILE = os.path.join(settings.BASE_DIR, "data", "capitalbot_metrics.db")


def init_metrics_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            response_time_ms INTEGER,
            source_type TEXT,
            best_score REAL,
            category TEXT,
            topic TEXT,
            used_ollama INTEGER DEFAULT 0,
            has_error INTEGER DEFAULT 0,
            user_ip TEXT,
            user_agent TEXT
        )
    """)

    cursor.execute("PRAGMA table_info(chat_logs)")
    columns = [column[1] for column in cursor.fetchall()]

    if "conversation_id" not in columns:
        cursor.execute("ALTER TABLE chat_logs ADD COLUMN conversation_id TEXT")

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_chat_logs_conversation_id
        ON chat_logs(conversation_id)
    """)

    conn.commit()
    conn.close()


def save_chat_log(
    conversation_id: Optional[str],
    question: str,
    answer: str,
    response_time_ms: int,
    source_type: str,
    best_score: Optional[float] = None,
    category: Optional[str] = None,
    topic: Optional[str] = None,
    used_ollama: bool = False,
    has_error: bool = False,
    user_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_logs (
            conversation_id,
            created_at,
            question,
            answer,
            response_time_ms,
            source_type,
            best_score,
            category,
            topic,
            used_ollama,
            has_error,
            user_ip,
            user_agent
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        conversation_id,
        datetime.now().isoformat(timespec="seconds"),
        question,
        answer,
        response_time_ms,
        source_type,
        best_score,
        category,
        topic,
        1 if used_ollama else 0,
        1 if has_error else 0,
        user_ip,
        user_agent
    ))

    conn.commit()
    conn.close()


def calculate_percentile(values: List[float], percentile: float) -> float:
    if not values:
        return 0.0

    values = sorted(values)
    k = (len(values) - 1) * (percentile / 100)
    f = math.floor(k)
    c = math.ceil(k)

    if f == c:
        return round(values[int(k)], 2)

    d0 = values[f] * (c - k)
    d1 = values[c] * (k - f)
    return round(d0 + d1, 2)


def classify_browser(user_agent: str) -> str:
    if not user_agent:
        return "Desconocido"

    ua = user_agent.lower()

    if "edg" in ua:
        return "Edge"
    if "chrome" in ua and "edg" not in ua:
        return "Chrome"
    if "firefox" in ua:
        return "Firefox"
    if "safari" in ua and "chrome" not in ua:
        return "Safari"
    if "opera" in ua or "opr/" in ua:
        return "Opera"

    return "Otros"


def get_summary_metrics(
    date_from: str = "",
    date_to: str = ""
) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    where = "WHERE 1 = 1"
    params = []

    if date_from:
        where += " AND DATE(REPLACE(created_at, 'T', ' ')) >= ?"
        params.append(date_from)

    if date_to:
        where += " AND DATE(REPLACE(created_at, 'T', ' ')) <= ?"
        params.append(date_to)

    cursor.execute(f"SELECT COUNT(*) AS total FROM chat_logs {where}", params)
    total = cursor.fetchone()["total"]

    cursor.execute(
        f"""
        SELECT COUNT(*) AS total
        FROM chat_logs
        {where}
        AND source_type IN ('json_direct', 'quick_answer')
        """,
        params
    )
    direct_total = cursor.fetchone()["total"]

    cursor.execute(
        f"""
        SELECT COUNT(*) AS total
        FROM chat_logs
        {where}
        AND used_ollama = 1
        """,
        params
    )
    ollama_total = cursor.fetchone()["total"]

    cursor.execute(
        f"""
        SELECT COUNT(*) AS total
        FROM chat_logs
        {where}
        AND source_type = 'no_match'
        """,
        params
    )
    no_match_total = cursor.fetchone()["total"]

    cursor.execute(
        f"""
        SELECT COUNT(*) AS total
        FROM chat_logs
        {where}
        AND has_error = 1
        """,
        params
    )
    errors_total = cursor.fetchone()["total"]

    cursor.execute(
        f"""
        SELECT COUNT(DISTINCT user_ip) AS total
        FROM chat_logs
        {where}
        AND user_ip IS NOT NULL
        AND user_ip != ''
        """,
        params
    )
    unique_users = cursor.fetchone()["total"]

    cursor.execute(
        f"""
        SELECT COUNT(DISTINCT conversation_id) AS total
        FROM chat_logs
        {where}
        AND conversation_id IS NOT NULL
        AND conversation_id != ''
        """,
        params
    )
    total_conversations = cursor.fetchone()["total"]

    cursor.execute(
        f"""
        SELECT response_time_ms
        FROM chat_logs
        {where}
        AND response_time_ms IS NOT NULL
        ORDER BY response_time_ms
        """,
        params
    )
    times = [row["response_time_ms"] for row in cursor.fetchall()]
    avg_time = round(sum(times) / len(times), 2) if times else 0
    p95_time = calculate_percentile(times, 95)

    cursor.execute(
        f"""
        SELECT question, COUNT(*) AS total
        FROM chat_logs
        {where}
        GROUP BY LOWER(question)
        ORDER BY total DESC
        LIMIT 10
        """,
        params
    )
    top_questions = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        f"""
        SELECT topic, COUNT(*) AS total
        FROM chat_logs
        {where}
        AND topic IS NOT NULL
        AND topic != ''
        GROUP BY topic
        ORDER BY total DESC
        LIMIT 10
        """,
        params
    )
    top_topics = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        f"""
        SELECT category, COUNT(*) AS total
        FROM chat_logs
        {where}
        AND category IS NOT NULL
        AND category != ''
        GROUP BY category
        ORDER BY total DESC
        LIMIT 10
        """,
        params
    )
    top_categories = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        f"""
        SELECT DATE(REPLACE(created_at, 'T', ' ')) AS date, COUNT(*) AS total
        FROM chat_logs
        {where}
        GROUP BY DATE(REPLACE(created_at, 'T', ' '))
        ORDER BY date ASC
        """,
        params
    )
    daily_usage = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        f"""
        SELECT strftime('%H', REPLACE(created_at, 'T', ' ')) AS hour, COUNT(*) AS total
        FROM chat_logs
        {where}
        GROUP BY strftime('%H', REPLACE(created_at, 'T', ' '))
        ORDER BY hour ASC
        """,
        params
    )
    hourly_usage = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        f"""
        SELECT source_type, COUNT(*) AS total
        FROM chat_logs
        {where}
        GROUP BY source_type
        ORDER BY total DESC
        """,
        params
    )
    source_distribution = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        f"""
        SELECT user_ip, COUNT(*) AS total
        FROM chat_logs
        {where}
        AND user_ip IS NOT NULL
        AND user_ip != ''
        GROUP BY user_ip
        ORDER BY total DESC
        LIMIT 10
        """,
        params
    )
    top_ips = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        f"""
        SELECT created_at, question, response_time_ms, source_type, topic
        FROM chat_logs
        {where}
        AND response_time_ms IS NOT NULL
        ORDER BY response_time_ms DESC
        LIMIT 10
        """,
        params
    )
    slowest_queries = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        f"""
        SELECT user_agent
        FROM chat_logs
        {where}
        AND user_agent IS NOT NULL
        AND user_agent != ''
        """,
        params
    )
    browser_rows = cursor.fetchall()
    browser_counter = Counter(classify_browser(row["user_agent"]) for row in browser_rows)
    top_browsers = [{"browser": k, "total": v} for k, v in browser_counter.most_common(10)]

    conn.close()

    direct_rate = round((direct_total / total) * 100, 2) if total else 0
    error_rate = round((errors_total / total) * 100, 2) if total else 0

    return {
        "total_queries": total,
        "total_conversations": total_conversations,
        "unique_users": unique_users,
        "direct_queries": direct_total,
        "ollama_queries": ollama_total,
        "no_match_queries": no_match_total,
        "error_queries": errors_total,
        "avg_response_time_ms": avg_time,
        "p95_response_time_ms": p95_time,
        "direct_rate_pct": direct_rate,
        "error_rate_pct": error_rate,
        "top_questions": top_questions,
        "top_topics": top_topics,
        "top_categories": top_categories,
        "daily_usage": daily_usage,
        "hourly_usage": hourly_usage,
        "source_distribution": source_distribution,
        "top_ips": top_ips,
        "top_browsers": top_browsers,
        "slowest_queries": slowest_queries
    }


def get_all_logs(
    search: str = "",
    conversation_id: str = "",
    source_type: str = "",
    date_from: str = "",
    date_to: str = ""
) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT *
        FROM chat_logs
        WHERE 1 = 1
    """

    params = []

    if search:
        query += """
            AND (
                LOWER(question) LIKE ?
                OR LOWER(answer) LIKE ?
                OR LOWER(topic) LIKE ?
                OR LOWER(category) LIKE ?
            )
        """
        value = f"%{search.lower()}%"
        params.extend([value, value, value, value])

    if conversation_id:
        query += " AND conversation_id LIKE ?"
        params.append(f"%{conversation_id}%")

    if source_type:
        query += " AND source_type = ?"
        params.append(source_type)

    if date_from:
        query += " AND DATE(REPLACE(created_at, 'T', ' ')) >= ?"
        params.append(date_from)

    if date_to:
        query += " AND DATE(REPLACE(created_at, 'T', ' ')) <= ?"
        params.append(date_to)

    query += " ORDER BY created_at DESC LIMIT 5000"

    cursor.execute(query, params)

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return rows