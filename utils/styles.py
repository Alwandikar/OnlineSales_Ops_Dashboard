# utils/styles.py  —  DSG brand theme

SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700;9..40,800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif !important;
    color: #0A0E1A !important;
}
.stApp { background: #F5F6F8 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2.5rem 3rem !important; max-width: 1400px !important; }

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #0A0E1A !important;
    border-right: none !important;
}
section[data-testid="stSidebar"] * { color: #D1D5DB !important; }
section[data-testid="stSidebar"] a:hover { color: #C9A035 !important; }
/* Keep collapse button visible */
button[data-testid="collapsedControl"] { visibility: visible !important; opacity: 1 !important; }

/* ── Tabs — DSG gold active ───────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid #E2E5EC !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.04) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #6B7280 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: .85rem !important;
    border-radius: 7px !important;
    padding: .5rem 1.6rem !important;
    border: none !important;
    transition: all .15s !important;
}
.stTabs [aria-selected="true"] {
    background: #0A0E1A !important;
    color: #C9A035 !important;
}
.stTabs [data-baseweb="tab-border"]    { display: none !important; }
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ── Top nav ──────────────────────────────────────────────────────────────── */
.top-nav {
    background: #0A0E1A;
    padding: 0.85rem 2.5rem;
    margin: 0 -2.5rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 100;
    box-shadow: 0 2px 12px rgba(10,14,26,.25);
}
.nav-brand { display: flex; align-items: center; gap: .85rem; }
.nav-logo  { width: 38px; height: 38px; border-radius: 8px; object-fit: contain; }
.nav-title { font-size: 1rem; font-weight: 700; color: #FFFFFF; letter-spacing: -.01em; }
.nav-sub   { font-size: .7rem; color: #9CA3AF; }
.nav-tag   {
    font-size: .68rem; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; padding: .35rem 1rem; border-radius: 6px;
    background: #C9A035; color: #0A0E1A; border: none;
}

/* ── Date filter bar ──────────────────────────────────────────────────────── */
.filter-bar {
    background: #FFFFFF; border: 1px solid #E2E5EC; border-radius: 12px;
    padding: .85rem 1.4rem; margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.filter-label {
    font-size: .72rem; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; color: #6B7280; white-space: nowrap;
}
.filter-chip {
    font-size: .75rem; font-weight: 600; padding: .3rem .9rem;
    border-radius: 6px; cursor: pointer; border: 1px solid #E2E5EC;
    background: #F5F6F8; color: #374151; transition: all .15s;
}
.filter-chip-active {
    background: #0A0E1A !important; color: #C9A035 !important;
    border-color: #0A0E1A !important;
}
.filter-range-text {
    font-size: .8rem; font-weight: 600; color: #0A0E1A;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Date banner ──────────────────────────────────────────────────────────── */
.date-banner {
    background: #FEF9EC; border: 1px solid #F6D860; border-radius: 10px;
    padding: .65rem 1.2rem; margin-bottom: 1.5rem;
    font-size: .82rem; color: #92400E; font-weight: 500;
    display: flex; align-items: center; gap: .5rem;
}

/* ── Section label ────────────────────────────────────────────────────────── */
.section-label {
    font-size: .65rem; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: #9CA3AF; margin: 2rem 0 .9rem;
}

/* ── KPI cards ────────────────────────────────────────────────────────────── */
.kpi-card {
    background: #FFFFFF; border-radius: 12px; padding: 1.3rem 1.5rem 1.1rem;
    border: 1px solid #E2E5EC; box-shadow: 0 1px 3px rgba(0,0,0,.04);
    position: relative; overflow: hidden;
    transition: box-shadow .2s, transform .2s; height: 100%;
}
.kpi-card:hover { box-shadow: 0 6px 20px rgba(10,14,26,.1); transform: translateY(-2px); }
.kpi-accent-bar { position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 12px 12px 0 0; }
.kpi-label { font-size: .65rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: #9CA3AF; margin-bottom: .5rem; }
.kpi-value       { font-size: 2.1rem; font-weight: 800; color: #0A0E1A; letter-spacing: -.04em; line-height: 1.1; }
.kpi-value-gold  { color: #C9A035; }
.kpi-value-green { color: #047857; }
.kpi-value-red   { color: #B91C1C; }
.kpi-value-blue  { color: #0047CC; }
.kpi-sub  { font-size: .7rem; color: #9CA3AF; margin-top: .4rem; }
.kpi-icon { position: absolute; top: 1.1rem; right: 1.3rem; font-size: 1.3rem; opacity: .12; }

/* ── Disposition cards ────────────────────────────────────────────────────── */
.disp-card {
    background: #FFFFFF; border-radius: 10px; padding: 1rem 1.2rem;
    border: 1px solid #E2E5EC; box-shadow: 0 1px 3px rgba(0,0,0,.04);
    position: relative; overflow: hidden; height: 100%;
    transition: box-shadow .18s, transform .15s;
}
.disp-card:hover { box-shadow: 0 4px 16px rgba(10,14,26,.09); transform: translateY(-2px); }
.disp-accent { position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 10px 10px 0 0; }
.disp-label  { font-size: .62rem; font-weight: 700; letter-spacing: .09em; text-transform: uppercase; color: #9CA3AF; }
.disp-count  { font-size: 1.8rem; font-weight: 800; color: #0A0E1A; letter-spacing: -.03em; line-height: 1.1; }
.disp-pct    { font-size: .78rem; font-weight: 600; color: #6B7280; margin-top: .15rem; font-family: 'JetBrains Mono', monospace; }

/* ── Campaign block ───────────────────────────────────────────────────────── */
.campaign-block {
    background: #FFFFFF; border-radius: 14px; border: 1px solid #E2E5EC;
    box-shadow: 0 1px 3px rgba(0,0,0,.04); padding: 1.6rem 1.8rem; margin-bottom: 1.4rem;
}
.campaign-chip {
    display: inline-flex; align-items: center; gap: .4rem;
    font-size: .65rem; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; padding: .28rem .85rem; border-radius: 6px; margin-bottom: .8rem;
}
.chip-sports  { background: #EEF2FF; color: #0047CC; border: 1px solid #C7D2FE; }
.chip-holiday { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
.campaign-name { font-size: 1.3rem; font-weight: 800; color: #0A0E1A; letter-spacing: -.02em; margin: 0 0 .2rem; }
.campaign-desc { font-size: .78rem; color: #9CA3AF; }

/* ── Agent section ────────────────────────────────────────────────────────── */
.agent-section {
    background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E5EC;
    box-shadow: 0 1px 3px rgba(0,0,0,.04); padding: 1.4rem 1.6rem; margin-bottom: 1rem;
}
.agent-name-header { font-size: 1.05rem; font-weight: 800; color: #0A0E1A; margin-bottom: .2rem; }
.agent-camp-chip   {
    display: inline-flex; align-items: center; gap: .3rem;
    font-size: .62rem; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; padding: .18rem .65rem; border-radius: 6px; margin-bottom: .8rem;
}

/* ── Leaderboard ──────────────────────────────────────────────────────────── */
.leaderboard-row {
    background: #FFFFFF; border-radius: 10px; border: 1px solid #E2E5EC;
    padding: .85rem 1.3rem; margin-bottom: .45rem;
    display: flex; align-items: center; gap: 1rem;
    transition: box-shadow .18s, transform .15s;
}
.leaderboard-row:hover { box-shadow: 0 4px 14px rgba(10,14,26,.08); transform: translateY(-1px); }
.rank-badge {
    width: 34px; height: 34px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: .82rem; font-weight: 800; flex-shrink: 0;
}
.rank-1 { background: #C9A035; color: #0A0E1A; }
.rank-2 { background: #E5E7EB; color: #374151; }
.rank-3 { background: #FEF3C7; color: #92400E; }
.rank-n { background: #F9FAFB; color: #9CA3AF; }
.lb-agent { font-size: .92rem; font-weight: 700; color: #0A0E1A; }
.lb-camp  { font-size: .62rem; font-weight: 600; text-transform: uppercase; letter-spacing: .07em; color: #9CA3AF; }
.lb-bar-bg   { background: #F3F4F6; border-radius: 999px; height: 5px; overflow: hidden; }
.lb-bar-fill { height: 5px; border-radius: 999px; }
.lb-pct  { font-size: .92rem; font-weight: 800; min-width: 52px; text-align: right; font-family: 'JetBrains Mono', monospace; }

/* ── Admin ────────────────────────────────────────────────────────────────── */
.admin-box       { background: #F9FAFB; border: 1px solid #E2E5EC; border-radius: 10px; padding: 1.1rem 1.4rem; margin-bottom: 1.4rem; }
.admin-box-title { font-size: .72rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #C9A035; margin-bottom: .8rem; }

/* ── Misc ─────────────────────────────────────────────────────────────────── */
.dash-divider { border: none; border-top: 1px solid #E2E5EC; margin: 1.6rem 0; }
.empty-state  { text-align: center; padding: 5rem 2rem; }
.empty-icon   { font-size: 3rem; margin-bottom: 1rem; }
.empty-title  { font-size: 1.05rem; font-weight: 700; color: #6B7280; margin-bottom: .4rem; }
.empty-sub    { font-size: .82rem; color: #9CA3AF; }

section[data-testid="stFileUploadDropzone"] {
    background: #FFFFFF !important; border: 2px dashed #E2E5EC !important; border-radius: 10px !important;
}
.stButton > button {
    background: #0A0E1A !important; color: #C9A035 !important;
    font-weight: 700 !important; border: none !important; border-radius: 7px !important;
}
.stButton > button:hover { background: #1a2035 !important; }
div[data-testid="metric-container"] { display: none; }
</style>
"""

def inject_css():
    import streamlit as st
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
