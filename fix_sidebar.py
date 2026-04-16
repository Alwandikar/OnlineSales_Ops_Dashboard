import re, os

# Fix styles.py — remove all problematic sidebar CSS
styles_path = "utils/styles.py"
content = open(styles_path).read()
new_sidebar = '''/* ── Sidebar ─────────────────────────────────────────────────────────────── */
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

'''
result = re.sub(r'/\* ── Sidebar.*?(?=/\* ── Tabs)', new_sidebar, content, flags=re.DOTALL)
open(styles_path, 'w').write(result)
print("styles.py fixed")

# Fix app.py — set expanded, remove JS injection
for f in ["app.py", "pages/2_Disposition_Detail.py"]:
    if not os.path.exists(f):
        continue
    c = open(f).read()
    c = c.replace('initial_sidebar_state="collapsed"', 'initial_sidebar_state="expanded"')
    # Remove the JS block if present
    js_start = c.find('\n# Force sidebar open via JS')
    js_end   = c.find('unsafe_allow_html=True)\n', js_start)
    if js_start > 0 and js_end > 0:
        c = c[:js_start] + c[js_end + len('unsafe_allow_html=True)\n'):]
    open(f, 'w').write(c)
    print(f"{f} fixed")

print("All done — run: git add . && git commit -m 'Fix sidebar' && git push")
