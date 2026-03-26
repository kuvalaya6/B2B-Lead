import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- BASIC CONFIG ----------
st.set_page_config(
    page_title="B2B Sales Automation Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data(path: str):
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    df["Status"] = df["Status"].astype(str).str.strip().str.title()
    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce")
    df["Follow_Up_Time"] = pd.to_numeric(df["Follow_Up_Time"], errors="coerce")
    return df

# ---------- SIDEBAR ----------
st.sidebar.title("Settings")

data_file = st.sidebar.text_input(
    "Excel file path",
    value="B2B_Leads_Dataset_1000Records.xlsx"
)

try:
    df = load_data(data_file)
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()

st.sidebar.success("Data loaded successfully!")

# Filter widgets
regions = ["All"] + sorted(df["Region"].dropna().unique().tolist())
industries = ["All"] + sorted(df["Industry"].dropna().unique().tolist())
sources = ["All"] + sorted(df["Lead_Source"].dropna().unique().tolist())

selected_region = st.sidebar.selectbox("Filter by Region", regions)
selected_industry = st.sidebar.selectbox("Filter by Industry", industries)
selected_source = st.sidebar.selectbox("Filter by Lead Source", sources)

# Apply filters
filtered_df = df.copy()
if selected_region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]
if selected_industry != "All":
    filtered_df = filtered_df[filtered_df["Industry"] == selected_industry]
if selected_source != "All":
    filtered_df = filtered_df[filtered_df["Lead_Source"] == selected_source]

# ---------- KPI CARDS ----------
st.title("AI-Driven B2B Sales Dashboard")

