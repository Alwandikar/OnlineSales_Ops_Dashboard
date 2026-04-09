"""
pages/2_Disposition_Detail.py — DSG Online Sales Team · Disposition Detail
"""
import streamlit as st
from utils.constants import AGENT_CAMPAIGN_MAP, ALL_DISPOSITIONS, CAMPAIGN_CONFIG
from utils.data import load_raw_cache, filter_raw_by_dates
from utils.styles import inject_css
from utils.components import (
    agent_disposition_bar, disp_card, disposition_stacked_bar,
    empty_state, render_date_filter, render_disposition_table,
    section_label, top_nav,
)

st.set_page_config(page_title="DSG Sales · Disposition Detail", page_icon="📋",
                   layout="wide", initial_sidebar_state="collapsed")
inject_css()

raw_df, cached_date = load_raw_cache()
nav_subtitle = f"Dashboard · {cached_date}" if cached_date else "Dashboard"
top_nav(subtitle=nav_subtitle, page_tag="Disposition Detail")

if raw_df is None:
    empty_state(title="No data loaded yet", sub="Upload a CSV on the Overview page.")
    st.stop()



# Campaign filter
section_label("Filter by Campaign", margin_top="0")
camp_filter = st.radio("Campaign", ["All Campaigns","Sports","Holiday"],
                       horizontal=True, label_visibility="collapsed")
if camp_filter != "All Campaigns":
    raw_df = raw_df[raw_df["Campaign"] == camp_filter]

total_rows = len(raw_df)

# Disposition summary cards
section_label("Overall Disposition Breakdown")
cols = st.columns(len(ALL_DISPOSITIONS))
for i, disp in enumerate(ALL_DISPOSITIONS):
    count = int((raw_df["Disposition"] == disp).sum())
    pct   = round(count / total_rows * 100, 1) if total_rows else 0.0
    with cols[i]:
        st.markdown(disp_card(disp, count, pct), unsafe_allow_html=True)

# Stacked bar — pivot built once
section_label("Disposition Mix · All Agents")
pivot = raw_df.groupby(["Agent","Disposition"]).size().unstack(fill_value=0)
for d in ALL_DISPOSITIONS:
    if d not in pivot.columns: pivot[d] = 0
pivot = pivot[ALL_DISPOSITIONS]
pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]
st.plotly_chart(disposition_stacked_bar(pivot), use_container_width=True, config={"displayModeBar": False})

# Agent × Disposition table
section_label("Agent × Disposition Table")
table_pivot = render_disposition_table(raw_df, AGENT_CAMPAIGN_MAP)

# Per-agent breakdown
st.markdown("<hr class='dash-divider'>", unsafe_allow_html=True)
section_label("Per-Agent Disposition Detail")

for agent in table_pivot.index.tolist():
    campaign = AGENT_CAMPAIGN_MAP.get(agent, "Unknown")
    cfg      = CAMPAIGN_CONFIG.get(campaign, {"chip_class":"chip-holiday","emoji":"❓"})
    total    = int(table_pivot.loc[agent, "Total"])

    st.markdown(f"""<div class="agent-section">
        <div class="agent-name-header">{agent}</div>
        <div class="agent-camp-chip {cfg['chip_class']}">{cfg['emoji']} {campaign}</div>
    """, unsafe_allow_html=True)

    dcols = st.columns(len(ALL_DISPOSITIONS))
    for i, disp in enumerate(ALL_DISPOSITIONS):
        count = int(table_pivot.loc[agent, disp])
        pct   = round(count / total * 100, 1) if total else 0.0
        with dcols[i]:
            st.markdown(disp_card(disp, count, pct, small=True), unsafe_allow_html=True)

    st.markdown("<div style='height:.7rem'></div>", unsafe_allow_html=True)
    counts = [int(table_pivot.loc[agent, d]) for d in ALL_DISPOSITIONS]
    pcts   = [round(c/total*100,1) if total else 0.0 for c in counts]
    st.plotly_chart(agent_disposition_bar(agent, counts, pcts),
                    use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)
