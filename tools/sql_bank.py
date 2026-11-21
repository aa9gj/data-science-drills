# Builds the SQL problem bank from pgexercises (CC BY-SA 3.0, Alisdair Owens), ported to SQLite.
import json, re, sqlite3

qs = {q['file'][9:-3]: q for q in json.load(open('pg_questions.json'))}

# file -> (skill, level)
MAP = {
 # Retrieving data
 'selectall':('retrieve',1),'selectspecific':('retrieve',1),'where':('retrieve',1),'where2':('retrieve',1),
 'where3':('retrieve',2),'where4':('retrieve',2),'classify':('retrieve',2),'date':('retrieve',2),'unique':('retrieve',2),
 'union':('retrieve',3),'agg':('retrieve',3),'agg2':('retrieve',3),
 # Joins & subqueries
 'simplejoin':('joins',1),'simplejoin2':('joins',1),'self':('joins',2),'self2':('joins',2),'threejoin':('joins',2),
 'threejoin2':('joins',3),'sub':('joins',3),'tjsub':('joins',3),
 # Aggregation
 'count':('agg',1),'count2':('agg',1),'count3':('agg',1),'fachours':('agg',1),'members1':('agg',1),
 'fachoursbymonth':('agg',2),'fachoursbymonth2':('agg',2),'fachours1a':('agg',2),'facrev':('agg',2),'fachours3':('agg',2),
 'facrev2':('agg',3),'fachours2':('agg',3),'fachoursbymonth3':('agg',3),'nbooking':('agg',3),
 # Window functions & advanced
 'countmembers':('window',1),'nummembers':('window',1),'fachours4':('window',2),'rankmembers':('window',2),'facrev3':('window',2),
 'classify@aggregates':('window',3),'payback':('window',3),'rollingavg':('window',3),
 'getupward':('window',2),'getdownward':('window',3),'getupwardall':('window',3),
 # Text
 'concat':('text',1),'like':('text',1),'case':('text',1),'reg':('text',2),'pad':('text',2),'substr':('text',2),'translate':('text',3),
 # Dates
 'extract':('dates',1),'bookingspermonth':('dates',1),'interval2':('dates',2),'endtimes':('dates',2),'daysremaining':('dates',2),
 'series':('dates',3),'utilisationpermonth':('dates',3),
}

