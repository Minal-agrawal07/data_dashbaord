import json
from pathlib import Path

from catalog.db import get_all_schema
from local_llm import generate


PROMPT_PATH = (
    Path(__file__).parent.parent
    / "prompts"
    / "visualisation.txt"
)


def _load_prompt() -> str:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()
from pathlib import Path



def build_schema_summary(csv_path: str) -> str:
    """
    Build schema summary for a CSV using its full path.
    """

    filename = Path(csv_path).name

    schema = get_all_schema()

    selected = None

    for file in schema:
        if file["filename"] == filename:
            selected = file
            break

    if selected is None:
        raise ValueError(f"CSV not found in catalog: {filename}")

    lines = []

    lines.append(f"Dataset: {selected['filename']}")
    lines.append(f"Rows: {selected['row_count']}")
    lines.append("Columns:")

    for col in selected["columns"]:

        sample = ", ".join(col["sample_values"][:3])

        lines.append(
            f"- {col['column_name']} "
            f"({col['data_type']}) "
            f"Samples: [{sample}]"
        )

    return "\n".join(lines)
import re
import time
def generate_dashboard_plan(csv_path: str):
    overall = time.perf_counter()
    system_prompt = _load_prompt()
 

    start = time.perf_counter()
    schema_text = build_schema_summary(csv_path)
    end = time.perf_counter()

    print(f"[TIME] Schema Summary: {end-start:.3f} sec")

    user_prompt = f"""
Dataset Schema

{schema_text}

Generate the executive dashboard plan.
"""

    print("=" * 80)
    print("SCHEMA SENT TO GEMMA")
    print(schema_text)
    print("=" * 80)

    raw = generate(
    user_prompt=user_prompt,
    system_prompt=system_prompt,
    max_tokens=900,
    temperature=0.1,
)

    print("=" * 80)
    print("RAW DASHBOARD PLAN")
    print(raw)
    print("=" * 80)

    try:

     raw = raw.strip()

    # Remove markdown if Gemma returns ```json
     if raw.startswith("```json"):
        raw = raw[len("```json"):]

     if raw.startswith("```"):
        raw = raw[3:]

     if raw.endswith("```"):
        raw = raw[:-3]

     raw = raw.strip()

     return json.loads(raw)

    except Exception:

     print("Planner JSON parsing failed.")

     raise RuntimeError(
        f"Dashboard planner returned invalid JSON.\n\n{raw}"
    )
    
if __name__ == "__main__":

    csv_path = input("Enter full CSV path: ").strip()

    plan = generate_dashboard_plan(csv_path)

    print("\n================ DASHBOARD PLAN ================\n")
    print(json.dumps(plan, indent=4))
    print("\n===============================================\n")