# Helper (needs src/pg/clubdata.sql from github.com/AlisdairO/pgexercises): converts the PostgreSQL club database dump into SQLite statements (club.sql).
import re, json, sys, glob
src=open('src/pg/clubdata.sql').read()
def copyblock(name):
    m=re.search(r'COPY '+name+r' \(([^)]*)\) FROM stdin;\n(.*?)\n\\\.',src,re.S)
    cols=[c.strip() for c in m.group(1).split(',')]
    rows=[l.split('\t') for l in m.group(2).split('\n') if l]
    return cols,rows
schema={
 'members':"memid INTEGER PRIMARY KEY, surname TEXT NOT NULL, firstname TEXT NOT NULL, address TEXT NOT NULL, zipcode INTEGER NOT NULL, telephone TEXT NOT NULL, recommendedby INTEGER, joindate TEXT NOT NULL",
 'facilities':"facid INTEGER PRIMARY KEY, name TEXT NOT NULL, membercost REAL NOT NULL, guestcost REAL NOT NULL, initialoutlay REAL NOT NULL, monthlymaintenance REAL NOT NULL",
 'bookings':"bookid INTEGER PRIMARY KEY, facid INTEGER NOT NULL, memid INTEGER NOT NULL, starttime TEXT NOT NULL, slots INTEGER NOT NULL"}
num={'memid','zipcode','recommendedby','facid','membercost','guestcost','initialoutlay','monthlymaintenance','bookid','slots'}
out=[]
for t in ['members','facilities','bookings']:
    cols,rows=copyblock(t)
    out.append(f"CREATE TABLE cd.{t} ({schema[t]});")
    vals=[]
    for r in rows:
        v=[]
        for c,x in zip(cols,r):
            if x=='\\N': v.append('NULL')
            elif c in num: v.append(x)
            else: v.append("'"+x.replace("'","''")+"'")
        vals.append('('+','.join(v)+')')
    for i in range(0,len(vals),500):
        out.append(f"INSERT INTO cd.{t} ({','.join(cols)}) VALUES "+','.join(vals[i:i+500])+';')
sql='\n'.join(out)
open('club.sql','w').write(sql)
print(len(sql), {t:len(copyblock(t)[1]) for t in ['members','facilities','bookings']})
