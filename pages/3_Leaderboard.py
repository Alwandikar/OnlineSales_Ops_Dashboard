"""
pages/3_Leaderboard.py — CS Online Team · Agent Leaderboard
"""

import plotly.graph_objects as go
import streamlit as st

from utils.constants import (
    AGENT_CAMPAIGN_MAP,
    CAMPAIGN_CONFIG,
    FONT,
    GRID,
    TXTC,
    ACCENT_GREEN,
)
from utils.data import load_cache
from utils.styles import inject_css
from utils.components import (
    date_banner,
    empty_state,
    kpi_card,
    pct_color,
    section_label,
    top_nav,
)

st.set_page_config(
    page_title="CS Online Team · Leaderboard",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

agent_df, cached_date = load_cache()
nav_subtitle = f"Dashboard for {cached_date}" if cached_date else "Dashboard"

top_nav(
    title="CS Online Team",
    subtitle=nav_subtitle,
    page_tag="Leaderboard",
    logo_class="nav-logo-leaderboard",
    tag_class="tag-green",
    logo_icon="🏆",
)

if agent_df is None:
    empty_state(
        title="No data loaded yet",
        sub="Go to the Overview page and upload today's CSV first.",
        icon="🏆",
    )
    st.stop()

date_banner(cached_date)

# ── Campaign filter ───────────────────────────────────────────────────────────
section_label("Filter by Campaign", margin_top="0")
camp_filter = st.radio(
    "Campaign", ["All", "Sports", "Holiday"],
    horizontal=True, label_visibility="collapsed",
)

display_df = agent_df.copy()
if camp_filter != "All":
    display_df = display_df[display_df["Campaign"] == camp_filter]

display_df = display_df.sort_values("Contact %", ascending=False).reset_index(drop=True)
total_agents = len(display_df)

# ── Summary KPIs ──────────────────────────────────────────────────────────────
section_label("Performance Summary")

top_agent = display_df.iloc[0] if not display_df.empty else None
avg_rate  = round(display_df["Contact %"].mean(), 1) if not display_df.empty else 0.0
above_50  = int((display_df["Contact %"] >= 50).sum())

k1, k2, k3, k4 = st.columns(4)
with k1:
    top_name = top_agent["Agent"] if top_agent is not None else "—"
    top_pct  = f"{top_agent['Contact %']}%" if top_agent is not None else "—"
    st.markdown(kpi_card("Top Agent", top_name, f"{top_pct} contact rate", "🥇", "#f59e0b"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card("Avg Contact Rate", f"{avg_rate}%", f"Across {total_agents} agents", "📊", ACCENT_GREEN, "kpi-value-pct"), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_card("Above Target (≥50%)", str(above_50), f"of {total_agents} agents", "✅", ACCENT_GREEN, "kpi-value-green"), unsafe_allow_html=True)
with k4:
    below = total_agents - above_50
    st.markdown(kpi_card("Below Target (<50%)", str(below), f"of {total_agents} agents", "⚠️", "#e85454", "kpi-value-red"), unsafe_allow_html=True)

# ── Ranked leaderboard rows ───────────────────────────────────────────────────
section_label("Agent Rankings")

max_pct = display_df["Contact %"].max() if not display_df.empty else 100

for i, row in display_df.iterrows():
    rank      = i + 1
    pct       = row["Contact %"]
    campaign  = row["Campaign"]
    cfg       = CAMPAIGN_CONFIG.get(campaign, {"chip_class": "chip-holiday", "emoji": "❓"})
    bar_color = pct_color(pct)
    bar_width = round(pct / max_pct * 100, 1) if max_pct else 0

    if   rank == 1: badge_class = "rank-1"
    elif rank == 2: badge_class = "rank-2"
    elif rank == 3: badge_class = "rank-3"
    else:           badge_class = "rank-n"

    medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, str(rank))

    st.markdown(f"""
    <div class="leaderboard-row">
        <div class="rank-badge {badge_class}">{medal}</div>
        <div style="min-width:130px">
            <div class="lb-agent">{row['Agent']}</div>
            <div class="lb-camp">{cfg['emoji']} {campaign}</div>
        </div>
        <div style="flex:1">
            <div class="lb-bar-bg">
                <div class="lb-bar-fill" style="width:{bar_width}%;background:{bar_color}"></div>
            </div>
        </div>
        <div style="min-width:100px;text-align:right">
            <div class="lb-pct" style="color:{bar_color}">{pct}%</div>
            <div style="font-size:.65rem;color:#535353;text-align:right">{int(row['Attempts'])} attempts</div>
        </div>
    </div>""", unsafe_allow_html=True)

# ── Performance band chart ────────────────────────────────────────────────────
section_label("Contact Rate Distribution")

bands = {
    "🔥 Elite (≥70%)":      display_df[display_df["Contact %"] >= 70],
    "✅ Good (50–69%)":     display_df[(display_df["Contact %"] >= 50) & (display_df["Contact %"] < 70)],
    "⚠️ Average (30–49%)":  display_df[(display_df["Contact %"] >= 30) & (display_df["Contact %"] < 50)],
    "❌ Below (<30%)":      display_df[display_df["Contact %"] < 30],
}
band_colors = [ACCENT_GREEN, "#1ed760", "#f59e0b", "#e85454"]

col_left, col_right = st.columns([3, 2])

with col_left:
    fig_dist = go.Figure()
    for (band_label, band_df), color in zip(bands.items(), band_colors):
        if band_df.empty:
            continue
        fig_dist.add_trace(go.Bar(
            name=band_label,
            x=band_df["Agent"],
            y=band_df["Contact %"],
            marker_color=color,
            marker_line_width=0,
            text=[f"{v}%" for v in band_df["Contact %"]],
            textposition="outside",
            textfont=dict(size=10, family=FONT, color="#FFFFFF"),
            hovertemplate="<b>%{x}</b><br>Contact: %{y}%<extra></extra>",
        ))
    fig_dist.add_shape(
        type="line", x0=-0.5, x1=len(display_df) - 0.5, y0=50, y1=50,
        line=dict(color="#535353", dash="dot", width=1.5),
    )
    fig_dist.add_annotation(
        x=len(display_df) - 0.5, y=50, text="50% target",
        showarrow=False, font=dict(size=9, color="#535353"),
        xanchor="right", yanchor="bottom",
    )
    max_y = max(display_df["Contact %"].max() + 20, 80) if not display_df.empty else 80
    fig_dist.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_family=FONT, font_color="#FFFFFF",
        margin=dict(l=0, r=0, t=10, b=0), height=320,
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.01,
                    xanchor="left", x=0, font_size=11, bgcolor="rgba(0,0,0,0)"),
        yaxis=dict(range=[0, max_y], showgrid=True, gridcolor=GRID, zeroline=False,
                   ticksuffix="%", tickfont=dict(size=10, color=TXTC)),
        xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#FFFFFF")),
    )
    st.plotly_chart(fig_dist, use_container_width=True, config={"displayModeBar": False})

