
from pathlib import Path

import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import math

# 1. Seiteneinstellungen
st.set_page_config(
    page_title="Financial Controlling Dashboard",
    page_icon="📊",
    layout="wide"
)

# 2. Daten laden
project_dir = Path(__file__).resolve().parent

actuals = pd.read_csv(
    project_dir / "data" / "actuals.csv",
    parse_dates=["Date"]
)

# Budgetdaten laden
budget = pd.read_csv(
    project_dir / "data" / "budget.csv",
    parse_dates=["Date"]
)

# 2.1 Datenqualität prüfen

def check_data_quality(df, dataset_name, financial_columns):
    missing_values = df.isna().sum().sum()
    duplicate_rows = df.duplicated().sum()

    invalid_values = 0

    for column in financial_columns:
        numeric_values = pd.to_numeric(df[column], errors="coerce")
        invalid_values += (
            numeric_values.isna() & df[column].notna()
        ).sum()

    if missing_values > 0 or duplicate_rows > 0 or invalid_values > 0:
        st.error(
            f"Datenqualitätsproblem in {dataset_name}: "
            f"{missing_values} fehlende Werte, "
            f"{duplicate_rows} doppelte Zeilen und "
            f"{invalid_values} ungültige Finanzwerte."
        )
        st.stop()


check_data_quality(
    actuals,
    "Ist-Daten",
    ["Revenue", "Costs"]
)

check_data_quality(
    budget,
    "Budgetdaten",
    ["BudgetRevenue", "BudgetCosts"]
)

# 2.2 Konsistenz zwischen Ist- und Budgetdaten prüfen

# Diese Spalten identifizieren einen Datensatz eindeutig
key_columns = ["Date", "CostCenterID", "ProductID"]

# Prüfen, ob Kombinationen mehrfach vorkommen
for dataset_name, df in [
    ("Ist-Daten", actuals),
    ("Budgetdaten", budget)
]:
    duplicate_keys = df.duplicated(
        subset=key_columns
    ).sum()

    if duplicate_keys > 0:
        st.error(
            f"{dataset_name}: {duplicate_keys} mehrfach "
            "vorhandene Kombinationen aus Datum, "
            "Kostenstelle und Produkt."
        )
        st.stop()


# Vorhandene Kombinationen vergleichen
actual_keys = actuals[key_columns].drop_duplicates()
budget_keys = budget[key_columns].drop_duplicates()

comparison = actual_keys.merge(
    budget_keys,
    on=key_columns,
    how="outer",
    indicator=True,
    validate="one_to_one"
)

# Kombinationen ohne passenden Budgeteintrag
missing_budget = (
    comparison["_merge"] == "left_only"
).sum()

# Kombinationen ohne passenden Ist-Eintrag
missing_actuals = (
    comparison["_merge"] == "right_only"
).sum()

if missing_budget > 0 or missing_actuals > 0:
    st.error(
        "Ist- und Budgetdaten sind nicht vollständig "
        "aufeinander abgestimmt. "
        f"{missing_budget} Kombinationen ohne Budgetdaten, "
        f"{missing_actuals} Kombinationen ohne Ist-Daten."
    )
    st.stop()

# 2.3 Plausibilitätsprüfung der Finanzdaten

def check_financial_plausibility(df, dataset_name, columns):

    for column in columns:

        # Finanzwerte sicher in Zahlen umwandeln
        numeric_values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        # Nicht interpretierbare Werte erkennen
        invalid_count = numeric_values.isna().sum()

        if invalid_count > 0:
            st.error(
                f"{dataset_name}: {invalid_count} ungültige "
                f"oder fehlende Werte in {column}."
            )
            st.stop()

        # Negative Finanzwerte erkennen
        negative_count = (numeric_values < 0).sum()

        if negative_count > 0:
            st.warning(
                f"{dataset_name}: {negative_count} negative "
                f"Werte in {column} gefunden. "
                "Bitte fachlich überprüfen."
            )


