# utils/components.py

from datetime import date, timedelta
import plotly.graph_objects as go
import streamlit as st

from utils.constants import (
    ALL_DISPOSITIONS, DISP_COLORS, DISP_ICONS,
    DSG_NAVY, DSG_GOLD, DSG_BORDER,
    FONT, GRID, TXTC,
)
from utils.data import format_duration, get_mtd_range


# ── Date filter ───────────────────────────────────────────────────────────────

def render_date_filter() -> tuple:
    """
    Date range filter with From, To, quick buttons, and a Submit button.
    Uses session_state so all 3 pages share the same active range.
    Returns (from_date, to_date) — only changes when Submit is clicked.
    """
    today = date.today()
    mtd_from, mtd_to = get_mtd_range()

    # Always reset to MTD on fresh load (no applied dates in session)
    if "date_from_applied" not in st.session_state:
        st.session_state["date_from_applied"] = mtd_from
        st.session_state["date_to_applied"]   = mtd_to
    if "date_from" not in st.session_state:
        st.session_state["date_from"] = mtd_from
    if "date_to" not in st.session_state:
        st.session_state["date_to"] = mtd_to

    # Quick-select buttons update staging values and auto-apply
    col_label, col_mtd, col_all, col_spacer = st.columns([1, 1.2, 1.2, 6])
    with col_label:
        st.markdown(
            "<div style='padding-top:.55rem;font-size:.68rem;font-weight:700;"
            "letter-spacing:.1em;text-transform:uppercase;color:#9CA3AF'>📅 Date Range</div>",
            unsafe_allow_html=True,
        )
    with col_mtd:
        if st.button("This Month", key="btn_mtd", use_container_width=True):
            st.session_state["date_from"]         = mtd_from
            st.session_state["date_to"]           = mtd_to
            st.session_state["date_from_applied"] = mtd_from
            st.session_state["date_to_applied"]   = mtd_to
            st.rerun()
    with col_all:
        if st.button("All Data", key="btn_all", use_container_width=True):
            st.session_state["date_from"]         = date(2025, 1, 1)
            st.session_state["date_to"]           = today
            st.session_state["date_from_applied"] = date(2025, 1, 1)
            st.session_state["date_to_applied"]   = today
            st.rerun()

    # From / To pickers + Submit
    c_from, c_to, c_submit = st.columns([2, 2, 1])
    with c_from:
        from_staging = st.date_input(
            "From", value=st.session_state["date_from"],
            min_value=date(2026, 1, 1), max_value=today,
            key="di_from", label_visibility="visible",
        )
    with c_to:
        max_to    = min(today, from_staging + timedelta(days=30))
        to_staging = st.session_state["date_to"]
        if to_staging > max_to: to_staging = max_to
        to_staging = st.date_input(
            "To", value=to_staging,
            min_value=from_staging, max_value=max_to,
            key="di_to", label_visibility="visible",
        )
    with c_submit:
        st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
        if st.button("Apply ✓", key="btn_apply", use_container_width=True, type="primary"):
            st.session_state["date_from"]         = from_staging
            st.session_state["date_to"]           = to_staging
            st.session_state["date_from_applied"] = from_staging
            st.session_state["date_to_applied"]   = to_staging
            st.rerun()

    # Always stage the picker values (even before Apply)
    st.session_state["date_from"] = from_staging
    st.session_state["date_to"]   = to_staging

    # Use the last *applied* values for actual filtering
    from_date = st.session_state["date_from_applied"]
    to_date   = st.session_state["date_to_applied"]

    days = (to_date - from_date).days + 1
    st.markdown(
        f'<div class="date-banner">📅 &nbsp;Showing &nbsp;'
        f'<strong>{from_date.strftime("%d %b %Y")}</strong>'
        f'&nbsp;→&nbsp;<strong>{to_date.strftime("%d %b %Y")}</strong>'
        f'&nbsp;&nbsp;({days} day{"s" if days != 1 else ""})</div>',
        unsafe_allow_html=True,
    )
    return from_date, to_date


# ── HTML helpers ──────────────────────────────────────────────────────────────

def kpi_card(label, value, sub_text, icon, accent, value_class=""):
    return f"""<div class="kpi-card">
        <div class="kpi-accent-bar" style="background:{accent}"></div>
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {value_class}">{value}</div>
        <div class="kpi-sub">{sub_text}</div>
    </div>"""


def disp_card(disp, count, pct, small=False):
    count_size = "1.5rem" if small else "1.8rem"
    icon_size  = ".95rem" if small else "1.2rem"
    return f"""<div class="disp-card">
        <div class="disp-accent" style="background:{DISP_COLORS[disp]}"></div>
        <div style="font-size:{icon_size};margin-bottom:.25rem">{DISP_ICONS[disp]}</div>
        <div class="disp-label">{disp}</div>
        <div style="font-size:{count_size};font-weight:800;color:#0A0E1A;letter-spacing:-.03em">{count:,}</div>
        <div class="disp-pct">{pct}%</div>
    </div>"""