with col_right:
    section_label("Band Summary", margin_top="0")
    for (band_label, band_df), color in zip(bands.items(), band_colors):
        count     = len(band_df)
        pct_share = round(count / total_agents * 100) if total_agents else 0
        st.markdown(f"""
        <div style="background:#181818;border-radius:12px;border:1px solid #282828;
             padding:.9rem 1.2rem;margin-bottom:.6rem;
             display:flex;align-items:center;justify-content:space-between">
            <div>
                <div style="font-size:.8rem;font-weight:700;color:#FFFFFF">{band_label}</div>
                <div style="font-size:.7rem;color:#535353;margin-top:.1rem">{count} agent{'s' if count != 1 else ''}</div>
            </div>
            <div style="font-size:1.4rem;font-weight:800;color:{color}">{pct_share}%</div>
        </div>""", unsafe_allow_html=True)

# ── Full table ────────────────────────────────────────────────────────────────
with st.expander("📋 Full Rankings Table"):
    table = display_df[["Agent", "Campaign", "Contact %", "Attempts", "Contacted", "NotContacted"]].copy()
    table.rename(columns={"NotContacted": "Not Contacted"}, inplace=True)
    table.insert(0, "Rank", range(1, len(table) + 1))
    st.dataframe(table, use_container_width=True, hide_index=True)