# Ist-Daten überprüfen
check_financial_plausibility(
    actuals,
    "Ist-Daten",
    ["Revenue", "Costs"]
)

# Budgetdaten überprüfen
check_financial_plausibility(
    budget,
    "Budgetdaten",
    ["BudgetRevenue", "BudgetCosts"]
)





# 3. Interaktive Dashboard-Filter

# Verfügbare Geschäftsjahre
available_years = sorted(
    actuals["Date"].dt.year.unique(),
    reverse=True
)

st.sidebar.header("Filter")
st.sidebar.caption("Die Auswahl wirkt auf die Finanzübersicht und die Diagramme. Der Jahresvergleich zeigt immer 2024 und 2025.")

selected_year = st.sidebar.selectbox(
    "Geschäftsjahr auswählen",
    options=available_years
)

# Kostenstellenfilter
available_cost_centers = sorted(
    actuals["CostCenterID"].unique()
)

selected_cost_centers = st.sidebar.multiselect(
    "Kostenstellen auswählen",
    options=available_cost_centers,
    default=available_cost_centers
)

# Produktfilter
available_products = sorted(
    actuals["ProductID"].unique()
)

selected_products = st.sidebar.multiselect(
    "Produkte auswählen",
    options=available_products,
    default=available_products
)

# Leere Auswahl verhindern
if not selected_cost_centers or not selected_products:
    st.warning(
        "Bitte mindestens eine Kostenstelle "
        "und ein Produkt auswählen."
    )
    st.stop()

# Ist-Daten filtern
filtered_actuals = actuals[
    (actuals["Date"].dt.year == selected_year)
    & (actuals["CostCenterID"].isin(selected_cost_centers))
    & (actuals["ProductID"].isin(selected_products))
]

# Budgetdaten filtern
filtered_budget = budget[
    (budget["Date"].dt.year == selected_year)
    & (budget["CostCenterID"].isin(selected_cost_centers))
    & (budget["ProductID"].isin(selected_products))
]





# 4. Finanzkennzahlen berechnen
revenue = filtered_actuals["Revenue"].sum()
costs = filtered_actuals["Costs"].sum()
profit = revenue - costs

margin = (
    profit / revenue * 100
    if revenue != 0 else 0
)

# 5. Budgetkennzahlen berechnen
budget_revenue = filtered_budget["BudgetRevenue"].sum()
budget_costs = filtered_budget["BudgetCosts"].sum()
budget_profit = budget_revenue - budget_costs

# 6. Plan-Ist-Abweichungen berechnen
revenue_variance = revenue - budget_revenue
cost_variance = costs - budget_costs
profit_variance = profit - budget_profit


# 6.1 Automatische Prüfung der Finanzberechnungen

def check_calculations():

    # Operatives Ergebnis überprüfen
    assert math.isclose(
        profit,
        revenue - costs,
        rel_tol=1e-9,
        abs_tol=0.01
    ), "Fehler bei der Berechnung des operativen Ergebnisses."

    # Operative Marge überprüfen
    expected_margin = (
        (revenue - costs) / revenue * 100
        if revenue != 0 else 0
    )

    assert math.isclose(
        margin,
        expected_margin,
        rel_tol=1e-9,
        abs_tol=0.0001
    ), "Fehler bei der Berechnung der operativen Marge."

    # Budgetergebnis überprüfen
    assert math.isclose(
        budget_profit,
        budget_revenue - budget_costs,
        rel_tol=1e-9,
        abs_tol=0.01
    ), "Fehler bei der Berechnung des Budgetergebnisses."

    # Plan-Ist-Abweichungen überprüfen
    assert math.isclose(
        revenue_variance,
        revenue - budget_revenue,
        abs_tol=0.01
    ), "Fehler bei der Umsatzabweichung."

    assert math.isclose(
        cost_variance,
        costs - budget_costs,
        abs_tol=0.01
    ), "Fehler bei der Kostenabweichung."

    assert math.isclose(
        profit_variance,
        revenue_variance - cost_variance,
        abs_tol=0.01
    ), "Fehler bei der Ergebnisabweichung."


