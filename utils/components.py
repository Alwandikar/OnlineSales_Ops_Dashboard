# utils/components.py — Reusable UI components and charts

from datetime import date, timedelta
import plotly.graph_objects as go
import streamlit as st

from utils.constants import (
    ALL_DISPOSITIONS, DISP_COLORS, DISP_ICONS,
    ACCENT_BLUE, FONT, GRID, TXTC,
    BG_CARD, BG_ELEVATED,
)
from utils.data import format_duration

# ── HTML helpers ──────────────────────────────────────────────────────────────

def top_nav(subtitle: str, page_tag: str):
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
         padding:.9rem 0 1.4rem;border-bottom:1px solid #38383A;margin-bottom:1.6rem">
        <div style="display:flex;align-items:center;gap:.8rem">
            <img src="https://www.dreamsetgo.com/DreamSetGo-48x48.png"
                 style="width:34px;height:34px;border-radius:8px;object-fit:contain"/>
            <div>
                <div style="font-size:1rem;font-weight:700;color:#FFFFFF;letter-spacing:-.01em">
                    DSG Online Sales Team</div>
                <div style="font-size:.7rem;color:#636366">{subtitle}</div>
            </div>
        </div>
        <div style="font-size:.65rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;
             padding:.3rem .85rem;border-radius:6px;background:#0A84FF22;
             color:#0A84FF;border:1px solid #0A84FF44">{page_tag}</div>
    </div>""", unsafe_allow_html=True)


def sidebar_nav():
    """Render DSG branding in sidebar."""
    st.sidebar.markdown("""
    <div style="padding:1.2rem 1rem 1rem;border-bottom:1px solid #38383A;margin-bottom:.5rem">
        <div style="display:flex;align-items:center;gap:.7rem">
            <img src="https://www.dreamsetgo.com/DreamSetGo-48x48.png"
                 style="width:30px;height:30px;border-radius:7px;object-fit:contain"/>
            <div>
                <div style="font-size:.85rem;font-weight:700;color:#FFFFFF">DSG Sales</div>
                <div style="font-size:.65rem;color:#636366">Online Team</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


def kpi_card(label, value, sub, icon, accent, value_class=""):
    return f"""<div class="kpi-card">
        <div class="kpi-accent" style="background:{accent}"></div>
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {value_class}">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""


def disp_card(disp, count, pct, small=False):
    sz = "1.4rem" if small else "1.7rem"
    return f"""<div class="disp-card">
        <div class="disp-accent" style="background:{DISP_COLORS[disp]}"></div>
        <div style="font-size:{'1rem' if small else '1.1rem'};margin-bottom:.2rem">{DISP_ICONS[disp]}</div>
        <div class="disp-label">{disp}</div>
        <div style="font-size:{sz};font-weight:700;color:#FFFFFF;letter-spacing:-.02em">{count:,}</div>
        <div class="disp-pct">{pct}%</div>
    </div>"""


def empty_state(title="No data", sub="Upload a CSV to get started.", icon="📊"):
    st.markdown(f"""<div class="empty-state">
        <div class="empty-icon">{icon}</div>
        <div class="empty-title">{title}</div>
        <div class="empty-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)


def section_label(text, mt="1.8rem"):
    st.markdown(f'<p class="section-label" style="margin-top:{mt}">{text}</p>',
                unsafe_allow_html=True)


# ── Date filter ───────────────────────────────────────────────────────────────

def render_date_filter(page_key: str) -> tuple[date, date]:
    """
    Crash-proof date filter with fixed 2026 bounds.
    page_key ensures each page has independent state.
    Returns (from_date, to_date) — only changes on Submit.
    """
    MIN_DATE = date(2026, 1, 1)
    MAX_DATE = date(2026, 12, 31)
    today    = date(2026, 4, 15)  # safe default; overridden by actual data

    from_key = f"applied_from_{page_key}"
    to_key   = f"applied_to_{page_key}"

    # Default: current month MTD
    if from_key not in st.session_state:
        st.session_state[from_key] = date(2026, 4, 1)
    if to_key not in st.session_state:
        st.session_state[to_key] = date(2026, 4, 9)

    st.markdown('<div class="date-filter-bar">', unsafe_allow_html=True)

    btn1, btn2, spacer = st.columns([1.2, 1.2, 6])
    with btn1:
        if st.button("📅 This Month", key=f"mtd_{page_key}", use_container_width=True):
            st.session_state[from_key] = date(2026, 4, 1)
            st.session_state[to_key]   = date(2026, 4, 9)
            st.rerun()
    with btn2:
        if st.button("📋 All Data", key=f"all_{page_key}", use_container_width=True):
            st.session_state[from_key] = MIN_DATE
            st.session_state[to_key]   = MAX_DATE
            st.rerun()

    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        from_val = st.date_input("From", value=st.session_state[from_key],
                                 min_value=MIN_DATE, max_value=MAX_DATE,
                                 key=f"di_from_{page_key}")
    with c2:
        to_min = from_val
        to_max = min(MAX_DATE, from_val + timedelta(days=30))
        to_val = st.session_state[to_key]
        if to_val < to_min: to_val = to_min
        if to_val > to_max: to_val = to_max
        to_val = st.date_input("To", value=to_val,
                               min_value=to_min, max_value=to_max,
                               key=f"di_to_{page_key}")
    with c3:
        st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
        if st.button("Apply ✓", key=f"apply_{page_key}",
                     use_container_width=True, type="primary"):
            st.session_state[from_key] = from_val
            st.session_state[to_key]   = to_val
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    f = st.session_state[from_key]
    t = st.session_state[to_key]
    days = (t - f).days + 1
    st.markdown(
        f'<div class="date-banner">📅 &nbsp;'
        f'<strong>{f.strftime("%d %b %Y")}</strong>'
        f' → <strong>{t.strftime("%d %b %Y")}</strong>'
        f' &nbsp;({days} day{"s" if days != 1 else ""})</div>',
        unsafe_allow_html=True,
    )
    return f, t


