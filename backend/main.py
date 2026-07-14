import os
import json
import shutil
import time
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


load_dotenv()

from catalog.db import (
    init_db, get_all_schema, save_chart, get_charts,
    save_dashboard, get_dashboards, update_dashboard_layout, get_aliases, save_alias
)
from catalog.save_chart_file import save_chart_image
from catalog.crawler import crawl_all, crawl_file
from catalog.watcher import start_watcher, stop_watcher
from pipeline.intent_parser import parse_intent
from pipeline.schema_matcher import resolve_schema
from pipeline.sql_generator import generate_sql, fix_sql_with_error
from pipeline.chart_selector import select_chart_type
from pipeline.chart_config import generate_chart_config
from query.executor import execute_query
from query.validator import QueryValidationError
from pipeline.dashboard_planner import generate_dashboard_plan
from pipeline.dashboard_executor import execute_dashboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    crawl_all()
    start_watcher()
    yield
    stop_watcher()


app = FastAPI(title="AI Dashboard Builder", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Models ───────────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    nl_query: str
    conversation_history: list[dict] = []
    dashboard_id: int | None = None


class RefineRequest(BaseModel):
    nl_query: str
    chart_id: int
    conversation_history: list[dict] = []


class RunSQLRequest(BaseModel):
    sql: str
    nl_query: str = ""


class DashboardCreate(BaseModel):
    name: str


class LayoutUpdate(BaseModel):
    layout_config: list[dict]


class AliasCreate(BaseModel):
    alias: str
    file_id: int
    column_name: str

class GenerateDashboardRequest(BaseModel):
    filename: str
# ─── Schema ───────────────────────────────────────────────────────────────────

@app.get("/api/schema")
def get_schema():
    return {"files": get_all_schema()}


@app.post("/api/schema/refresh")
def refresh_schema():
    crawl_all()
    return {"status": "ok", "files": get_all_schema()}

@app.post("/api/upload")
async def upload_csv(
    file: UploadFile = File(...),
    access_key: str = Form("")
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )

    # Maximum file size = 10 MB
    MAX_FILE_SIZE = 100 * 1024

    contents = await file.read()

    has_access = access_key == ACCESS_KEY

    if not has_access and len(contents) > MAX_FILE_SIZE:
     raise HTTPException(
        status_code=400,
        detail="CSV file size must not exceed 100 KB without a valid access key."
    )

    file.file.seek(0)

    # Save inside backend/../csvs
    csv_folder = Path(__file__).parent.parent / "csvs"
    csv_folder.mkdir(parents=True, exist_ok=True)

    file_path = csv_folder / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Crawl only this file
    info = crawl_file(str(file_path))

    from catalog.db import upsert_csv_file, replace_columns

    file_id = upsert_csv_file(
        info["filename"],
        info["filepath"],
        info["row_count"],
        info["last_modified"],
    )

    replace_columns(file_id, info["columns"])

    return {
        "status": "success",
        "filename": info["filename"],
        "rows": info["row_count"],
        "columns": len(info["columns"]),
    }

    # Save inside backend/../csvs
    csv_folder = Path(__file__).parent.parent / "csvs"
    csv_folder.mkdir(parents=True, exist_ok=True)

    file_path = csv_folder / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Crawl only this file
    info = crawl_file(str(file_path))

    from catalog.db import upsert_csv_file, replace_columns

    file_id = upsert_csv_file(
        info["filename"],
        info["filepath"],
        info["row_count"],
        info["last_modified"],
    )

    replace_columns(file_id, info["columns"])

    return {
        "status": "success",
        "filename": info["filename"],
        "rows": info["row_count"],
        "columns": len(info["columns"]),
    }



@app.get("/api/aliases")
def list_aliases():
    return {"aliases": get_aliases()}


@app.post("/api/aliases")
def create_alias(body: AliasCreate):
    save_alias(body.alias, body.file_id, body.column_name)
    return {"status": "ok"}


# ─── Chart Generation ─────────────────────────────────────────────────────────

def _run_pipeline(nl_query: str, conversation_history: list[dict]) -> dict:
    intent = parse_intent(nl_query, conversation_history)

    if intent.get("clarification_needed"):
        return {
            "clarification_needed": True,
            "question": intent.get("clarification_question", "Can you clarify your request?"),
        }
    start = time.perf_counter()

    resolved = resolve_schema(intent)

    end = time.perf_counter()

    print(f"[TIME] Schema Matching: {end-start:.3f} sec")
    

    print("="*60)
    print(intent)
    print("=" * 60)
    print(resolved)


    start_sql = time.perf_counter()
    sql = generate_sql(intent, resolved, conversation_history)

    end_sql = time.perf_counter()

    sql_generation_time = end_sql - start_sql

    print(f"[Timing] SQL generation took {sql_generation_time:.3f} seconds")
    print("=" * 60)
    print(sql)
    print("=" * 60)
    #
    validated_sql, result_data = None, None
    last_error = None
    for attempt in range(3):
        try:
            validated_sql, result_data = execute_query(sql)
            break
        except QueryValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except RuntimeError as e:
            last_error = str(e)
            if attempt < 2:
                sql = fix_sql_with_error(sql, last_error, intent, resolved)
            else:
                raise HTTPException(status_code=500, detail=f"Could not generate a working query: {last_error}")

    print("=" * 60)
    print(validated_sql)
    print("\n================ RESULT DATA ================")
    print(f"Rows returned: {len(result_data)}")

    for i, row in enumerate(result_data[:15]):
     print(f"{i}: {row}")

    print("=============================================\n")
    print("=" * 60)
    print(result_data)

    start = time.perf_counter()

    chart_type = select_chart_type(intent, result_data, nl_query)

    end = time.perf_counter()

    print(f"[TIME] Chart Selection: {end-start:.3f} sec")
    start = time.perf_counter()

    chart_config = generate_chart_config(
    chart_type,
    result_data,
    intent,
    nl_query,
)

    end = time.perf_counter()

    print(f"[TIME] Chart Config: {end-start:.3f} sec")

    print("=" * 60)
    print(chart_type)
    print("=" * 60)
    print(chart_config)

    return {
    "clarification_needed": False,
    "question": None,
    "intent": intent,
    "sql": validated_sql,
    "chart_type": chart_type,
    "chart_config": chart_config,
    "row_count": len(result_data),
    "data": result_data,
}


@app.post("/api/charts/generate")
def generate_chart(body: GenerateRequest):
    result = _run_pipeline(body.nl_query, body.conversation_history)

    if result.get("clarification_needed"):
        return result
    
    history = body.conversation_history + [
    {"role": "user", "content": body.nl_query},
    {
        "role": "assistant",
        "content": "Chart generated.",
        "sql": result["sql"],
    },
]

    

    start = time.perf_counter()

    save_chart_image(result["chart_config"])

    end = time.perf_counter()

    print(f"[TIME] Save Chart: {end-start:.3f} sec")

    chart_id = save_chart(
    body.dashboard_id,
    body.nl_query,
    result["sql"],
    result["chart_config"],
    history,
)

    return {
    **result,
    "chart_id": chart_id,
}

    # history = body.conversation_history + [
    #     {"role": "user", "content": body.nl_query},
    #     {"role": "assistant", "content": "Chart generated.", "sql": result["sql"]},
    # ]
    #
    
    # chart_id = save_chart(
    #     body.dashboard_id,
    #     body.nl_query,
    #     result["sql"],
    #     result["chart_config"],
    #     history,
    # )
    #
    # return {**result, "chart_id": chart_id}


@app.post("/api/charts/{chart_id}/refine")
def refine_chart(chart_id: int, body: RefineRequest):
    result = _run_pipeline(body.nl_query, body.conversation_history)

    if result.get("clarification_needed"):
        return result

    history = body.conversation_history + [
        {"role": "user", "content": body.nl_query},
        {"role": "assistant", "content": "Chart updated.", "sql": result["sql"]},
    ]

    new_chart_id = save_chart(
        None,
        body.nl_query,
        result["sql"],
        result["chart_config"],
        history,
    )

    return {**result, "chart_id": new_chart_id}


@app.post("/api/charts/run-sql")
def run_custom_sql(body: RunSQLRequest):
    try:
        validated_sql, result_data = execute_query(body.sql)
    except QueryValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    chart_type = "table"
    chart_config = generate_chart_config(chart_type, result_data, {}, body.nl_query or body.sql)

    return {
    "clarification_needed": False,
    "question": None,
    "intent": {},
    "sql": validated_sql,
    "chart_type": chart_type,
    "chart_config": chart_config,
    "row_count": len(result_data),
    "data": result_data,
}


@app.get("/api/charts")
def list_charts(dashboard_id: int | None = None):
    return {"charts": get_charts(dashboard_id)}


# ─── Dashboards ───────────────────────────────────────────────────────────────

@app.post("/api/dashboards")
def create_dashboard(body: DashboardCreate):
    did = save_dashboard(body.name)
    return {"id": did, "name": body.name}


@app.get("/api/dashboards")
def list_dashboards():
    return {"dashboards": get_dashboards()}


@app.put("/api/dashboards/{dashboard_id}/layout")
def update_layout(dashboard_id: int, body: LayoutUpdate):
    update_dashboard_layout(dashboard_id, body.layout_config)
    return {"status": "ok"}



import math
def clean_json(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj

    if isinstance(obj, dict):
        return {
            k: clean_json(v)
            for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [
            clean_json(x)
            for x in obj
        ]

    return obj



ACCESS_KEY = "hie123"

class VerifyRequest(BaseModel):
    key: str

@app.post("/api/verify-key")
def verify_key(req: VerifyRequest):
    return {"valid": req.key == ACCESS_KEY}
@app.post("/api/dashboard/generate")
def generate_dashboard(body: GenerateDashboardRequest):

    csv_path = (
        Path(__file__).parent.parent
        / "csvs"
        / body.filename
    )

    if not csv_path.exists():
        raise HTTPException(
            status_code=404,
            detail="CSV not found."
        )

    planner_start = time.perf_counter()

    plan = generate_dashboard_plan(str(csv_path))

    planner_end = time.perf_counter()

    print(
        f"[TIME] Dashboard Planner: "
        f"{planner_end - planner_start:.3f} sec"
    )

    executor_start = time.perf_counter()

    dashboard = execute_dashboard(
        plan,
        [],
    )

    executor_end = time.perf_counter()

    print(
        f"[TIME] Dashboard Executor: "
        f"{executor_end - executor_start:.3f} sec"
    )
    print(json.dumps(dashboard, indent=2, default=str))
    dashboard = clean_json(dashboard)
    return {
        

        
        "cards": dashboard
    }

# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    schema = get_all_schema()
    return {
        "status": "ok",
        "csv_files": len(schema),
        "model_path_set": bool(os.getenv("GEMMA_MODEL_PATH")),
    }
