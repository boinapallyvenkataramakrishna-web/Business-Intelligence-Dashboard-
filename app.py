
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Business Intelligence Dashboard", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    web = pd.read_csv("web_traffic.csv")
    churn = pd.read_csv("customer_churn.csv")
    regional = pd.read_csv("regional_market.csv")
    ab = pd.read_csv("checkout_ab_test.csv")

    web["Date"] = pd.to_datetime(web["Date"], errors="coerce")
    churn["TotalChargesINR"] = pd.to_numeric(churn["TotalChargesINR"], errors="coerce")
    ab["Timestamp"] = pd.to_datetime(ab["Timestamp"], errors="coerce")
    return web, churn, regional, ab

web, churn, regional, ab = load_data()

st.title("📊 Business Intelligence Dashboard")
st.caption("Interactive analysis built from the supplied internship datasets • Streamlit + Plotly")

# ---------------- Sidebar filters ----------------
st.sidebar.header("🔎 Dashboard Filters")

min_date = web["Date"].min().date()
max_date = web["Date"].max().date()
date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date),
                                    min_value=min_date, max_value=max_date)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

regions = sorted(set(web["Region"].dropna().unique()) | set(churn["Region"].dropna().unique()))
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

categories = sorted(web["LandingPage"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect("Category / Landing Page", categories, default=categories)

# Filter web data
web_f = web[
    (web["Date"].dt.date >= start_date) &
    (web["Date"].dt.date <= end_date) &
    (web["Region"].isin(selected_regions)) &
    (web["LandingPage"].isin(selected_categories))
].copy()

# Filter churn data by region (customer data has no date field)
churn_f = churn[churn["Region"].isin(selected_regions)].copy()
# If region filter has no selected values, show empty customer data rather than ignoring filter.
if not selected_regions:
    churn_f = churn.iloc[0:0].copy()
    web_f = web.iloc[0:0].copy()

# ---------------- KPI calculations ----------------
revenue = churn_f["TotalChargesINR"].sum(skipna=True)
active_users = (churn_f["Churn"].eq("No")).sum()
total_customers = len(churn_f)
churn_pct = (churn_f["Churn"].eq("Yes").mean() * 100) if total_customers else 0
avg_ticket = (revenue / active_users) if active_users else 0

# Traffic metrics
sessions = len(web_f)
registered = web_f["Registered"].eq("Yes").sum()
conversion_pct = registered / sessions * 100 if sessions else 0
bounce_pct = web_f["Bounced"].eq("Yes").mean() * 100 if sessions else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Total Revenue", f"₹{revenue:,.0f}")
c2.metric("👥 Active Users", f"{active_users:,}")
c3.metric("📉 Churn", f"{churn_pct:.1f}%")
c4.metric("🎫 Avg Ticket Size", f"₹{avg_ticket:,.0f}")

st.divider()

# ---------------- Overview charts ----------------
left, right = st.columns(2)

with left:
    daily = web_f.groupby("Date", as_index=False).agg(
        Sessions=("SessionID", "count"),
        Registrations=("Registered", lambda x: (x == "Yes").sum())
    )
    fig = px.line(daily, x="Date", y=["Sessions", "Registrations"],
                  markers=True, title="Traffic & Registrations Over Time")
    fig.update_layout(legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

with right:
    region_churn = churn_f.groupby("Region", dropna=False).agg(
        Customers=("CustomerID", "count"),
        Churned=("Churn", lambda x: (x == "Yes").sum())
    ).reset_index()
    region_churn["Churn %"] = np.where(
        region_churn["Customers"] > 0,
        region_churn["Churned"] / region_churn["Customers"] * 100, 0
    )
    fig = px.bar(region_churn.sort_values("Churn %", ascending=False),
                 x="Region", y="Churn %", text_auto=".1f",
                 title="Churn Rate by Region")
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)

with left:
    source = web_f.groupby("Source", as_index=False).agg(
        Sessions=("SessionID", "count"),
        Registered=("Registered", lambda x: (x == "Yes").sum())
    )
    source["Conversion %"] = source["Registered"] / source["Sessions"] * 100
    fig = px.bar(source.sort_values("Conversion %", ascending=False),
                 x="Source", y="Conversion %", text_auto=".1f",
                 title="Conversion Rate by Traffic Source")
    st.plotly_chart(fig, use_container_width=True)

with right:
    sub = churn_f.groupby("SubscriptionType", as_index=False).agg(
        Revenue=("TotalChargesINR", "sum"),
        Customers=("CustomerID", "count")
    )
    fig = px.bar(sub, x="SubscriptionType", y="Revenue",
                 title="Revenue by Subscription Type", text_auto=".2s")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Interactive detail section ----------------
st.subheader("📌 Interactive Customer & Market Analysis")
tab1, tab2, tab3 = st.tabs(["Customer Churn", "Regional Market", "Checkout A/B Test"])

with tab1:
    a, b = st.columns(2)
    with a:
        fig = px.histogram(churn_f, x="TenureMonths", color="Churn",
                           nbins=20, barmode="overlay",
                           title="Tenure Distribution by Churn")
        st.plotly_chart(fig, use_container_width=True)
    with b:
        fig = px.box(churn_f, x="ContractType", y="MonthlyChargesINR",
                     color="Churn", title="Monthly Charges by Contract & Churn")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    market = regional.copy()
    market["LeadConversionPct"] = market["LeadConversionRate"] * 100
    fig = px.scatter(market, x="MonthlySearchDemand", y="LeadConversionPct",
                     size="MedianAnnualIncomeINR", color="PopulationSegment",
                     hover_name="City",
                     hover_data=["State", "ExistingCompetitors", "EstimatedAcquisitionCostINR"],
                     title="Regional Market Opportunity")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        market[["City","State","PopulationSegment","MonthlySearchDemand",
                "ExistingCompetitors","LeadConversionPct",
                "EstimatedAcquisitionCostINR"]].sort_values("MonthlySearchDemand", ascending=False),
        use_container_width=True, hide_index=True
    )

with tab3:
    ab2 = ab.copy()
    summary = ab2.groupby("Variant", as_index=False).agg(
        Visitors=("VisitorID", "count"),
        CheckoutStarted=("CheckoutStarted", lambda x: (x == "Yes").sum()),
        Conversions=("Converted", lambda x: (x == "Yes").sum()),
        Revenue=("OrderValueINR", "sum")
    )
    summary["Conversion %"] = summary["Conversions"] / summary["Visitors"] * 100
    summary["Checkout Start %"] = summary["CheckoutStarted"] / summary["Visitors"] * 100
    st.dataframe(summary, use_container_width=True, hide_index=True)
    fig = px.bar(summary, x="Variant", y="Conversion %", text_auto=".2f",
                 title="Checkout Conversion by Variant")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Data quality ----------------
with st.expander("🧹 Data Quality & KPI Definitions"):
    st.write("The supplied ZIP contains web traffic, customer churn, regional market, and checkout A/B-test datasets.")
    st.markdown("""
    **KPI definitions used in this dashboard**
    - **Total Revenue:** sum of valid `TotalChargesINR` from the customer churn dataset.
    - **Active Users:** customers where `Churn = No`.
    - **Churn %:** churned customers ÷ filtered customers × 100.
    - **Avg Ticket Size:** Total Revenue ÷ Active Users. This is a revenue-per-active-customer proxy because the supplied datasets do not contain a dedicated order/ticket table.
    - **Date Range:** applied to the web-traffic dataset because it is the supplied dataset containing dates.
    - **Region:** applied to both web-traffic and customer datasets.
    - **Category:** represented by `LandingPage`, the closest category-like field in the supplied web dataset.
    """)
    st.write("Missing/invalid `TotalChargesINR` values are excluded from the revenue calculation.")

st.caption("Internship BI Dashboard • Built with Streamlit and Plotly")
