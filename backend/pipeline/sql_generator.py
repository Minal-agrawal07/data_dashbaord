import json
import re

from catalog.db import get_all_schema
from pipeline.intent_parser import build_schema_context
from local_llm import generate


SQL_SYSTEM = """
You are an expert DuckDB SQL generator.

IMPORTANT:
- Return ONLY SQL.
- Never output <think>.
- Never explain.
- Never output markdown.
- The first word MUST be SELECT.
- The last character MUST be ;
- Never invent joins.
- Never use columns from another CSV unless explicitly requested.

Rules:
1. Only generate SELECT queries.
2. Use ONLY tables and columns provided in the schema.
3. Quote column names when necessary.
4. Use DATE_TRUNC('month', ...) for monthly grouping.
5. Add LIMIT 50000 if not present.

Aggregation Rules:
- Every non-aggregated column in SELECT MUST appear in GROUP BY.
- ORDER BY can ONLY use:
    * a column in GROUP BY
    * an aggregate alias (SUM, COUNT, AVG, MAX, MIN)
- NEVER ORDER BY a column that is not grouped or aggregated.
- If a metric like SUM(conversions) is selected, prefer:
      ORDER BY total_conversions DESC
  instead of ordering by another column.
- Never ORDER BY date after GROUP BY unless using MAX(date) or MIN(date).
"""

def _clean_sql(raw: str) -> str:

    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)

    raw = raw.replace("```sql", "")
    raw = raw.replace("```", "")

    match = re.search(
        r"(SELECT[\s\S]*?;)",
        raw,
        flags=re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    # if no semicolon found
    match = re.search(
        r"(SELECT[\s\S]*)",
        raw,
        flags=re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return raw.strip()

import re

def generate_sql(
    intent: dict,
    resolved: dict,
    conversation_history: list[dict],
) -> str:
    schema = get_all_schema()
    schema_context = build_schema_context(schema)

    filepaths = resolved.get("filepaths", {})

    filepath_info = (
    "Available tables:\n"
    + "\n".join(
        f"  {fname.replace('.csv','')}"
        for fname in filepaths.keys()
    )
)

    prior_sql = "\n".join(
        f"Previous SQL:\n{turn['sql']}"
        for turn in conversation_history[-4:]
        if turn.get("sql")
    )

    history_section = ""
    if prior_sql:
        history_section = "\n" + prior_sql

    user_prompt = f"""User intent:
{json.dumps(intent, indent=2)}

Resolved columns:
Metrics:
{json.dumps(resolved['metrics'], indent=2)}

Dimensions:
{json.dumps(resolved['dimensions'], indent=2)}

{filepath_info}
{history_section}

Write the DuckDB SQL query.

IMPORTANT:
- Use the table names above.
- NEVER use read_csv_auto().
"""

    system_prompt = SQL_SYSTEM + "\n\n" + schema_context

    print(schema_context)
    raw = generate(
    user_prompt=user_prompt,
    system_prompt=system_prompt,
    max_tokens=500,
)

    sql = _clean_sql(raw)

# Replace filename-only paths with full paths
    for filename, fullpath in filepaths.items():

     
      pattern = rf"read_csv_auto\(\s*['\"]{re.escape(filename)}['\"]\s*\)"

      sql = re.sub(
    pattern,
    lambda m: f"read_csv_auto('{fullpath}')",
    sql,
    flags=re.IGNORECASE,
)

    return sql


def fix_sql_with_error(
    sql: str,
    error: str,
    intent: dict,
    resolved: dict,
) -> str:
    schema = get_all_schema()
    schema_context = build_schema_context(schema)

    filepaths = resolved.get("filepaths", {})

    filepath_info = "\n".join(
        f"  {fname}: read_csv_auto('{fpath}')"
        for fname, fpath in filepaths.items()
    )

    user_prompt = f"""The following DuckDB SQL query failed with an error.

Failed SQL:
{sql}

Error:
{error}

File paths:
{filepath_info}

Return ONLY the corrected SQL query.
"""

    system_prompt = SQL_SYSTEM + "\n\n" + schema_context

    raw = generate(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        max_tokens=500,
    )

    return _clean_sql(raw)