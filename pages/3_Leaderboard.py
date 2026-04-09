"""
pages/3_Leaderboard.py — DSG Online Sales Team · Leaderboard
"""
import plotly.graph_objects as go
import streamlit as st

from utils.constants import CAMPAIGN_CONFIG, DSG_GOLD, FONT, GRID, TXTC
from utils.data import (
    load_raw_cache, filter_raw_by_dates, summarise_raw, format_duration,
)
from utils.styles import inject_css
from utils.components import (
    empty_state, kpi_card, pct_color, render_date_filter,
    section_label, top_nav,
)

st.set_page_config(page_title="DSG Sales · Leaderboard", page_icon="🏆",
                   layout="wide", initial_sidebar_state="collapsed")
inject_css()

raw_df, cached_date = load_raw_cache()
nav_subtitle = f"Dashboard · {cached_date}" if cached_date else "Dashboard"
top_nav(subtitle=nav_subtitle, page_tag="Leaderboard")

if raw_df is None:
    empty_state(title="No data loaded yet", sub="Upload a CSV on the Overview page.", icon="🏆")
    st.stop()

# Force fresh state on new deployment
APP_VERSION = "v5"
if st.session_state.get("_app_version") != APP_VERSION:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state["_app_version"] = APP_VERSION
    st.rerun()

# Date filter
from_date, to_date = render_date_filter()
filtered = filter_raw_by_dates(raw_df, from_date, to_date)

if filtered.empty:
    empty_state(title="No data for this date range", sub="Try a different range.", icon="📅")
    st.stop()

agent_df = summarise_raw(filtered)

# Campaign filter
section_label("Filter by Campaign", margin_top="0")
camp_filter = st.radio("Campaign", ["All","Sports","Holiday"],
                       horizontal=True, label_visibility="collapsed")
display_df = agent_df.copy()
if camp_filter != "All":
    display_df = display_df[display_df["Campaign"] == camp_filter]
display_df = display_df.sort_values("Contact %", ascending=False).reset_index(drop=True)
total_agents = len(display_df)

