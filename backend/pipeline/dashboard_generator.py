import asyncio
import time

from pipeline.dashboard_planner import generate_dashboard_plan
from pipeline.dashboard_worker import generate_chart_worker


async def _run_worker(recommendation):
    """
    Run one worker in a background thread.
    """
    return await asyncio.to_thread(
        generate_chart_worker,
        recommendation,
    )


async def generate_dashboard(csv_path: str):

    overall = time.perf_counter()

    # ---------------------------------------
    # Step 1 : Generate dashboard plan
    # ---------------------------------------
    print("\nGenerating Dashboard Plan...\n")

    plan = generate_dashboard_plan(csv_path)

    print(f"\nPlanner generated {len(plan)} visualizations.\n")

    # ---------------------------------------
    # Step 2 : Create async tasks
    # ---------------------------------------
    tasks = []

    for recommendation in plan:

        tasks.append(
            asyncio.create_task(
                _run_worker(recommendation)
            )
        )

    print("\nLaunching workers concurrently...\n")

    # ---------------------------------------
    # Step 3 : Wait for all workers
    # ---------------------------------------
    results = await asyncio.gather(
        *tasks,
        return_exceptions=True,
    )

    final_results = []

    for r in results:

        if isinstance(r, Exception):

            print(r)

        else:

            final_results.append(r)

    print(
        f"\nDashboard generated in "
        f"{time.perf_counter()-overall:.2f} sec"
    )

    return final_results


if __name__ == "__main__":

    csv_path = input("Enter CSV Path : ").strip().strip('"')

    dashboard = asyncio.run(
        generate_dashboard(csv_path)
    )

    print("\n================ DASHBOARD =================\n")

    for chart in dashboard:

        print(chart["title"])

    print("\n============================================")