total_leads = len(filtered_df)
converted_leads = (filtered_df["Status"] == "Converted").sum()
conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
avg_follow_up = filtered_df["Follow_Up_Time"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Leads", f"{total_leads}")
col2.metric("Converted Leads", f"{converted_leads}")
col3.metric("Conversion Rate (%)", f"{conversion_rate:.2f}")
col4.metric("Average Follow-up Time (hrs)", f"{avg_follow_up:.2f}" if pd.notnull(avg_follow_up) else "N/A")

st.markdown("---")

# ---------- VISUALIZATIONS ----------

# Leads by Region (Bar Chart)
st.subheader("Leads by Region")
if not filtered_df.empty:
    leads_by_region = filtered_df.groupby("Region")["Lead_ID"].count().reset_index()
    leads_by_region = leads_by_region.sort_values("Lead_ID", ascending=False)
    fig_region = px.bar(
        leads_by_region,
        x="Region",
        y="Lead_ID",
        labels={"Lead_ID": "Number of Leads"},
        color="Region",
        title="Number of Leads by Region"
    )
    st.plotly_chart(fig_region, use_container_width=True)
else:
    st.info("No data available for the selected filters.")

st.markdown("---")

# Conversion Rate by Industry
st.subheader("Conversion Rate by Industry")
if not filtered_df.empty:
    conv_by_industry = (
        filtered_df
        .groupby("Industry")
        .apply(lambda x: (x["Status"] == "Converted").mean() * 100)
        .reset_index(name="Conversion_Rate")
    )
    conv_by_industry = conv_by_industry.sort_values("Conversion_Rate", ascending=False)
    fig_industry = px.bar(
        conv_by_industry,
        x="Industry",
        y="Conversion_Rate",
        labels={"Conversion_Rate": "Conversion Rate (%)"},
        color="Industry",
        title="Conversion Rate by Industry"
    )
    st.plotly_chart(fig_industry, use_container_width=True)
else:
    st.info("No data available for conversion rate by industry.")

st.markdown("---")

# Revenue Trend (Line Chart)
st.subheader("Revenue Trend (by Lead_ID order)")
if not filtered_df.empty:
    revenue_trend = filtered_df.sort_values("Lead_ID")
    fig_revenue = px.line(
        revenue_trend,
        x="Lead_ID",
        y="Revenue",
        title="Revenue Trend (Sequence of Leads)",
        labels={"Revenue": "Revenue", "Lead_ID": "Lead ID"},
    )
    st.plotly_chart(fig_revenue, use_container_width=True)
else:
    st.info("No data available for revenue trend.")

st.markdown("---")

# Lead Source Analysis
st.subheader("Lead Source Analysis")
if not filtered_df.empty:
    leads_by_source = (
        filtered_df.groupby("Lead_Source")["Lead_ID"].count().reset_index(name="Lead_Count")
    )
    leads_by_source = leads_by_source.sort_values("Lead_Count", ascending=False)
    fig_source = px.bar(
        leads_by_source,
        x="Lead_Source",
        y="Lead_Count",
        labels={"Lead_Count": "Number of Leads"},
        color="Lead_Source",
        title="Number of Leads by Source"
    )
    st.plotly_chart(fig_source, use_container_width=True)
else:
    st.info("No data available for lead source analysis.")

st.markdown("---")

# ---------- BUSINESS INSIGHTS (Part D) ----------

st.header("Business Insights & Recommendations")

if not df.empty:
    # 1. Region with highest conversion rate
    conv_by_region = (
        df
        .groupby("Region")
        .apply(lambda x: (x["Status"] == "Converted").mean() * 100)
        .reset_index(name="Conversion_Rate")
    )

    if not conv_by_region.empty:
        best_region_row = conv_by_region.sort_values("Conversion_Rate", ascending=False).iloc[0]
        best_region = best_region_row["Region"]
        best_region_rate = best_region_row["Conversion_Rate"]
        st.write(f"1. Region with highest conversion rate: **{best_region}** ({best_region_rate:.2f}%).")
    else:
        st.write("1. Not enough data to calculate region conversion rates.")

    # 2. Best performing lead source
    conv_by_source = (
        df
        .groupby("Lead_Source")
        .apply(lambda x: (x["Status"] == "Converted").mean() * 100)
        .reset_index(name="Conversion_Rate")
    )
    if not conv_by_source.empty:
        best_source_row = conv_by_source.sort_values("Conversion_Rate", ascending=False).iloc[0]
        best_source = best_source_row["Lead_Source"]
        best_source_rate = best_source_row["Conversion_Rate"]
        st.write(f"2. Best performing lead source: **{best_source}** ({best_source_rate:.2f}%).")
    else:
        st.write("2. Not enough data to calculate lead source performance.")

    # 3. Relationship between follow-up time and conversion
    st.subheader("Follow-up Time vs Conversion")
    conversion_time = df[["Follow_Up_Time", "Status"]].dropna()
    if not conversion_time.empty:
        avg_time_converted = conversion_time[conversion_time["Status"] == "Converted"]["Follow_Up_Time"].mean()
        avg_time_not_converted = conversion_time[conversion_time["Status"] == "Not Converted"]["Follow_Up_Time"].mean()

        st.write(
            f"- Average follow-up time for **Converted** leads: {avg_time_converted:.2f} hours."
        )
        st.write(
            f"- Average follow-up time for **Not Converted** leads: {avg_time_not_converted:.2f} hours."
        )

        if avg_time_converted < avg_time_not_converted:
            st.write(
                "3. Insight: Faster follow-up is associated with higher conversion, "
                "because converted leads have a lower average follow-up time."
            )
        else:
            st.write(
                "3. Insight: Converted leads do not show a clearly lower follow-up time "
                "than non-converted leads. Other factors may be more important."
            )

        fig_scatter = px.box(
            df,
            x="Status",
            y="Follow_Up_Time",
            title="Distribution of Follow-up Time by Status",
            labels={"Follow_Up_Time": "Follow-up Time (hours)"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.write("3. Not enough data to analyze follow-up time vs conversion.")

    # 4. Recommendations
    st.subheader("Recommended Business Strategies")
    st.markdown("""
    1. **Prioritize best-performing region and source**  
       Allocate more budget and sales capacity to the region and lead source with the highest conversion rates.

    2. **Reduce follow-up time for new leads**  
       Set internal SLAs (for example, first contact within 24 hours) and use Make.com automation plus alerts to ensure quick responses.

    3. **Segment and personalize outreach**  
       Use industry and lead source filters to create tailored messaging and offers, and continuously test what works best in each segment.
    """)
else:
    st.write("No data available for insights.")
