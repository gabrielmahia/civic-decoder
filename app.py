"""
Civic Decoder — Kenya legislative and civic intelligence.

Three tools in one:
  1. MP Tracker      — attendance, bills sponsored, questions asked, CDF absorption
  2. Bill Tracker    — legislation status, votes, plain-language summaries
  3. CDF Watchdog    — constituency fund utilisation ranked by county

Data: parliament.go.ke, NG-CDF Annual Reports, Kenya Gazette (public domain).
Seed data covers 15 MPs and 10 bills from the 13th Parliament (2022–2027).
Community submissions expand the dataset via the Contribute page.

This tool does NOT track private individuals. All subjects are elected
public officials acting in their official capacity. Data is factual and
sourced. Opinions and analysis are clearly labelled.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Hakiki — Civic Intelligence Kenya",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Mobile CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

.cd-header {
    background: linear-gradient(135deg, #0a2342 0%, #1a3a5c 60%, #2c5282 100%);
    color: white; padding: 1.6rem 2rem; border-radius: 10px; margin-bottom: 1.2rem;
}
.cd-header h1 { font-family:'IBM Plex Mono',monospace; font-size:1.8rem; margin:0 0 .2rem; letter-spacing:-1px; }
.cd-header p  { font-size:.9rem; opacity:.75; margin:0; }

.metric-card {
    background:#f8f9fa; border-radius:8px; padding:1rem 1.2rem;
    border-left:4px solid #2c5282; margin-bottom:.6rem;
}
.metric-card .label { font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; color:#6c757d; }
.metric-card .value { font-family:'IBM Plex Mono',monospace; font-size:1.5rem; font-weight:600; color:#0a2342; }

.badge-confirmed { background:#d4edda; color:#155724; padding:2px 8px; border-radius:20px; font-size:.78rem; }
.badge-est       { background:#fff3cd; color:#856404; padding:2px 8px; border-radius:20px; font-size:.78rem; }
.badge-seed      { background:#e2d9f3; color:#6f42c1; padding:2px 8px; border-radius:20px; font-size:.78rem; }

.data-note {
    background:#e8f4fd; border-left:4px solid #2c5282;
    padding:.7rem 1rem; border-radius:4px; font-size:.83rem; margin-bottom:1rem;
}

@media (max-width: 768px) {
    [data-testid="column"] { width:100% !important; flex:1 1 100% !important; min-width:100% !important; }
    [data-testid="stMetricValue"] { font-size:1.4rem !important; }
    [data-testid="stDataFrame"]   { overflow-x:auto !important; }
    .stButton>button { width:100% !important; min-height:48px !important; }
    .cd-header h1 { font-size:1.3rem !important; }
    .stSelectbox  { font-size:.9rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Data loading ──────────────────────────────────────────────────────────────
DATA = Path(__file__).parent / "data"

@st.cache_data(ttl=3600)
def load_mps():
    return pd.read_csv(DATA / "mps" / "mps_seed.csv")

@st.cache_data(ttl=3600)
def load_bills():
    df = pd.read_csv(DATA / "bills" / "bills_seed.csv")
    df["introduced_date"] = pd.to_datetime(df["introduced_date"])
    return df

@st.cache_data(ttl=3600)
def load_cdf():
    return pd.read_csv(DATA / "cdf" / "cdf_seed.csv")

mps   = load_mps()
bills = load_bills()
cdf   = load_cdf()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="cd-header">
  <h1>🏛️ Macho ya Wananchi — Civic Decoder Kenya</h1>
  <p>MP performance · Bill tracker · CDF watchdog — 13th Parliament (2022–2027)</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="data-note">
📋 <strong>Seed dataset:</strong> 15 of 350 MPs (4.3%), 10 bills, 14 of 290 constituencies (4.8%).<br>
This is a <strong>demonstration of what full civic coverage would look like</strong> — not a complete
parliamentary accountability tool. Data is from public parliament.go.ke records and NG-CDF Annual Reports.
<strong>Do not draw conclusions about MPs not in this dataset.</strong>
Community contributions expand coverage — use the Contribute tab.
</div>
""", unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
tab_mp, tab_bills, tab_cdf, tab_contribute = st.tabs([
    "👤 MP Tracker", "📜 Bill Tracker", "💰 CDF Watchdog", "➕ Contribute"
])

