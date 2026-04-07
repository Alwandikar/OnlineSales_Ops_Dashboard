# utils/components.py
# ── Reusable UI components and chart builders ─────────────────────────────────

import plotly.graph_objects as go
import streamlit as st

from utils.constants import (
    ALL_DISPOSITIONS,
    DISP_COLORS,
    DISP_ICONS,
    FONT,
    GRID,
    TXTC,
    ACCENT_GREEN,
    TXT_PRIMARY,
    TXT_SECONDARY,
    BG_ELEVATED,
    BG_RAISED,
)


# ── HTML component helpers ────────────────────────────────────────────────────

def kpi_card(label: str, value: str, sub_text: str, icon: str,
             accent: str, value_class: str = "") -> str:
    """Return HTML string for a KPI metric card."""
    return f"""
    <div class="kpi-card">
        <div class="kpi-accent-bar" style="background:{accent}"></div>
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {value_class}">{value}</div>
        <div class="kpi-sub">{sub_text}</div>
    </div>"""


def disp_card(disp: str, count: int, pct: float, small: bool = False) -> str:
    """Return HTML string for a single disposition metric card."""
    count_size  = "1.5rem" if small else "1.9rem"
    icon_size   = "1rem"   if small else "1.3rem"
    return f"""
    <div class="disp-card">
        <div class="disp-accent" style="background:{DISP_COLORS[disp]}"></div>
        <div style="font-size:{icon_size};margin-bottom:.3rem">{DISP_ICONS[disp]}</div>
        <div class="disp-label">{disp}</div>
        <div style="font-size:{count_size};font-weight:800;color:#FFFFFF;letter-spacing:-.03em">{count:,}</div>
        <div class="disp-pct">{pct}%</div>
    </div>"""


def empty_state(title: str = "No data loaded yet",
                sub: str = "Upload a CSV on the Overview page.",
                icon: str = "📂") -> None:
    """Render a centered empty-state message."""
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-icon">{icon}</div>
        <div class="empty-title">{title}</div>
        <div class="empty-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)


def top_nav(title: str, subtitle: str, page_tag: str,
            logo_class: str, tag_class: str, logo_icon: str) -> None:
    """Render the sticky top navigation bar."""
    st.markdown(f"""
    <div class="top-nav">
        <div class="nav-brand">
            <div class="nav-logo {logo_class}">{logo_icon}</div>
            <div>
                <div class="nav-title">{title}</div>
                <div class="nav-sub">{subtitle}</div>
            </div>
        </div>
        <div class="nav-tag {tag_class}">{page_tag}</div>
    </div>""", unsafe_allow_html=True)


def date_banner(date_str: str, extra: str = "") -> None:
    """Render the yellow date context banner."""
    tail = f" &nbsp;·&nbsp; {extra}" if extra else ""
    st.markdown(
        f'<div class="date-banner">📅 &nbsp; Showing data for <strong>{date_str}</strong>{tail}</div>',
        unsafe_allow_html=True,
    )


def section_label(text: str, margin_top: str = "2rem") -> None:
    """Render an uppercase section heading label."""
    st.markdown(
        f'<p class="section-label" style="margin-top:{margin_top}">{text}</p>',
        unsafe_allow_html=True,
    )


# ── Plotly chart builders ─────────────────────────────────────────────────────

def _base_layout(**overrides) -> dict:
    """Common Plotly layout defaults."""
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family=FONT,
        font_color=TXTC,
        margin=dict(l=0, r=0, t=10, b=0),
    )
    base.update(overrides)
    return base


def pct_color(v: float) -> str:
    """Traffic-light colour for a contact-rate percentage (dark theme)."""
    if v >= 60: return "#1DB954"   # Spotify green
    if v >= 40: return "#f59e0b"   # amber
    return "#e85454"               # red


def agent_bar_chart(sub, accent: str) -> go.Figure:
    """Horizontal stacked bar — Contacted vs Not Contacted per agent."""
    sub = sub.sort_values("Contact %", ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Contacted", y=sub["Agent"], x=sub["Contacted"], orientation="h",
        marker_color=accent, marker_line_width=0,
        text=sub["Contacted"], textposition="inside",
        textfont=dict(color="#000", size=11, family=FONT),
    ))
    fig.add_trace(go.Bar(
        name="Not Contacted", y=sub["Agent"], x=sub["NotContacted"], orientation="h",
        marker_color="#333333", marker_line_width=0,
        text=sub["NotContacted"], textposition="inside",
        textfont=dict(color="#B3B3B3", size=11, family=FONT),
    ))
    fig.update_layout(
        **_base_layout(height=max(200, len(sub) * 52), showlegend=True),
        barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font_size=11, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False,
                   tickfont=dict(size=11, color=TXTC)),
        yaxis=dict(showgrid=False, tickfont=dict(size=12, color="#FFFFFF")),
    )
    return fig


