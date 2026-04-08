"""
app.py — DSG Online Sales Team · Overview
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import date

from utils.constants import (
    ADMIN_PASSWORD, CAMPAIGN_CONFIG,
    DSG_NAVY, DSG_GOLD, DSG_BORDER,
    FONT, GRID, TXTC,
)
from utils.data import (
    campaign_totals, load_cache, load_raw_cache,
    process_csv, save_cache, filter_raw_by_dates,
    summarise_raw, format_duration, get_mtd_range,
)
from utils.styles import inject_css
from utils.components import (
    agent_bar_chart, connect_pct_bar, disposition_donut,
    empty_state, kpi_card, render_agent_summary_table,
    render_date_filter, section_label, top_nav,
)

st.set_page_config(
    page_title="DSG Online Sales Team · Overview",
    page_icon="https://www.dreamsetgo.com/DreamSetGo-48x48.png",
    layout="wide", initial_sidebar_state="expanded",
)
inject_css()

# Session state
if "admin_unlocked" not in st.session_state: st.session_state.admin_unlocked = False
if "pw_error"       not in st.session_state: st.session_state.pw_error = False

# Load raw cache (source of truth for date-filtered views)
raw_df, cached_date = load_raw_cache()
nav_subtitle = f"Dashboard · {cached_date}" if cached_date else "Dashboard"

top_nav(subtitle=nav_subtitle, page_tag="Overview")

# Admin panel
with st.expander("🔒 Admin — Upload Data", expanded=False):
    if not st.session_state.admin_unlocked:
        st.markdown("<div class='admin-box'><div class='admin-box-title'>Admin Access Required</div>", unsafe_allow_html=True)
        pw = st.text_input("Password", type="password", key="pw_input")
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
        uploaded = st.file_uploader("Upload InTalk CSV", type=["csv"])
        if uploaded is not None:
            try:
                file_bytes = uploaded.read()
                new_df, new_raw, new_date, warnings = process_csv(file_bytes, uploaded.name)
                save_cache(new_df, new_raw, new_date)
                for w in warnings:
                    st.warning(f"⚠️ {w}")
                st.success(f"✅ Uploaded for {new_date}!")
                st.rerun()
            except ValueError as e:
                st.error(f"❌ CSV format error: {e}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")
        if st.button("🔒 Lock Admin", key="lock_btn"):
            st.session_state.admin_unlocked = False
            st.rerun()

# Empty state
if raw_df is None:
    empty_state(title="No data loaded yet", sub="Admin needs to upload the InTalk CSV above.")
    st.stop()

# ── Date filter ───────────────────────────────────────────────────────────────
from_date, to_date = render_date_filter()

# Filter raw data and rebuild summary for the selected date range
filtered_raw = filter_raw_by_dates(raw_df, from_date, to_date)
agent_df     = summarise_raw(filtered_raw)

if agent_df.empty:
    empty_state(
        title="No data for this date range",
        sub="Try selecting a different date range or upload more data.",
        icon="📅",
    )
    st.stop()

# ── Overall KPIs ──────────────────────────────────────────────────────────────
total_att   = int(agent_df["Attempts"].sum())
total_cont  = int(agent_df["Contacted"].sum())
total_nc    = int(agent_df["NotContacted"].sum())
total_pct   = round(total_cont / total_att * 100, 1) if total_att else 0.0
total_talk  = float(agent_df["TalkTimeSecs"].sum()) if "TalkTimeSecs" in agent_df.columns else 0.0

section_label("Overall Team Performance", margin_top="0")
o1, o2, o3, o4, o5 = st.columns(5)
with o1: st.markdown(kpi_card("Total Attempts",   f"{total_att:,}",  "All agents",              "📞", "#6366F1"),                       unsafe_allow_html=True)
with o2: st.markdown(kpi_card("Total Contacted",  f"{total_cont:,}", "Line answered / reached", "✅", "#047857", "kpi-value-green"),     unsafe_allow_html=True)
with o3: st.markdown(kpi_card("Not Contacted",    f"{total_nc:,}",   "No answer / DNC / Redial","📵", "#B91C1C", "kpi-value-red"),       unsafe_allow_html=True)
with o4: st.markdown(kpi_card("Contact Rate",     f"{total_pct}%",   "Contacted ÷ Attempts",    "📈", DSG_GOLD,  "kpi-value-gold"),      unsafe_allow_html=True)
with o5: st.markdown(kpi_card("Total Talk Time",  format_duration(total_talk), "Only calls > 0s", "🎙️", "#0047CC", "kpi-value-blue"),   unsafe_allow_html=True)

# All-agents contact rate bar
section_label("All Agents · Contact Rate")
all_sorted = agent_df.sort_values("Contact %", ascending=False)
bar_colors = [CAMPAIGN_CONFIG["Sports"]["accent"] if c == "Sports"
              else CAMPAIGN_CONFIG["Holiday"]["accent"]
              for c in all_sorted["Campaign"]]

# Build one trace per campaign so legend works cleanly
fig_all = go.Figure()
for camp_name, camp_cfg in CAMPAIGN_CONFIG.items():
    camp_data = all_sorted[all_sorted["Campaign"] == camp_name]
    if camp_data.empty:
        continue
    fig_all.add_trace(go.Bar(
        name=f"{camp_cfg['emoji']} {camp_name}",
        x=camp_data["Agent"], y=camp_data["Contact %"],
        marker_color=camp_cfg["accent"], marker_line_width=0,
        text=[f"{v}%" for v in camp_data["Contact %"]],
        textposition="outside",
        textfont=dict(size=11, family=FONT, color="#0A0E1A"),
        hovertemplate="<b>%{x}</b><br>Campaign: " + camp_name + "<br>Contact: %{y}%<extra></extra>",
    ))
fig_all.add_shape(type="line", x0=-.5, x1=len(all_sorted)-.5, y0=50, y1=50,
                  line=dict(color="#D1D5DB", dash="dot", width=1.5))
fig_all.add_annotation(x=len(all_sorted)-.5, y=50, text="50% benchmark",
    showarrow=False, font=dict(size=9, color="#9CA3AF"), xanchor="right", yanchor="bottom")
# Legend via legendgroup on the bars themselves - no dummy traces needed
max_y = max(agent_df["Contact %"].max()+18, 70) if not agent_df.empty else 70
fig_all.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_family=FONT, font_color="#0A0E1A",
    margin=dict(l=0,r=0,t=10,b=0), height=280,
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
                font_size=11, bgcolor="rgba(0,0,0,0)"),
    yaxis=dict(range=[0,max_y], showgrid=True, gridcolor=GRID, zeroline=False,
               ticksuffix="%", tickfont=dict(size=10, color=TXTC)),
    xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#0A0E1A")),
)
st.plotly_chart(fig_all, use_container_width=True, config={"displayModeBar": False})


# ── Campaign renderer ─────────────────────────────────────────────────────────

def render_campaign(df, filtered_raw, campaign):
    cfg    = CAMPAIGN_CONFIG[campaign]
    accent = cfg["accent"]
    chip   = cfg["chip_class"]
    emoji  = cfg["emoji"]

    att, cont, not_cont, pct, talk = campaign_totals(df, campaign)
    sub = df[df["Campaign"] == campaign]

    st.markdown(f"""<div class="campaign-block">
        <div class="campaign-chip {chip}">{emoji}&nbsp; {campaign} Campaign</div>
        <div class="campaign-name">{campaign} Team</div>
        <div class="campaign-desc">{len(sub)} agents &nbsp;·&nbsp; {att:,} total attempts</div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(kpi_card("Attempts",     f"{att:,}",           "Total calls",           "📞", accent),                      unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Contacted",    f"{cont:,}",          "Line answered",         "✅", accent, "kpi-value-green"),    unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Not Contacted",f"{not_cont:,}",      "No answer / DNC",       "📵", "#B91C1C", "kpi-value-red"),   unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Contact Rate", f"{pct}%",            "Contacted ÷ Attempts",  "📈", DSG_GOLD, "kpi-value-gold"),   unsafe_allow_html=True)
    with c5: st.markdown(kpi_card("Talk Time",    format_duration(talk),"Calls with duration>0", "🎙️", "#0047CC", "kpi-value-blue"),  unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
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
        st.markdown("<div style='text-align:center;font-size:.65rem;color:#9CA3AF;font-weight:700;"
                    "letter-spacing:.08em;text-transform:uppercase;margin-top:-.4rem'>Contact Rate</div>",
                    unsafe_allow_html=True)

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
    section_label("Agent Breakdown")
    render_agent_summary_table(sub)


# ── Tabs ──────────────────────────────────────────────────────────────────────
st.markdown("<hr class='dash-divider'>", unsafe_allow_html=True)
section_label("Campaign Breakdown")

tab_sports, tab_holiday = st.tabs(["🏅  Sports", "🏖️  Holiday"])
with tab_sports:
    render_campaign(agent_df, filtered_raw, "Sports")
with tab_holiday:
    render_campaign(agent_df, filtered_raw, "Holiday")

with st.expander("🗂  Raw data"):
    st.dataframe(agent_df, use_container_width=True, hide_index=True)
