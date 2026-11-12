# Financial Performance & Controlling Dashboard

Learning portfolio project: Power BI, Power Query, DAX, financial controlling and Git.

## Dataset
All data is **synthetic**, generated reproducibly with `scripts/generate_data.py` (random seed 42). Currency: EUR. Each record is one month × cost center × product. The date is the first day of the month and represents the month, not a transaction date.

- `actuals.csv`: monthly actual revenue and costs
- `budget.csv`: monthly planned revenue and costs
- `cost_centers.csv`: cost center dimension
- `products.csv`: product dimension

## Measures to implement
Revenue, Costs, Operating Profit = Revenue - Costs, Operating Margin = Operating Profit / Revenue, Budget Revenue, Budget Costs, Budget Profit, Revenue Variance = Revenue - Budget Revenue, Cost Variance = Costs - Budget Costs.

## Model
Use a star schema with shared Date, Product and Cost Center dimensions filtering both fact tables (Actuals and Budget). Do not directly relate the two fact tables.

## Run
`python3 scripts/generate_data.py`

## Roadmap
- [ ] Week 1: inspect and clean data
- [ ] Week 2: create Power BI star schema
- [ ] Week 3: DAX measures and validation
- [ ] Week 4: executive overview
- [ ] Week 5: variance and profitability dashboards
- [ ] Week 6: screenshots and findings

## Privacy
No company, customer, or internship data are included.
