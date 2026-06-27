import sqlite3
import json
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "catalog.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS csv_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            filepath TEXT NOT NULL,
            row_count INTEGER,
            last_modified REAL,
            last_crawled REAL
        );

        CREATE TABLE IF NOT EXISTS csv_columns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL REFERENCES csv_files(id) ON DELETE CASCADE,
            column_name TEXT NOT NULL,
            data_type TEXT NOT NULL,
            sample_values TEXT,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS user_aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alias TEXT NOT NULL,
            file_id INTEGER NOT NULL,
            column_name TEXT NOT NULL,
            UNIQUE(alias)
        );

        CREATE TABLE IF NOT EXISTS query_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cache_key TEXT UNIQUE NOT NULL,
            sql_query TEXT NOT NULL,
            result_json TEXT NOT NULL,
            chart_config TEXT NOT NULL,
            created_at REAL NOT NULL,
            expires_at REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS dashboards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            layout_config TEXT DEFAULT '[]',
            created_at REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS charts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dashboard_id INTEGER REFERENCES dashboards(id) ON DELETE CASCADE,
            nl_query TEXT NOT NULL,
            sql_query TEXT,
            chart_config TEXT,
            conversation_history TEXT DEFAULT '[]',
            created_at REAL NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def upsert_csv_file(filename: str, filepath: str, row_count: int, last_modified: float) -> int:
    import time
    conn = get_conn()
    conn.execute("""
        INSERT INTO csv_files (filename, filepath, row_count, last_modified, last_crawled)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(filename) DO UPDATE SET
            filepath=excluded.filepath,
            row_count=excluded.row_count,
            last_modified=excluded.last_modified,
            last_crawled=excluded.last_crawled
    """, (filename, filepath, row_count, last_modified, time.time()))
    conn.commit()
    row = conn.execute("SELECT id FROM csv_files WHERE filename=?", (filename,)).fetchone()
    file_id = row["id"]
    conn.close()
    return file_id


def replace_columns(file_id: int, columns: list[dict]):
    conn = get_conn()
    conn.execute("DELETE FROM csv_columns WHERE file_id=?", (file_id,))
    for col in columns:
        conn.execute(
            "INSERT INTO csv_columns (file_id, column_name, data_type, sample_values) VALUES (?,?,?,?)",
            (file_id, col["column_name"], col["data_type"], json.dumps(col["sample_values"]))
        )
    conn.commit()
    conn.close()


def get_all_schema() -> list[dict]:
    conn = get_conn()
    files = conn.execute("SELECT * FROM csv_files ORDER BY filename").fetchall()
    result = []
    for f in files:
        cols = conn.execute(
            "SELECT * FROM csv_columns WHERE file_id=? ORDER BY id", (f["id"],)
        ).fetchall()
        result.append({
            "id": f["id"],
            "filename": f["filename"],
            "filepath": f["filepath"],
            "row_count": f["row_count"],
            "columns": [
                {
                    "column_name": c["column_name"],
                    "data_type": c["data_type"],
                    "sample_values": json.loads(c["sample_values"] or "[]"),
                    "description": c["description"],
                }
                for c in cols
            ]
        })
    conn.close()
    return result


def get_aliases() -> dict:
    conn = get_conn()
    rows = conn.execute("""
        SELECT ua.alias, cf.filename, ua.column_name
        FROM user_aliases ua
        JOIN csv_files cf ON cf.id = ua.file_id
    """).fetchall()
    conn.close()
    return {r["alias"]: {"filename": r["filename"], "column_name": r["column_name"]} for r in rows}


def save_alias(alias: str, file_id: int, column_name: str):
    conn = get_conn()
    conn.execute("""
        INSERT INTO user_aliases (alias, file_id, column_name) VALUES (?,?,?)
        ON CONFLICT(alias) DO UPDATE SET file_id=excluded.file_id, column_name=excluded.column_name
    """, (alias.lower(), file_id, column_name))
    conn.commit()
    conn.close()


def get_cache(cache_key: str) -> dict | None:
    import time
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM query_cache WHERE cache_key=? AND expires_at > ?",
        (cache_key, time.time())
    ).fetchone()
    conn.close()
    if row:
        return {
            "sql_query": row["sql_query"],
            "result_json": json.loads(row["result_json"]),
            "chart_config": json.loads(row["chart_config"]),
        }
    return None


def set_cache(cache_key: str, sql_query: str, result_json: list, chart_config: dict, ttl: int = 900):
    import time
    now = time.time()
    conn = get_conn()
    conn.execute("""
        INSERT INTO query_cache (cache_key, sql_query, result_json, chart_config, created_at, expires_at)
        VALUES (?,?,?,?,?,?)
        ON CONFLICT(cache_key) DO UPDATE SET
            sql_query=excluded.sql_query,
            result_json=excluded.result_json,
            chart_config=excluded.chart_config,
            created_at=excluded.created_at,
            expires_at=excluded.expires_at
    """, (cache_key, sql_query, json.dumps(result_json), json.dumps(chart_config), now, now + ttl))
    conn.commit()
    conn.close()


def save_chart(dashboard_id: int | None, nl_query: str, sql_query: str, chart_config: dict, conversation_history: list) -> int:
    import time
    conn = get_conn()
    cursor = conn.execute("""
        INSERT INTO charts (dashboard_id, nl_query, sql_query, chart_config, conversation_history, created_at)
        VALUES (?,?,?,?,?,?)
    """, (dashboard_id, nl_query, sql_query, json.dumps(chart_config), json.dumps(conversation_history), time.time()))
    chart_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return chart_id


def get_charts(dashboard_id: int | None = None) -> list[dict]:
    conn = get_conn()
    if dashboard_id:
        rows = conn.execute("SELECT * FROM charts WHERE dashboard_id=? ORDER BY created_at DESC", (dashboard_id,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM charts ORDER BY created_at DESC LIMIT 50").fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "dashboard_id": r["dashboard_id"],
            "nl_query": r["nl_query"],
            "sql_query": r["sql_query"],
            "chart_config": json.loads(r["chart_config"] or "{}"),
            "conversation_history": json.loads(r["conversation_history"] or "[]"),
        }
        for r in rows
    ]


def save_dashboard(name: str) -> int:
    import time
    conn = get_conn()
    cursor = conn.execute(
        "INSERT INTO dashboards (name, created_at) VALUES (?,?)", (name, time.time())
    )
    did = cursor.lastrowid
    conn.commit()
    conn.close()
    return did


def get_dashboards() -> list[dict]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM dashboards ORDER BY created_at DESC").fetchall()
    conn.close()
    return [{"id": r["id"], "name": r["name"], "layout_config": json.loads(r["layout_config"] or "[]")} for r in rows]


def update_dashboard_layout(dashboard_id: int, layout_config: list):
    conn = get_conn()
    conn.execute("UPDATE dashboards SET layout_config=? WHERE id=?", (json.dumps(layout_config), dashboard_id))
    conn.commit()
    conn.close()