# ═══════════════════════════════════════════════════════════
# TAB 1: MP TRACKER
# ═══════════════════════════════════════════════════════════
with tab_mp:
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        search = st.text_input("🔍 Search MP by name or constituency", placeholder="e.g. Odhiambo, Rarieda…")
    with col_f2:
        party_filter = st.selectbox("Party", ["All"] + sorted(mps["party"].unique().tolist()))

    filtered = mps.copy()
    if search:
        mask = (
            filtered["name"].str.contains(search, case=False, na=False) |
            filtered["constituency"].str.contains(search, case=False, na=False) |
            filtered["county"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]
    if party_filter != "All":
        filtered = filtered[filtered["party"] == party_filter]

    st.caption(f"Showing {len(filtered)} of {len(mps)} MPs in seed dataset")

    if filtered.empty:
        st.info("No MPs match your search. Try a different name or constituency.")
    else:
        # Summary KPIs
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Avg. Attendance", f"{filtered['attendance_pct'].mean():.1f}%")
        k2.metric("Total Bills Sponsored", int(filtered["bills_sponsored"].sum()))
        k3.metric("Total Questions Asked", int(filtered["questions_asked"].sum()))
        k4.metric("MPs shown", len(filtered))

        st.divider()

        # Per-MP cards
        for _, mp in filtered.iterrows():
            with st.expander(f"**{mp['name']}** — {mp['constituency']}, {mp['county']} ({mp['party']})"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Attendance", f"{mp['attendance_pct']:.1f}%",
                          delta="Above avg" if mp["attendance_pct"] > 75 else "Below avg",
                          delta_color="normal" if mp["attendance_pct"] > 75 else "inverse")
                c2.metric("Bills Sponsored", int(mp["bills_sponsored"]))
                c3.metric("Questions Asked", int(mp["questions_asked"]))

                st.markdown(f"**Committees:** {mp.get('committees','—').replace(';',' · ')}")
                st.markdown(f"**First elected:** {int(mp['elected_year'])} · **Gender:** {'♀' if mp['gender']=='F' else '♂'}")

                # CDF data for this MP
                # Match on first two name tokens to handle surname variants
                # (e.g. "Millie Odhiambo Mabona" → search "Millie Odhiambo")
                _name_tokens = mp["name"].replace("Hon. ", "").split()
                _name_key = " ".join(_name_tokens[:2]) if len(_name_tokens) >= 2 else " ".join(_name_tokens)
                mp_cdf = cdf[cdf["mp_name"].str.contains(_name_key, case=False, na=False)]
                if not mp_cdf.empty:
                    row = mp_cdf.iloc[0]
                    st.markdown(f"""
**CDF {row['fy']}:** KSh {row['utilised_kes_m']:.1f}M utilised of KSh {row['allocated_kes_m']:.0f}M
({row['absorption_pct']:.1f}% absorption) · {int(row['projects_complete'])} of {int(row['projects_total'])} projects complete
· Top sector: **{row['top_sector']}**
""")
                src = mp.get("source","parliament.go.ke")
                st.caption(f"Source: {src} · Verified: {mp.get('verified','see source')}")

        st.divider()
        # Attendance scatter
        st.subheader("📊 Attendance vs. Legislative Activity")
        fig = px.scatter(
            filtered,
            x="attendance_pct", y="questions_asked",
            size="bills_sponsored", color="party",
            hover_name="name",
            hover_data={"constituency": True, "county": True},
            labels={"attendance_pct": "Attendance %", "questions_asked": "Questions Asked"},
            color_discrete_map={"UDA": "#e63946", "ODM": "#457b9d", "JUBILEE": "#2d6a4f"},
            title="MP Activity Map — bubble size = bills sponsored",
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Source: parliament.go.ke — seed data, 13th Parliament")

# ═══════════════════════════════════════════════════════════
# TAB 2: BILL TRACKER
# ═══════════════════════════════════════════════════════════
with tab_bills:
    STATUS_COLORS = {
        "Enacted":        "#155724",
        "Committee Stage":"#0c5460",
        "Second Reading": "#856404",
        "First Reading":  "#856404",
        "Passed Senate":  "#004085",
        "Withdrawn":      "#721c24",
    }
    CATEGORY_FILTER = ["All"] + sorted(bills["category"].unique().tolist())
    STATUS_FILTER   = ["All"] + sorted(bills["status"].unique().tolist())

    cf1, cf2 = st.columns(2)
    with cf1:
        cat_f = st.selectbox("Category", CATEGORY_FILTER)
    with cf2:
        stat_f = st.selectbox("Status", STATUS_FILTER)

    fb = bills.copy()
    if cat_f  != "All": fb = fb[fb["category"] == cat_f]
    if stat_f != "All": fb = fb[fb["status"]   == stat_f]

    st.caption(f"Showing {len(fb)} bills")

    # Status summary pills
    status_counts = bills["status"].value_counts()
    pill_html = " &nbsp; ".join(
        f'<span style="background:{STATUS_COLORS.get(s,"#999")};color:white;'
        f'padding:3px 10px;border-radius:20px;font-size:.78rem;">{s}: {n}</span>'
        for s, n in status_counts.items()
    )
    st.markdown(pill_html, unsafe_allow_html=True)
    st.divider()

    for _, b in fb.sort_values("introduced_date", ascending=False).iterrows():
        col_status = STATUS_COLORS.get(b["status"], "#999")
        passed_icon = "✅" if b["passed"] else ("⛔" if b["status"] == "Withdrawn" else "⏳")
        with st.expander(f"{passed_icon} **{b['title']}** — {b['status']}"):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Sponsor:** {b['sponsor']}")
                st.markdown(f"**Introduced:** {b['introduced_date'].strftime('%d %b %Y')} · **Category:** {b['category']} · **Reading:** {b['reading']}")
                st.markdown(f"**Summary:** {b['summary']}")
            with c2:
                if b["votes_for"] > 0 or b["votes_against"] > 0:
                    total_votes = b["votes_for"] + b["votes_against"]
                    st.metric("For", f"{b['votes_for']} ({b['votes_for']/total_votes*100:.0f}%)")
                    st.metric("Against", f"{b['votes_against']}")
                else:
                    st.caption("No vote recorded yet")
            st.caption(f"Source: {b['source']} · {b['verified']}")

    st.divider()
    # Timeline
    st.subheader("📅 Bills Timeline")
    fig2 = px.timeline(
        bills.assign(
            end_date=bills["introduced_date"] + pd.Timedelta(days=90),
            label=bills["title"].str[:45] + "…"
        ),
        x_start="introduced_date", x_end="end_date",
        y="label", color="status",
        color_discrete_map={k: v for k, v in STATUS_COLORS.items()},
        title="Bill progress — 13th Parliament seed data",
    )
    fig2.update_layout(height=420, showlegend=True)
    st.plotly_chart(fig2, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# TAB 3: CDF WATCHDOG
# ═══════════════════════════════════════════════════════════
with tab_cdf:
    st.subheader("💰 CDF Absorption Ranking — FY 2022/23")
    st.caption(
        "Source: NG-CDF Annual Report 2023 (public). "
        "Absorption % = funds actually spent ÷ funds released. "
        "Low absorption = money allocated but not deployed to communities."
    )

    county_filter = st.selectbox("Filter by county", ["All"] + sorted(cdf["county"].unique().tolist()))
    cdf_f = cdf if county_filter == "All" else cdf[cdf["county"] == county_filter]

    cdf_sorted = cdf_f.sort_values("absorption_pct", ascending=False)

    # Bar chart
    fig3 = px.bar(
        cdf_sorted,
        x="absorption_pct", y="mp_name",
        orientation="h",
        color="absorption_pct",
        color_continuous_scale=["#e63946", "#f4a261", "#2d6a4f"],
        range_color=[50, 100],
        labels={"absorption_pct": "Absorption %", "mp_name": "MP"},
        title="CDF Utilisation — higher = more funds reaching communities",
    )
    fig3.add_vline(x=80, line_dash="dash", line_color="gray",
                   annotation_text="80% benchmark", annotation_position="top right")
    fig3.update_layout(height=420, coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

    # Table
    st.dataframe(
        cdf_sorted[[
            "constituency", "county", "mp_name",
            "allocated_kes_m", "utilised_kes_m", "absorption_pct",
            "projects_complete", "projects_total", "top_sector"
        ]].rename(columns={
            "constituency":     "Constituency",
            "county":           "County",
            "mp_name":          "MP",
            "allocated_kes_m":  "Allocated (KSh M)",
            "utilised_kes_m":   "Utilised (KSh M)",
            "absorption_pct":   "Absorption %",
            "projects_complete":"Projects Done",
            "projects_total":   "Projects Total",
            "top_sector":       "Top Sector",
        }),
        use_container_width=True,
        hide_index=True,
    )
    st.caption("⚠️ Seed data — 14 constituencies. Full 290-constituency dataset requires NG-CDF API integration.")

# ═══════════════════════════════════════════════════════════
# TAB 4: CONTRIBUTE
# ═══════════════════════════════════════════════════════════
with tab_contribute:
    st.subheader("➕ Help expand the dataset")
    st.markdown("""
This tool runs on **public domain data** compiled by hand from parliament.go.ke and
NG-CDF annual reports. You can help by:

- **Reporting a data error** — attendance figure wrong, bill status stale, MP left office
- **Submitting a missing MP** — must include a parliament.go.ke profile link
- **Submitting a CDF project** — include the NG-CDF project reference number
- **Flagging a missing bill** — include the bill number from the Kenya Gazette

All submissions are reviewed before publication. This tool does not publish
unverified personal data about private individuals.
""")

    with st.form("contribute_form"):
        contrib_type = st.selectbox("Contribution type",
            ["Error correction", "Missing MP", "Missing bill", "Missing CDF project", "Other"])
        contrib_text = st.text_area("Details (include source URL)", height=120,
            placeholder="e.g. Hon. X's attendance figure should be 78.3% — see parliament.go.ke/hansard/2024-03-12")
        contrib_source = st.text_input("Source URL", placeholder="https://parliament.go.ke/…")
        submitted = st.form_submit_button("Submit contribution", type="primary")
        if submitted:
            if contrib_text.strip():
                st.success("✅ Contribution received — thank you. We review all submissions within 14 days.")
                st.caption("Note: Database writes are not active in demo mode. Submit a GitHub issue at github.com/gabrielmahia/civic-decoder for immediate review.")
            else:
                st.error("Please describe your contribution before submitting.")

    st.divider()
    st.markdown("""
**Want to go deeper?** The full parliament.go.ke dataset can be downloaded at:
- [National Assembly Hansard](https://parliament.go.ke/the-national-assembly/house-business/hansard)
- [NG-CDF Annual Reports](https://ngcdf.go.ke/annual-reports/)
- [Kenya Gazette](https://kenyagazette.go.ke)
- [Mzalendo — parliament watchdog](https://mzalendo.com)
""")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Macho ya Wananchi · Civic Decoder Kenya · Data: parliament.go.ke, NG-CDF Annual Reports, Kenya Gazette · "
    "CC BY-NC-ND 4.0 · contact@aikungfu.dev · "
    "Not affiliated with Parliament of Kenya or NG-CDF Board"
)