def empty_state(title="No data loaded yet", sub="Upload a CSV on the Overview page.", icon="📂"):
    st.markdown(f"""<div class="empty-state">
        <div class="empty-icon">{icon}</div>
        <div class="empty-title">{title}</div>
        <div class="empty-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)


def top_nav(subtitle, page_tag, **_):
    st.markdown(f"""<div class="top-nav">
        <div class="nav-brand">
            <img src="https://www.dreamsetgo.com/DreamSetGo-48x48.png"
                 class="nav-logo" alt="DSG"/>
            <div>
                <div class="nav-title">DSG Online Sales Team</div>
                <div class="nav-sub">{subtitle}</div>
            </div>
        </div>
        <div class="nav-tag">{page_tag}</div>
    </div>""", unsafe_allow_html=True)


def section_label(text, margin_top="2rem"):
    st.markdown(
        f'<p class="section-label" style="margin-top:{margin_top}">{text}</p>',
        unsafe_allow_html=True,
    )


# ── Chart helpers ─────────────────────────────────────────────────────────────

def _base(height=300, **kw):
    d = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
             font_family=FONT, font_color="#0A0E1A",
             margin=dict(l=0, r=0, t=10, b=0), height=height)
    d.update(kw)
    return d


def pct_color(v):
    if v >= 60: return "#047857"
    if v >= 40: return "#B45309"
    return "#B91C1C"


def agent_bar_chart(sub, accent):
    sub = sub.sort_values("Contact %", ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Contacted", y=sub["Agent"], x=sub["Contacted"], orientation="h",
        marker_color=accent, marker_line_width=0,
        text=sub["Contacted"], textposition="inside",
        textfont=dict(color="#fff", size=11, family=FONT),
    ))
    fig.add_trace(go.Bar(
        name="Not Contacted", y=sub["Agent"], x=sub["NotContacted"], orientation="h",
        marker_color="#E5E7EB", marker_line_width=0,
        text=sub["NotContacted"], textposition="inside",
        textfont=dict(color="#6B7280", size=11, family=FONT),
    ))
    fig.update_layout(**_base(height=max(200, len(sub)*52), showlegend=True), barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font_size=11, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, tickfont=dict(size=11, color=TXTC)),
        yaxis=dict(showgrid=False, tickfont=dict(size=12, color="#0A0E1A")),
    )
    return fig


def connect_pct_bar(sub):
    sub = sub.sort_values("Contact %", ascending=False)
    fig = go.Figure(go.Bar(
        x=sub["Agent"], y=sub["Contact %"],
        marker_color=[pct_color(v) for v in sub["Contact %"]],
        marker_line_width=0,
        text=[f"{v}%" for v in sub["Contact %"]],
        textposition="outside",
        textfont=dict(size=11, family=FONT, color="#0A0E1A"),
    ))
    fig.add_shape(type="line", x0=-.5, x1=len(sub)-.5, y0=50, y1=50,
                  line=dict(color="#D1D5DB", dash="dot", width=1.5))
    fig.add_annotation(x=len(sub)-.5, y=50, text="50% target", showarrow=False,
                       font=dict(size=9, color="#9CA3AF"), xanchor="right", yanchor="bottom")
    max_y = max(sub["Contact %"].max()+15, 70) if not sub.empty else 70
    fig.update_layout(**_base(height=250, showlegend=False, margin=dict(l=0,r=0,t=24,b=0)),
        yaxis=dict(range=[0,max_y], showgrid=True, gridcolor=GRID, zeroline=False,
                   ticksuffix="%", tickfont=dict(size=10, color=TXTC)),
        xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#0A0E1A")),
    )
    return fig


def disposition_donut(att, conn, fail, accent):
    if att == 0:
        fig = go.Figure(go.Pie(labels=["No data"], values=[1], hole=.62,
            marker=dict(colors=["#E5E7EB"]), textinfo="none", hoverinfo="skip"))
        fig.add_annotation(text="—", x=0.5, y=0.5, showarrow=False,
                           font=dict(size=22, color="#9CA3AF", family=FONT))
        fig.update_layout(**_base(height=180, showlegend=False))
        return fig
    other = max(att - conn - fail, 0)
    pct   = round(conn / att * 100, 1)
    fig = go.Figure(go.Pie(
        labels=["Contacted","Not Contacted","Other"],
        values=[conn, fail, other], hole=.62,
        marker=dict(colors=[accent, "#E5E7EB", "#F3F4F6"],
                    line=dict(color="#fff", width=2)),
        textinfo="none",
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
    ))
    fig.add_annotation(text=f"<b>{pct}%</b>", x=0.5, y=0.5, showarrow=False,
                       font=dict(size=20, color="#0A0E1A", family=FONT))
    fig.update_layout(**_base(height=180, showlegend=False))
    return fig


def disposition_stacked_bar(pivot):
    fig = go.Figure()
    totals = pivot.sum(axis=1)
    for disp in ALL_DISPOSITIONS:
        col_data = pivot[disp] if disp in pivot.columns else [0]*len(pivot)
        pcts = (col_data / totals * 100).round(1)
        fig.add_trace(go.Bar(
            name=f"{DISP_ICONS[disp]} {disp}", x=pivot.index, y=col_data,
            marker_color=DISP_COLORS[disp], marker_line_width=0,
            text=[f"{c} ({p}%)" for c,p in zip(col_data, pcts)],
            textposition="inside", textfont=dict(size=10, color="#fff", family=FONT),
            hovertemplate=f"<b>%{{x}}</b><br>{disp}: %{{y}}<extra></extra>",
        ))
    fig.update_layout(**_base(height=320), barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
                    font_size=11, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#0A0E1A")),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, tickfont=dict(size=10, color=TXTC)),
    )
    return fig


def agent_disposition_bar(agent_name, counts, pcts):
    fig = go.Figure()
    for disp, count, pct in zip(ALL_DISPOSITIONS, counts, pcts):
        fig.add_trace(go.Bar(
            name=disp, x=[count], y=[agent_name], orientation="h",
            marker_color=DISP_COLORS[disp], marker_line_width=0,
            text=f"{count} ({pct}%)", textposition="inside",
            textfont=dict(size=10, color="#fff", family=FONT), showlegend=False,
        ))
    fig.update_layout(**_base(height=70, margin=dict(l=0,r=0,t=4,b=0)), barmode="stack",
        xaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, tickfont=dict(size=10, color=TXTC)),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#0A0E1A")),
    )
    return fig


# ── Table helpers ─────────────────────────────────────────────────────────────

def _table_styles():
    return [
        {"selector": "th", "props": [
            ("font-size","11px"),("font-weight","700"),("letter-spacing",".06em"),
            ("text-transform","uppercase"),("color","#9CA3AF"),("background","#F9FAFB"),
            ("border-bottom","1px solid #E2E5EC"),("padding","10px 14px"),
        ]},
        {"selector": "td", "props": [
            ("padding","10px 14px"),("border-bottom","1px solid #F3F4F6"),("color","#0A0E1A"),
        ]},
        {"selector": "tr:last-child td", "props": [("border-bottom","none")]},
        {"selector": "tr:hover td",      "props": [("background-color","#F9FAFB")]},
    ]


def render_agent_summary_table(sub):
    import pandas as pd
    display = sub[["Agent","Attempts","Contacted","NotContacted","Contact %","TalkTimeSecs"]].copy()
    display.rename(columns={"NotContacted":"Not Contacted"}, inplace=True)
    display["Talk Time"] = display["TalkTimeSecs"].apply(format_duration)
    display["Contact %"] = display["Contact %"].apply(lambda v: f"{v}%")
    display.drop(columns=["TalkTimeSecs"], inplace=True)

    def _row_style(row):
        v  = float(row["Contact %"].replace("%",""))
        bg = "#F0FDF4" if v >= 60 else ("#FFFBEB" if v >= 40 else "#FEF2F2")
        cols = list(row.index)
        cp_idx = cols.index("Contact %")
        return [""] * cp_idx + [f"background:{bg};font-weight:700"] + [""] * (len(cols) - cp_idx - 1)

    styled = (
        display.style.apply(_row_style, axis=1)
               .set_properties(**{"font-size":"13px","font-family":"DM Sans, sans-serif"})
               .set_table_styles(_table_styles())
               .hide(axis="index")
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)


def render_disposition_table(raw_df, camp_map):
    import pandas as pd
    table_pivot = raw_df.groupby(["Agent","Disposition"]).size().unstack(fill_value=0)
    for d in ALL_DISPOSITIONS:
        if d not in table_pivot.columns: table_pivot[d] = 0
    table_pivot = table_pivot[ALL_DISPOSITIONS].copy()
    table_pivot["Total"] = table_pivot.sum(axis=1)
    table_pivot = table_pivot.sort_values("Total", ascending=False)

    rows = []
    for agent, row in table_pivot.iterrows():
        total = row["Total"]
        r = {"Agent": agent, "Campaign": camp_map.get(agent, "Unknown")}
        for d in ALL_DISPOSITIONS:
            c = int(row[d]); p = round(c/total*100,1) if total else 0.0
            r[d] = f"{c}  ({p}%)"
        r["Total"] = int(total)
        rows.append(r)

    display_df = pd.DataFrame(rows)

    def _colour_camp(val):
        if val == "Sports":  return "color:#0A0E1A;font-weight:700"
        if val == "Holiday": return "color:#0A0E1A;font-weight:700"
        return ""

    styled = (
        display_df.style.map(_colour_camp, subset=["Campaign"])
                  .set_properties(**{"font-size":"13px","font-family":"DM Sans, sans-serif"})
                  .set_table_styles(_table_styles())
                  .hide(axis="index")
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)
    return table_pivot
