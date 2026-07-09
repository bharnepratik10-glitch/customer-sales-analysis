from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "customer_sales.csv"
REPORT_PATH = ROOT / "reports" / "sales_summary.md"
CHART_DIR = ROOT / "charts"

SalesRow = dict[str, Any]


def money(value: float | int) -> str:
    return f"${float(value):,.2f}"


def load_rows() -> list[SalesRow]:
    rows: list[SalesRow] = []
    with DATA_PATH.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            order_date = datetime.strptime(row["order_date"], "%Y-%m-%d").date()
            units_sold = int(row["units_sold"])
            unit_price = float(row["unit_price"])
            discount_pct = float(row["discount_pct"])
            delivery_days = int(row["delivery_days"])
            satisfaction_score = float(row["satisfaction_score"])
            gross_sales = units_sold * unit_price
            discount_amount = gross_sales * discount_pct / 100
            net_sales = gross_sales - discount_amount

            parsed_row: SalesRow = {
                "region": row["region"],
                "customer_segment": row["customer_segment"],
                "product_category": row["product_category"],
                "units_sold": units_sold,
                "unit_price": unit_price,
                "discount_pct": discount_pct,
                "marketing_channel": row["marketing_channel"],
                "delivery_days": delivery_days,
                "satisfaction_score": satisfaction_score,
                "order_date": order_date,
                "gross_sales": gross_sales,
                "discount_amount": discount_amount,
                "net_sales": net_sales,
                "month": order_date.strftime("%Y-%m"),
            }
            rows.append(parsed_row)
    return rows


def group_sum(rows: list[SalesRow], field: str, value: str = "net_sales") -> dict[str, float]:
    grouped: dict[str, float] = defaultdict(float)
    for row in rows:
        key = str(row.get(field, "unknown"))
        grouped[key] += float(row.get(value, 0.0))
    return dict(sorted(grouped.items()))


def group_average(rows: list[SalesRow], field: str, value: str) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(field, "unknown"))].append(float(row.get(value, 0.0)))
    return {key: mean(values) for key, values in sorted(grouped.items())}


def top_items(grouped: dict[str, float], count: int = 5) -> list[tuple[str, float]]:
    return sorted(grouped.items(), key=lambda item: item[1], reverse=True)[:count]