# Summary KPIs
section_label("Performance Summary")
top_agent = display_df.iloc[0] if not display_df.empty else None
avg_rate  = round(display_df["Contact %"].mean(), 1) if not display_df.empty else 0.0
above_50  = int((display_df["Contact %"] >= 50).sum())
total_talk = float(display_df["TalkTimeSecs"].sum()) if "TalkTimeSecs" in display_df.columns else 0.0

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    top_name = top_agent["Agent"] if top_agent is not None else "—"
    top_pct  = f"{top_agent['Contact %']}%" if top_agent is not None else "—"
    st.markdown(kpi_card("Top Agent", top_name, f"{top_pct} contact rate", "🥇", DSG_GOLD, "kpi-value-gold"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card("Avg Contact Rate", f"{avg_rate}%", f"Across {total_agents} agents", "📊", "#0047CC", "kpi-value-blue"), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_card("Above Target (≥50%)", str(above_50), f"of {total_agents} agents", "✅", "#047857", "kpi-value-green"), unsafe_allow_html=True)
with k4:
    below = total_agents - above_50
    st.markdown(kpi_card("Below Target (<50%)", str(below), f"of {total_agents} agents", "⚠️", "#B91C1C", "kpi-value-red"), unsafe_allow_html=True)
with k5:
    st.markdown(kpi_card("Total Talk Time", format_duration(total_talk), "Calls with duration > 0s", "🎙️", "#0047CC", "kpi-value-blue"), unsafe_allow_html=True)

# Ranked rows
section_label("Agent Rankings")
max_pct = display_df["Contact %"].max() if not display_df.empty else 100

for i, row in display_df.iterrows():
    rank      = i + 1
    pct       = row["Contact %"]
    campaign  = row["Campaign"]
    cfg       = CAMPAIGN_CONFIG.get(campaign, {"chip_class":"chip-holiday","emoji":"❓"})
    bar_color = pct_color(pct)
    bar_width = round(pct / max_pct * 100, 1) if max_pct else 0
    talk      = format_duration(row["TalkTimeSecs"]) if "TalkTimeSecs" in row else "—"

    badge = "rank-1" if rank==1 else "rank-2" if rank==2 else "rank-3" if rank==3 else "rank-n"
    medal = {1:"🥇",2:"🥈",3:"🥉"}.get(rank, str(rank))

    st.markdown(f"""<div class="leaderboard-row">
        <div class="rank-badge {badge}">{medal}</div>
        <div style="min-width:130px">
            <div class="lb-agent">{row['Agent']}</div>
            <div class="lb-camp">{cfg['emoji']} {campaign}</div>
        </div>
        <div style="flex:1">
            <div class="lb-bar-bg">
                <div class="lb-bar-fill" style="width:{bar_width}%;background:{bar_color}"></div>
            </div>
        </div>
        <div style="min-width:80px;text-align:right">
            <div class="lb-pct" style="color:{bar_color}">{pct}%</div>
            <div style="font-size:.65rem;color:#9CA3AF">{int(row['Attempts'])} attempts</div>
        </div>
        <div style="min-width:70px;text-align:right">
            <div style="font-size:.85rem;font-weight:700;color:#0047CC;font-family:'JetBrains Mono',monospace">{talk}</div>
            <div style="font-size:.62rem;color:#9CA3AF">talk time</div>
        </div>
    </div>""", unsafe_allow_html=True)

# Distribution chart
section_label("Contact Rate Distribution")
bands = {
    "🔥 Elite (≥70%)":      display_df[display_df["Contact %"] >= 70],
    "✅ Good (50–69%)":     display_df[(display_df["Contact %"] >= 50) & (display_df["Contact %"] < 70)],
    "⚠️ Average (30–49%)":  display_df[(display_df["Contact %"] >= 30) & (display_df["Contact %"] < 50)],
    "❌ Below (<30%)":      display_df[display_df["Contact %"] < 30],
}
band_colors = ["#047857","#0047CC","#B45309","#B91C1C"]

col_left, col_right = st.columns([3, 2])
with col_left:
    fig = go.Figure()
    for (lbl, bdf), color in zip(bands.items(), band_colors):
        if bdf.empty: continue
        fig.add_trace(go.Bar(
            name=lbl, x=bdf["Agent"], y=bdf["Contact %"],
            marker_color=color, marker_line_width=0,
            text=[f"{v}%" for v in bdf["Contact %"]], textposition="outside",
            textfont=dict(size=10, family=FONT, color="#0A0E1A"),
            hovertemplate="<b>%{x}</b><br>Contact: %{y}%<extra></extra>",
        ))
    fig.add_shape(type="line", x0=-.5, x1=len(display_df)-.5, y0=50, y1=50,
                  line=dict(color="#D1D5DB", dash="dot", width=1.5))
    max_y = max(display_df["Contact %"].max()+20, 80) if not display_df.empty else 80
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_family=FONT, font_color="#0A0E1A",
        margin=dict(l=0,r=0,t=10,b=0), height=320, barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
                    font_size=11, bgcolor="rgba(0,0,0,0)"),
        yaxis=dict(range=[0,max_y], showgrid=True, gridcolor=GRID, zeroline=False,
                   ticksuffix="%", tickfont=dict(size=10, color=TXTC)),
        xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#0A0E1A")),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with col_right:
    section_label("Band Summary", margin_top="0")
    for (lbl, bdf), color in zip(bands.items(), band_colors):
        count = len(bdf)
        pct_share = round(count / total_agents * 100) if total_agents else 0
        st.markdown(f"""<div style="background:#FFFFFF;border-radius:10px;border:1px solid #E2E5EC;
             padding:.85rem 1.1rem;margin-bottom:.5rem;
             display:flex;align-items:center;justify-content:space-between">
            <div>
                <div style="font-size:.8rem;font-weight:700;color:#0A0E1A">{lbl}</div>
                <div style="font-size:.68rem;color:#9CA3AF;margin-top:.1rem">{count} agent{'s' if count!=1 else ''}</div>
            </div>
            <div style="font-size:1.4rem;font-weight:800;color:{color}">{pct_share}%</div>
        </div>""", unsafe_allow_html=True)

with st.expander("📋 Full Rankings Table"):
    table = display_df[["Agent","Campaign","Contact %","Attempts","Contacted","NotContacted"]].copy()
    if "TalkTimeSecs" in display_df.columns:
        table["Talk Time"] = display_df["TalkTimeSecs"].apply(format_duration)
    table.rename(columns={"NotContacted":"Not Contacted"}, inplace=True)
    table.insert(0, "Rank", range(1, len(table)+1))
    st.dataframe(table, use_container_width=True, hide_index=True)
