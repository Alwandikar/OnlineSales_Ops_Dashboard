"""
pages/2_Disposition_Detail.py — DSG Online Sales Team · Disposition Detail
"""
import streamlit as st

from utils.constants import AGENT_CAMPAIGN_MAP, ALL_DISPOSITIONS, CAMPAIGN_CONFIG
from utils.data import filter_by_dates, build_summary
from utils.github_store import load_data
from utils.styles import inject_css
from utils.components import (
    agent_disp_bar, disp_card, disposition_stacked_bar,
    disp_table, empty_state, render_date_filter,
    section_label, sidebar_nav, top_nav,
)

st.set_page_config(
    page_title="DSG Online Sales · Disposition Detail",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# ── Sidebar ───────────────────────────────────────────────────────────────────
sidebar_nav()

# ── Load data ─────────────────────────────────────────────────────────────────
all_data = load_data()

nav_sub = "Dashboard"
if not all_data.empty and "Date" in all_data.columns:
    max_date = all_data["Date"].max()
    nav_sub  = f"Last updated: {max_date.strftime('%d %b %Y') if hasattr(max_date,'strftime') else max_date}"

top_nav(subtitle=nav_sub, page_tag="Disposition Detail")

if all_data.empty:
    empty_state(title="No data yet", sub="Upload a CSV via the sidebar on the Overview page.")
    st.stop()

# ── Date filter ───────────────────────────────────────────────────────────────
from_date, to_date = render_date_filter("disp")

raw_df = filter_by_dates(all_data, from_date, to_date)

if raw_df.empty:
    empty_state(title="No data for this range", sub="Try a wider date range.", icon="📅")
    st.stop()

# ── Campaign filter ───────────────────────────────────────────────────────────
section_label("Filter by Campaign", mt="0")
camp_filter = st.radio("Campaign", ["All", "Sports", "Holiday"],
                       horizontal=True, label_visibility="collapsed")
if camp_filter != "All":
    raw_df = raw_df[raw_df["Campaign"] == camp_filter]

total_rows = len(raw_df)

# ── Disposition summary cards ─────────────────────────────────────────────────
section_label("Overall Disposition Breakdown")
cols = st.columns(len(ALL_DISPOSITIONS))
for i, disp in enumerate(ALL_DISPOSITIONS):
    count = int((raw_df["Disposition"] == disp).sum())
    pct   = round(count / total_rows * 100, 1) if total_rows else 0.0
    with cols[i]:
        st.markdown(disp_card(disp, count, pct), unsafe_allow_html=True)

# ── Stacked bar ───────────────────────────────────────────────────────────────
section_label("Disposition Mix · All Agents")
pivot = raw_df.groupby(["Agent","Disposition"]).size().unstack(fill_value=0)
for d in ALL_DISPOSITIONS:
    if d not in pivot.columns: pivot[d] = 0
pivot = pivot[ALL_DISPOSITIONS]
pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]
st.plotly_chart(
    disposition_stacked_bar(pivot),
    use_container_width=True,
    config={"displayModeBar": False},
)

# ── Agent × Disposition table ─────────────────────────────────────────────────
section_label("Agent × Disposition Table")
table_pivot = disp_table(raw_df, AGENT_CAMPAIGN_MAP)

# ── Per-agent detail ──────────────────────────────────────────────────────────
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
section_label("Per-Agent Breakdown")

for agent in table_pivot.index.tolist():
    campaign = AGENT_CAMPAIGN_MAP.get(agent, "Unknown")
    cfg      = CAMPAIGN_CONFIG.get(campaign, {"chip": "chip-holiday", "emoji": "❓"})
    total    = int(table_pivot.loc[agent, "Total"])

    st.markdown(f"""<div class="agent-section">
        <div class="agent-name">{agent}</div>
        <div class="agent-chip {cfg['chip']}">{cfg['emoji']} {campaign}</div>
    """, unsafe_allow_html=True)

    dcols = st.columns(len(ALL_DISPOSITIONS))
    for i, disp in enumerate(ALL_DISPOSITIONS):
        count = int(table_pivot.loc[agent, disp])
        pct   = round(count / total * 100, 1) if total else 0.0
        with dcols[i]:
            st.markdown(disp_card(disp, count, pct, small=True), unsafe_allow_html=True)

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
    counts = [int(table_pivot.loc[agent, d]) for d in ALL_DISPOSITIONS]
    pcts   = [round(c/total*100,1) if total else 0.0 for c in counts]
    st.plotly_chart(
        agent_disp_bar(agent, counts, pcts),
        use_container_width=True,
        config={"displayModeBar": False},
    )
    st.markdown("</div>", unsafe_allow_html=True)
