# Helper (needs a checkout of github.com/AlisdairO/pgexercises with its question folders copied to src/pg/): parses the .ex question files into pg_questions.json and test-runs their queries on SQLite.
import re, glob, json, sqlite3
def parse(f):
    t=open(f).read()
    parts=re.split(r'^\|([A-Z]+)\|\s*$',t,flags=re.M)
    d={}
    for i in range(1,len(parts),2): d[parts[i]]=parts[i+1].strip()
    return d
cats=['basic','joins','aggregates','string','date','recursive']
qs=[]
for c in cats:
    for f in sorted(glob.glob(f'src/pg/{c}/*.ex')):
        d=parse(f); d['cat']=c; d['file']=f.split('/')[-1]; qs.append(d)
con=sqlite3.connect(':memory:'); con.execute("ATTACH ':memory:' AS cd"); con.executescript(open('club.sql').read())
ok=0
for q in qs:
    try:
        rows=con.execute(q['QUERY']).fetchall(); q['ok']=True; q['n']=len(rows); ok+=1
    except Exception as e:
        q['ok']=False; q['errmsg']=str(e)[:70]
json.dump(qs,open('pg_questions.json','w'),indent=1)
print('ok',ok,'of',len(qs))
for q in qs: print(('OK ' if q['ok'] else 'ERR'), q['cat'][:5], q['file'][9:], q.get('n',''), q.get('errmsg',''))
