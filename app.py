"""
app.py — CS Online Team · Overview (Page 1 of 3)
─────────────────────────────────────────────────
Overall team KPIs at top, then Sports / Holiday tabs below.
"""

import streamlit as st
import plotly.graph_objects as go

from utils.constants import (
    ADMIN_PASSWORD,
    CAMPAIGN_CONFIG,
    FONT,
    GRID,
    TXTC,
    ACCENT_GREEN,
)
from utils.data import (
    campaign_totals,
    load_cache,
    process_csv,
    save_cache,
)
from utils.styles import inject_css
from utils.components import (
    agent_bar_chart,
    connect_pct_bar,
    date_banner,
    disposition_donut,
    empty_state,
    kpi_card,
    pct_color,
    render_agent_summary_table,
    section_label,
    top_nav,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CS Online Team · Overview",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# ── Session state ─────────────────────────────────────────────────────────────
if "admin_unlocked" not in st.session_state:
    st.session_state.admin_unlocked = False
if "pw_error" not in st.session_state:
    st.session_state.pw_error = False

# ── Load data ─────────────────────────────────────────────────────────────────
cached_df, cached_date = load_cache()
nav_subtitle = f"Dashboard for {cached_date}" if cached_date else "Dashboard"

# ── Top nav ───────────────────────────────────────────────────────────────────
top_nav(
    title="CS Online Team",
    subtitle=nav_subtitle,
    page_tag="Overview",
    logo_class="nav-logo-overview",
    tag_class="tag-green",
    logo_icon="📊",
)

# ── Admin upload panel ────────────────────────────────────────────────────────
with st.expander("🔒 Admin — Upload Today's Data", expanded=False):
    if not st.session_state.admin_unlocked:
        st.markdown(
            "<div class='admin-box'><div class='admin-box-title'>Admin Access Required</div>",
            unsafe_allow_html=True,
        )
        pw = st.text_input("Enter admin password", type="password", key="pw_input")
        if st.button("Unlock", key="unlock_btn"):
            if pw == ADMIN_PASSWORD:
                st.session_state.admin_unlocked = True
                st.session_state.pw_error = False
                st.rerun()
            else:
                st.session_state.pw_error = True
        if st.session_state.pw_error:
            st.error("Incorrect password.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("✅ Admin access granted")
        uploaded = st.file_uploader("Upload today's InTalk CSV", type=["csv"])
        if uploaded is not None:
            try:
                file_bytes = uploaded.read()
                new_df, raw_clean, new_date, warnings = process_csv(file_bytes, uploaded.name)
                save_cache(new_df, raw_clean, new_date)
                for w in warnings:
                    st.warning(f"⚠️ {w}")
                st.success(f"✅ Data uploaded for {new_date}!")
                st.rerun()
            except ValueError as e:
                st.error(f"❌ CSV format error: {e}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")
        if st.button("🔒 Lock Admin", key="lock_btn"):
            st.session_state.admin_unlocked = False
            st.rerun()

# ── Empty state ───────────────────────────────────────────────────────────────
if cached_df is None:
    empty_state(
        title="No data loaded yet",
        sub="An admin needs to upload today's CSV using the section above.",
    )
    st.stop()

agent_df = cached_df
date_banner(cached_date, extra="Upload a new file above to update")

# ── Overall Team KPIs (always visible, no tab) ────────────────────────────────
total_att  = int(agent_df["Attempts"].sum())
total_cont = int(agent_df["Contacted"].sum())
total_nc   = int(agent_df["NotContacted"].sum())
total_pct  = round(total_cont / total_att * 100, 1) if total_att else 0.0

section_label("Overall Team Performance", margin_top="0")
o1, o2, o3, o4 = st.columns(4)
with o1: st.markdown(kpi_card("Total Attempts",    f"{total_att:,}",  "All agents combined",          "📞", "#6366f1"),                      unsafe_allow_html=True)
with o2: st.markdown(kpi_card("Total Contacted",   f"{total_cont:,}", "Line was answered / reached",  "✅", ACCENT_GREEN, "kpi-value-green"), unsafe_allow_html=True)
with o3: st.markdown(kpi_card("Not Contacted",     f"{total_nc:,}",   "No answer / DNC / Redial",     "📵", "#e85454",    "kpi-value-red"),   unsafe_allow_html=True)
with o4: st.markdown(kpi_card("Contact Rate",      f"{total_pct}%",   "Contacted ÷ Attempts",         "📈", ACCENT_GREEN, "kpi-value-pct"),   unsafe_allow_html=True)

# All-agents contact-rate bar
section_label("All Agents · Contact Rate")
all_sorted = agent_df.sort_values("Contact %", ascending=False)
bar_colors = [ACCENT_GREEN if c == "Sports" else "#1ed760" for c in all_sorted["Campaign"]]

fig_all = go.Figure(go.Bar(
    x=all_sorted["Agent"], y=all_sorted["Contact %"],
    marker_color=bar_colors, marker_line_width=0,
    text=[f"{v}%" for v in all_sorted["Contact %"]],
    textposition="outside",
    textfont=dict(size=11, family=FONT, color="#FFFFFF"),
    customdata=all_sorted["Campaign"],
    hovertemplate="<b>%{x}</b><br>Campaign: %{customdata}<br>Contact: %{y}%<extra></extra>",
))
fig_all.add_shape(
    type="line", x0=-0.5, x1=len(all_sorted) - 0.5, y0=50, y1=50,
    line=dict(color="#535353", dash="dot", width=1.5),
)
fig_all.add_annotation(
    x=len(all_sorted) - 0.5, y=50, text="50% benchmark",
    showarrow=False, font=dict(size=9, color="#535353"),
    xanchor="right", yanchor="bottom",
)
for label, color in [("🏅 Sports", ACCENT_GREEN), ("🏖️ Holiday", "#1ed760")]:
    fig_all.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(color=color, size=10, symbol="square"),
        name=label, showlegend=True,
    ))