def svg_bar_chart(
    title: str,
    data: dict[str, float],
    path: Path,
    value_formatter: Callable[[float | int], str] = money,
) -> None:
    width = 900
    margin_left = 170
    margin_right = 40
    margin_top = 58
    row_height = 48
    bar_height = 26
    max_value = max(data.values()) if data else 1
    plot_width = width - margin_left - margin_right

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="420" viewBox="0 0 900 420">',
        '<rect width="900" height="420" fill="#f7f3ea"/>',
        f'<text x="32" y="34" font-family="Arial" font-size="24" font-weight="700" fill="#1f2933">{title}</text>',
    ]

    for index, (label, value) in enumerate(sorted(data.items(), key=lambda item: item[1], reverse=True)):
        y = margin_top + index * row_height
        bar_width = 0 if max_value <= 0 else (value / max_value) * plot_width
        color = ["#2f6f73", "#c65f37", "#6b7f35", "#415a77", "#8c4a62", "#7a6f46"][index % 6]
        lines.extend(
            [
                f'<text x="32" y="{y + 19}" font-family="Arial" font-size="15" fill="#1f2933">{label}</text>',
                f'<rect x="{margin_left}" y="{y}" width="{bar_width:.1f}" height="{bar_height}" rx="3" fill="{color}"/>',
                f'<text x="{margin_left + bar_width + 10:.1f}" y="{y + 19}" font-family="Arial" font-size="14" fill="#1f2933">{value_formatter(value)}</text>',
            ]
        )

    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def svg_line_chart(title: str, data: dict[str, float], path: Path) -> None:
    width = 900
    height = 420
    margin_left = 70
    margin_right = 40
    margin_top = 62
    margin_bottom = 70
    labels = list(data.keys())
    values = list(data.values())

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="420" viewBox="0 0 900 420">',
        '<rect width="900" height="420" fill="#f7f3ea"/>',
        f'<text x="32" y="34" font-family="Arial" font-size="24" font-weight="700" fill="#1f2933">{title}</text>',
        f'<line x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" stroke="#9aa5b1"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" stroke="#9aa5b1"/>',
    ]

    if not values:
        lines.append("</svg>")
        path.write_text("\n".join(lines), encoding="utf-8")
        return

    min_value = min(values)
    max_value = max(values)
    span = max(max_value - min_value, 1.0)
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    points: list[tuple[float, float, float, str]] = []
    for index, value in enumerate(values):
        x = margin_left + (index / max(len(values) - 1, 1)) * plot_width
        y = margin_top + (1 - ((value - min_value) / span)) * plot_height
        points.append((x, y, value, labels[index]))

    point_string = " ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in points)
    lines.append(f'<polyline points="{point_string}" fill="none" stroke="#2f6f73" stroke-width="4"/>')

    for x, y, value, label in points:
        lines.extend(
            [
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#c65f37"/>',
                f'<text x="{x - 28:.1f}" y="{height - 36}" font-family="Arial" font-size="13" fill="#1f2933">{label}</text>',
                f'<text x="{x - 36:.1f}" y="{y - 12:.1f}" font-family="Arial" font-size="13" fill="#1f2933">{money(value)}</text>',
            ]
        )

    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_report(rows: list[SalesRow]) -> str:
    if not rows:
        return "# Customer Sales Analysis Report\n\nNo sales data is available.\n"

    revenue_by_region = group_sum(rows, "region")
    revenue_by_category = group_sum(rows, "product_category")
    revenue_by_channel = group_sum(rows, "marketing_channel")
    revenue_by_month = group_sum(rows, "month")
    satisfaction_by_category = group_average(rows, "product_category", "satisfaction_score")

    total_revenue = sum(float(row["net_sales"]) for row in rows)
    total_orders = len(rows)
    total_units = sum(int(row["units_sold"]) for row in rows)
    avg_order_value = total_revenue / total_orders
    avg_delivery_days = mean(int(row["delivery_days"]) for row in rows)
    avg_satisfaction = mean(float(row["satisfaction_score"]) for row in rows)
    best_region, best_region_value = top_items(revenue_by_region, 1)[0]
    best_category, best_category_value = top_items(revenue_by_category, 1)[0]
    best_channel, best_channel_value = top_items(revenue_by_channel, 1)[0]
    top_satisfaction_category, top_satisfaction_value = max(
        satisfaction_by_category.items(),
        key=lambda item: item[1],
        default=("N/A", 0.0),
    )
    latest_month = max(revenue_by_month.items(), key=lambda item: item[1], default=("N/A", 0.0))[0]

    lines = [
        "# Customer Sales Analysis Report",
        "",
        "## Executive Summary",
        "",
        f"- Total net revenue: **{money(total_revenue)}**",
        f"- Orders analyzed: **{total_orders}**",
        f"- Units sold: **{total_units}**",
        f"- Average order value: **{money(avg_order_value)}**",
        f"- Average delivery time: **{avg_delivery_days:.1f} days**",
        f"- Average satisfaction score: **{avg_satisfaction:.2f}/5.00**",
        f"- Highest revenue region: **{best_region}** with **{money(best_region_value)}**",
        f"- Highest revenue category: **{best_category}** with **{money(best_category_value)}**",
        "",
        "## Revenue By Region",
        "",
    ]

    for region, value in top_items(revenue_by_region, 10):
        lines.append(f"- {region}: {money(value)}")

    lines.extend(["", "## Revenue By Product Category", ""])
    for category, value in top_items(revenue_by_category, 10):
        lines.append(f"- {category}: {money(value)}")

    lines.extend(["", "## Revenue By Marketing Channel", ""])
    for channel, value in top_items(revenue_by_channel, 10):
        lines.append(f"- {channel}: {money(value)}")

    lines.extend(["", "## Monthly Revenue Trend", ""])
    for month, value in top_items(revenue_by_month, 12):
        lines.append(f"- {month}: {money(value)}")

    lines.extend(["", "## Average Satisfaction By Product Category", ""])
    for category, value in sorted(satisfaction_by_category.items(), key=lambda item: item[1], reverse=True):
        lines.append(f"- {category}: {value:.2f}/5.00")

    lines.extend(
        [
            "",
            "## Key Insights",
            "",
            f"- {best_category} generates the most revenue, totaling {money(best_category_value)}.",
            f"- {top_satisfaction_category} has the strongest customer satisfaction at {top_satisfaction_value:.2f}/5.00.",
            f"- {best_channel} contributes the highest channel revenue, totaling {money(best_channel_value)}.",
            f"- The latest monthly revenue point is {latest_month}, which helps frame the current growth trend.",
            "",
            "## Generated Charts",
            "",
            "- `charts/revenue_by_region.svg`",
            "- `charts/revenue_by_category.svg`",
            "- `charts/monthly_revenue.svg`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = load_rows()
    CHART_DIR.mkdir(exist_ok=True)
    REPORT_PATH.parent.mkdir(exist_ok=True)

    svg_bar_chart("Revenue by Region", group_sum(rows, "region"), CHART_DIR / "revenue_by_region.svg")
    svg_bar_chart("Revenue by Product Category", group_sum(rows, "product_category"), CHART_DIR / "revenue_by_category.svg")
    svg_line_chart("Monthly Revenue Trend", group_sum(rows, "month"), CHART_DIR / "monthly_revenue.svg")
    REPORT_PATH.write_text(build_report(rows), encoding="utf-8")
    print(f"Report written to {REPORT_PATH}")
    print(f"Charts written to {CHART_DIR}")


if __name__ == "__main__":
    main()