# ── Chart helpers ─────────────────────────────────────────────────────────────

def _base(h=300, **kw):
    d = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
             font_family=FONT, font_color="#FFFFFF",
             margin=dict(l=0,r=0,t=10,b=0), height=h)
    d.update(kw)
    return d


def pct_color(v):
    if v >= 60: return "#30D158"
    if v >= 40: return "#FF9F0A"
    return "#FF453A"


def agent_bar_chart(sub, accent):
    sub = sub.sort_values("Contact %", ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Contacted", y=sub["Agent"], x=sub["Contacted"],
        orientation="h", marker_color=accent, marker_line_width=0,
        text=sub["Contacted"], textposition="inside",
        textfont=dict(color="#fff", size=11, family=FONT)))
    fig.add_trace(go.Bar(name="Not Contacted", y=sub["Agent"], x=sub["NotContacted"],
        orientation="h", marker_color="#2C2C2E", marker_line_width=0,
        text=sub["NotContacted"], textposition="inside",
        textfont=dict(color="#8E8E93", size=11, family=FONT)))
    fig.update_layout(**_base(h=max(200,len(sub)*52), showlegend=True), barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font_size=11, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, tickfont=dict(size=11,color=TXTC)),
        yaxis=dict(showgrid=False, tickfont=dict(size=12,color="#FFFFFF")))
    return fig


def contact_rate_bar(sub):
    sub = sub.sort_values("Contact %", ascending=False)
    fig = go.Figure(go.Bar(
        x=sub["Agent"], y=sub["Contact %"],
        marker_color=[pct_color(v) for v in sub["Contact %"]],
        marker_line_width=0,
        text=[f"{v}%" for v in sub["Contact %"]], textposition="outside",
        textfont=dict(size=11, family=FONT, color="#FFFFFF")))
    fig.add_shape(type="line", x0=-.5, x1=len(sub)-.5, y0=50, y1=50,
                  line=dict(color="#48484A", dash="dot", width=1.5))
    fig.add_annotation(x=len(sub)-.5, y=50, text="50% target", showarrow=False,
                       font=dict(size=9, color="#636366"), xanchor="right", yanchor="bottom")
    max_y = max(sub["Contact %"].max()+15, 70) if not sub.empty else 70
    fig.update_layout(**_base(h=250, showlegend=False, margin=dict(l=0,r=0,t=24,b=0)),
        yaxis=dict(range=[0,max_y], showgrid=True, gridcolor=GRID, zeroline=False,
                   ticksuffix="%", tickfont=dict(size=10,color=TXTC)),
        xaxis=dict(showgrid=False, tickfont=dict(size=12,color="#FFFFFF")))
    return fig


def donut_chart(att, cont, nc, accent):
    if att == 0:
        fig = go.Figure(go.Pie(labels=["No data"], values=[1], hole=.62,
            marker=dict(colors=["#2C2C2E"]), textinfo="none", hoverinfo="skip"))
        fig.add_annotation(text="—", x=0.5, y=0.5, showarrow=False,
                           font=dict(size=20,color="#636366",family=FONT))
        fig.update_layout(**_base(h=180, showlegend=False))
        return fig
    pct = round(cont/att*100,1)
    fig = go.Figure(go.Pie(
        labels=["Contacted","Not Contacted"], values=[cont,nc], hole=.62,
        marker=dict(colors=[accent,"#2C2C2E"], line=dict(color="#000",width=2)),
        textinfo="none", hovertemplate="%{label}: %{value} (%{percent})<extra></extra>"))
    fig.add_annotation(text=f"<b>{pct}%</b>", x=0.5, y=0.5, showarrow=False,
                       font=dict(size=20,color="#FFFFFF",family=FONT))
    fig.update_layout(**_base(h=180, showlegend=False))
    return fig