max_y = max(all_sorted["Contact %"].max() + 18, 70) if not all_sorted.empty else 70
fig_all.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_family=FONT, font_color="#FFFFFF",
    margin=dict(l=0, r=0, t=10, b=0), height=280,
    legend=dict(orientation="h", yanchor="bottom", y=1.01,
                xanchor="right", x=1, font_size=11, bgcolor="rgba(0,0,0,0)"),
    yaxis=dict(range=[0, max_y], showgrid=True, gridcolor=GRID, zeroline=False,
               ticksuffix="%", tickfont=dict(size=10, color=TXTC)),
    xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#FFFFFF")),
)
st.plotly_chart(fig_all, use_container_width=True, config={"displayModeBar": False})


# ── Campaign renderer ─────────────────────────────────────────────────────────

def render_campaign(df, campaign: str) -> None:
    """Render KPIs, charts, and agent table for one campaign inside a tab."""
    cfg    = CAMPAIGN_CONFIG[campaign]
    accent = cfg["accent"]
    emoji  = cfg["emoji"]
    chip   = cfg["chip_class"]

    att, cont, not_cont, pct = campaign_totals(df, campaign)
    sub = df[df["Campaign"] == campaign]

    st.markdown(f"""
    <div class="campaign-block">
        <div class="campaign-chip {chip}">{emoji}&nbsp; {campaign} Campaign</div>
        <div class="campaign-name">{campaign} Team</div>
        <div class="campaign-desc">{len(sub)} agents &nbsp;·&nbsp; {att:,} total call attempts</div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi_card("Call Attempts",  f"{att:,}",      "Total rows in CSV",              "📞", accent),                      unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Contacted",      f"{cont:,}",     "Line answered / reached",        "✅", accent, "kpi-value-green"),    unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Not Contacted",  f"{not_cont:,}", "No answer / DNC / Redial",       "📵", "#e85454", "kpi-value-red"),   unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Contact Rate",   f"{pct}%",       "Contacted ÷ Attempts",           "📈", accent, "kpi-value-pct"),      unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    left, mid, right = st.columns([2.2, 1.8, 1])
    with left:
        section_label("Contacted vs Not Contacted · by Agent")
        st.plotly_chart(agent_bar_chart(sub, accent), use_container_width=True, config={"displayModeBar": False})
    with mid:
        section_label("Contact Rate · by Agent")
        st.plotly_chart(connect_pct_bar(sub), use_container_width=True, config={"displayModeBar": False})
    with right:
        section_label("Outcome Split")
        st.plotly_chart(disposition_donut(att, cont, not_cont, accent), use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            "<div style='text-align:center;font-size:.7rem;color:#535353;font-weight:700;"
            "letter-spacing:.08em;text-transform:uppercase;margin-top:-.4rem'>Contact Rate</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
    section_label("Agent Breakdown")
    render_agent_summary_table(sub)


# ── Campaign tabs ─────────────────────────────────────────────────────────────
st.markdown("<hr class='dash-divider'>", unsafe_allow_html=True)
section_label("Campaign Breakdown")

tab_sports, tab_holiday = st.tabs(["🏅  Sports", "🏖️  Holiday"])

with tab_sports:
    render_campaign(agent_df, "Sports")

with tab_holiday:
    render_campaign(agent_df, "Holiday")

# ── Raw data expander ─────────────────────────────────────────────────────────
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
with st.expander("🗂  Raw agent data"):
    st.dataframe(agent_df, use_container_width=True, hide_index=True)