check_calculations()


# 5. Dashboard-Oberfläche
st.title("Financial Controlling Dashboard")

st.write(
    "Interaktive Analyse von Umsatz, "
    "Kosten und Profitabilität."
)

st.divider()

st.header(f"Finanzübersicht {selected_year}")
st.caption("Alle Kennzahlen berücksichtigen die ausgewählten Kostenstellen und Produkte.")




# 7. KPI-Karten mit Budgetabweichungen


# Einheitliche Zahlenformatierung

def format_eur(value):
    return f"{value:,.0f}".replace(",", ".") + " €"


def format_percent(value, signed=False):
    if signed:
        return f"{value:+.2f}".replace(".", ",") + " %"

    return f"{value:.2f}".replace(".", ",") + " %"


def format_percentage_points(value):
    return f"{value:+.2f}".replace(".", ",") + " PP"



# Vier KPI-Karten nebeneinander darstellen
col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    with st.container(border=True):
        st.metric(
            label="Umsatz",
            value=format_eur(revenue),
            delta=format_eur(revenue_variance)
        )

with col2:
    with st.container(border=True):
        st.metric(
            label="Kosten",
            value=format_eur(costs),
            delta=format_eur(cost_variance),
            delta_color="inverse"
        )

with col3:
    with st.container(border=True):
        st.metric(
            label="Operatives Ergebnis",
            value=format_eur(profit),
            delta=format_eur(profit_variance)
        )

with col4:
    with st.container(border=True):
        st.metric(
            label="Operative Marge",
            value=format_percent(margin)
        )


st.caption("Plan-Ist-Abweichung = Istwert minus Budgetwert. Bei Kosten ist eine positive Abweichung eine Budgetüberschreitung. Das operative Ergebnis ist hier vereinfacht Umsatz minus erfasste Kosten.")

# 8. Monatliche Umsatzentwicklung

st.divider()
st.header("Monatliche Umsatzentwicklung")
st.caption("Vergleich der tatsächlichen Umsätze mit dem geplanten Umsatz je Monat im gewählten Geschäftsjahr.")

# Monatliche Ist-Umsätze aggregieren
monthly_actuals = (
    filtered_actuals
    .groupby("Date")["Revenue"]
    .sum()
    .reset_index()
)

# Monatliche Budget-Umsätze aggregieren
monthly_budget = (
    filtered_budget
    .groupby("Date")["BudgetRevenue"]
    .sum()
    .reset_index()
)

# Ist- und Budgetdaten zusammenführen
monthly_data = pd.merge(
    monthly_actuals,
    monthly_budget,
    on="Date",
    how="outer"
).sort_values("Date")

# Interaktives Diagramm erstellen
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=monthly_data["Date"],
        y=monthly_data["Revenue"],
        mode="lines+markers",
        name="Umsatz Ist"
    )
)

fig.add_trace(
    go.Scatter(
        x=monthly_data["Date"],
        y=monthly_data["BudgetRevenue"],
        mode="lines+markers",
        name="Umsatz Budget"
    )
)

fig.update_layout(
    title="Umsatzentwicklung: Ist vs. Budget",
    xaxis_title="Monat",
    yaxis_title="Umsatz in EUR",
    hovermode="x unified",
    legend_title="Kennzahl",
    height=450
)

# Diagramm in Streamlit anzeigen
st.plotly_chart(fig, use_container_width=True)


# 9. Kostenstellenanalyse und Produktprofitabilität

st.divider()

col_costs, col_products = st.columns(2, gap="large")



# Ist-Kosten nach Kostenstelle
cc_actuals = (
    filtered_actuals
    .groupby("CostCenterID")["Costs"]
    .sum()
    .reset_index()
)

