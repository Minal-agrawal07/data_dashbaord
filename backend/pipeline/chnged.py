import json
from local_llm import generate
import ast
import re
CONFIG_SYSTEM = """
You are an Apache ECharts JSON generator.

IMPORTANT:

Return ONLY valid JSON.

Do NOT output <think>.
Do NOT explain.
Do NOT output markdown.
Do NOT output code fences.

The FIRST character MUST be {
The LAST character MUST be }

The response MUST be valid JSON parsable by json.loads().

Rules:
- Make titles clear and descriptive.
- Put time on the x-axis.
- Use readable labels.
- Always include tooltip.
- Use only valid JSON.
- Never use comments.
- Never use trailing commas.
- Never output JavaScript objects.
"""

def fix_truncated_json(raw: str):
    open_braces = raw.count("{")
    close_braces = raw.count("}")

    if open_braces > close_braces:
        raw += "}" * (open_braces - close_braces)

    return raw

def _clean_json(raw: str) -> dict:

    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)

    raw = raw.replace("```json", "")
    raw = raw.replace("```", "")

    match = re.search(r"\{.*\}", raw, re.DOTALL)

    if not match:
        raise ValueError(f"No JSON found.\n\n{raw}")

    raw = match.group(0)

    return json.loads(raw)



def generate_chart_config(chart_type: str, result_data: list[dict], intent: dict, nl_query: str) -> dict:
    if not result_data:
        return {"type": "empty", "message": "No data returned for this query."}

    cols = list(result_data[0].keys()) if result_data else []
    full_data = result_data if len(result_data) <= 100 else result_data[:100]

    user_prompt = f"""Chart type: {chart_type}
User query: {nl_query}
Columns available: {cols}
Sample data (first 5 rows): {json.dumps(result_data[:5], indent=2)}
Total rows: {len(result_data)}
Full data: {json.dumps(full_data, indent=2)}{"..." if len(result_data) > 100 else ""}

Generate the ECharts config JSON."""

    raw = generate(user_prompt, system_prompt=CONFIG_SYSTEM, max_tokens=512, temperature=0.1)
    return _clean_json(raw)
