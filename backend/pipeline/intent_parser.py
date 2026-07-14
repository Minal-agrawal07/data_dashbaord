import json
from catalog.db import get_all_schema
from local_llm import generate

INTENT_SYSTEM = """You are a data analyst assistant. Given a user's natural language request and their CSV schema, extract the intent as structured JSON.IMPORTANT:

Return ONLY valid JSON.

Do not explain.

Do not think.

Do not output <think>.

Do not output markdown.

The first character of your answer must be {

The last character must be }

Return ONLY valid JSON with this structure:
{
  "metrics": ["column_name_or_term"],
  "dimensions": ["column_name_or_term"],
  "time_range": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD", "granularity": "day|week|month|year"} or null,
  "filters": [{"column": "name", "operator": "=|>|<|>=|<=|!=|LIKE|IN", "value": "..."}],
  "aggregation": "sum|avg|count|min|max|none",
  "sort": {"by": "column", "order": "asc|desc"} or null,
  "chart_type_hint": "bar|line|pie|scatter|kpi|histogram|table" or null,
  "source_files": ["filename.csv"],
  "limit": null or integer,
  "clarification_needed": false,
  "clarification_question": null
}

Rules:
- If the request is ambiguous about which column to use, set clarification_needed=true and ask a specific question.
- "source_files" should list only CSVs that are likely relevant.
- If no time range is mentioned, set time_range to null.
- If no aggregation is clear, infer from context (count for "how many", sum for "total", avg for "average").
- For "top N" requests, set limit to N.

- If the request compares categories such as "active vs inactive",
  "true vs false", "yes vs no", or any status comparison,
  include the corresponding status/boolean column as a dimension.

- For boolean columns (e.g. is_active, active, status),
  include that column in "dimensions" whenever the user is asking
  for a comparison between its values.
"""

import time

start = time.perf_counter()
def build_schema_context(schema: list[dict]) -> str:
    lines = ["Available CSV files and their columns:\n"]
    for f in schema:
        lines.append(f"File: {f['filename']} ({f['row_count']} rows)")
        for col in f["columns"]:
            samples = ", ".join(col["sample_values"][:3]) if col["sample_values"] else "N/A"
            lines.append(f"  - {col['column_name']} ({col['data_type']}) — samples: {samples}")
        lines.append("")
    return "\n".join(lines)


def _format_history(conversation_history: list[dict]) -> str:
    if not conversation_history:
        return ""
    lines = ["Previous conversation context:"]
    for turn in conversation_history[-6:]:
        role = "User" if turn["role"] == "user" else "Assistant"
        lines.append(f"{role}: {turn['content']}")
    return "\n".join(lines) + "\n\n"


import re
import json

def _clean_json(raw: str) -> dict:
    raw = raw.strip()

    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)

    raw = raw.replace("```json", "")
    raw = raw.replace("```", "")

    match = re.search(r"\{.*\}", raw, re.DOTALL)

    if not match:
        raise ValueError("No JSON found.")

    return json.loads(match.group())


def parse_intent(nl_query: str, conversation_history: list[dict]) -> dict:
    schema = get_all_schema()
    if not schema:
        return {
            "clarification_needed": True,
            "clarification_question": "No CSV files found. Please add CSV files to the csvs/ folder first."
        }

    schema_context = build_schema_context(schema)
    history_context = _format_history(conversation_history)

    user_prompt = f"{history_context}User request: {nl_query}\n\nReturn the intent JSON."
    system_prompt = INTENT_SYSTEM + "\n\n" + schema_context

    raw = generate(user_prompt, system_prompt=system_prompt, max_tokens=1024, temperature=0.1)
    print("\n" + "="*80)
    print("RAW LLM RESPONSE:")
    print(repr(raw))
    print("="*80 + "\n")
    try:
     intent = _clean_json(raw)
     end = time.perf_counter()
     print(f"[TIME] Intent Parser: {end-start:.3f} sec")
     return intent

    except Exception as e:
     print("JSON Parse Error:", e)
     print(raw)

     return {
        "clarification_needed": True,
        "clarification_question": "LLM failed to generate valid JSON."
    }