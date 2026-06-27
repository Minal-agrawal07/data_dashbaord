import os
import duckdb
from pathlib import Path
from catalog.db import upsert_csv_file, replace_columns

CSV_FOLDER = Path(__file__).parent.parent.parent / "csvs"


def get_csv_folder() -> Path:
    return CSV_FOLDER


def crawl_file(filepath: str) -> dict:
    path = Path(filepath)
    conn = duckdb.connect()

    try:
        describe = conn.execute(f"DESCRIBE SELECT * FROM read_csv_auto('{filepath}')").fetchall()
        columns = []
        for row in describe:
            col_name = row[0]
            col_type = row[1]
            try:
                samples = conn.execute(
                    f"SELECT DISTINCT \"{col_name}\" FROM read_csv_auto('{filepath}') "
                    f"WHERE \"{col_name}\" IS NOT NULL LIMIT 5"
                ).fetchall()
                sample_values = [str(s[0]) for s in samples]
            except Exception:
                sample_values = []
            columns.append({
                "column_name": col_name,
                "data_type": col_type,
                "sample_values": sample_values,
            })

        row_count = conn.execute(f"SELECT COUNT(*) FROM read_csv_auto('{filepath}')").fetchone()[0]
    finally:
        conn.close()

    return {
        "filename": path.name,
        "filepath": str(path),
        "row_count": row_count,
        "columns": columns,
        "last_modified": path.stat().st_mtime,
    }


def crawl_all():
    folder = get_csv_folder()
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
        return

    for csv_file in sorted(folder.glob("*.csv")):
        try:
            info = crawl_file(str(csv_file))
            file_id = upsert_csv_file(
                info["filename"], info["filepath"], info["row_count"], info["last_modified"]
            )
            replace_columns(file_id, info["columns"])
            print(f"[crawler] Crawled {info['filename']} — {info['row_count']} rows, {len(info['columns'])} columns")
        except Exception as e:
            print(f"[crawler] Error crawling {csv_file.name}: {e}")
