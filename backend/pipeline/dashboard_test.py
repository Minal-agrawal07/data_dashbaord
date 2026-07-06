import time

from pipeline.dashboard_planner import generate_dashboard_plan
from pipeline.dashboard_executor import execute_dashboard
import json

csv_path = r"C:\Users\agraw\OneDrive\Desktop\projectsss\data_dashboard_deepseek\data_dashboard_gemma\data_dashboard_gemma_final\data_dashboard\csvs\website_traffic.csv"

# ---------------- Overall Timer ----------------
overall_start = time.perf_counter()

# ---------------- Dashboard Planner ----------------
planner_start = time.perf_counter()

# Generate dashboard plan
plan = generate_dashboard_plan(csv_path)

planner_end = time.perf_counter()

print(f"\n[TIME] Dashboard Planner: {planner_end - planner_start:.3f} sec")

print("\n========== DASHBOARD PLAN ==========\n")
print(json.dumps(plan, indent=4))

# Execute dashboard

# ---------------- Dashboard Executor ----------------
executor_start = time.perf_counter()

dashboard = execute_dashboard(
    plan,
    []
)
executor_end = time.perf_counter()

print(f"\n[TIME] Dashboard Executor: {executor_end - executor_start:.3f} sec")

# ---------------- Overall ----------------
overall_end = time.perf_counter()

print("=" * 70)
print(f"[TIME] TOTAL PIPELINE: {overall_end - overall_start:.3f} sec")
print("=" * 70)

print("\n========== FINAL DASHBOARD ==========\n")
print("\n========== FINAL DASHBOARD ==========\n")

for i, chart in enumerate(dashboard, 1):
    print(f"\nChart {i}")
    print("Title:", chart["title"])
    print("SQL:")
    print(chart["sql"])
    print("Chart Type:", chart["chart_type"])
    print("Rows:", chart["row_count"])