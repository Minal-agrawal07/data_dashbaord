from pipeline.intent_parser import parse_intent
from pipeline.schema_matcher import resolve_schema
from pipeline.sql_generator import generate_sql, fix_sql_with_error
from pipeline.chart_selector import select_chart_type
from pipeline.chart_config import generate_chart_config

from query.executor import execute_query
from query.validator import QueryValidationError


def process_dashboard_card(card, conversation_history):

    nl_query = card["nl_query"]

    # Intent
    intent = parse_intent(nl_query, conversation_history)

    if intent.get("clarification_needed"):
        return {
            "clarification_needed": True,
            "question": intent["clarification_question"]
        }

    # Schema Matching
    resolved = resolve_schema(intent)

    # SQL Generation
    sql = generate_sql(intent, resolved, conversation_history)

    # Execute SQL
    validated_sql, result_data = execute_query(sql)

    # Chart Selection
    chart_type = select_chart_type(
        intent,
        result_data,
        nl_query
    )

    # Chart Config
    chart_config = generate_chart_config(
        chart_type,
        result_data,
        intent,
        nl_query,
    )

    return {
        "title": card["title"],
        "description": card["description"],
        "sql": validated_sql,
        "chart_type": chart_type,
        "chart_config": chart_config,
        "data": result_data,
        "row_count": len(result_data),
    }


def execute_dashboard(plan, conversation_history):

    dashboard = []

    for card in plan:

        print(f"Generating : {card['title']}")

        result = process_dashboard_card(
            card,
            conversation_history,
        )

        dashboard.append(result)

    return dashboard