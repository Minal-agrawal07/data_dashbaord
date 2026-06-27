import time

from pipeline.intent_parser import parse_intent
from pipeline.schema_matcher import resolve_schema
from pipeline.sql_generator import generate_sql
from pipeline.chart_selector import select_chart_type
from pipeline.chart_config import generate_chart_config
from query.executor import execute_query
from query.validator import QueryValidationError
from catalog.save_chart_file import save_chart_image


def generate_chart_worker(recommendation: dict):
    """
    Generate one dashboard chart from one planner recommendation.
    """

    nl_query = recommendation["nl_query"]

    print(f"\n{'='*70}")
    print(f"[Worker] {recommendation['title']}")
    print(f"{'='*70}")

    overall_start = time.perf_counter()

    # ----------------------------
    # Intent
    # ----------------------------
    start = time.perf_counter()

    intent = parse_intent(nl_query, [])

    print(f"[TIME] Intent Parsing: {time.perf_counter()-start:.3f}s")

    # ----------------------------
    # Schema Matching
    # ----------------------------
    start = time.perf_counter()

    resolved = resolve_schema(intent)

    print(f"[TIME] Schema Matching: {time.perf_counter()-start:.3f}s")

    # ----------------------------
    # SQL Generation
    # ----------------------------
    start = time.perf_counter()

    sql = generate_sql(intent, resolved, [])

    print(f"[TIME] SQL Generation: {time.perf_counter()-start:.3f}s")

    # ----------------------------
    # SQL Execution
    # ----------------------------
    start = time.perf_counter()

    try:
        validated_sql, result_data = execute_query(sql)

    except QueryValidationError as e:
        return {
            "title": recommendation["title"],
            "error": str(e),
        }

    except RuntimeError as e:
        return {
            "title": recommendation["title"],
            "error": str(e),
        }

    print(f"[TIME] SQL Execution: {time.perf_counter()-start:.3f}s")

    # ----------------------------
    # Chart Selection
    # ----------------------------
    start = time.perf_counter()

    chart_type = select_chart_type(
        intent,
        result_data,
        nl_query,
    )

    print(f"[TIME] Chart Selection: {time.perf_counter()-start:.3f}s")

    # ----------------------------
    # Chart Config
    # ----------------------------
    start = time.perf_counter()

    chart_config = generate_chart_config(
        chart_type,
        result_data,
        intent,
        nl_query,
    )

    print(f"[TIME] Chart Config: {time.perf_counter()-start:.3f}s")

    # ----------------------------
    # Save Image
    # ----------------------------
    start = time.perf_counter()

    image_path = save_chart_image(
        chart_config,
        filename=f"chart_{recommendation['priority']}.png",
    )

    print(f"[TIME] Save Image: {time.perf_counter()-start:.3f}s")

    print(
        f"[TIME] TOTAL ({recommendation['title']}): "
        f"{time.perf_counter()-overall_start:.3f}s"
    )

    return {
        "priority": recommendation["priority"],
        "title": recommendation["title"],
        "description": recommendation["description"],
        "nl_query": recommendation["nl_query"],
        "sql": validated_sql,
        "chart_type": chart_type,
        "chart_config": chart_config,
        "image_path": image_path,
        "rows": len(result_data),
    }