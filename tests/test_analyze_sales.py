import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "analyze_sales.py"

spec = importlib.util.spec_from_file_location("analyze_sales", MODULE_PATH)
assert spec is not None and spec.loader is not None
analyze_sales = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyze_sales)


class AnalyzeSalesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = [
            {
                "region": "North",
                "product_category": "Electronics",
                "marketing_channel": "Search",
                "units_sold": 2,
                "unit_price": 100.0,
                "discount_pct": 10.0,
                "delivery_days": 3,
                "satisfaction_score": 4.5,
                "net_sales": 180.0,
                "month": "2025-01",
            },
            {
                "region": "South",
                "product_category": "Furniture",
                "marketing_channel": "Email",
                "units_sold": 1,
                "unit_price": 50.0,
                "discount_pct": 5.0,
                "delivery_days": 7,
                "satisfaction_score": 3.0,
                "net_sales": 47.5,
                "month": "2025-02",
            },
        ]

    def test_group_sum_aggregates_values(self) -> None:
        grouped = analyze_sales.group_sum(self.rows, "region")

        self.assertEqual(grouped["North"], 180.0)
        self.assertEqual(grouped["South"], 47.5)

    def test_build_report_includes_monthly_trend_section(self) -> None:
        report = analyze_sales.build_report(self.rows)

        self.assertIn("## Monthly Revenue Trend", report)
        self.assertIn("2025-01", report)
        self.assertIn("2025-02", report)

    def test_build_report_handles_empty_rows(self) -> None:
        report = analyze_sales.build_report([])

        self.assertIn("No sales data is available", report)


if __name__ == "__main__":
    unittest.main()
