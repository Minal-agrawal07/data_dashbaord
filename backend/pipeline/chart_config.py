"""
Generic Chart Engine

Converts SQL result rows into Apache ECharts config.

Pipeline

SQL Result
      ↓
Analyze Schema
      ↓
Chart Builder
      ↓
ECharts JSON
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from numbers import Number
from typing import Any


# ------------------------------------------------------------
# Utility
# ------------------------------------------------------------

TIME_WORDS = {
    "date",
    "day",
    "week",
    "month",
    "year",
    "time",
    "timestamp",
    "created_at",
    "updated_at",
    "order_date",
    "signup_date",
}


def normalize_name(name: str) -> str:
    return (
        name.replace("_", " ")
        .replace("-", " ")
        .title()
    )


def is_number(value: Any) -> bool:
    return isinstance(value, Number) and not isinstance(value, bool)


def is_date_value(value: Any) -> bool:

    if isinstance(value, (date, datetime)):
        return True

    if isinstance(value, str):

        try:
            datetime.fromisoformat(value.replace("Z", ""))

            return True

        except Exception:

            return False

    return False


def unique_preserve_order(values):

    seen = set()

    out = []

    for v in values:

        if v not in seen:

            seen.add(v)

            out.append(v)

    return out


# ------------------------------------------------------------
# Schema Analyzer
# ------------------------------------------------------------

def analyze_schema(rows: list[dict]):

    if not rows:

        return None

    first = rows[0]

    numeric = []

    categorical = []

    time_dimension = None

    for col, value in first.items():

        lower = col.lower()

        if lower in TIME_WORDS or is_date_value(value):

            time_dimension = col

            continue

        if is_number(value):

            numeric.append(col)

        else:

            categorical.append(col)

    return {

        "time_dimension": time_dimension,

        "dimensions": categorical,

        "measures": numeric,

        "columns": list(first.keys())

    }


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def chart_title(intent, rows):

    if intent and intent.get("metrics"):

        metric = normalize_name(intent["metrics"][0])

    else:

        analysis = analyze_schema(rows)

        metric = normalize_name(
            analysis["measures"][0]
        ) if analysis["measures"] else "Chart"

    return metric


def empty_chart():

    return {

        "type": "empty",

        "message": "No data found."

    }


def make_axis(values):

    return {

        "type": "category",

        "data": values

    }



# ------------------------------------------------------------
# BAR CHART
# ------------------------------------------------------------
def build_bar(rows, intent):

    analysis = analyze_schema(rows)

    if analysis is None:
        return empty_chart()

    measures = analysis["measures"]
    dims = analysis["dimensions"]
    time_dim = analysis["time_dimension"]

    if not measures:
        return empty_chart()

    value_col = measures[0]

    # --------------------------------------------------
    # Case 1: Time + Category (e.g. monthly sales by region)
    # --------------------------------------------------


    if time_dim and not dims:

     return {
        "title": {
            "text": chart_title(intent, rows)
        },
        "tooltip": {
            "trigger": "axis"
        },
        "xAxis": make_axis(
            [str(r[time_dim]) for r in rows]
        ),
        "yAxis": {
            "type": "value"
        },
        "series": [
            {
                "type": "bar",
                "name": normalize_name(value_col),
                "data": [
                    r[value_col]
                    for r in rows
                ]
            }
        ]
    }


    if time_dim and dims:

        series_col = dims[0]

        x_values = unique_preserve_order(
            [str(r[time_dim]) for r in rows]
        )

        grouped = defaultdict(dict)

        for r in rows:
            grouped[str(r[series_col])][str(r[time_dim])] = r[value_col]

        series = []

        for name, vals in grouped.items():

            series.append({
                "name": name,
                "type": "bar",
                "data": [
                    vals.get(x, 0)
                    for x in x_values
                ]
            })

        return {
            "title": {
                "text": chart_title(intent, rows)
            },
            "tooltip": {
                "trigger": "axis"
            },
            "legend": {},
            "xAxis": make_axis(x_values),
            "yAxis": {
                "type": "value"
            },
            "series": series
        }

    # --------------------------------------------------
    # Case 2: Two categorical columns
    # Example:
    # region | is_active | count
    # --------------------------------------------------
    if len(dims) >= 2:

        x_col = dims[0]
        series_col = dims[1]

        x_values = unique_preserve_order(
            [str(r[x_col]) for r in rows]
        )

        grouped = defaultdict(dict)

        for r in rows:
            grouped[str(r[series_col])][str(r[x_col])] = r[value_col]

        series = []

        for name, vals in grouped.items():

            series.append({
                "name": name,
                "type": "bar",
                "data": [
                    vals.get(x, 0)
                    for x in x_values
                ]
            })

        return {
            "title": {
                "text": chart_title(intent, rows)
            },
            "tooltip": {
                "trigger": "axis"
            },
            "legend": {},
            "xAxis": make_axis(x_values),
            "yAxis": {
                "type": "value"
            },
            "series": series
        }

    # --------------------------------------------------
    # Case 3: One categorical column
    # --------------------------------------------------
    if len(dims) == 1:

        x = dims[0]

        return {
            "title": {
                "text": chart_title(intent, rows)
            },
            "tooltip": {
                "trigger": "axis"
            },
            "legend": {},
            "xAxis": make_axis(
                [str(r[x]) for r in rows]
            ),
            "yAxis": {
                "type": "value"
            },
            "series": [
                {
                    "type": "bar",
                    "name": normalize_name(value_col),
                    "data": [
                        r[value_col]
                        for r in rows
                    ]
                }
            ]
        }

    return empty_chart()


# ------------------------------------------------------------
# LINE CHART
# ------------------------------------------------------------

def build_line(rows, intent):

    analysis = analyze_schema(rows)

    if analysis is None:
        return empty_chart()

    measures = analysis["measures"]
    dims = analysis["dimensions"]
    time_dim = analysis["time_dimension"]

    if not measures:
        return empty_chart()

    value_col = measures[0]

    # --------------------------------------------------
# Case: Time series with no categorical dimension
# Example:
# date | sum(sessions)
# --------------------------------------------------
    if time_dim and not dims:

     return {
        "title": {
            "text": chart_title(intent, rows)
        },
        "tooltip": {
            "trigger": "axis"
        },
        "xAxis": make_axis(
            [str(r[time_dim]) for r in rows]
        ),
        "yAxis": {
            "type": "value"
        },
        "series": [
            {
                "type": "line",
                "smooth": True,
                "name": normalize_name(value_col),
                "data": [
                    r[value_col]
                    for r in rows
                ]
            }
        ]
    }

    if time_dim and dims:

        series_col = dims[0]

        x_values = unique_preserve_order(
            [str(r[time_dim]) for r in rows]
        )

        grouped = defaultdict(dict)

        for r in rows:

            grouped[str(r[series_col])][str(r[time_dim])] = r[value_col]

        series = []

        for name, vals in grouped.items():

            series.append({

                "name": name,

                "type": "line",

                "smooth": True,

                "data": [

                    vals.get(x)

                    for x in x_values

                ]

            })

        return {

            "title": {

                "text": chart_title(intent, rows)

            },

            "tooltip": {

                "trigger": "axis"

            },

            "legend": {},

            "xAxis": make_axis(x_values),

            "yAxis": {

                "type": "value"

            },

            "series": series

        }

    if dims:

        x = dims[0]

        return {

            "title": {

                "text": chart_title(intent, rows)

            },

            "tooltip": {

                "trigger": "axis"

            },

            "legend": {},

            "xAxis": make_axis(

                [str(r[x]) for r in rows]

            ),

            "yAxis": {

                "type": "value"

            },

            "series": [

                {

                    "type": "line",

                    "smooth": True,

                    "name": normalize_name(value_col),

                    "data": [

                        r[value_col]

                        for r in rows

                    ]

                }

            ]

        }

    return empty_chart()


# ------------------------------------------------------------
# PIE
# ------------------------------------------------------------

def build_pie(rows, intent):

    analysis = analyze_schema(rows)

    if analysis is None:
        return empty_chart()

    if not analysis["dimensions"] or not analysis["measures"]:
        return empty_chart()

    dim = analysis["dimensions"][0]
    measure = analysis["measures"][0]

    return {

        "title": {

            "text": chart_title(intent, rows)

        },

        "tooltip": {},

        "legend": {

            "bottom": 0

        },

        "series": [

            {

                "type": "pie",

                "radius": "65%",

                "data": [

                    {

                        "name": str(r[dim]),

                        "value": r[measure]

                    }

                    for r in rows

                ]

            }

        ]

    }


# ------------------------------------------------------------
# KPI
# ------------------------------------------------------------

def build_kpi(rows, intent):

    analysis = analyze_schema(rows)

    if analysis is None:
        return empty_chart()

    if not analysis["measures"]:
        return empty_chart()

    value = rows[0][analysis["measures"][0]]

    return {

        "type": "kpi",

        "label": chart_title(intent, rows),

        "value": value,

        "unit": ""

    }


# ------------------------------------------------------------
# TABLE
# ------------------------------------------------------------

def build_table(rows, intent):

    return {

        "type": "table",

        "columns": list(rows[0].keys()),

        "rows": rows

    }


# ------------------------------------------------------------
# SCATTER
# ------------------------------------------------------------

def build_scatter(rows, intent):

    analysis = analyze_schema(rows)

    if analysis is None:
        return empty_chart()

    measures = analysis["measures"]

    if len(measures) < 2:
        return empty_chart()

    x = measures[0]
    y = measures[1]

    return {

        "title": {

            "text": f"{normalize_name(y)} vs {normalize_name(x)}"

        },

        "tooltip": {

            "trigger": "item"

        },

        "xAxis": {

            "type": "value",

            "name": normalize_name(x)

        },

        "yAxis": {

            "type": "value",

            "name": normalize_name(y)

        },

        "series": [

            {

                "type": "scatter",

                "data": [

                    [

                        r[x],

                        r[y]

                    ]

                    for r in rows

                ]

            }

        ]

    }


# ------------------------------------------------------------
# HISTOGRAM
# ------------------------------------------------------------

def build_histogram(rows, intent):

    analysis = analyze_schema(rows)

    if analysis is None:
        return empty_chart()

    if not analysis["measures"]:
        return empty_chart()

    col = analysis["measures"][0]

    values = [

        r[col]

        for r in rows

    ]

    return {

        "title": {

            "text": normalize_name(col)

        },

        "tooltip": {},

        "xAxis": {

            "type": "category",

            "data": list(range(len(values)))

        },

        "yAxis": {

            "type": "value"

        },

        "series": [

            {

                "type": "bar",

                "data": values

            }

        ]

    }


# ------------------------------------------------------------
# AUTO CHART
# ------------------------------------------------------------

def auto_chart(rows, intent):

    analysis = analyze_schema(rows)

    if analysis is None:
        return empty_chart()

    if len(rows) == 1 and len(analysis["measures"]) == 1:
        return build_kpi(rows, intent)

    if analysis["time_dimension"]:
        return build_line(rows, intent)

    if len(analysis["dimensions"]) == 1:
        return build_bar(rows, intent)

    if len(analysis["measures"]) >= 2:
        return build_scatter(rows, intent)

    return build_table(rows, intent)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def generate_chart_config(
    chart_type: str,
    result_data: list[dict],
    intent: dict,
    nl_query: str,
):

    if not result_data:
        return empty_chart()

    chart_type = (chart_type or "").lower()

    if chart_type == "bar":
        return build_bar(result_data, intent)

    if chart_type == "line":
        return build_line(result_data, intent)

    if chart_type == "pie":
        return build_pie(result_data, intent)

    if chart_type == "scatter":
        return build_scatter(result_data, intent)

    if chart_type == "histogram":
        return build_histogram(result_data, intent)

    if chart_type == "table":
        return build_table(result_data, intent)

    if chart_type == "kpi":
        return build_kpi(result_data, intent)

    return auto_chart(result_data, intent)


