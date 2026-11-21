# Builds the single-page app from the template parts and the question banks.
# Usage: OUT=.. python3 assemble2.py   (add ARTIFACT=1 to also write the body-only page.html)
import json, os, re, shutil
OUT = os.environ.get('OUT', 'out')
t = open('template.html').read()
css = t[t.index('<style>'):t.index('</style>')]
css = css.replace('/* Layout: three-pane workbench', '/* Layout: three-pane workbench')
extra = """
.toprow{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.settings{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin-bottom:14px;display:grid;gap:10px}
.settings h2{margin:0 0 6px;font-size:1.05rem}
.settings p{margin:0 0 8px;max-width:80ch}
.settings a{color:var(--accent)}
.keyrow{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.keyrow label{font-weight:600;font-size:.88rem}
.keyrow input{font:.86rem var(--mono);padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);min-width:0;flex:1 1 220px}
.verdict.info{background:var(--sunk);color:var(--fg)}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
select.ghost{padding:6px 8px;background:var(--panel)}
footer p{margin:0}
.mixbar{margin:0 0 10px}
.mixrow{display:grid;grid-template-columns:1fr auto;gap:4px}
.mixbtn{border:1px solid var(--accent);background:var(--accent);color:var(--accent-fg);border-radius:6px;padding:7px 8px;font-weight:600;font-size:.84rem;text-align:left}
.mixbtn.alt{background:var(--panel);color:var(--accent)}
.mixhelp{margin:6px 2px 0;font-size:.76rem;color:var(--muted)}
.mixon{display:grid;gap:4px;padding:8px 10px;border:1px solid var(--accent);border-radius:8px}
.mixon span{font-size:.8rem;color:var(--muted);font-variant-numeric:tabular-nums}
.mixon .ghost{justify-self:start;padding:4px 9px;font-size:.8rem}
.mixnote{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;padding:7px 10px;margin-bottom:12px;border-radius:8px;background:var(--sunk);font:600 .78rem var(--mono);color:var(--accent);font-variant-numeric:tabular-nums}
.mixnote .ghost{padding:3px 9px;font:inherit;font-weight:500;font-size:.78rem}
.ok{color:var(--pass)} .bad{color:var(--fail)}
"""
harness = t[t.index('const PY_HARNESS = String.raw`') + len('const PY_HARNESS = String.raw`'):]
harness = harness[:harness.index('\n`;')]
add_cmp = """    if isinstance(b, np.ndarray):
        try:
            a = np.asarray(a)
        except Exception:
            return f'Expected an array, but your value is a {type(a).__name__}.'
        if a.shape != b.shape:
            return f'Expected shape {b.shape}, but yours is {a.shape}.'
        try:
            same = bool(np.allclose(a.astype(float), b.astype(float), rtol=1e-4, atol=1e-6, equal_nan=True))
        except Exception:
            same = bool(np.array_equal(a, b))
        return None if same else f'Expected {np.array2string(b, threshold=50)}, got {np.array2string(a, threshold=50)}.'
    if isinstance(b, dict):
        if not isinstance(a, dict) or set(a) != set(b):
            return f'Expected {b!r}, got {a!r}.'
        for k in b:
            m = _cmp(a[k], b[k], True)
            if m: return f'{k}: {m}'
        return None
    if isinstance(b, (bool, np.bool_)):"""
assert "    if isinstance(b, (bool, np.bool_)):" in harness
harness = harness.replace("    if isinstance(b, (bool, np.bool_)):", add_cmp, 1)
old_list = "    if isinstance(b, (list, tuple)):\n        if not isinstance(a, (list, tuple))"
assert old_list in harness
harness = harness.replace(old_list, "    if isinstance(b, (list, tuple)):\n        if isinstance(a, np.ndarray): a = a.tolist()\n        if not isinstance(a, (list, tuple))", 1)
script = open('part_script.js').read().replace('/*__PY_HARNESS__*/', harness)
assert '`' not in harness
bank = []
for f in ['bank_sql.json', 'bank_sql_de.json', 'bank_py.json', 'bank_py_ml.json', 'bank_r.json', 'bank_sas.json']:
    bank += json.load(open(f))
for p in bank:
    p.pop('nrows', None)
    if p.get('check') is None and p['lang'] == 'sql': p.pop('check', None)
ids = [p['id'] for p in bank]; assert len(ids) == len(set(ids)), 'duplicate ids'
data = json.dumps(bank, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
head = '<title>Data Science Drills</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">\n'
page = head + css + extra + '</style>\n\n' + open('part_body.html').read() + '\n<script type="application/json" id="bankData">' + data + '</script>\n<script>\n' + script + '</script>\n'
os.makedirs(os.path.join(OUT, 'data'), exist_ok=True)
if os.environ.get('ARTIFACT'):
    open(os.path.join(OUT, 'page.html'), 'w').write(page)   # body-only page for a claude.ai artifact
# standalone index.html for GitHub Pages: same page in a full HTML document
open(os.path.join(OUT, 'index.html'), 'w').write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="description" content="Adaptive, in-browser practice problems for SQL, Python (pandas, scikit-learn), R and SAS.">\n<style>[hidden]{display:none!important}body{margin:0}</style>\n</head>\n<body>\n' + page + '</body>\n</html>\n')
open(os.path.join(OUT, 'data', 'club.sql.txt'), 'w').write(re.sub(r'\bcd\.', '', open('club.sql').read()))
shutil.copy('shop.sql', os.path.join(OUT, 'data', 'shop.sql.txt'))
shutil.copy('gapminder.csv', os.path.join(OUT, 'data', 'gapminder.csv'))
from collections import Counter
print(len(bank), 'problems', dict(Counter(p['lang'] for p in bank)), len(page)//1024, 'KB')
