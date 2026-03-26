import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------
# PAGE CONFIG + RENAISSANCE THEME
# ---------------------------------------
st.set_page_config(page_title="B2B Sales Intelligence", layout="wide")

# Custom Dark Renaissance Theme
st.markdown("""
<style>
body {
    background-color: #1a1410;
    color: #f5e6cc;
}
.stApp {
    background-color: #1a1410;
}
h1, h2, h3 {
    color: #d4a373;
    font-family: 'Georgia', serif;
}
.css-1d391kg {
    background-color: #2b1d14;
}
</style>
""", unsafe_allow_html=True)

st.title("📜 B2B Sales Renaissance Dashboard")
st.caption("Lead Intelligence • Conversion Analytics • Strategic Insights")

# ---------------------------------------
# LOAD DATA
# ---------------------------------------
@st.cache_data
def load_data():
    return pd.read_excel("B2B_Leads_Dataset_1000Records.xlsx")

df = load_data()

# ---------------------------------------
# COLUMN VALIDATION
# ---------------------------------------
required_cols = [
    "Lead_ID", "Client_Name", "Industry",
    "Region", "Lead_Source", "Revenue",
    "Status", "Follow_Up_Time"
]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

# ---------------------------------------
# DATA PROCESSING
# ---------------------------------------
df["Converted"] = df["Status"].map({"Converted": 1, "Not Converted": 0})

# ---------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------
st.sidebar.header("🎯 Filters")

regions = st.sidebar.multiselect("Region", df["Region"].unique(), default=df["Region"].unique())
industries = st.sidebar.multiselect("Industry", df["Industry"].unique(), default=df["Industry"].unique())
sources = st.sidebar.multiselect("Lead Source", df["Lead_Source"].unique(), default=df["Lead_Source"].unique())

filtered = df[
    (df["Region"].isin(regions)) &
    (df["Industry"].isin(industries)) &
    (df["Lead_Source"].isin(sources))
]

# ---------------------------------------
# KPI SECTION
# ---------------------------------------
total_leads = len(filtered)
converted = filtered["Converted"].sum()
conversion_rate = (converted / total_leads * 100) if total_leads else 0
avg_followup = filtered["Follow_Up_Time"].mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Leads", total_leads)
k2.metric("Converted Leads", int(converted))
k3.metric("Conversion Rate", f"{conversion_rate:.2f}%")
k4.metric("Avg Follow-up Time (hrs)", f"{avg_followup:.1f}")

st.divider()

# ---------------------------------------
# VISUALIZATIONS
# ---------------------------------------
c1, c2 = st.columns(2)

# Leads by Region
with c1:
    st.subheader("Leads by Region")
    region_counts = filtered["Region"].value_counts()
    fig, ax = plt.subplots()
    ax.bar(region_counts.index, region_counts.values)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Conversion Rate by Industry
with c2:
    st.subheader("Conversion Rate by Industry")
    conv_ind = filtered.groupby("Industry")["Converted"].mean() * 100
    fig2, ax2 = plt.subplots()
    ax2.bar(conv_ind.index, conv_ind.values)
    plt.xticks(rotation=45)
    st.pyplot(fig2)

st.divider()

c3, c4 = st.columns(2)

# Revenue Trend (simulated using Lead_ID order)
with c3:
    st.subheader("Revenue Trend")
    trend = filtered.sort_values("Lead_ID")
    fig3, ax3 = plt.subplots()
    ax3.plot(trend["Revenue"].values)
    st.pyplot(fig3)

# Lead Source Analysis
with c4:
    st.subheader("Lead Source Performance")
    source_perf = filtered.groupby("Lead_Source")["Converted"].mean() * 100
    fig4, ax4 = plt.subplots()
    ax4.bar(source_perf.index, source_perf.values)
    plt.xticks(rotation=45)
    st.pyplot(fig4)

st.divider()

# ---------------------------------------
# INSIGHTS SECTION
# ---------------------------------------
st.subheader("🧠 Business Insights")

# Best Region
best_region = filtered.groupby("Region")["Converted"].mean().idxmax()

# Best Source
best_source = filtered.groupby("Lead_Source")["Converted"].mean().idxmax()

# Follow-up impact
corr = filtered["Follow_Up_Time"].corr(filtered["Converted"])

st.write(f"📍 **Highest Conversion Region:** {best_region}")
st.write(f"🚀 **Best Lead Source:** {best_source}")
st.write(f"⏱️ **Follow-up vs Conversion Correlation:** {corr:.2f}")

if corr < 0:
    st.success("Faster follow-ups increase conversion likelihood.")
else:
    st.warning("Follow-up time may not strongly impact conversion.")

# ---------------------------------------
# STRATEGY SECTION
# ---------------------------------------
st.subheader("📈 Strategic Recommendations")

st.write("""
1. **Reduce Follow-Up Time**
   Automate lead responses to reduce delay and increase engagement.

2. **Focus on High-Converting Sources**
   Allocate more budget to top-performing lead sources.

3. **Regional Optimization**
   Replicate strategies from high-performing regions to weaker markets.
""")

# ---------------------------------------
# DATA VIEW
# ---------------------------------------
st.subheader("📄 Data Preview")
st.dataframe(filtered.head(100), use_container_width=True)
