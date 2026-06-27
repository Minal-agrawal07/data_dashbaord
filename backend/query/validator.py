import re
from pathlib import Path
from catalog.crawler import get_csv_folder


BLOCKED_KEYWORDS = re.compile(
    r'\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|REPLACE|MERGE|GRANT|REVOKE|EXEC|EXECUTE)\b',
    re.IGNORECASE
)


class QueryValidationError(Exception):
    pass


def validate_sql(sql: str) -> str:
    stripped = sql.strip()

    if BLOCKED_KEYWORDS.search(stripped):
        raise QueryValidationError("Only SELECT queries are allowed.")

    if not re.match(r'^\s*SELECT\b', stripped, re.IGNORECASE):
        raise QueryValidationError("Query must start with SELECT.")

    _check_path_scope(stripped)

    if not re.search(r'\bLIMIT\b', stripped, re.IGNORECASE):
        stripped = stripped.rstrip(";") + " LIMIT 50000"

    return stripped


def _check_path_scope(sql: str):
    csv_folder = str(get_csv_folder().resolve())
    paths = re.findall(r"'([^']+\.csv)'", sql, re.IGNORECASE)
    for p in paths:
        if ".." in p:
            raise QueryValidationError(f"Path traversal not allowed: {p}")
        resolved = str(Path(p).resolve())
        if not resolved.startswith(csv_folder):
            raise QueryValidationError(f"File outside allowed folder: {p}")
