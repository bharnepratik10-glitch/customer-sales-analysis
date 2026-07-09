# Customer Sales Analysis

This project analyzes a sample retail customer sales dataset and turns raw order data into a short business report with charts.

## Project Structure

```text
customer-sales-analysis/
  data/
    customer_sales.csv
  src/
    analyze_sales.py
  charts/
    revenue_by_region.svg
    revenue_by_category.svg
    monthly_revenue.svg
  reports/
    sales_summary.md
  README.md
  requirements.txt
  .gitignore
```

## Dataset

The dataset contains 60 customer orders from January through June 2025. Each row includes:

- Order date
- Region
- Customer segment
- Product category
- Units sold
- Unit price
- Discount percentage
- Marketing channel
- Delivery days
- Satisfaction score

The analysis script calculates net sales after discount and summarizes revenue performance across regions, categories, channels, and months.

## Questions Answered

- Which region generates the most revenue?
- Which product category performs best?
- Which marketing channels contribute the most sales?
- How does monthly revenue change over time?
- Which categories have the highest customer satisfaction?

## How To Run

This project uses only the Python standard library.

```bash
python src/analyze_sales.py
```

Running the script regenerates:

- `reports/sales_summary.md`
- `charts/revenue_by_region.svg`
- `charts/revenue_by_category.svg`
- `charts/monthly_revenue.svg`

## Running Tests

To run the automated test suite:

```bash
python -m unittest discover -s tests -v
```

## Key Findings

- Electronics generates the highest net revenue because of higher unit prices.
- Office Supplies has the highest satisfaction scores and faster delivery times.
- Search is the strongest marketing channel by revenue.
- Furniture orders show a pattern of longer delivery times and lower satisfaction.

## Suggested Improvements

- Add profit margin data to compare revenue with profitability.
- Add customer IDs for retention and repeat-purchase analysis.
- Add city-level geography for more detailed regional analysis.
- Convert the script into a notebook for portfolio storytelling.

## License

This sample project and dataset are provided for educational and portfolio use.