# SQLite ports for PostgreSQL-specific questions: file -> dict(query=..., question=optional new text, note=...)
PORTS = {
 'fachoursbymonth2': dict(query="""select facid, cast(strftime('%m', starttime) as integer) as month, sum(slots) as "Total Slots"
  from bookings
  where strftime('%Y', starttime) = '2012'
  group by facid, month
order by facid, month;""", note="SQLite has no <code>EXTRACT</code>; use <code>strftime('%m', starttime)</code> and cast it to an integer."),
 'fachoursbymonth3': dict(query="""select facid, month, slots from (
  select facid, cast(strftime('%m', starttime) as integer) as month, sum(slots) as slots
    from bookings where starttime >= '2012-01-01' and starttime < '2013-01-01'
    group by facid, month
  union all
  select facid, null, sum(slots)
    from bookings where starttime >= '2012-01-01' and starttime < '2013-01-01'
    group by facid
  union all
  select null, null, sum(slots)
    from bookings where starttime >= '2012-01-01' and starttime < '2013-01-01'
)
order by facid is null, facid, month is null, month;""",
  note="SQLite has no <code>ROLLUP</code>. Build the subtotal and grand-total rows yourself with <code>UNION ALL</code>, and sort NULLs last with <code>ORDER BY facid IS NULL, facid, month IS NULL, month</code>."),
 'fachours3': dict(query="""select facs.facid, facs.name,
  printf('%.2f', sum(bks.slots)/2.0) as "Total Hours"
  from bookings bks
  inner join facilities facs on facs.facid = bks.facid
  group by facs.facid, facs.name
order by facs.facid;""", note="In SQLite, format numbers with <code>printf('%.2f', x)</code>."),
 'rollingavg': dict(query="""with recursive dates(d) as (
  select '2012-08-01'
  union all
  select date(d, '+1 day') from dates where d < '2012-08-31'
)
select d as date,
  (select sum(case when memid = 0 then slots * facs.guestcost else slots * membercost end)
     from bookings bks inner join facilities facs on bks.facid = facs.facid
     where bks.starttime > date(d, '-14 days') and bks.starttime < date(d, '+1 day')
  ) / 15.0 as revenue
from dates
order by d;""", note="SQLite has no <code>generate_series</code>. Generate the dates with a recursive CTE and shift them with <code>date(d, '-14 days')</code>."),
 'reg': dict(query="""select memid, telephone from members
where telephone like '%(%' or telephone like '%)%'
order by memid;""", note="SQLite has no regex operator by default; <code>LIKE '%(%'</code> does the job here."),
 'pad': dict(query="""select substr('00000' || zipcode, -5) as zip from members order by zip;""",
  note="SQLite has no <code>LPAD</code>. Prepend zeros and keep the last five characters with <code>substr('00000' || zipcode, -5)</code>, or use <code>printf('%05d', zipcode)</code>."),
 'translate': dict(query="""select memid,
  replace(replace(replace(replace(telephone, '-', ''), '(', ''), ')', ''), ' ', '') as telephone
from members
order by memid;""", note="SQLite has no <code>TRANSLATE</code>. Nest <code>replace()</code> calls, one per character to remove."),
 'extract': dict(query="""select cast(strftime('%d', '2012-08-31') as integer) as day;""",
  question="Get the day of the month from the timestamp <code>'2012-08-31'</code> as an integer.",
  note="SQLite stores timestamps as text. <code>strftime('%d', ts)</code> pulls out the day as text; cast it to an integer."),
 'interval2': dict(query="""select cast(round((julianday('2012-09-02 00:00:00') - julianday('2012-08-31 01:00:00')) * 86400) as integer) as seconds;""",
  question="Work out the number of seconds between the timestamps <code>'2012-08-31 01:00:00'</code> and <code>'2012-09-02 00:00:00'</code>.",
  note="<code>julianday()</code> converts a timestamp to a number of days. Subtract two of them and multiply by 86,400."),
 'endtimes': dict(query="""select starttime, datetime(starttime, '+' || (slots * 30) || ' minutes') as endtime
from bookings
order by endtime desc, starttime desc
limit 10;""", note="Add minutes with <code>datetime(starttime, '+90 minutes')</code>; build the modifier string with <code>||</code>."),
 'bookingspermonth': dict(query="""select strftime('%Y-%m', starttime) as month, count(*) as count
from bookings
group by month
order by month;""", question="Return a count of bookings for each month (formatted like <code>2012-07</code>), sorted by month.",
  note="<code>strftime('%Y-%m', starttime)</code> truncates a timestamp to its month."),
 'daysremaining': dict(query="""select cast(julianday(date('2012-02-11 01:00:00', 'start of month', '+1 month')) - julianday(date('2012-02-11 01:00:00')) as integer) as remaining;""",
  question="For a given timestamp, work out the number of days remaining in the month. The current day counts as a whole day, regardless of the time. Use <code>'2012-02-11 01:00:00'</code> as the example timestamp and return a single integer.",
  note="<code>date(ts, 'start of month', '+1 month')</code> gives the first day of next month. Subtract <code>julianday</code> values to count days."),
 'series': dict(query="""with recursive days(d) as (
  select '2012-10-01'
  union all
  select date(d, '+1 day') from days where d < '2012-10-31'
)
select d from days;""", question="Produce a list of all the dates in October 2012, one row per date.",
  note="Use a recursive CTE that starts at <code>'2012-10-01'</code> and adds a day with <code>date(d, '+1 day')</code> until the 31st."),
 'utilisationpermonth': dict(query="""select name, month, round(100.0 * slots / (25 * days), 1) as utilisation
from (
  select facs.name as name,
         strftime('%Y-%m', starttime) as month,
         sum(slots) as slots,
         max(cast(julianday(date(starttime, 'start of month', '+1 month')) - julianday(date(starttime, 'start of month')) as integer)) as days
  from bookings bks
  inner join facilities facs on bks.facid = facs.facid
  group by facs.facid, month
)
order by name, month;""", question="Work out the utilisation percentage for each facility by month (formatted like <code>2012-07</code>), sorted by name and month, rounded to 1 decimal place. Opening time is 8am and closing time is 8.30pm, so there are 25 half-hour slots a day. Treat every month as a full month.",
  note="Days in a month: <code>julianday(date(ts,'start of month','+1 month')) - julianday(date(ts,'start of month'))</code>."),
 'getdownward': dict(query="""with recursive recommendeds(memid) as (
  select memid from members where recommendedby = 1
  union all
  select mems.memid
    from recommendeds recs
    inner join members mems on mems.recommendedby = recs.memid
)
select recs.memid, mems.firstname, mems.surname
from recommendeds recs
inner join members mems on recs.memid = mems.memid
order by recs.memid;"""),
}
SKIP = {'timestamp', 'interval', 'daysinmonth'}  # depend on PostgreSQL's timestamp/interval types

def html(s):
    s = s.replace('<c>', '<code>').replace('</c>', '</code>')
    s = re.sub(r'<a [^>]*>(.*?)</a>', r'\1', s, flags=re.S)
    return s.strip()

def strip_cd(q): return re.sub(r'\bcd\.', '', q)

con = sqlite3.connect(':memory:')
con.executescript(strip_cd(open('club.sql').read()))

out = []
for key, q in qs.items():
    if key in SKIP: continue
    mkey = 'classify@aggregates' if (key == 'classify' and q['cat'] == 'aggregates') else key
    if mkey not in MAP: print('UNMAPPED', key, q['cat']); continue
    skill, level = MAP[mkey]
    port = PORTS.get(key, {})
    query = port.get('query') or strip_cd(q['QUERY']).strip()
    rows = con.execute(query).fetchall()
    assert rows, key
    explain = html(q.get('ANSWER', ''))
    if port.get('note'):
        explain = f"<p><b>SQLite note.</b> {port['note']}</p>" + (explain if key not in ('extract','interval2','bookingspermonth','daysremaining','series','utilisationpermonth','endtimes','rollingavg','reg','pad','translate','fachours3','fachoursbymonth2','fachoursbymonth3') else '')
    hint = html(q.get('HINT', ''))
    if port.get('note'): hint = (hint + ' ' if key not in ('extract','interval2','bookingspermonth','daysremaining','series','utilisationpermonth','endtimes','rollingavg') else '') + port['note']
    out.append(dict(
        id='sql-' + ('agg-classify' if mkey == 'classify@aggregates' else key), lang='sql', skill=skill, level=level,
        title=q['QUESTIONNAME'].strip(), body='<p>' + html(port.get('question') or q['QUESTION']) + '</p>',
        starter='-- Tables: members, facilities, bookings\n', hint=hint, solution=query.strip(),
        explain=explain, ordered=q.get('SORTED', '0').strip() == '1', src='pgx', nrows=len(rows)))

order = {'retrieve':0,'joins':1,'agg':2,'window':3,'text':4,'dates':5}
out.sort(key=lambda p: (order[p['skill']], p['level']))
json.dump(out, open('bank_sql.json', 'w'), indent=1)
from collections import Counter
print(len(out), Counter((p['skill'], p['level']) for p in out))
