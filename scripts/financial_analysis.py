
from pathlib import Path
import pandas as pd

# 1. Projektordner bestimmen
project_dir = Path(__file__).resolve().parent.parent

# 2. Finanzdaten laden
actuals = pd.read_csv(
    project_dir / "data" / "actuals.csv",
    parse_dates=["Date"]
)

budget = pd.read_csv(
    project_dir / "data" / "budget.csv",
    parse_dates=["Date"]
)

# 3. Daten auf das Jahr 2025 begrenzen
actuals_2025 = actuals[
    actuals["Date"].dt.year == 2025
]

budget_2025 = budget[
    budget["Date"].dt.year == 2025
]

# 4. Ist-Kennzahlen berechnen
actual_revenue = actuals_2025["Revenue"].sum()
actual_costs = actuals_2025["Costs"].sum()
actual_profit = actual_revenue - actual_costs

actual_margin = (
    actual_profit / actual_revenue * 100
    if actual_revenue != 0 else 0
)

# 5. Budget-Kennzahlen berechnen
budget_revenue = budget_2025["BudgetRevenue"].sum()
budget_costs = budget_2025["BudgetCosts"].sum()
budget_profit = budget_revenue - budget_costs

# 6. Abweichungen berechnen
revenue_variance = actual_revenue - budget_revenue
cost_variance = actual_costs - budget_costs
profit_variance = actual_profit - budget_profit

# 7. Prozentuale Abweichungen
revenue_variance_pct = (
    revenue_variance / budget_revenue * 100
    if budget_revenue != 0 else 0
)

cost_variance_pct = (
    cost_variance / budget_costs * 100
    if budget_costs != 0 else 0
)

profit_variance_pct = (
    profit_variance / abs(budget_profit) * 100
    if budget_profit != 0 else 0
)

# 8. Ergebnisse ausgeben
print("\n========== FINANCIAL REPORT 2025 ==========")

print(f"Umsatz Ist:          {actual_revenue:,.2f} EUR")
print(f"Umsatz Budget:       {budget_revenue:,.2f} EUR")
print(f"Umsatzabweichung:    {revenue_variance:+,.2f} EUR "
      f"({revenue_variance_pct:+.2f} %)")

print()

print(f"Kosten Ist:          {actual_costs:,.2f} EUR")
print(f"Kosten Budget:       {budget_costs:,.2f} EUR")
print(f"Kostenabweichung:    {cost_variance:+,.2f} EUR "
      f"({cost_variance_pct:+.2f} %)")

print()

print(f"Ergebnis Ist:        {actual_profit:,.2f} EUR")
print(f"Ergebnis Budget:     {budget_profit:,.2f} EUR")
print(f"Ergebnisabweichung:  {profit_variance:+,.2f} EUR "
      f"({profit_variance_pct:+.2f} %)")

print()
print(f"Operative Marge:     {actual_margin:.2f} %")

print("===========================================")


# 9. Kostenstellenanalyse für 2025

# Ist-Werte nach Kostenstelle gruppieren
cost_center_actuals = (
    actuals_2025
    .groupby("CostCenterID")[["Revenue", "Costs"]]
    .sum()
    .reset_index()
)

# Budgetwerte nach Kostenstelle gruppieren
cost_center_budget = (
    budget_2025
    .groupby("CostCenterID")[["BudgetRevenue", "BudgetCosts"]]
    .sum()
    .reset_index()
)

# Ist- und Budgetwerte zusammenführen
cost_center_analysis = pd.merge(
    cost_center_actuals,
    cost_center_budget,
    on="CostCenterID",
    how="outer",
    validate="one_to_one"
)

# Fehlende Werte erkennen
if cost_center_analysis.isna().any().any():
    raise ValueError("Fehlende Ist- oder Budgetwerte gefunden.")

# Operatives Ergebnis berechnen
cost_center_analysis["OperatingProfit"] = (
    cost_center_analysis["Revenue"]
    - cost_center_analysis["Costs"]
)

# Absolute Kostenabweichung
cost_center_analysis["CostVariance"] = (
    cost_center_analysis["Costs"]
    - cost_center_analysis["BudgetCosts"]
)

# Prozentuale Kostenabweichung
cost_center_analysis["CostVariancePct"] = (
    cost_center_analysis["CostVariance"]
    / cost_center_analysis["BudgetCosts"].replace(0, float("nan"))
    * 100
)

# Nach höchster Kostenüberschreitung sortieren
cost_center_analysis = cost_center_analysis.sort_values(
    by="CostVariance",
    ascending=False
)

# Ergebnisse anzeigen
print("\n========== COST CENTER ANALYSIS 2025 ==========")

print(
    cost_center_analysis[
        [
            "CostCenterID",
            "Costs",
            "BudgetCosts",
            "CostVariance",
            "CostVariancePct",
            "OperatingProfit"
        ]
    ].round(2).to_string(index=False)
)

print("===============================================")

import matplotlib.pyplot as plt

# Monatliche Umsätze berechnen
monthly_actuals = (
    actuals_2025.groupby("Date")["Revenue"]
    .sum()
)

monthly_budget = (
    budget_2025.groupby("Date")["BudgetRevenue"]
    .sum()
)

# Diagramm erstellen
plt.figure(figsize=(12, 6))

plt.plot(
    monthly_actuals.index,
    monthly_actuals.values,
    marker="o",
    label="Umsatz Ist"
)

plt.plot(
    monthly_budget.index,
    monthly_budget.values,
    marker="o",
    label="Umsatz Budget"
)

plt.title("Monatliche Umsatzentwicklung 2025")
plt.xlabel("Monat")
plt.ylabel("Umsatz in EUR")

plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

# Diagramm speichern
output_dir = project_dir / "outputs"
output_dir.mkdir(exist_ok=True)

plt.savefig(
    output_dir / "revenue_2025.png",
    dpi=150
)

plt.show()

