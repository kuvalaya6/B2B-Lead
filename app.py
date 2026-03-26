import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="B2B Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .kpi-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
        border-radius: 12px;
        padding: 20px 24px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        margin-bottom: 10px;
    }
    .kpi-label {
        font-size: 13px;
        font-weight: 500;
        opacity: 0.85;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 32px;
        font-weight: 700;
        line-height: 1;
    }
    .kpi-sub {
        font-size: 12px;
        opacity: 0.7;
        margin-top: 6px;
    }
    .section-header {
        font-size: 18px;
        font-weight: 700;
        color: #1e3a5f;
        border-left: 4px solid #2d6a9f;
        padding-left: 12px;
        margin: 24px 0 14px 0;
    }
    .insight-box {
        background: #f0f6ff;
        border: 1px solid #c3d9f7;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 10px;
        color: #1e3a5f;
    }
    .insight-box strong { color: #2d6a9f; }
    .stApp { background-color: #f8fafc; }
</style>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("B2B_Leads_Dataset_1000Records.xlsx")
    df["Converted"] = (df["Status"] == "Converted").astype(int)
    return df

df = load_data()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bar-chart.png", width=60)
    st.title("🔎 Filters")
    st.markdown("---")

    regions = ["All"] + sorted(df["Region"].unique().tolist())
    sel_region = st.multiselect("Region", options=regions[1:], default=regions[1:])

    industries = sorted(df["Industry"].unique().tolist())
    sel_industry = st.multiselect("Industry", options=industries, default=industries)

    sources = sorted(df["Lead_Source"].unique().tolist())
    sel_source = st.multiselect("Lead Source", options=sources, default=sources)

    st.markdown("---")
    st.caption("B2B Sales Analytics · 2024")

# Apply filters
filtered = df[
    df["Region"].isin(sel_region) &
    df["Industry"].isin(sel_industry) &
    df["Lead_Source"].isin(sel_source)
]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 B2B Sales Automation & Analytics Dashboard")
st.markdown(f"Showing **{len(filtered):,}** of **{len(df):,}** total leads based on current filters.")
st.markdown("---")

# ── KPI Cards ─────────────────────────────────────────────────────────────────
total      = len(filtered)
converted  = filtered["Converted"].sum()
conv_rate  = (converted / total * 100) if total else 0
avg_follow = filtered["Follow_Up_Time"].mean() if total else 0
total_rev  = filtered["Revenue"].sum()

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Total Leads</div>
        <div class="kpi-value">{total:,}</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Converted Leads</div>
        <div class="kpi-value">{converted:,}</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Conversion Rate</div>
        <div class="kpi-value">{conv_rate:.1f}%</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Avg Follow-Up Time</div>
        <div class="kpi-value">{avg_follow:.1f}h</div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-value">${total_rev/1e6:.2f}M</div>
    </div>""", unsafe_allow_html=True)

# ── Charts Row 1 ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📍 Regional & Industry Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    region_data = (
        filtered.groupby("Region")
        .agg(Total=("Lead_ID", "count"), Converted=("Converted", "sum"))
        .reset_index()
    )
    region_data["Not Converted"] = region_data["Total"] - region_data["Converted"]
    region_data = region_data.sort_values("Total", ascending=False)

    fig_region = px.bar(
        region_data, x="Region", y=["Converted", "Not Converted"],
        title="Leads by Region (Converted vs Not Converted)",
        color_discrete_map={"Converted": "#2d6a9f", "Not Converted": "#b0c4de"},
        barmode="stack",
        template="plotly_white",
    )
    fig_region.update_layout(legend_title="Status", title_font_size=14)
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    ind_data = (
        filtered.groupby("Industry")
        .agg(Total=("Lead_ID", "count"), Converted=("Converted", "sum"))
        .reset_index()
    )
    ind_data["Conversion Rate (%)"] = (ind_data["Converted"] / ind_data["Total"] * 100).round(1)
    ind_data = ind_data.sort_values("Conversion Rate (%)", ascending=True)

    fig_ind = px.bar(
        ind_data, x="Conversion Rate (%)", y="Industry",
        orientation="h",
        title="Conversion Rate by Industry (%)",
        color="Conversion Rate (%)",
        color_continuous_scale="Blues",
        template="plotly_white",
        text="Conversion Rate (%)",
    )
    fig_ind.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_ind.update_layout(coloraxis_showscale=False, title_font_size=14)
    st.plotly_chart(fig_ind, use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">💰 Revenue & Lead Source Analysis</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    # Revenue trend by Industry (sorted)
    rev_data = (
        filtered.groupby("Industry")["Revenue"]
        .sum()
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )
    rev_data["Revenue ($K)"] = (rev_data["Revenue"] / 1000).round(1)

    fig_rev = px.line(
        rev_data, x="Industry", y="Revenue ($K)",
        title="Revenue by Industry ($K)",
        markers=True,
        template="plotly_white",
        color_discrete_sequence=["#2d6a9f"],
    )
    fig_rev.update_traces(line_width=3, marker_size=8)
    fig_rev.update_layout(title_font_size=14)
    st.plotly_chart(fig_rev, use_container_width=True)

with col4:
    src_data = (
        filtered.groupby("Lead_Source")
        .agg(Total=("Lead_ID", "count"), Converted=("Converted", "sum"))
        .reset_index()
    )
    src_data["Conv Rate"] = (src_data["Converted"] / src_data["Total"] * 100).round(1)

    fig_src = px.scatter(
        src_data, x="Total", y="Conv Rate",
        size="Total", color="Lead_Source",
        title="Lead Source Analysis (Volume vs Conversion Rate)",
        labels={"Total": "Total Leads", "Conv Rate": "Conversion Rate (%)"},
        template="plotly_white",
        size_max=50,
        text="Lead_Source",
    )
    fig_src.update_traces(textposition="top center")
    fig_src.update_layout(showlegend=False, title_font_size=14)
    st.plotly_chart(fig_src, use_container_width=True)

# ── Follow-Up Time Analysis ───────────────────────────────────────────────────
st.markdown('<div class="section-header">⏱️ Follow-Up Time vs Conversion</div>', unsafe_allow_html=True)

col5, col6 = st.columns(2)

with col5:
    bins = pd.cut(filtered["Follow_Up_Time"], bins=[0, 12, 24, 48, 72, 96], 
                  labels=["0–12h", "12–24h", "24–48h", "48–72h", "72–96h"])
    followup_data = (
        filtered.groupby(bins, observed=True)
        .agg(Total=("Lead_ID", "count"), Converted=("Converted", "sum"))
        .reset_index()
    )
    followup_data["Conv Rate (%)"] = (followup_data["Converted"] / followup_data["Total"] * 100).round(1)
    followup_data.columns = ["Time Bucket", "Total", "Converted", "Conv Rate (%)"]

    fig_ft = px.bar(
        followup_data, x="Time Bucket", y="Conv Rate (%)",
        title="Conversion Rate by Follow-Up Time Window",
        color="Conv Rate (%)",
        color_continuous_scale="Blues",
        template="plotly_white",
        text="Conv Rate (%)",
    )
    fig_ft.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_ft.update_layout(coloraxis_showscale=False, title_font_size=14)
    st.plotly_chart(fig_ft, use_container_width=True)

with col6:
    fig_box = px.box(
        filtered, x="Status", y="Follow_Up_Time",
        color="Status",
        title="Follow-Up Time Distribution by Conversion Status",
        color_discrete_map={"Converted": "#2d6a9f", "Not Converted": "#b0c4de"},
        template="plotly_white",
    )
    fig_box.update_layout(showlegend=False, title_font_size=14)
    st.plotly_chart(fig_box, use_container_width=True)

# ── Business Insights ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">💡 Business Insights & Recommendations</div>', unsafe_allow_html=True)

# Compute insights dynamically from filtered data
best_region = (
    filtered.groupby("Region")
    .apply(lambda x: x["Converted"].sum() / len(x) * 100, include_groups=False)
    .idxmax()
)
best_region_rate = (
    filtered.groupby("Region")
    .apply(lambda x: x["Converted"].sum() / len(x) * 100, include_groups=False)
    .max()
)

src_conv = (
    filtered.groupby("Lead_Source")
    .apply(lambda x: x["Converted"].sum() / len(x) * 100, include_groups=False)
)
best_source = src_conv.idxmax()
best_source_rate = src_conv.max()

avg_ft_conv = filtered[filtered["Status"] == "Converted"]["Follow_Up_Time"].mean()
avg_ft_not  = filtered[filtered["Status"] == "Not Converted"]["Follow_Up_Time"].mean()
ft_diff     = avg_ft_not - avg_ft_conv

i1, i2 = st.columns(2)

with i1:
    st.markdown(f"""<div class="insight-box">
        🏆 <strong>Q1 – Best Region:</strong> <strong>{best_region}</strong> has the highest conversion rate 
        at <strong>{best_region_rate:.1f}%</strong>. Focus sales resources and campaigns here for maximum ROI.
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="insight-box">
        🎯 <strong>Q2 – Best Lead Source:</strong> <strong>{best_source}</strong> delivers the highest conversion 
        rate at <strong>{best_source_rate:.1f}%</strong>. Increase budget and effort on this channel.
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="insight-box">
        ⏱️ <strong>Q3 – Follow-Up Impact:</strong> Converted leads are followed up 
        <strong>{ft_diff:.1f} hours faster</strong> on average than non-converted leads 
        (Converted avg: {avg_ft_conv:.1f}h | Not Converted avg: {avg_ft_not:.1f}h). 
        Speed is a critical success factor.
    </div>""", unsafe_allow_html=True)

with i2:
    st.markdown("""<div class="insight-box">
        📌 <strong>Strategy 1 – Speed-to-Lead Protocol:</strong> Implement a rule requiring all new leads 
        to receive a first response within <strong>12 hours</strong>. Automate immediate acknowledgement 
        emails via Make.com the moment a form is submitted.
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="insight-box">
        📌 <strong>Strategy 2 – Channel Reallocation:</strong> Shift 30% of marketing budget from 
        low-performing lead sources to the top-performing channel. Use A/B testing to continuously 
        optimize messaging on that channel.
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="insight-box">
        📌 <strong>Strategy 3 – Regional Playbook:</strong> Study what the best-performing region 
        does differently (sales scripts, pricing, timing) and replicate that playbook in underperforming 
        regions with localized training and incentives.
    </div>""", unsafe_allow_html=True)

# ── Raw Data Table ────────────────────────────────────────────────────────────
with st.expander("🗂️ View Raw Data (Filtered)"):
    st.dataframe(
        filtered.style.format({"Revenue": "${:,.2f}", "Follow_Up_Time": "{:.1f}h"}),
        use_container_width=True,
        height=300,
    )
    st.download_button(
        "⬇️ Download Filtered Data as CSV",
        data=filtered.to_csv(index=False),
        file_name="filtered_leads.csv",
        mime="text/csv",
    )