# Budgetkosten nach Kostenstelle
cc_budget = (
    filtered_budget
    .groupby("CostCenterID")["BudgetCosts"]
    .sum()
    .reset_index()
)

# Daten zusammenführen
cc_data = pd.merge(
    cc_actuals,
    cc_budget,
    on="CostCenterID",
    how="outer",
    validate="one_to_one"
)

# Prüfen, ob Werte fehlen
if cc_data[["Costs", "BudgetCosts"]].isna().any().any():
    st.error("Für mindestens eine Kostenstelle fehlen Daten.")
    st.stop()

# Budgetabweichung berechnen
cc_data["CostVariance"] = (
    cc_data["Costs"] - cc_data["BudgetCosts"]
)

# Positive Abweichung = Budgetüberschreitung
cc_data["Status"] = cc_data["CostVariance"].apply(
    lambda value: "Budgetüberschreitung"
    if value > 0 else "Im Budget"
)

# Nach Kostenabweichung sortieren
cc_data = cc_data.sort_values(
    "CostVariance",
    ascending=False
)

# Balkendiagramm
fig_cc = go.Figure()

for status, color in [
    ("Budgetüberschreitung", "#EF4444"),
    ("Im Budget", "#22C55E")
]:
    subset = cc_data[cc_data["Status"] == status]

    fig_cc.add_trace(
        go.Bar(
            x=subset["CostCenterID"],
            y=subset["CostVariance"],
            name=status,
            marker_color=color,
            hovertemplate=(
                "Kostenstelle: %{x}"
                "<br>Abweichung: %{y:,.2f} €"
                "<extra></extra>"
            )
        )
    )

fig_cc.update_layout(
    xaxis_title="Kostenstelle",
    yaxis_title="Abweichung in EUR",
    barmode="relative",
    height=400,
    margin=dict(l=10, r=10, t=20, b=10)
)

with col_costs:
    st.subheader("Kostenstellenanalyse")
    st.caption("Positive Werte zeigen Budgetüberschreitungen; negative Werte zeigen Einsparungen gegenüber dem Kostenbudget.")
    st.plotly_chart(fig_cc, use_container_width=True)


# 10. Produktprofitabilität

# Umsatz und Kosten nach Produkt zusammenfassen
product_data = (
    filtered_actuals
    .groupby("ProductID")[["Revenue", "Costs"]]
    .sum()
    .reset_index()
)

# Operatives Ergebnis berechnen
product_data["OperatingProfit"] = (
    product_data["Revenue"] - product_data["Costs"]
)

# Operative Marge berechnen
product_data["Margin"] = (
    product_data["OperatingProfit"]
    / product_data["Revenue"].replace(0, float("nan"))
    * 100
)

# Nach operativem Ergebnis sortieren
product_data = product_data.sort_values(
    "OperatingProfit",
    ascending=False
)

# Balkendiagramm erstellen
fig_products = go.Figure()

fig_products.add_trace(
    go.Bar(
        x=product_data["ProductID"],
        y=product_data["OperatingProfit"],
        marker_color="#3B82F6",
        customdata=product_data[
            ["Revenue", "Costs", "Margin"]
        ].to_numpy(),
        hovertemplate=(
            "Produkt: %{x}"
            "<br>Ergebnis: %{y:,.2f} €"
            "<br>Umsatz: %{customdata[0]:,.2f} €"
            "<br>Kosten: %{customdata[1]:,.2f} €"
            "<br>Marge: %{customdata[2]:.2f} %"
            "<extra></extra>"
        )
    )
)

fig_products.update_layout(
    xaxis_title="Produkt",
    yaxis_title="Operatives Ergebnis in EUR",
    height=400,
    margin=dict(l=10, r=10, t=20, b=10)
)