def connect_pct_bar(sub) -> go.Figure:
    """Vertical bar — contact rate per agent with traffic-light colours."""
    sub = sub.sort_values("Contact %", ascending=False)
    fig = go.Figure(go.Bar(
        x=sub["Agent"], y=sub["Contact %"],
        marker_color=[pct_color(v) for v in sub["Contact %"]],
        marker_line_width=0,
        text=[f"{v}%" for v in sub["Contact %"]],
        textposition="outside",
        textfont=dict(size=11, family=FONT, color="#FFFFFF"),
    ))
    fig.add_shape(type="line", x0=-0.5, x1=len(sub) - 0.5, y0=50, y1=50,
                  line=dict(color="#535353", dash="dot", width=1.5))
    fig.add_annotation(x=len(sub) - 0.5, y=50, text="50% target", showarrow=False,
                       font=dict(size=9, color="#535353"), xanchor="right", yanchor="bottom")
    max_y = max(sub["Contact %"].max() + 15, 70) if not sub.empty else 70
    fig.update_layout(
        **_base_layout(height=250, showlegend=False, margin=dict(l=0, r=0, t=24, b=0)),
        yaxis=dict(range=[0, max_y], showgrid=True, gridcolor=GRID, zeroline=False,
                   ticksuffix="%", tickfont=dict(size=10, color=TXTC)),
        xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#FFFFFF")),
    )
    return fig


def disposition_donut(att: int, conn: int, fail: int, accent: str) -> go.Figure:
    """Donut chart showing connected / failed / other split."""
    if att == 0:
        # Render an empty placeholder ring when there's no data
        fig = go.Figure(go.Pie(
            labels=["No data"], values=[1], hole=.62,
            marker=dict(colors=["#e5e7eb"]),
            textinfo="none", hoverinfo="skip",
        ))
        fig.add_annotation(text="—", x=0.5, y=0.5, showarrow=False,
                           font=dict(size=22, color="#9ca3af", family=FONT))
        fig.update_layout(**_base_layout(height=180, showlegend=False))
        return fig

    other = max(att - conn - fail, 0)
    pct   = round(conn / att * 100, 1)
    fig   = go.Figure(go.Pie(
        labels=["Connected", "Failed", "Other"],
        values=[conn, fail, other],
        hole=.62,
        marker=dict(colors=[accent, "#fca5a5", "#e5e7eb"],
                    line=dict(color="#fff", width=2)),
        textinfo="none",
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
    ))
    fig.add_annotation(text=f"<b>{pct}%</b>", x=0.5, y=0.5, showarrow=False,
                       font=dict(size=22, color="#FFFFFF", family=FONT))
    fig.update_layout(**_base_layout(height=180, showlegend=False))
    return fig


def disposition_stacked_bar(pivot) -> go.Figure:
    """Stacked bar of disposition counts for all agents."""
    fig = go.Figure()
    totals = pivot.sum(axis=1)
    for disp in ALL_DISPOSITIONS:
        col_data = pivot[disp] if disp in pivot.columns else [0] * len(pivot)
        pcts = (col_data / totals * 100).round(1)
        fig.add_trace(go.Bar(
            name=f"{DISP_ICONS[disp]} {disp}",
            x=pivot.index,
            y=col_data,
            marker_color=DISP_COLORS[disp],
            marker_line_width=0,
            text=[f"{c} ({p}%)" for c, p in zip(col_data, pcts)],
            textposition="inside",
            textfont=dict(size=10, color="#fff", family=FONT),
            hovertemplate=f"<b>%{{x}}</b><br>{disp}: %{{y}}<extra></extra>",
        ))
    fig.update_layout(
        **_base_layout(height=320),
        barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.01,
                    xanchor="left", x=0, font_size=11, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False, tickfont=dict(size=12, color=TXTC)),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False,
                   tickfont=dict(size=10, color="#9ca3af")),
    )
    return fig


