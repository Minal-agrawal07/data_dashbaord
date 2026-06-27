# from local_llm import generate
import json
# result_data = [{'category': 'Clothing', 'total_amount': 1454.8100000000002}, {'category': 'Home', 'total_amount': 1109.91}, {'category': 'Electronics', 'total_amount': 14276.0}, {'category': 'Books', 'total_amount': 969.8700000000001}]
#
# chart_type = 'bar'
# nl_query = 'xyz'
#
#
# CONFIG_SYSTEM = """You are a data visualization expert. Given query results and a chart type, generate an Apache ECharts JSON configuration.
#
# Return ONLY valid JSON — no explanation, no markdown.
#
# Rules:
# - Make titles clear and descriptive based on the data.
# - Use readable axis labels (humanize column names: snake_case → Title Case).
# - For bar/line charts with a time dimension, put time on x-axis.
# - For pie charts, use "series[0].data" as [{name, value}] array.
# - For KPI cards, return {"type": "kpi", "value": <number>, "label": "<metric name>", "unit": ""}.
# - For tables, return {"type": "table", "columns": [...], "rows": [...]}.
# - Always include tooltip configuration.
# - Use a clean color palette: ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#3b82f6", "#8b5cf6"].
# - Keep the config concise — no unnecessary properties.
# """
#
#
#
# cols = list(result_data[0].keys()) if result_data else []
# full_data = result_data if len(result_data) <= 100 else result_data[:100]
#
# user_prompt = f"""Chart type: {chart_type}
# User query: {nl_query}
# Columns available: {cols}
# Sample data (first 5 rows): {json.dumps(result_data[:5], indent=2)}
# Total rows: {len(result_data)}
# Full data: {json.dumps(full_data, indent=2)}{"..." if len(result_data) > 100 else ""}
#
# Generate the ECharts config JSON."""
#
# raw = generate(user_prompt, system_prompt=CONFIG_SYSTEM, max_tokens=2048, temperature=0.1)
# print(raw)
# print(type(raw))


raw = {
    "type": "bar",
    "data": {
        "labels": ["Clothing", "Home", "Electronics", "Books"],
        "datasets": [
            {
                "label": "Total Revenue",
                "data": [1454.81, 1109.91, 14276.0, 969.87],
                "backgroundColor": ["#6366f1", "#10b981", "#f59e0b", "#ef4444"]
            }
        ]
    },
    "options": {
        "title": {
            "display": true,
            "text": "Monthly Total Revenue by Category"
        },
        "scales": {
            "y": {
                "beginAtZero": true,
                "title": {
                    "display": true,
                    "text": "Total Amount"
                }
            },
            "x": {
                "title": {
                    "display": true,
                    "text": "Category"
                }
            }
        },
        "plugins": {
            "tooltip": {
                "mode": "index",
                "intersect": false
            }
        }
    }
}

def _clean_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


X = _clean_json(raw)
print(X)
print(type(X))