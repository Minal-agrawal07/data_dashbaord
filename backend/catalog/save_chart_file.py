import os
import matplotlib.pyplot as plt
from pathlib import Path


def save_chart_image(
    chart_config,
    base_folder=Path(__file__).resolve().parent.parent / "output",
):
    print("TYPE:", type(chart_config))
    print("CONFIG:", chart_config)
    print("TYPE:", type(chart_config))
    print("CONFIG:", chart_config)
    

    chart_type = (
    chart_config.get("type")
    or chart_config.get("series", [{}])[0].get("type", "bar")
)

    title = chart_config.get("title", {})
    if isinstance(title, dict):
        title = title.get("text", "Chart")
    else:
        title = str(title)


        
    if chart_type in ["bar", "line"]:

        labels = chart_config["xAxis"]["data"]
        values = chart_config["series"][0]["data"]

        plt.figure(figsize=(8, 5))

        if chart_type == "bar":
            plt.bar(labels, values)
        else:
            plt.plot(labels, values, marker="o")

        plt.title(title)
        plt.xlabel(chart_config["xAxis"].get("name", ""))
        plt.ylabel(chart_config["yAxis"].get("name", ""))

    elif chart_type == "pie":

        labels = [x["name"] for x in chart_config["series"][0]["data"]]
        values = [x["value"] for x in chart_config["series"][0]["data"]]

        plt.figure(figsize=(6, 6))
        plt.pie(values, labels=labels, autopct="%1.1f%%")
        plt.title(title)

    else:
        print(f"Chart type '{chart_type}' not supported for saving.")
        return
    base_folder.mkdir(parents=True, exist_ok=True)

    output_file = base_folder / "chart.png"

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close("all")

    print("Saved:", output_file.resolve())