with col_products:
    st.subheader("Produktprofitabilität")
    st.caption("Operatives Ergebnis je Produkt: Umsatz abzüglich der erfassten Kosten.")
    st.plotly_chart(fig_products, use_container_width=True)

# 11. Jahresvergleich

st.divider()
st.header("Jahresvergleich 2024 vs. 2025")
st.caption("Der Jahresvergleich berücksichtigt die ausgewählten Produkte und Kostenstellen, unabhängig vom oben gewählten Geschäftsjahr.")

# Daten nach Kostenstellen und Produkten filtern
comparison_actuals = actuals[
    (actuals["CostCenterID"].isin(selected_cost_centers))
    & (actuals["ProductID"].isin(selected_products))
    & (actuals["Date"].dt.year.isin([2024, 2025]))
].copy()

# Geschäftsjahr ergänzen
comparison_actuals["Year"] = comparison_actuals["Date"].dt.year

# Finanzkennzahlen nach Jahr aggregieren
yearly_data = (
    comparison_actuals
    .groupby("Year")[["Revenue", "Costs"]]
    .sum()
    .reset_index()
)

# Operatives Ergebnis berechnen
yearly_data["OperatingProfit"] = (
    yearly_data["Revenue"] - yearly_data["Costs"]
)

# Diagramm erstellen
fig_year = go.Figure()

for year in [2024, 2025]:
    year_data = yearly_data[yearly_data["Year"] == year]

    if year_data.empty:
        continue

    values = year_data.iloc[0]

    fig_year.add_trace(
        go.Bar(
            name=str(year),
            x=["Umsatz", "Kosten", "Operatives Ergebnis"],
            y=[
                values["Revenue"],
                values["Costs"],
                values["OperatingProfit"]
            ]
        )
    )

fig_year.update_layout(
    barmode="group",
    xaxis_title="Kennzahl",
    yaxis_title="Betrag in EUR",
    height=450,
    legend_title="Geschäftsjahr",
    hovermode="x unified"
)

st.plotly_chart(fig_year, use_container_width=True)


# 12. Veränderungen gegenüber dem Vorjahr

st.subheader("Veränderung gegenüber dem Vorjahr")

# Standardwerte für fehlende Jahresdaten
revenue_change_pct = None
costs_change_pct = None
profit_change_pct = None

# Daten für 2024 und 2025 abrufen
data_2024 = yearly_data[yearly_data["Year"] == 2024]
data_2025 = yearly_data[yearly_data["Year"] == 2025]

if not data_2024.empty and not data_2025.empty:

    previous = data_2024.iloc[0]
    current = data_2025.iloc[0]

    # Absolute Veränderungen
    revenue_change = current["Revenue"] - previous["Revenue"]
    costs_change = current["Costs"] - previous["Costs"]
    profit_change = (
        current["OperatingProfit"]
        - previous["OperatingProfit"]
    )

    # Prozentuale Veränderungen
    def calculate_change(current_value, previous_value):
        if previous_value == 0:
            return None

        return (
            (current_value - previous_value)
            / abs(previous_value)
            * 100
        )

    revenue_change_pct = calculate_change(
        current["Revenue"], previous["Revenue"]
    )

    costs_change_pct = calculate_change(
        current["Costs"], previous["Costs"]
    )

    profit_change_pct = calculate_change(
        current["OperatingProfit"],
        previous["OperatingProfit"]
    )

    # Prozentwerte formatieren
    def format_pct(value):
        if value is None:
            return "Nicht berechenbar"
        return format_percent(value, signed=True)

    # Drei Kennzahlen nebeneinander
    col_rev, col_cost, col_profit = st.columns(3)

    with col_rev:
        st.metric(
            label="Umsatzveränderung",
            value=format_pct(revenue_change_pct),
            delta=format_eur(revenue_change)
        )

    with col_cost:
        st.metric(
            label="Kostenveränderung",
            value=format_pct(costs_change_pct),
            delta=format_eur(costs_change),
            delta_color="inverse"
        )

    with col_profit:
        st.metric(
            label="Ergebnisveränderung",
            value=format_pct(profit_change_pct),
            delta=format_eur(profit_change)

        )

