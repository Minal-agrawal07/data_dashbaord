import re

TIME_KEYWORDS = re.compile(
    r"\b(over time|trend|timeline|daily|weekly|monthly|yearly)\b",
    re.IGNORECASE,
)

PIE_KEYWORDS = re.compile(
    r"\b(composition|share|proportion|percentage|breakdown|pie|donut)\b",
    re.IGNORECASE,
)

SCATTER_KEYWORDS = re.compile(
    r"\b(correlation|relationship|scatter|vs\.?|versus)\b",
    re.IGNORECASE,
)

HISTOGRAM_KEYWORDS = re.compile(
    r"\b(distribution|histogram|frequency|spread)\b",
    re.IGNORECASE,
)

RANK_KEYWORDS = re.compile(
    r"\b(top|bottom|highest|lowest|best|worst|ranking|ranked)\b",
    re.IGNORECASE,
)

TABLE_KEYWORDS = re.compile(
    r"\b(table|list|details|show all|all rows)\b",
    re.IGNORECASE,
)


def select_chart_type(intent: dict, result_data: list[dict], nl_query: str = "") -> str:
    """
    Select the most appropriate chart type based on
    planner hints, SQL result shape and NL query.
    """

    nl_query = (nl_query or "").lower()

    dims = intent.get("dimensions", []) or []
    metrics = intent.get("metrics", []) or []

    hint = (intent.get("chart_type_hint") or "").lower()

    valid_hints = {
        "bar",
        "line",
        "pie",
        "donut",
        "scatter",
        "histogram",
        "table",
        "kpi",
        "area",
    }

    # ---------------------------------------------------------
    # 1. Planner hint always wins
    # ---------------------------------------------------------

    if hint in valid_hints:
        return hint

    num_rows = len(result_data)
    num_cols = len(result_data[0]) if result_data else 0

    # ---------------------------------------------------------
    # 2. Table requests
    # ---------------------------------------------------------

    if TABLE_KEYWORDS.search(nl_query):
        return "table"

    # ---------------------------------------------------------
    # 3. KPI
    # ---------------------------------------------------------

    if num_rows == 1 and num_cols == 1:
        return "kpi"

    if num_rows == 1 and len(metrics) == 1:
        return "kpi"

    # ---------------------------------------------------------
    # 4. Scatter
    # ---------------------------------------------------------

    if SCATTER_KEYWORDS.search(nl_query):
        return "scatter"

    if len(metrics) >= 2:
        return "scatter"

    # ---------------------------------------------------------
    # 5. Histogram
    # ---------------------------------------------------------

    if HISTOGRAM_KEYWORDS.search(nl_query):
        return "histogram"

    # ---------------------------------------------------------
    # 6. Pie / Donut
    # ---------------------------------------------------------

    if PIE_KEYWORDS.search(nl_query):

        if 2 <= num_rows <= 8:

            return "pie"

    # ---------------------------------------------------------
    # 7. Trend
    # ---------------------------------------------------------

    if TIME_KEYWORDS.search(nl_query):

        return "line"

    if intent.get("time_range"):

        return "line"

    # ---------------------------------------------------------
    # 8. Ranking
    # ---------------------------------------------------------

    if RANK_KEYWORDS.search(nl_query):

        if num_rows <= 10:

            return "bar"

        return "table"

    # ---------------------------------------------------------
    # 9. Generic category comparison
    # ---------------------------------------------------------

    if len(dims) == 1 and len(metrics) >= 1:

        return "bar"

    # ---------------------------------------------------------
    # 10. Wide result
    # ---------------------------------------------------------

    if num_cols >= 5:

        return "table"

    # ---------------------------------------------------------
    # 11. Distribution fallback
    # ---------------------------------------------------------

    if num_cols == 1 and num_rows > 10:

        return "histogram"

    # ---------------------------------------------------------
    # 12. Final fallback
    # ---------------------------------------------------------

    return "bar"