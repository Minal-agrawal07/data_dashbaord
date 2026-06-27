import re


TIME_KEYWORDS = re.compile(r'\b(daily|weekly|monthly|yearly|over time|trend|by (day|week|month|year|date))\b', re.IGNORECASE)
PIE_KEYWORDS = re.compile(r'\b(breakdown|share|proportion|percentage|composition|distribution of|pie|donut)\b', re.IGNORECASE)
SCATTER_KEYWORDS = re.compile(r'\b(correlation|scatter|vs\.?|versus|relationship between)\b', re.IGNORECASE)
HISTOGRAM_KEYWORDS = re.compile(r'\b(distribution|spread|histogram|frequency)\b', re.IGNORECASE)
RANK_KEYWORDS = re.compile(r'\b(top|bottom|ranked|ranking|best|worst|highest|lowest)\b', re.IGNORECASE)
KPI_KEYWORDS = re.compile(r'\b(total|overall|grand total|summary|how many|how much|average|mean)\b', re.IGNORECASE)
TABLE_KEYWORDS = re.compile(r'\b(table|list|show all|all rows|details)\b', re.IGNORECASE)


def select_chart_type(intent: dict, result_data: list[dict], nl_query: str = "") -> str:
    dims = intent.get("dimensions", [])
    metrics = intent.get("metrics", [])
    hint = (intent.get("chart_type_hint") or "").lower()
    # Respect explicit chart requested by the user
    if hint in (
    "bar",
    "line",
    "pie",
    "scatter",
    "kpi",
    "histogram",
    "table",
    "area",
    "donut",
):
     return hint

    if hint in ("bar", "line", "scatter", "kpi", "histogram", "table", "area", "donut"):
       return hint

    
    time_range = intent.get("time_range")
    num_rows = len(result_data)
    num_cols = len(result_data[0]) if result_data else 0

    if TABLE_KEYWORDS.search(nl_query):
        return "table"

    if num_cols == 1 and num_rows == 1:
        return "kpi"

    if not dims and len(metrics) == 1 and num_rows <= 3:
        return "kpi"

    if SCATTER_KEYWORDS.search(nl_query) and len(metrics) >= 2:
        return "scatter"

    if HISTOGRAM_KEYWORDS.search(nl_query) and not dims:
        return "histogram"

    if PIE_KEYWORDS.search(nl_query) and len(dims) == 1:
        return "pie"

    if time_range or TIME_KEYWORDS.search(nl_query):
        return "line"

    if RANK_KEYWORDS.search(nl_query) and len(dims) == 1:
        return "bar"

    if len(dims) == 1 and len(metrics) == 1:
        return "bar"

    if len(dims) >= 1 and len(metrics) >= 1:
        return "bar"

    if num_cols > 4:
        return "table"

    return "bar"