def agent_disposition_bar(agent_name: str, counts: list[int],
                           pcts: list[float]) -> go.Figure:
    """Single horizontal stacked bar for one agent's disposition mix."""
    fig = go.Figure()
    for disp, count, pct in zip(ALL_DISPOSITIONS, counts, pcts):
        fig.add_trace(go.Bar(
            name=disp, x=[count], y=[agent_name],
            orientation="h",
            marker_color=DISP_COLORS[disp],
            marker_line_width=0,
            text=f"{count} ({pct}%)",
            textposition="inside",
            textfont=dict(size=10, color="#fff", family=FONT),
            showlegend=False,
        ))
    fig.update_layout(
        **_base_layout(height=70, margin=dict(l=0, r=0, t=4, b=0)),
        barmode="stack",
        xaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False,
                   tickfont=dict(size=10, color="#9ca3af")),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color=TXTC)),
    )
    return fig


# ── Table helpers ─────────────────────────────────────────────────────────────

def _table_styles() -> list[dict]:
    return [
        {"selector": "th", "props": [
            ("font-size", "11px"), ("font-weight", "700"),
            ("letter-spacing", ".06em"), ("text-transform", "uppercase"),
            ("color", "#535353"), ("background", "#181818"),
            ("border-bottom", "1px solid #282828"), ("padding", "10px 14px"),
        ]},
        {"selector": "td",               "props": [("padding", "10px 14px"), ("border-bottom", "1px solid #282828"), ("color", "#FFFFFF"), ("background", "#181818")]},
        {"selector": "tr:last-child td", "props": [("border-bottom", "none")]},
        {"selector": "tr:hover td",      "props": [("background-color", "#282828 !important")]},
    ]


def render_agent_summary_table(sub) -> None:
    """Render the per-agent summary table for a campaign block."""
    display = sub[["Agent", "Attempts", "Contacted", "NotContacted", "Contact %"]].copy()
    display.rename(columns={"NotContacted": "Not Contacted"}, inplace=True)
    display["Contact %"] = display["Contact %"].apply(lambda v: f"{v}%")

    def _row_style(row):
        v   = float(row["Contact %"].replace("%", ""))
        bg  = "background:#1a2e1a;color:#1DB954;font-weight:700" if v >= 60 \
              else ("background:#2a2510;color:#f59e0b;font-weight:700" if v >= 40 \
              else "background:#2a1515;color:#e85454;font-weight:700")
        return [""] * (len(row) - 1) + [bg]

    styled = (
        display.style
               .apply(_row_style, axis=1)
               .set_properties(**{"font-size": "13px", "font-family": "DM Sans, sans-serif",
                                  "color": "#FFFFFF", "background-color": "#181818"})
               .set_table_styles(_table_styles())
               .hide(axis="index")
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)


def render_disposition_table(raw_df, camp_map: dict) -> None:
    """Render the Agent × Disposition pivot table."""
    from utils.constants import ALL_DISPOSITIONS

    table_pivot = raw_df.groupby(["Agent", "Disposition"]).size().unstack(fill_value=0)
    for d in ALL_DISPOSITIONS:
        if d not in table_pivot.columns:
            table_pivot[d] = 0
    table_pivot = table_pivot[ALL_DISPOSITIONS].copy()
    table_pivot["Total"] = table_pivot.sum(axis=1)
    table_pivot = table_pivot.sort_values("Total", ascending=False)

    rows = []
    for agent, row in table_pivot.iterrows():
        total = row["Total"]
        r = {"Agent": agent, "Campaign": camp_map.get(agent, "Unknown")}
        for d in ALL_DISPOSITIONS:
            c = int(row[d])
            p = round(c / total * 100, 1) if total else 0.0
            r[d] = f"{c}  ({p}%)"
        r["Total"] = int(total)
        rows.append(r)

    display_df = pd.DataFrame(rows)

    def _colour_camp(val):
        if val == "Sports":  return "color:#1d4ed8;font-weight:600"
        if val == "Holiday": return "color:#be185d;font-weight:600"
        return ""

    styled = (
        display_df.style
                  .applymap(_colour_camp, subset=["Campaign"])
                  .set_properties(**{"font-size": "13px", "font-family": "Sora, sans-serif"})
                  .set_table_styles(_table_styles())
                  .hide(axis="index")
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    return table_pivot  # return so callers can reuse without re-grouping
