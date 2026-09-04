import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Business Operations Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data.csv", parse_dates=["Date"])


df = load_data()

# -----------------------------
# TITLE
# -----------------------------
st.title("📊 Business Operations Performance Dashboard")
st.caption(
    "Operational performance, KPI monitoring and business insights"
)

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔎 Dashboard Filters")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

region = st.sidebar.multiselect(
    "Region",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

team = st.sidebar.multiselect(
    "Team",
    options=sorted(df["Team"].unique()),
    default=sorted(df["Team"].unique())
)

product = st.sidebar.multiselect(
    "Product",
    options=sorted(df["Product"].unique()),
    default=sorted(df["Product"].unique())
)

status = st.sidebar.multiselect(
    "Order Status",
    options=sorted(df["Order_Status"].unique()),
    default=sorted(df["Order_Status"].unique())
)

# -----------------------------
# FILTER DATA
# -----------------------------
if len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = df[
        (df["Date"].dt.date >= start_date)
        & (df["Date"].dt.date <= end_date)
        & (df["Region"].isin(region))
        & (df["Team"].isin(team))
        & (df["Product"].isin(product))
        & (df["Order_Status"].isin(status))
    ]
else:
    filtered_df = df.copy()

# -----------------------------
# EMPTY DATA CHECK
# -----------------------------
if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# -----------------------------
# KPI CALCULATIONS
# -----------------------------
total_revenue = filtered_df["Revenue"].sum()
total_orders = filtered_df["Orders"].sum()
avg_conversion = filtered_df["Conversion_Rate"].mean()
avg_sla = filtered_df["SLA_Adherence"].mean()
avg_satisfaction = filtered_df["Customer_Satisfaction"].mean()
avg_processing = filtered_df["Processing_Time"].mean()

# -----------------------------
# KPI CARDS
# -----------------------------
st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "Total Revenue",
    f"₹{total_revenue:,.0f}"
)

col2.metric(
    "Total Orders",
    f"{total_orders:,.0f}"
)

col3.metric(
    "Conversion Rate",
    f"{avg_conversion:.2f}%"
)

col4.metric(
    "SLA Adherence",
    f"{avg_sla:.2f}%"
)

col5.metric(
    "Customer Satisfaction",
    f"{avg_satisfaction:.2f}/5"
)

col6.metric(
    "Avg Processing Time",
    f"{avg_processing:.1f} hrs"
)

st.divider()

# -----------------------------
# MONTHLY TRENDS
# -----------------------------
monthly = (
    filtered_df
    .assign(Month=filtered_df["Date"].dt.to_period("M").astype(str))
    .groupby("Month", as_index=False)
    .agg(
        Revenue=("Revenue", "sum"),
        Orders=("Orders", "sum")
    )
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Monthly Revenue")

    fig = px.line(
        monthly,
        x="Month",
        y="Revenue",
        markers=True,
        title="Revenue Trend"
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📦 Monthly Orders")

    fig = px.line(
        monthly,
        x="Month",
        y="Orders",
        markers=True,
        title="Orders Trend"
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Orders"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# REGIONAL PERFORMANCE
# -----------------------------
col1, col2 = st.columns(2)

region_data = (
    filtered_df
    .groupby("Region", as_index=False)
    .agg(
        Revenue=("Revenue", "sum"),
        SLA=("SLA_Adherence", "mean"),
        Satisfaction=("Customer_Satisfaction", "mean")
    )
)

with col1:
    st.subheader("🌍 Revenue by Region")

    fig = px.bar(
        region_data,
        x="Region",
        y="Revenue",
        title="Regional Revenue"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("⏱️ SLA by Region")

    fig = px.bar(
        region_data,
        x="Region",
        y="SLA",
        title="SLA Adherence by Region"
    )

    fig.add_hline(
        y=90,
        line_dash="dash",
        annotation_text="90% Target"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TEAM PERFORMANCE
# -----------------------------
st.subheader("👥 Team Performance")

team_data = (
    filtered_df
    .groupby("Team", as_index=False)
    .agg(
        Revenue=("Revenue", "sum"),
        SLA=("SLA_Adherence", "mean"),
        Satisfaction=("Customer_Satisfaction", "mean")
    )
)

fig = px.bar(
    team_data,
    x="Team",
    y="SLA",
    title="SLA Adherence by Team",
    text_auto=".1f"
)

fig.add_hline(
    y=90,
    line_dash="dash",
    annotation_text="Target: 90%"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# ORDER STATUS
# -----------------------------
st.subheader("📦 Order Status Distribution")

status_data = (
    filtered_df
    .groupby("Order_Status", as_index=False)
    .agg(Orders=("Orders", "sum"))
)

fig = px.pie(
    status_data,
    names="Order_Status",
    values="Orders",
    hole=0.4
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# BUSINESS INSIGHTS
# -----------------------------
st.divider()

st.header("💡 Key Business Insights")

highest_revenue_region = (
    region_data.loc[
        region_data["Revenue"].idxmax(),
        "Region"
    ]
)

lowest_sla_region = (
    region_data.loc[
        region_data["SLA"].idxmin(),
        "Region"
    ]
)

best_team = (
    team_data.loc[
        team_data["SLA"].idxmax(),
        "Team"
    ]
)

highest_month = (
    monthly.loc[
        monthly["Revenue"].idxmax(),
        "Month"
    ]
)

st.write(
    f"• **Highest revenue region:** {highest_revenue_region}"
)

st.write(
    f"• **Region requiring SLA attention:** {lowest_sla_region}"
)

st.write(
    f"• **Best SLA-performing team:** {best_team}"
)

st.write(
    f"• **Highest revenue month:** {highest_month}"
)

st.write(
    f"• **Overall SLA adherence:** {avg_sla:.2f}%"
)

# -----------------------------
# RECOMMENDATIONS
# -----------------------------
st.header("🎯 Recommended Actions")

if avg_sla < 90:
    st.warning(
        "SLA adherence is below the 90% target. "
        "Review workload distribution and operational bottlenecks."
    )
else:
    st.success(
        "SLA adherence is currently above the 90% target."
    )

if avg_satisfaction < 4:
    st.warning(
        "Customer satisfaction is below 4/5. "
        "Investigate customer pain points and service quality."
    )
else:
    st.success(
        "Customer satisfaction is currently at a healthy level."
    )

# -----------------------------
# DATA TABLE
# -----------------------------
st.divider()

with st.expander("📋 View Detailed Data"):
    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered Data",
        data=csv,
        file_name="filtered_business_data.csv",
        mime="text/csv"
    )

st.caption(
    "Portfolio project: Business Operations & Analytics Dashboard"
)
