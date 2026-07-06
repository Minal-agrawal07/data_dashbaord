import json
import time
from pathlib import Path

from catalog.db import get_all_schema
from local_llm import generate


PROMPT_PATH = (
    Path(__file__).parent.parent
    / "prompts"
    / "visualisation.txt"
)
def load_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def build_schema_summary(csv_path: str) -> str:
    filename = Path(csv_path).name

    schema = get_all_schema()

    selected = None

    for file in schema:
        if file["filename"] == filename:
            selected = file
            break

    if selected is None:
        raise ValueError(f"{filename} not found in schema catalog.")

    lines = []

    lines.append(f"Dataset: {selected['filename']}")
    lines.append(f"Rows: {selected['row_count']}")
    lines.append("Columns:")

    for col in selected["columns"]:
        sample = ", ".join(map(str, col["sample_values"][:3]))

        lines.append(
            f"- {col['column_name']} "
            f"({col['data_type']}) "
            f"Samples: [{sample}]"
        )

    return "\n".join(lines)


def generate_dashboard_plan(csv_path: str):

    system_prompt = load_prompt()

    schema_text = build_schema_summary(csv_path)

    user_prompt = f"""
Dataset Schema

{schema_text}

Generate the executive dashboard plan.
"""

    print("\n" + "=" * 80)
    print("SYSTEM PROMPT")
    print(system_prompt)

    print("\n" + "=" * 80)
    print("USER PROMPT")
    print(user_prompt)

    start = time.perf_counter()

    raw = generate(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        max_tokens=700,
        temperature=0.1,
    )

    end = time.perf_counter()

    print(f"\nLLM Time: {end-start:.2f} sec")

    print("\n" + "=" * 80)
    print("RAW RESPONSE")
    print(raw)

    raw = raw.strip()

    if raw.startswith("```json"):
        raw = raw[len("```json"):]

    if raw.startswith("```"):
        raw = raw[3:]

    if raw.endswith("```"):
        raw = raw[:-3]

    raw = raw.strip()

    return json.loads(raw)


if __name__ == "__main__":

    csv_path = input("Enter CSV path: ").strip()

    plan = generate_dashboard_plan(csv_path)

    print("\n")
    print("=" * 80)
    print("FINAL DASHBOARD PLAN")
    print("=" * 80)

    print(json.dumps(plan, indent=4))