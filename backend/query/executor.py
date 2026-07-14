import hashlib
import json
import os
import time
import duckdb
from pathlib import Path
from query.validator import validate_sql, QueryValidationError
from catalog.db import get_cache, set_cache
from catalog.crawler import get_csv_folder


def _cache_key(sql: str) -> str:
    folder = get_csv_folder()
    file_mtimes = {}
    if folder.exists():
        for f in folder.glob("*.csv"):
            file_mtimes[f.name] = f.stat().st_mtime
    payload = sql + json.dumps(file_mtimes, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def execute_query(sql: str, timeout_seconds: int = 30) -> tuple[str, list[dict]]:
    start = time.perf_counter()

    validated_sql = validate_sql(sql)

    end = time.perf_counter()

    print(f"[TIME] SQL Validation: {end-start:.3f} sec")

    key = _cache_key(validated_sql)
    cached = get_cache(key)
    if cached:
        return validated_sql, cached["result_json"]

    conn = duckdb.connect()

    try:
        conn.execute("SET threads TO 4")

        folder = get_csv_folder()

        for csv_file in folder.glob("*.csv"):
         table_name = csv_file.stem

         conn.execute(f"""
            CREATE OR REPLACE VIEW {table_name} AS
            SELECT *
            FROM read_csv_auto('{csv_file.as_posix()}');
        """)

        start = time.perf_counter()

        for csv_file in folder.glob("*.csv"):
         table_name = csv_file.stem

         create_view_sql = f"""
    CREATE OR REPLACE VIEW "{table_name}" AS
    SELECT *
    FROM read_csv_auto('{csv_file.as_posix()}');
    """

         print("=" * 80)
         print(create_view_sql)
         print("=" * 80)

         conn.execute(create_view_sql)

        try:
           df = conn.execute(validated_sql).df()
        except Exception as e:
          import traceback
          traceback.print_exc()
          print("SQL WAS:")
          print(validated_sql)
          raise

        end = time.perf_counter()

        print(f"[TIME] DuckDB Execution: {end-start:.3f} sec")
        if len(df) > 50000:
            df = df.head(50000)
        records = df.to_dict(orient="records")
        for record in records:
            for k, v in record.items():
                if hasattr(v, 'item'):
                    record[k] = v.item()
                elif str(type(v)) in ["<class 'pandas._libs.tslibs.timestamps.Timestamp'>",
                                       "<class 'datetime.date'>"]:
                    record[k] = str(v)
    except QueryValidationError:
        raise
    except Exception as e:
        raise RuntimeError(f"Query execution failed: {e}")
    finally:
        conn.close()

    return validated_sql, records


def execute_and_cache(sql: str, chart_config: dict) -> tuple[str, list[dict]]:
    validated_sql, records = execute_query(sql)
    key = _cache_key(validated_sql)
    set_cache(key, validated_sql, records, chart_config)
    return validated_sql, records


def invalidate_cache_for_file(filename: str):
    pass
