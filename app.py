"""
app.py — DSG Online Sales Team · Overview
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import date

from utils.constants import (
    ADMIN_PASSWORD, CAMPAIGN_CONFIG,
    ACCENT_BLUE, FONT, GRID, TXTC,
)
from utils.data import parse_intalk_csv, build_summary, filter_by_dates, campaign_totals, format_duration
from utils.github_store import load_data, append_day
from utils.styles import inject_css
from utils.components import (
    agent_bar_chart, contact_rate_bar, donut_chart,
    empty_state, kpi_card, agent_table,
    render_date_filter, section_label, sidebar_nav, top_nav,
)

st.set_page_config(
    page_title="DSG Online Sales · Overview",
    page_icon="https://www.dreamsetgo.com/DreamSetGo-48x48.png",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# ── Sidebar ───────────────────────────────────────────────────────────────────
sidebar_nav()

with st.sidebar:
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    # Upload button — opens expander
    with st.expander("⬆️ Upload Data", expanded=False):
        if "admin_open" not in st.session_state:
            st.session_state.admin_open = False

        pw = st.text_input("Admin password", type="password", key="sidebar_pw",
                           label_visibility="collapsed",
                           placeholder="Enter admin password")

        if not st.session_state.get("admin_auth"):
            if st.button("Unlock", key="sidebar_unlock", use_container_width=True):
                if pw == ADMIN_PASSWORD:
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.error("Wrong password")
        else:
            st.success("✅ Access granted")
            uploaded = st.file_uploader("Choose InTalk CSV", type=["csv"],
                                        label_visibility="collapsed")
            if uploaded:
                st.session_state["pending_file"] = uploaded.read()
                st.session_state["pending_name"] = uploaded.name

            if st.session_state.get("pending_file"):
                if st.button("📤 Upload & Refresh", key="upload_btn",
                             use_container_width=True, type="primary"):
                    with st.spinner("Processing..."):
                        try:
                            raw_df, report_date, warnings = parse_intalk_csv(
                                st.session_state["pending_file"]
                            )
                            ok, msg = append_day(raw_df, report_date)
                            if ok:
                                # Clear pending and cached data
                                del st.session_state["pending_file"]
                                del st.session_state["pending_name"]
                                st.session_state["admin_auth"] = False
                                st.session_state["upload_msg"] = msg
                                for w in warnings:
                                    st.warning(w)
                                st.switch_page("app.py")
                            else:
                                st.error(msg)
                        except Exception as e:
                            st.error(f"Error: {e}")

            if st.button("🔒 Lock", key="sidebar_lock", use_container_width=True):
                st.session_state.admin_auth = False
                st.rerun()

    # Show upload success message
    if st.session_state.get("upload_msg"):
        st.success(st.session_state.pop("upload_msg"))

# ── Load data ─────────────────────────────────────────────────────────────────
all_data = load_data()

nav_sub = "Dashboard"
if not all_data.empty and "Date" in all_data.columns:
    max_date = all_data["Date"].max()
    nav_sub  = f"Last updated: {max_date.strftime('%d %b %Y') if hasattr(max_date,'strftime') else max_date}"

top_nav(subtitle=nav_sub, page_tag="Overview")

# ── Date filter ───────────────────────────────────────────────────────────────
from_date, to_date = render_date_filter("overview")

# ── Filter data ───────────────────────────────────────────────────────────────
if all_data.empty:
    empty_state(
        title="No data yet",
        sub="Click '⬆️ Upload Data' in the sidebar to load your first CSV.",
        icon="📊",
    )
    st.stop()

filtered = filter_by_dates(all_data, from_date, to_date)

if filtered.empty:
    empty_state(
        title="No data for this date range",
        sub="Try a wider range or click 'All Data'.",
        icon="📅",
    )
    st.stop()

agent_df = build_summary(filtered)

# ── Overall KPIs ──────────────────────────────────────────────────────────────
total_att  = int(agent_df["Attempts"].sum())
total_cont = int(agent_df["Contacted"].sum())
total_nc   = int(agent_df["NotContacted"].sum())
total_pct  = round(total_cont/total_att*100,1) if total_att else 0.0
total_talk = float(agent_df["TalkTimeSecs"].sum())

section_label("Overall Team Performance", mt="0")
c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.markdown(kpi_card("Total Attempts",  f"{total_att:,}",  "All agents",             "📞","#6366F1"),                        unsafe_allow_html=True)
with c2: st.markdown(kpi_card("Total Contacted", f"{total_cont:,}", "Line answered",          "✅","#30D158","kpi-value-green"),       unsafe_allow_html=True)
with c3: st.markdown(kpi_card("Not Contacted",   f"{total_nc:,}",   "No answer/DNC",          "📵","#FF453A","kpi-value-red"),         unsafe_allow_html=True)
with c4: st.markdown(kpi_card("Contact Rate",    f"{total_pct}%",   "Contacted ÷ Attempts",   "📈","#0A84FF","kpi-value-blue"),        unsafe_allow_html=True)
with c5: st.markdown(kpi_card("Talk Time",       format_duration(total_talk),"Calls > 0s",    "🎙️","#FFD60A","kpi-value-gold"),       unsafe_allow_html=True)

# ── All agents bar ────────────────────────────────────────────────────────────
section_label("All Agents · Contact Rate")
all_sorted = agent_df.sort_values("Contact %", ascending=False)

fig = go.Figure()
for camp, cfg in CAMPAIGN_CONFIG.items():
    cd = all_sorted[all_sorted["Campaign"]==camp]
    if cd.empty: continue
    fig.add_trace(go.Bar(
        name=f"{cfg['emoji']} {camp}",
        x=cd["Agent"], y=cd["Contact %"],
        marker_color=cfg["accent"], marker_line_width=0,
        text=[f"{v}%" for v in cd["Contact %"]], textposition="outside",
        textfont=dict(size=11,family=FONT,color="#FFFFFF"),
        hovertemplate=f"<b>%{{x}}</b><br>{camp}: %{{y}}%<extra></extra>"))

fig.add_shape(type="line", x0=-.5, x1=len(all_sorted)-.5, y0=50, y1=50,
              line=dict(color="#48484A",dash="dot",width=1.5))
fig.add_annotation(x=len(all_sorted)-.5, y=50, text="50% target",
    showarrow=False, font=dict(size=9,color="#636366"), xanchor="right", yanchor="bottom")
max_y = max(all_sorted["Contact %"].max()+18, 70) if not all_sorted.empty else 70
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_family=FONT, font_color="#FFFFFF",
    margin=dict(l=0,r=0,t=10,b=0), height=270,
    legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1,
                font_size=11,bgcolor="rgba(0,0,0,0)"),
    yaxis=dict(range=[0,max_y],showgrid=True,gridcolor=GRID,zeroline=False,
               ticksuffix="%",tickfont=dict(size=10,color=TXTC)),
    xaxis=dict(showgrid=False,tickfont=dict(size=12,color="#FFFFFF")),
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})


# ── Campaign renderer ─────────────────────────────────────────────────────────
def render_campaign(df, campaign):
    cfg    = CAMPAIGN_CONFIG[campaign]
    accent = cfg["accent"]
    chip   = cfg["chip"]
    emoji  = cfg["emoji"]
    t      = campaign_totals(df, campaign)
    sub    = df[df["Campaign"]==campaign]

    st.markdown(f"""<div class="campaign-block">
        <div class="campaign-chip {chip}">{emoji} {campaign}</div>
        <div class="campaign-name">{campaign} Team</div>
        <div class="campaign-desc">{len(sub)} agents · {t['att']:,} attempts</div>
    </div>""", unsafe_allow_html=True)

    k1,k2,k3,k4,k5 = st.columns(5)
    with k1: st.markdown(kpi_card("Attempts",     f"{t['att']:,}",          "Total calls",          "📞",accent),                      unsafe_allow_html=True)
    with k2: st.markdown(kpi_card("Contacted",    f"{t['cont']:,}",         "Line answered",        "✅",accent,"kpi-value-green"),     unsafe_allow_html=True)
    with k3: st.markdown(kpi_card("Not Contacted",f"{t['nc']:,}",           "No answer/DNC",        "📵","#FF453A","kpi-value-red"),    unsafe_allow_html=True)
    with k4: st.markdown(kpi_card("Contact Rate", f"{t['pct']}%",           "Contacted ÷ Attempts", "📈","#0A84FF","kpi-value-blue"),   unsafe_allow_html=True)
    with k5: st.markdown(kpi_card("Talk Time",    format_duration(t['talk']),"Calls > 0s",          "🎙️","#FFD60A","kpi-value-gold"),  unsafe_allow_html=True)

    st.markdown("<div style='height:.9rem'></div>", unsafe_allow_html=True)
    l, m, r = st.columns([2.2,1.8,1])
    with l:
        section_label("Contacted vs Not Contacted")
        st.plotly_chart(agent_bar_chart(sub,accent), use_container_width=True, config={"displayModeBar":False})
    with m:
        section_label("Contact Rate by Agent")
        st.plotly_chart(contact_rate_bar(sub), use_container_width=True, config={"displayModeBar":False})
    with r:
        section_label("Outcome Split")
        st.plotly_chart(donut_chart(t['att'],t['cont'],t['nc'],accent), use_container_width=True, config={"displayModeBar":False})
        st.markdown("<div style='text-align:center;font-size:.62rem;color:#636366;font-weight:600;"
                    "letter-spacing:.07em;text-transform:uppercase;margin-top:-.3rem'>Contact Rate</div>",
                    unsafe_allow_html=True)

    section_label("Agent Breakdown")
    agent_table(sub)


# ── Tabs ──────────────────────────────────────────────────────────────────────
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
section_label("Campaign Breakdown")
tab_s, tab_h = st.tabs(["🏅  Sports", "🏖️  Holiday"])
with tab_s: render_campaign(agent_df, "Sports")
with tab_h: render_campaign(agent_df, "Holiday")

with st.expander("🗂 Raw data"):
    st.dataframe(agent_df, use_container_width=True, hide_index=True)
