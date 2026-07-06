from rapidfuzz import fuzz, process
from catalog.db import get_all_schema, get_aliases
from catalog.crawler import get_csv_folder


def _all_columns() -> list[dict]:
    schema = get_all_schema()
    columns = []

    for f in schema:
        for col in f["columns"]:
            columns.append(
                {
                    "filename": f["filename"],
                    "filepath": f["filepath"],
                    "column_name": col["column_name"],
                    "data_type": col["data_type"],
                }
            )

    return columns


def match_term(
    term: str,
    columns: list[dict],
    aliases: dict,
    preferred_files=None,
) -> dict | None:

    term_lower = term.lower()

    # Prefer columns from already selected files
    if preferred_files:
        filtered = [
            c for c in columns
            if c["filename"] in preferred_files
        ]
        if filtered:
            columns = filtered

    # Alias lookup
    if term_lower in aliases:
        alias = aliases[term_lower]
        return {
            "term": term,
            "filename": alias["filename"],
            "column_name": alias["column_name"],
            "confidence": 1.0,
            "match_type": "alias",
        }

    # Fuzzy match
    col_names_only = [c["column_name"] for c in columns]

    result = process.extractOne(
        term_lower,
        col_names_only,
        scorer=fuzz.token_sort_ratio,
    )

    if result is None:
        return None

    best_name, score, idx = result

    if score >= 60:
        col = columns[idx]
        return {
            "term": term,
            "filename": col["filename"],
            "column_name": col["column_name"],
            "confidence": round(score / 100, 2),
            "match_type": "fuzzy",
        }

    return None


def resolve_schema(intent: dict) -> dict:

    columns = _all_columns()
    aliases = get_aliases()

    def filepath_for(filename: str) -> str:
        return str(get_csv_folder() / filename)

    # -------------------------
    # Resolve metrics first
    # -------------------------

    resolved_metrics = []

    for term in (intent.get("metrics") or []):
        match = match_term(term, columns, aliases)

        if match:
            match["filepath"] = filepath_for(match["filename"])
            resolved_metrics.append(match)
        else:
            resolved_metrics.append(
                {
                    "term": term,
                    "filename": None,
                    "column_name": term,
                    "confidence": 0.5,
                    "filepath": None,
                }
            )

    # Files chosen by metrics
    metric_files = {
        m["filename"]
        for m in resolved_metrics
        if m.get("filename")
    }

    # -------------------------
    # Resolve dimensions
    # -------------------------

    resolved_dims = []

    for term in (intent.get("dimensions") or []):

        match = match_term(
            term,
            columns,
            aliases,
            preferred_files=metric_files if metric_files else None,
        )

        if match:
            match["filepath"] = filepath_for(match["filename"])
            resolved_dims.append(match)
        else:
            resolved_dims.append(
                {
                    "term": term,
                    "filename": None,
                    "column_name": term,
                    "confidence": 0.5,
                    "filepath": None,
                }
            )

    source_files = list(
        {
            m["filename"]
            for m in resolved_metrics + resolved_dims
            if m.get("filename")
        }
    )

    return {
        "metrics": resolved_metrics,
        "dimensions": resolved_dims,
        "source_files": source_files,
        "filepaths": {
            f: filepath_for(f)
            for f in source_files
        },
    }