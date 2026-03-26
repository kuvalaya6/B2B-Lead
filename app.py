import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================
# PAGE CONFIG + THEME
# ==============================
st.set_page_config(
    page_title="B2B Renaissance Leads Intelligence",
    layout="wide"
)

# Custom dark/brown renaissance style
st.markdown(
    """
    <style>
        body {
            background-color: #1b130f;
        }
        .stApp {
            background: radial-gradient(circle at top, #3b2618 0%, #120c08 55%, #050301 100%);
            color: #f5e6ca;
            font-family: "Georgia", "Serif";
        }
        h1, h2, h3, h4 {
            color: #f5e6ca;
        }
        .block-container {
            padding-top: 1.5rem;
        }
        .css-1d391KG, .css-1fcdlhc {
            background-color: #24160f !important;
        }
        .st-tabs [role="tab"] {
            background-color: #2a1b11;
            color: #f5e6ca;
            border-radius: 4px 4px 0 0;
            padding: 0.5rem 1rem;
            border: 1px solid #5e3b1f;
            margin-right: 0.25rem;
        }
        .st-tabs [role="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #5e3b1f, #3b2618);
            color: #fdf3dc;
        }
        .stMetric {
            background-color: #2d1c12;
            border-radius: 8px;
            padding: 0.75rem;
            border: 1px solid #6d3f1f;
        }
        .stDataFrame {
            background-color: #2d1c12 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Title / caption in a "renaissance" tone
st.title("🕯️ B2B Lead Renaissance Intelligence")
st.caption("Leads • Conversion • Revenue • Timely Follow-up – Illuminated on a dark, renaissance canvas")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data(path: str):
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    # Basic cleaning
    df["Status"] = df["Status"].astype(str).str.strip().str.title()   # Converted / Not Converted
    df["Industry"] = df["Industry"].astype(str).str.strip()
    df["Region"] = df["Region"].astype(str).str.strip()
    df["Lead_Source"] = df["Lead_Source"].astype(str).str.strip()
    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce")
    df["Follow_Up_Time"] = pd.to_numeric(df["Follow_Up_Time"], errors="coerce")
    return df

data_file = "B2B_Leads_Dataset_1000Records.xlsx"
df = load_data(data_file)

# ==============================
# SAFETY CHECK
# ==============================
required_cols = [
    "Lead_ID", "Client_Name", "Industry", "Region",
    "Lead_Source", "Revenue", "Status", "Follow_Up_Time"
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error("Dataset is missing columns: " + ", ".join(missing))
    st.stop()

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("Filters – Choose Your Realm")

regions = sorted(df["Region"].dropna().unique())
industries = sorted(df["Industry"].dropna().unique())
sources = sorted(df["Lead_Source"].dropna().unique())

sel_region = st.sidebar.multiselect("Region", regions, default=regions)
sel_industry = st.sidebar.multiselect("Industry", industries, default=industries)
sel_source = st.sidebar.multiselect("Lead Source", sources, default=sources)

rev_min, rev_max = float(df["Revenue"].min()), float(df["Revenue"].max())
sel_rev = st.sidebar.slider(
    "Revenue Range",
    min_value=rev_min,
    max_value=rev_max,
    value=(rev_min, rev_max)
)

filtered = df[
    df["Region"].isin(sel_region)
    & df["Industry"].isin(sel_industry)
    & df["Lead_Source"].isin(sel_source)
    & (df["Revenue"] >= sel_rev[0])
    & (df["Revenue"] <= sel_rev[1])
].copy()

# ==============================
# TABS
# ==============================
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Dashboard", "📈 Visual Stories", "🧠 Business Insights", "📄 Data View"]
)

# =======================================
# TAB 1: MAIN DASHBOARD (KPIs + quick)
# =======================================
with tab1:
    st.subheader("Golden Metrics of the Lead Kingdom")

    total_leads = len(filtered)
    converted_leads = int((filtered["Status"] == "Converted").sum())
    conversion_rate = (converted_leads / total_leads * 100) if total_leads else 0
    avg_follow = filtered["Follow_Up_Time"].mean() if total_leads else 0
    total_revenue = filtered["Revenue"].sum() if total_leads else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Leads", f"{total_leads}")
    k2.metric("Converted Leads", f"{converted_leads}")
    k3.metric("Conversion Rate", f"{conversion_rate:.2f}%")
    k4.metric("Avg Follow-up (hrs)", f"{avg_follow:.2f}")
    k5.metric("Total Revenue", f"{total_revenue:,.0f}")

    st.divider()

    c1, c2 = st.columns(2)

    # Leads by Region (bar)
    with c1:
        st.markdown("### 🗺️ Leads by Region")
        if not filtered.empty:
            leads_by_region = (
                filtered.groupby("Region")["Lead_ID"].count().reset_index(name="Lead_Count")
            )
            leads_by_region = leads_by_region.sort_values("Lead_Count", ascending=False)

            plt.style.use("dark_background")
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(
                data=leads_by_region,
                x="Region",
                y="Lead_Count",
                ax=ax,
                palette=["#f0c27b", "#e0a96d", "#a97142", "#6b3e26", "#3e2417"]
            )
            ax.set_xlabel("Region", color="#f5e6ca")
            ax.set_ylabel("Number of Leads", color="#f5e6ca")
            ax.tick_params(colors="#f5e6ca")
            fig.patch.set_facecolor("#1b130f")
            ax.set_facecolor("#1b130f")
            st.pyplot(fig)
        else:
            st.info("No data under current filters.")

    # Lead Source distribution
    with c2:
        st.markdown("### 🕊️ Lead Source Mix")
        if not filtered.empty:
            ls = (
                filtered.groupby("Lead_Source")["Lead_ID"].count().reset_index(name="Lead_Count")
            )
            ls = ls.sort_values("Lead_Count", ascending=False)

            fig2, ax2 = plt.subplots(figsize=(6, 4))
            sns.barplot(
                data=ls,
                x="Lead_Source",
                y="Lead_Count",
                ax=ax2,
                palette=["#e0a96d", "#f0c27b", "#a97142", "#6b3e26", "#3e2417", "#987554"]
            )
            ax2.set_xlabel("Lead Source", color="#f5e6ca")
            ax2.set_ylabel("Number of Leads", color="#f5e6ca")
            ax2.tick_params(colors="#f5e6ca", axis="x", rotation=30)
            fig2.patch.set_facecolor("#1b130f")
            ax2.set_facecolor("#1b130f")
            st.pyplot(fig2)
        else:
            st.info("No data under current filters.")

    st.divider()

    st.markdown("### 🔎 Lead Explorer")
    lead_id_input = st.text_input("Enter Lead_ID (exact):", value="")
    if lead_id_input:
        row = filtered[filtered["Lead_ID"].astype(str) == lead_id_input]
        if row.empty:
            st.warning("No such Lead_ID under current filters.")
        else:
            r = row.iloc[0]
            cA, cB, cC, cD = st.columns(4)
            cA.metric("Client", r["Client_Name"])
            cB.metric("Industry", r["Industry"])
            cC.metric("Region", r["Region"])
            cD.metric("Status", r["Status"])
            st.write("Lead Details")
            st.dataframe(row, use_container_width=True)

    st.download_button(
        "⬇️ Download Filtered Leads (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_b2b_leads.csv",
        mime="text/csv"
    )

# =======================================
# TAB 2: VISUAL STORIES
# =======================================
with tab2:
    st.subheader("Visual Stories in the Ledger")

    c1, c2 = st.columns(2)

    # Conversion rate by Industry
    with c1:
        st.markdown("### 🏛️ Conversion Rate by Industry")
        if not filtered.empty:
            conv_ind = (
                filtered.groupby("Industry")
                .apply(lambda x: (x["Status"] == "Converted").mean() * 100)
                .reset_index(name="Conversion_Rate")
            ).sort_values("Conversion_Rate", ascending=False)

            fig3, ax3 = plt.subplots(figsize=(6, 4))
            sns.barplot(
                data=conv_ind,
                x="Industry",
                y="Conversion_Rate",
                ax=ax3,
                palette="copper"
            )
            ax3.set_ylabel("Conversion Rate (%)", color="#f5e6ca")
            ax3.set_xlabel("Industry", color="#f5e6ca")
            ax3.tick_params(colors="#f5e6ca", axis="x", rotation=30)
            fig3.patch.set_facecolor("#1b130f")
            ax3.set_facecolor("#1b130f")
            st.pyplot(fig3)
        else:
            st.info("No data under current filters.")

    # Revenue trend by Lead_ID order
    with c2:
        st.markdown("### 📜 Revenue Trend (Lead Sequence)")
        if not filtered.empty:
            ordered = filtered.sort_values("Lead_ID")
            fig4, ax4 = plt.subplots(figsize=(6, 4))
            ax4.plot(
                ordered["Lead_ID"],
                ordered["Revenue"],
                color="#e0a96d",
                marker=".",
                linewidth=1
            )
            ax4.set_xlabel("Lead_ID (ordered)", color="#f5e6ca")
            ax4.set_ylabel("Revenue", color="#f5e6ca")
            ax4.tick_params(colors="#f5e6ca", axis="x", rotation=45)
            fig4.patch.set_facecolor("#1b130f")
            ax4.set_facecolor("#1b130f")
            st.pyplot(fig4)
        else:
            st.info("No data under current filters.")

    st.divider()

    st.markdown("### ⏳ Follow-up Time vs Conversion")
    if not filtered.empty:
        fig5, ax5 = plt.subplots(figsize=(7, 4))
        sns.boxplot(
            data=filtered,
            x="Status",
            y="Follow_Up_Time",
            ax=ax5,
            palette=["#f0c27b", "#6b3e26"]
        )
        ax5.set_xlabel("Status", color="#f5e6ca")
        ax5.set_ylabel("Follow-up Time (hrs)", color="#f5e6ca")
        ax5.tick_params(colors="#f5e6ca")
        fig5.patch.set_facecolor("#1b130f")
        ax5.set_facecolor("#1b130f")
        st.pyplot(fig5)
    else:
        st.info("No data under current filters.")

# =======================================
# TAB 3: BUSINESS INSIGHTS (Part D)
# =======================================
with tab3:
    st.subheader("🧠 Business Insights & Renaissance Counsel")

    if not df.empty:
        # 1) Region with highest conversion rate
        conv_region = (
            df.groupby("Region")
            .apply(lambda x: (x["Status"] == "Converted").mean() * 100)
            .reset_index(name="Conversion_Rate")
        )
        if not conv_region.empty:
            best_reg_row = conv_region.sort_values("Conversion_Rate", ascending=False).iloc[0]
            st.write(
                f"**1. Region with highest conversion rate:** "
                f"{best_reg_row['Region']} (~{best_reg_row['Conversion_Rate']:.2f}%)."
            )
        else:
            st.write("1. Not enough data to compare regions.")

        # 2) Best lead source
        conv_source = (
            df.groupby("Lead_Source")
            .apply(lambda x: (x["Status"] == "Converted").mean() * 100)
            .reset_index(name="Conversion_Rate")
        )
        if not conv_source.empty:
            best_src_row = conv_source.sort_values("Conversion_Rate", ascending=False).iloc[0]
            st.write(
                f"**2. Best-performing lead source:** "
                f"{best_src_row['Lead_Source']} (~{best_src_row['Conversion_Rate']:.2f}%)."
            )
        else:
            st.write("2. Not enough data to compare lead sources.")

        # 3) Follow-up time vs conversion
        st.markdown("**3. Is follow-up time affecting conversion?**")
        temp = df[["Follow_Up_Time", "Status"]].dropna()
        if not temp.empty:
            avg_follow_conv = temp[temp["Status"] == "Converted"]["Follow_Up_Time"].mean()
            avg_follow_not = temp[temp["Status"] == "Not Converted"]["Follow_Up_Time"].mean()
            st.write(
                f"- Average follow-up time for **Converted** leads: {avg_follow_conv:.2f} hours."
            )
            st.write(
                f"- Average follow-up time for **Not Converted** leads: {avg_follow_not:.2f} hours."
            )
            if avg_follow_conv < avg_follow_not:
                st.write(
                    "Insight: Faster follow-up is associated with better conversion "
                    "(converted leads are contacted sooner on average)."
                )
            else:
                st.write(
                    "Insight: Converted leads are not consistently contacted faster; "
                    "conversion may depend more on other factors (quality, channel, etc.)."
                )
        else:
            st.write("Not enough follow-up time data to analyze impact on conversion.")

        st.markdown("**4. Suggested strategies to improve conversion:**")
        st.markdown(
            """
            1. **Prioritise high-performing regions and sources**  
               Focus budget and sales effort where conversion rates are already strong, and replicate those playbooks in weaker regions.

            2. **Reduce follow-up time using automation**  
               Use Make.com to instantly confirm new leads, log them in a sheet/CRM, and notify sales reps so that first contact happens within a defined SLA (e.g., 24 hours).

            3. **Segmented nurturing journeys**  
               Create different nurture flows by industry and lead source, with tailored messaging, case studies, and offers, to increase relevance and trust.

            """
        )
    else:
        st.info("Dataset is empty – cannot derive insights.")

# =======================================
# TAB 4: DATA VIEW
# =======================================
with tab4:
    st.subheader("📄 Ledger of Leads (Data View)")
    st.caption("Preview to show your professor the data behind the renaissance visuals.")

    st.dataframe(filtered.head(200), use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows (filtered)", len(filtered))
    c2.metric("Unique Industries", filtered["Industry"].nunique())
    c3.metric("Unique Regions", filtered["Region"].nunique())
    c4.metric("Avg Revenue", f"{filtered['Revenue'].mean():.0f}" if len(filtered) else "NA")