def disposition_stacked_bar(pivot):
    fig = go.Figure()
    totals = pivot.sum(axis=1)
    for disp in ALL_DISPOSITIONS:
        col = pivot[disp] if disp in pivot.columns else [0]*len(pivot)
        pcts = (col/totals*100).round(1)
        fig.add_trace(go.Bar(
            name=f"{DISP_ICONS[disp]} {disp}", x=pivot.index, y=col,
            marker_color=DISP_COLORS[disp], marker_line_width=0,
            text=[f"{c}({p}%)" for c,p in zip(col,pcts)],
            textposition="inside", textfont=dict(size=9,color="#fff",family=FONT),
            hovertemplate=f"<b>%{{x}}</b><br>{disp}: %{{y}}<extra></extra>"))
    fig.update_layout(**_base(h=300), barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
                    font_size=11, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False, tickfont=dict(size=12,color="#FFFFFF")),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, tickfont=dict(size=10,color=TXTC)))
    return fig


def agent_disp_bar(agent, counts, pcts):
    fig = go.Figure()
    for disp, c, p in zip(ALL_DISPOSITIONS, counts, pcts):
        fig.add_trace(go.Bar(name=disp, x=[c], y=[agent], orientation="h",
            marker_color=DISP_COLORS[disp], marker_line_width=0,
            text=f"{c}({p}%)", textposition="inside",
            textfont=dict(size=9,color="#fff",family=FONT), showlegend=False))
    fig.update_layout(**_base(h=65, margin=dict(l=0,r=0,t=3,b=0)), barmode="stack",
        xaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, tickfont=dict(size=9,color=TXTC)),
        yaxis=dict(showgrid=False, tickfont=dict(size=10,color="#FFFFFF")))
    return fig


# ── Table helpers ─────────────────────────────────────────────────────────────

def _tbl_styles():
    return [
        {"selector":"th","props":[("font-size","11px"),("font-weight","700"),
            ("letter-spacing",".06em"),("text-transform","uppercase"),("color","#636366"),
            ("background","#1C1C1E"),("border-bottom","1px solid #38383A"),("padding","9px 12px")]},
        {"selector":"td","props":[("padding","9px 12px"),("border-bottom","1px solid #2C2C2E"),
            ("color","#FFFFFF"),("background","#1C1C1E")]},
        {"selector":"tr:last-child td","props":[("border-bottom","none")]},
        {"selector":"tr:hover td","props":[("background","#2C2C2E !important")]},
    ]


def agent_table(sub):
    import pandas as pd
    d = sub[["Agent","Attempts","Contacted","NotContacted","Contact %","TalkTimeSecs"]].copy()
    d.rename(columns={"NotContacted":"Not Contacted"}, inplace=True)
    d["Talk Time"] = d["TalkTimeSecs"].apply(format_duration)
    d["Contact %"] = d["Contact %"].apply(lambda v: f"{v}%")
    d.drop(columns=["TalkTimeSecs"], inplace=True)

    def _style(row):
        v  = float(row["Contact %"].replace("%",""))
        bg = "#30D15822" if v>=60 else ("#FF9F0A22" if v>=40 else "#FF453A22")
        cols = list(row.index)
        idx  = cols.index("Contact %")
        return [""]*idx + [f"background:{bg};font-weight:700;color:#FFFFFF"] + [""]*(len(cols)-idx-1)

    styled = (d.style.apply(_style, axis=1)
               .set_properties(**{"font-size":"13px"})
               .set_table_styles(_tbl_styles())
               .hide(axis="index"))
    st.dataframe(styled, use_container_width=True, hide_index=True)


def disp_table(raw_df, camp_map):
    import pandas as pd
    pivot = raw_df.groupby(["Agent","Disposition"]).size().unstack(fill_value=0)
    for d in ALL_DISPOSITIONS:
        if d not in pivot.columns: pivot[d] = 0
    pivot = pivot[ALL_DISPOSITIONS].copy()
    pivot["Total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("Total", ascending=False)

    rows = []
    for agent, row in pivot.iterrows():
        total = row["Total"]
        r = {"Agent":agent, "Campaign":camp_map.get(agent,"Unknown")}
        for d in ALL_DISPOSITIONS:
            c = int(row[d]); p = round(c/total*100,1) if total else 0.0
            r[d] = f"{c} ({p}%)"
        r["Total"] = int(total)
        rows.append(r)

    df = pd.DataFrame(rows)
    styled = (df.style
               .set_properties(**{"font-size":"13px"})
               .set_table_styles(_tbl_styles())
               .hide(axis="index"))
    st.dataframe(styled, use_container_width=True, hide_index=True)
    return pivot