else:
    st.info("Für den Jahresvergleich fehlen Daten.")


# 13. Operative Marge im Jahresvergleich

st.divider()
st.subheader("Operative Marge im Jahresvergleich")

# Marge für beide Geschäftsjahre berechnen
yearly_data["OperatingMargin"] = (
    yearly_data["OperatingProfit"]
    / yearly_data["Revenue"].replace(0, float("nan"))
    * 100
)

# Daten für 2024 und 2025 auswählen
margin_2024_data = yearly_data[
    yearly_data["Year"] == 2024
]

margin_2025_data = yearly_data[
    yearly_data["Year"] == 2025
]

if not margin_2024_data.empty and not margin_2025_data.empty:

    margin_2024 = margin_2024_data.iloc[0]["OperatingMargin"]
    margin_2025 = margin_2025_data.iloc[0]["OperatingMargin"]

    # Veränderung in Prozentpunkten
    margin_change = margin_2025 - margin_2024

    # Kennzahlen darstellen
    col_m1, col_m2, col_m3 = st.columns(3)

    with col_m1:
        st.metric(
            label="Operative Marge 2024",
            value=format_percent(margin_2024)
        )

    with col_m2:
        st.metric(
            label="Operative Marge 2025",
            value=format_percent(margin_2025)
        )

    with col_m3:
        st.metric(
            label="Veränderung der Marge",
            value=format_percentage_points(margin_change)
        )

else:
    st.info("Für den Margenvergleich fehlen Daten.")


# 14. Automatische Controlling-Insights

st.divider()
st.header("Automatische Controlling-Insights")

# Prozentwerte deutsch formatieren
def format_insight_pct(value):
    return f"{abs(value):.2f}".replace(".", ",") + " %"


# 1. Umsatzentwicklung analysieren
if revenue_change_pct is not None:
    if revenue_change_pct > 0:
        st.success(
            "📈 Umsatzentwicklung: Der Umsatz ist gegenüber "
            f"2024 um {format_insight_pct(revenue_change_pct)} gestiegen."
        )
    elif revenue_change_pct < 0:
        st.warning(
            "📉 Umsatzentwicklung: Der Umsatz ist gegenüber "
            f"2024 um {format_insight_pct(revenue_change_pct)} gesunken."
        )
    else:
        st.info("Der Umsatz ist gegenüber 2024 unverändert.")


# 2. Kostenentwicklung analysieren
if costs_change_pct is not None:
    if costs_change_pct > 0:
        st.warning(
            "📈 Kostenentwicklung: Die Kosten sind gegenüber "
            f"2024 um {format_insight_pct(costs_change_pct)} gestiegen."
        )
    elif costs_change_pct < 0:
        st.success(
            "📉 Kostenentwicklung: Die Kosten sind gegenüber "
            f"2024 um {format_insight_pct(costs_change_pct)} gesunken."
        )
    else:
        st.info("Die Kosten sind gegenüber 2024 unverändert.")


# 3. Profitabilität analysieren
if (
    not margin_2024_data.empty
    and not margin_2025_data.empty
    and pd.notna(margin_change)
):
    margin_change_formatted = (
        f"{abs(margin_change):.2f}".replace(".", ",")
    )

    if margin_change > 0:
        st.success(
            "✅ Profitabilität: Die operative Marge hat sich "
            f"um {margin_change_formatted} Prozentpunkte verbessert."
        )
    elif margin_change < 0:
        st.warning(
            "⚠️ Profitabilität: Die operative Marge hat sich "
            f"um {margin_change_formatted} Prozentpunkte verschlechtert."
        )
    else:
        st.info("Die operative Marge ist unverändert.")
