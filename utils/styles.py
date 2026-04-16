# utils/styles.py — iOS dark theme

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ────────────────────────────────────────────────────────────────── */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #FFFFFF !important;
}
.stApp { background: #000000 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 1.8rem 3rem !important; max-width: 1300px !important; }

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #1C1C1E;
    border-right: 1px solid #38383A;
}
[data-testid="stSidebarNav"] a {
    color: #8E8E93;
    font-weight: 500;
    border-radius: 8px;
}
[data-testid="stSidebarNav"] a:hover { color: #FFFFFF; }
[data-testid="stSidebarNav"] a[aria-selected="true"] { color: #0A84FF; }

/* ── Tabs ────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #1C1C1E !important;
    border-radius: 10px !important;
    padding: 3px !important;
    gap: 2px !important;
    border: 1px solid #38383A !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #8E8E93 !important;
    font-weight: 600 !important;
    font-size: .85rem !important;
    border-radius: 8px !important;
    padding: .45rem 1.4rem !important;
    border: none !important;
}
.stTabs [aria-selected="true"] { background: #2C2C2E !important; color: #FFFFFF !important; }
.stTabs [data-baseweb="tab-border"], .stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ── Date filter bar ─────────────────────────────────────────────────────── */
.date-filter-bar {
    background: #1C1C1E;
    border: 1px solid #38383A;
    border-radius: 12px;
    padding: .8rem 1.2rem;
    margin-bottom: 1.2rem;
}

/* ── Date banner ─────────────────────────────────────────────────────────── */
.date-banner {
    background: #1C1C1E;
    border: 1px solid #38383A;
    border-left: 3px solid #0A84FF;
    border-radius: 10px;
    padding: .6rem 1rem;
    margin-bottom: 1.2rem;
    font-size: .82rem;
    color: #8E8E93;
}
.date-banner strong { color: #0A84FF; }

/* ── Section label ───────────────────────────────────────────────────────── */
.section-label {
    font-size: .65rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #636366;
    margin: 1.8rem 0 .8rem;
}

/* ── KPI cards ───────────────────────────────────────────────────────────── */
.kpi-card {
    background: #1C1C1E;
    border-radius: 14px;
    padding: 1.2rem 1.4rem 1rem;
    border: 1px solid #38383A;
    position: relative;
    overflow: hidden;
    transition: background .15s;
    height: 100%;
}
.kpi-card:hover { background: #2C2C2E; }
.kpi-accent { position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 14px 14px 0 0; }
.kpi-label  { font-size: .65rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: #636366; margin-bottom: .4rem; }
.kpi-value  { font-size: 2rem; font-weight: 700; color: #FFFFFF; letter-spacing: -.03em; line-height: 1.1; }
.kpi-value-blue  { color: #0A84FF; }
.kpi-value-green { color: #30D158; }
.kpi-value-red   { color: #FF453A; }
.kpi-value-gold  { color: #FFD60A; }
.kpi-sub    { font-size: .7rem; color: #636366; margin-top: .35rem; }
.kpi-icon   { position: absolute; top: 1rem; right: 1.2rem; font-size: 1.2rem; opacity: .15; }

/* ── Disposition cards ───────────────────────────────────────────────────── */
.disp-card {
    background: #1C1C1E;
    border-radius: 12px;
    padding: .9rem 1rem;
    border: 1px solid #38383A;
    position: relative;
    overflow: hidden;
    height: 100%;
    transition: background .15s;
}
.disp-card:hover { background: #2C2C2E; }
.disp-accent { position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 12px 12px 0 0; }
.disp-label  { font-size: .6rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #636366; }
.disp-count  { font-size: 1.7rem; font-weight: 700; color: #FFFFFF; letter-spacing: -.02em; line-height: 1.1; }
.disp-pct    { font-size: .75rem; font-weight: 500; color: #8E8E93; margin-top: .1rem; font-family: 'JetBrains Mono', monospace; }

/* ── Campaign block ──────────────────────────────────────────────────────── */
.campaign-block {
    background: #1C1C1E;
    border-radius: 14px;
    border: 1px solid #38383A;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
}
.campaign-chip {
    display: inline-flex; align-items: center; gap: .35rem;
    font-size: .65rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase;
    padding: .22rem .75rem; border-radius: 999px; margin-bottom: .7rem;
}
.chip-sports  { background: #0A84FF22; color: #0A84FF; border: 1px solid #0A84FF44; }
.chip-holiday { background: #30D15822; color: #30D158; border: 1px solid #30D15844; }
.campaign-name { font-size: 1.2rem; font-weight: 700; color: #FFFFFF; margin: 0 0 .15rem; }
.campaign-desc { font-size: .75rem; color: #636366; }

/* ── Agent section ───────────────────────────────────────────────────────── */
.agent-section {
    background: #1C1C1E;
    border-radius: 12px;
    border: 1px solid #38383A;
    padding: 1.2rem 1.4rem;
    margin-bottom: .9rem;
}
.agent-name { font-size: 1rem; font-weight: 700; color: #FFFFFF; margin-bottom: .15rem; }
.agent-chip {
    display: inline-flex; align-items: center; gap: .3rem;
    font-size: .6rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase;
    padding: .18rem .6rem; border-radius: 999px; margin-bottom: .7rem;
}

/* ── Misc ────────────────────────────────────────────────────────────────── */
.divider { border: none; border-top: 1px solid #38383A; margin: 1.5rem 0; }
.empty-state { text-align: center; padding: 5rem 2rem; }
.empty-icon  { font-size: 3rem; margin-bottom: 1rem; }
.empty-title { font-size: 1rem; font-weight: 600; color: #8E8E93; margin-bottom: .3rem; }
.empty-sub   { font-size: .82rem; color: #636366; }

/* ── Streamlit widget overrides ──────────────────────────────────────────── */
.stTextInput input, .stDateInput input {
    background: #2C2C2E !important;
    color: #FFFFFF !important;
    border: 1px solid #48484A !important;
    border-radius: 8px !important;
}
.stButton > button {
    background: #0A84FF !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: .85rem !important;
}
.stButton > button:hover { background: #0077ED !important; }
section[data-testid="stFileUploadDropzone"] {
    background: #2C2C2E !important;
    border: 2px dashed #48484A !important;
    border-radius: 10px !important;
}
.streamlit-expanderHeader {
    background: #1C1C1E !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
}
div[data-testid="metric-container"] { display: none !important; }
</style>
"""

def inject_css():
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
