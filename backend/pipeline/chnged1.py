from typing import Any

from collections import defaultdict
def detect_columns(rows: list[dict]) -> tuple[str, list[str]]:
    """
    Returns:
        x_column
        numeric_columns
    """

    if not rows:
        return "", []

    first = rows[0]

    numeric = []
    categorical = []

    for key, value in first.items():

        if isinstance(value, (int, float)):
            numeric.append(key)
        else:
            categorical.append(key)

    x_col = categorical[0] if categorical else list(first.keys())[0]

    return x_col, numeric

def build_bar(rows):

    if not rows:
        return {"type": "empty"}

    first = rows[0]

    numeric = []
    categorical = []

    for k, v in first.items():
        if isinstance(v, (int, float)):
            numeric.append(k)
        else:
            categorical.append(k)

    if not numeric:
        return {"type": "empty"}

    value_col = numeric[0]

    # One categorical column
    if len(categorical) == 1:

        x = categorical[0]

        return {
            "tooltip": {"trigger": "axis"},
            "legend": {},
            "xAxis": {
                "type": "category",
                "data": [str(r[x]) for r in rows]
            },
            "yAxis": {
                "type": "value"
            },
            "series": [
                {
                    "type": "bar",
                    "name": value_col,
                    "data": [r[value_col] for r in rows]
                }
            ]
        }

    # Two categorical columns
    series_col = categorical[0]
    x_col = categorical[1]

    x_values = []
    grouped = defaultdict(dict)

    for r in rows:

        x = str(r[x_col])
        s = str(r[series_col])

        if x not in x_values:
            x_values.append(x)

        grouped[s][x] = r[value_col]

    series = []

    for s, vals in grouped.items():

        series.append({

            "name": s,

            "type": "bar",

            "data": [

                vals.get(x, 0)

                for x in x_values

            ]

        })

    return {

        "tooltip": {

            "trigger": "axis"

        },

        "legend": {},

        "xAxis": {

            "type": "category",

            "data": x_values

        },

        "yAxis": {

            "type": "value"

        },

        "series": series

    }
def build_pie(rows):

    x_col, numeric_cols = detect_columns(rows)

    if not numeric_cols:
        return {"type": "empty"}

    return {
        "tooltip": {},
        "series": [
            {
                "type": "pie",
                "data": [
                    {
                        "name": str(r[x_col]),
                        "value": r[numeric_cols[0]]
                    }
                    for r in rows
                ]
            }
        ]
    }
def build_line(rows):

    if not rows:
        return {"type": "empty"}

    first = rows[0]

    numeric = []
    categorical = []

    for k, v in first.items():
        if isinstance(v, (int, float)):
            numeric.append(k)
        else:
            categorical.append(k)

    if not numeric:
        return {"type": "empty"}

    value_col = numeric[0]

    if len(categorical) == 1:

        x = categorical[0]

        return {
            "tooltip": {"trigger": "axis"},
            "legend": {},
            "xAxis": {
                "type": "category",
                "data": [str(r[x]) for r in rows]
            },
            "yAxis": {
                "type": "value"
            },
            "series": [
                {
                    "type": "line",
                    "name": value_col,
                    "data": [r[value_col] for r in rows]
                }
            ]
        }

    series_col = categorical[0]
    x_col = categorical[1]

    x_values = []
    grouped = defaultdict(dict)

    for r in rows:

        x = str(r[x_col])
        s = str(r[series_col])

        if x not in x_values:
            x_values.append(x)

        grouped[s][x] = r[value_col]

    series = []

    for s, vals in grouped.items():

        series.append({

            "name": s,

            "type": "line",

            "data": [

                vals.get(x, 0)

                for x in x_values

            ]

        })

    return {

        "tooltip": {

            "trigger": "axis"

        },

        "legend": {},

        "xAxis": {

            "type": "category",

            "data": x_values

        },

        "yAxis": {

            "type": "value"

        },

        "series": series

    }

def build_table(rows):

    return {

        "type": "table",

        "columns": list(rows[0].keys()) if rows else [],

        "rows": rows

    }


def build_kpi(rows):

    if not rows:
        return {
            "type": "kpi",
            "value": None
        }

    first = rows[0]

    key = list(first.keys())[0]

    return {

        "type": "kpi",

        "label": key,

        "value": first[key]

    }


def build_scatter(rows):

    _, numeric = detect_columns(rows)

    if len(numeric) < 2:
        return {
            "type": "empty"
        }

    return {

        "tooltip": {},

        "xAxis": {},

        "yAxis": {},

        "series": [

            {

                "type": "scatter",

                "data": [

                    [

                        r[numeric[0]],

                        r[numeric[1]]

                    ]

                    for r in rows

                ]

            }

        ]

    }


def generate_chart_config(
    chart_type: str,
    result_data: list[dict],
    intent: dict,
    nl_query: str,
):

    if not result_data:

        return {

            "type": "empty",

            "message": "No data found."

        }

    chart_type = (chart_type or "").lower()

    if chart_type == "bar":
        return build_bar(result_data)

    elif chart_type == "line":
        return build_line(result_data)

    elif chart_type == "pie":
        return build_pie(result_data)

    elif chart_type == "scatter":
        return build_scatter(result_data)

    elif chart_type == "table":
        return build_table(result_data)

    elif chart_type == "kpi":
        return build_kpi(result_data)

    else:
        return build_bar(result_data)