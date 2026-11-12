# Financial Performance & Controlling Dashboard

An interactive financial controlling dashboard built with **Python, Streamlit, Pandas, and Plotly**.

This portfolio project demonstrates how financial data can be analyzed, visualized, and transformed into actionable management insights.

## Project Overview

The dashboard provides an interactive overview of financial performance across different business years, cost centers, and products.

It enables users to monitor financial KPIs, compare actual performance against budget targets, analyze profitability, and identify financial trends.

The project focuses on practical applications of financial controlling, business analytics, and data-driven decision-making.

## Key Features

### Financial KPI Monitoring
- Revenue
- Costs
- Operating Profit
- Operating Margin

### Budget vs. Actual Analysis
- Revenue variance
- Cost variance
- Operating profit variance
- Monthly actual vs. budget revenue comparison

### Cost Center Analysis
- Comparison of actual costs against budgeted costs
- Identification of budget overruns and cost savings
- Interactive visualization of cost variances

### Product Profitability
- Operating profit analysis by product
- Product-level profitability comparison

### Year-over-Year Analysis
- Comparison of financial performance between 2024 and 2025
- Revenue, cost, and operating profit growth rates
- Operating margin development

### Automated Controlling Insights
- Rule-based interpretation of revenue changes
- Identification of increasing or decreasing costs
- Assessment of operating margin development

### Interactive Filters
- Business year
- Cost center
- Product

### Data Validation
- Missing value detection
- Duplicate record detection
- Actual and budget data consistency checks
- Financial value plausibility checks
- Calculation consistency checks

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Financial calculations and application logic |
| Pandas | Data processing and aggregation |
| Streamlit | Interactive dashboard interface |
| Plotly | Financial data visualization |
| Git & GitHub | Version control and project documentation |

## Dataset

All financial data used in this project is **synthetic** and does not contain confidential company or customer information.

The data is generated reproducibly using `scripts/generate_data.py` with a fixed random seed.

The dataset includes monthly financial records for 2024 and 2025 across four cost centers and three products.

Main datasets:

- `actuals.csv` – Actual revenue and costs
- `budget.csv` – Budgeted revenue and costs
- `cost_centers.csv` – Cost center reference data
- `products.csv` – Product reference data

## Financial Calculations

**Operating Profit**

Operating Profit = Revenue − Costs

**Operating Margin**

Operating Margin = Operating Profit / Revenue × 100

**Revenue Variance**

Revenue Variance = Actual Revenue − Budget Revenue

**Cost Variance**

Cost Variance = Actual Costs − Budget Costs

**Operating Profit Variance**

Operating Profit Variance = Actual Operating Profit − Budget Operating Profit

Operating profit is a simplified measure based on the revenue and costs included in the synthetic dataset. It should not be interpreted as formally reported EBIT.

## How to Run the Dashboard

1. Clone the repository:

   `git clone https://github.com/tamerazizdemiral/financial-controlling-powerbi.git`

2. Navigate to the project directory:

   `cd financial-controlling-powerbi`

3. Create a virtual environment:

   `python3 -m venv .venv`

4. Activate the environment on macOS or Linux:

   `source .venv/bin/activate`

5. Install dependencies:

   `pip install -r requirements.txt`

6. Launch the dashboard:

   `streamlit run app.py`

The dashboard will open in your browser.

## Business Value

The dashboard demonstrates how financial data analytics can support management decision-making through:

- Transparent monitoring of financial performance
- Early identification of budget deviations
- Cost center performance analysis
- Product profitability assessment
- Year-over-year financial comparisons
- Automated interpretation of selected financial KPIs

## Future Improvements

Potential extensions include:

- Financial data integration from external sources
- Additional financial KPIs and forecasting
- Automated reporting and export functionality
- More advanced variance analysis
- Online deployment

## Data Privacy

All data is artificially generated for educational and portfolio purposes.

No confidential company, customer, or internship information is included.