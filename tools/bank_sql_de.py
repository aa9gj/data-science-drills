# Advanced analytics and data engineering SQL problems (original), on the synthetic "shop" warehouse.
# Each solution is run here with SQLite; state-changing problems are checked with a follow-up query.
import json, sqlite3

P = []
def add(id, skill, level, title, body, solution, hint, ordered=True, check=None, starter=None):
    P.append(dict(id='sqlx-' + id, lang='sql', db='shop', skill=skill, level=level, title=title,
                  body=body, starter=starter or '-- Write your SQL below\n', solution=solution.strip(), hint=hint,
                  ordered=ordered, check=check, src='own'))

REV = "Revenue means the sum of <code>quantity × price</code> from <code>order_items</code> joined to <code>products</code>, for orders with <code>status = 'completed'</code>."
STATE = '<p class="note">This task changes the database. After your SQL runs, the checker runs <code>{q}</code> and compares the result with the expected state.</p>'

# ---------------- Advanced analytics
add('rev-month','adv',1,'Monthly revenue',f'<p>Return each <code>month</code> (formatted <code>YYYY-MM</code>) and its <code>revenue</code> rounded to 2 decimals, oldest month first.</p><p class="note">{REV}</p>',
"""select strftime('%Y-%m', o.order_date) as month, round(sum(oi.quantity * p.price), 2) as revenue
from orders o
join order_items oi on oi.order_id = o.order_id
join products p on p.product_id = oi.product_id
where o.status = 'completed'
group by month
order by month;""",'Join the three tables, filter completed orders, and group by <code>strftime(\'%Y-%m\', order_date)</code>.')
add('top5','adv',1,'Top five customers',f'<p>Return the <code>name</code> and <code>revenue</code> (rounded to 2) of the five customers with the highest revenue. Break ties by name.</p><p class="note">{REV}</p>',
"""select c.name, round(sum(oi.quantity * p.price), 2) as revenue
from customers c
join orders o on o.customer_id = c.customer_id
join order_items oi on oi.order_id = o.order_id
join products p on p.product_id = oi.product_id
where o.status = 'completed'
group by c.customer_id, c.name
order by revenue desc, c.name
limit 5;""",'Group by customer, order by revenue descending, then <code>LIMIT 5</code>.')
add('best-product','adv',2,'Best seller in each category','<p>For completed orders, find the product with the most units sold in each category. If two products tie, pick the lower <code>product_id</code>. Return <code>category</code>, <code>name</code>, <code>units</code>, sorted by category.</p>',
"""with u as (
  select p.category, p.product_id, p.name, sum(oi.quantity) as units
  from order_items oi
  join orders o on o.order_id = oi.order_id
  join products p on p.product_id = oi.product_id
  where o.status = 'completed'
  group by p.product_id
), r as (
  select *, row_number() over (partition by category order by units desc, product_id) as rn from u
)
select category, name, units from r where rn = 1 order by category;""",'Aggregate units per product in a CTE, then <code>ROW_NUMBER() OVER (PARTITION BY category ORDER BY units DESC, product_id)</code> and keep row 1.')
add('date-spine','adv',2,'Revenue for every day',f'<p>Return one row for <b>every</b> day in June 2025 with columns <code>day</code> and <code>revenue</code> (rounded to 2). Days without orders must show 0.</p><p class="note">{REV}</p>',
"""with recursive days(d) as (
  select '2025-06-01'
  union all
  select date(d, '+1 day') from days where d < '2025-06-30'
), rev as (
  select o.order_date as d, sum(oi.quantity * p.price) as revenue
  from orders o
  join order_items oi on oi.order_id = o.order_id
  join products p on p.product_id = oi.product_id
  where o.status = 'completed'
  group by o.order_date
)
select days.d as day, round(coalesce(rev.revenue, 0), 2) as revenue
from days left join rev on rev.d = days.d
order by day;""",'Build a date spine with a recursive CTE, then <code>LEFT JOIN</code> daily revenue onto it and <code>COALESCE</code> missing days to 0.')
add('pivot','adv',2,'Pivot statuses into columns','<p>For orders placed in 2025, return one row per <code>month</code> (<code>YYYY-MM</code>) with three columns counting orders by status: <code>completed</code>, <code>returned</code>, <code>cancelled</code>. Oldest month first.</p>',
"""select strftime('%Y-%m', order_date) as month,
       sum(status = 'completed') as completed,
       sum(status = 'returned') as returned,
       sum(status = 'cancelled') as cancelled
from orders
where order_date >= '2025-01-01'
group by month
order by month;""",'Conditional aggregation: in SQLite a comparison is 1 or 0, so <code>SUM(status = \'completed\')</code> counts matches. <code>SUM(CASE WHEN ... THEN 1 ELSE 0 END)</code> works everywhere.')
add('pareto','adv',2,'Cumulative revenue share',f'<p>Rank customers by revenue (highest first, ties by name) and return <code>name</code>, <code>revenue</code> (rounded to 2), and <code>cum_pct</code>: the running share of total revenue in percent, rounded to 1. The last row should be 100.0.</p><p class="note">{REV}</p>',
"""with r as (
  select c.name, sum(oi.quantity * p.price) as revenue
  from customers c
  join orders o on o.customer_id = c.customer_id
  join order_items oi on oi.order_id = o.order_id
  join products p on p.product_id = oi.product_id
  where o.status = 'completed'
  group by c.customer_id, c.name
)
select name, round(revenue, 2) as revenue,
       round(100.0 * sum(revenue) over (order by revenue desc, name rows unbounded preceding)
             / sum(revenue) over (), 1) as cum_pct
from r
order by revenue desc, name;""",'A running total is <code>SUM(x) OVER (ORDER BY ... ROWS UNBOUNDED PRECEDING)</code>; the grand total is <code>SUM(x) OVER ()</code>.')
add('median','adv',3,'Median order value by segment','<p>An order\'s value is the sum of <code>quantity × price</code> over its items. For completed orders, return each customer <code>segment</code> and its <code>median_value</code> (rounded to 2), sorted by segment. SQLite has no MEDIAN function.</p>',
"""with v as (
  select c.segment, o.order_id, sum(oi.quantity * p.price) as value
  from orders o
  join customers c on c.customer_id = o.customer_id
  join order_items oi on oi.order_id = o.order_id
  join products p on p.product_id = oi.product_id
  where o.status = 'completed'
  group by o.order_id
), r as (
  select segment, value,
         row_number() over (partition by segment order by value) as rn,
         count(*) over (partition by segment) as n
  from v
)
select segment, round(avg(value), 2) as median_value
from r
where rn in ((n + 1) / 2, (n + 2) / 2)
group by segment
order by segment;""",'Number the values within each segment and count them. The median is the middle row, or the average of the two middle rows: <code>rn IN ((n+1)/2, (n+2)/2)</code> with integer division.')
add('cohort','adv',3,'Signup cohort conversion','<p>Group customers by signup month (<code>cohort</code>, <code>YYYY-MM</code>). For each cohort return <code>customers</code>, <code>converted</code> (customers with a completed order within 90 days of signing up) and <code>pct</code> (converted as a percent, rounded to 1). Oldest cohort first.</p>',
"""with f as (
  select c.customer_id, strftime('%Y-%m', c.signup_date) as cohort,
         exists (select 1 from orders o
                 where o.customer_id = c.customer_id and o.status = 'completed'
                   and julianday(o.order_date) - julianday(c.signup_date) <= 90) as converted
  from customers c
)
select cohort, count(*) as customers, sum(converted) as converted,
       round(100.0 * sum(converted) / count(*), 1) as pct
from f
group by cohort
order by cohort;""",'Flag each customer first (an <code>EXISTS</code> subquery returns 1 or 0), then aggregate the flags by cohort.')
add('funnel','adv',3,'Ordered conversion funnel','<p>Using <code>events</code>, count distinct users at each funnel step. A user counts as <code>viewed</code> if they have any view; as <code>carted</code> only if they added to cart <i>after</i> their first view; as <code>purchased</code> only if they purchased <i>after</i> their first qualifying add-to-cart. Return one row: <code>viewed</code>, <code>carted</code>, <code>purchased</code>.</p>',
"""with v as (
  select user_id, min(event_time) as t from events where event_type = 'view' group by user_id
), c as (
  select e.user_id, min(e.event_time) as t
  from events e join v on v.user_id = e.user_id
  where e.event_type = 'add_to_cart' and e.event_time > v.t
  group by e.user_id
), p as (
  select e.user_id, min(e.event_time) as t
  from events e join c on c.user_id = e.user_id
  where e.event_type = 'purchase' and e.event_time > c.t
  group by e.user_id
)
select (select count(*) from v) as viewed,
       (select count(*) from c) as carted,
       (select count(*) from p) as purchased;""",'Chain CTEs: first view per user, then first cart after that view, then first purchase after that cart.')

# ---------------- Data engineering
add('dq-nulls','de',1,'Data quality: missing values','<p>Profile the <code>customers</code> table. Return one row with <code>total_rows</code>, <code>null_city</code> (rows with no city) and <code>null_segment</code>.</p>',
"""select count(*) as total_rows,
       sum(city is null) as null_city,
       sum(segment is null) as null_segment
from customers;""",'<code>COUNT(*)</code> counts rows; <code>SUM(col IS NULL)</code> counts missing values. <code>COUNT(col)</code> counts non-missing ones.')
add('dup-count','de',1,'Spot duplicate loads','<p><code>raw_orders</code> is a landing table: some orders were ingested more than once. Return <code>total_rows</code>, <code>distinct_orders</code> (distinct <code>order_id</code>s) and <code>exact_duplicates</code> (rows that are identical copies of another row in every column).</p>',
"""select count(*) as total_rows,
       count(distinct order_id) as distinct_orders,
       count(*) - (select count(*) from (select distinct * from raw_orders)) as exact_duplicates
from raw_orders;""",'<code>SELECT DISTINCT *</code> collapses identical rows; compare its count with the total.')
add('view','de',1,'Create a reporting view','<p>Create a view <code>v_order_totals</code> with one row per order: <code>order_id</code>, <code>order_date</code>, <code>status</code> and <code>order_total</code> (sum of <code>quantity × price</code>, rounded to 2). Items whose product is missing are left out.</p>'+STATE.format(q='SELECT * FROM v_order_totals ORDER BY order_id'),
"""create view v_order_totals as
select o.order_id, o.order_date, o.status, round(sum(oi.quantity * p.price), 2) as order_total
from orders o
join order_items oi on oi.order_id = o.order_id
join products p on p.product_id = oi.product_id
group by o.order_id, o.order_date, o.status;""",'<code>CREATE VIEW name AS SELECT ...</code>. An inner join to <code>products</code> drops items with unknown products.',check='SELECT * FROM v_order_totals ORDER BY order_id')
add('create-load','de',1,'Create and load a staging table','<p>Create a table <code>stg_gear</code> with columns <code>product_id INTEGER PRIMARY KEY</code>, <code>name TEXT NOT NULL</code> and <code>price REAL</code> with a check that price is positive. Load it with every product in the Gear category.</p>'+STATE.format(q='SELECT product_id, name, price FROM stg_gear ORDER BY product_id'),
"""create table stg_gear (
  product_id integer primary key,
  name text not null,
  price real check (price > 0)
);
insert into stg_gear (product_id, name, price)
select product_id, name, price from products where category = 'Gear';""",'<code>CREATE TABLE</code> with a <code>CHECK (price &gt; 0)</code> constraint, then <code>INSERT INTO ... SELECT ...</code>.',check='SELECT product_id, name, price FROM stg_gear ORDER BY product_id')
add('dedupe-latest','de',2,'Keep the latest version','<p>In <code>raw_orders</code>, an order can appear several times; the row with the latest <code>ingested_at</code> is the current version. Return the current version of every order: <code>order_id</code>, <code>status</code>, <code>ingested_at</code>, sorted by order_id.</p>',
"""with r as (
  select *, row_number() over (partition by order_id order by ingested_at desc) as rn
  from raw_orders
)
select order_id, status, ingested_at from r where rn = 1 order by order_id;""",'<code>ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY ingested_at DESC)</code>, keep <code>rn = 1</code>.')
add('orphans','de',2,'Referential integrity check','<p>Find rows in <code>order_items</code> whose <code>product_id</code> doesn\'t exist in <code>products</code>. Return <code>order_id</code> and <code>product_id</code>, sorted by order_id.</p>',
"""select oi.order_id, oi.product_id
from order_items oi
left join products p on p.product_id = oi.product_id
where p.product_id is null
order by oi.order_id;""",'An anti-join: <code>LEFT JOIN</code> and keep rows where the right side is NULL (or use <code>NOT EXISTS</code>).')
add('upsert','de',2,'Upsert from a staging table','<p><code>product_updates</code> holds new prices for some products and two brand-new products. Apply it to <code>products</code> in one statement: update existing rows and insert new ones.</p>'+STATE.format(q='SELECT * FROM products ORDER BY product_id'),
"""insert into products (product_id, name, category, price)
select product_id, name, category, price from product_updates where true
on conflict(product_id) do update set
  name = excluded.name,
  category = excluded.category,
  price = excluded.price;""",'<code>INSERT ... SELECT ... ON CONFLICT(product_id) DO UPDATE SET col = excluded.col</code>. SQLite needs a <code>WHERE</code> clause (even <code>WHERE true</code>) on the SELECT so it can parse the ON CONFLICT.',check='SELECT * FROM products ORDER BY product_id')
add('incremental','de',2,'Incremental load with a watermark','<p><code>fact_orders(order_id, order_date, amount)</code> holds completed orders up to the latest <code>order_date</code> already loaded. Load only the newer completed orders, with <code>amount</code> = sum of <code>quantity × price</code> rounded to 2. Use the table\'s own maximum date as the watermark, so running your SQL twice never adds duplicates.</p>'+STATE.format(q='SELECT count(*), round(sum(amount), 2), max(order_date) FROM fact_orders'),
"""insert into fact_orders (order_id, order_date, amount)
select o.order_id, o.order_date, round(sum(oi.quantity * p.price), 2)
from orders o
join order_items oi on oi.order_id = o.order_id
join products p on p.product_id = oi.product_id
where o.status = 'completed'
  and o.order_date > (select max(order_date) from fact_orders)
group by o.order_id, o.order_date;""",'Filter with <code>order_date &gt; (SELECT MAX(order_date) FROM fact_orders)</code> inside an <code>INSERT ... SELECT</code>.',check='SELECT count(*), round(sum(amount), 2), max(order_date) FROM fact_orders')
add('json','de',2,'Parse JSON payloads','<p><code>raw_events_json.payload</code> holds JSON like <code>{"user": {"id": 3, "tier": "gold"}, "event": "view", "device": "ios", "cart_value": null}</code>. Return each <code>device</code>, the number of <code>events</code>, and <code>avg_cart_value</code> (average of non-null cart values, rounded to 2), sorted by device.</p>',
"""select json_extract(payload, '$.device') as device,
       count(*) as events,
       round(avg(json_extract(payload, '$.cart_value')), 2) as avg_cart_value
from raw_events_json
group by device
order by device;""",'<code>json_extract(payload, \'$.device\')</code> pulls a field out. <code>AVG</code> ignores NULLs.')
add('asof','de',2,'Point-in-time join to an SCD2 dimension','<p><code>dim_customer</code> is a type-2 slowly changing dimension: each row is valid from <code>valid_from</code> (inclusive) to <code>valid_to</code> (exclusive). For completed orders placed in 2025, return revenue by the city the customer lived in <b>when they ordered</b>. Show missing cities as <code>Unknown</code>. Columns <code>city</code>, <code>revenue</code> (rounded to 2), highest revenue first.</p>',
"""select coalesce(d.city, 'Unknown') as city, round(sum(oi.quantity * p.price), 2) as revenue
from orders o
join dim_customer d on d.customer_id = o.customer_id
                   and o.order_date >= d.valid_from and o.order_date < d.valid_to
join order_items oi on oi.order_id = o.order_id
join products p on p.product_id = oi.product_id
where o.status = 'completed' and o.order_date >= '2025-01-01'
group by coalesce(d.city, 'Unknown')
order by revenue desc;""",'Join on the customer id <i>and</i> the date range: <code>order_date &gt;= valid_from AND order_date &lt; valid_to</code>.')
add('scd2','de',3,'Apply an SCD type 2 load','<p><code>customer_updates</code> holds today\'s customer records (<code>updated_on</code> = 2025-07-01). Apply them to <code>dim_customer</code> as SCD type 2:</p><ul><li>If a customer\'s city or segment changed, close their current row (<code>valid_to</code> = updated_on, <code>is_current</code> = 0) and insert a new current row (<code>valid_from</code> = updated_on, <code>valid_to</code> = \'9999-12-31\', <code>is_current</code> = 1).</li><li>If nothing changed, leave them alone.</li><li>New customers get a current row.</li></ul><p class="note">Cities can be NULL, so compare with <code>IS NOT</code>, not <code>&lt;&gt;</code>. <code>customer_key</code> fills itself in.</p>'+STATE.format(q='SELECT customer_id, city, segment, valid_from, valid_to, is_current FROM dim_customer ORDER BY customer_id, valid_from'),
"""-- 1. close current rows that changed
update dim_customer
set valid_to = (select u.updated_on from customer_updates u where u.customer_id = dim_customer.customer_id),
    is_current = 0
where is_current = 1
  and exists (select 1 from customer_updates u
              where u.customer_id = dim_customer.customer_id
                and (u.city is not dim_customer.city or u.segment is not dim_customer.segment));

-- 2. insert a current row for every changed or new customer
insert into dim_customer (customer_id, city, segment, valid_from, valid_to, is_current)
select u.customer_id, u.city, u.segment, u.updated_on, '9999-12-31', 1
from customer_updates u
where not exists (select 1 from dim_customer d where d.customer_id = u.customer_id and d.is_current = 1);""",
'Two statements: an <code>UPDATE</code> that closes changed current rows, then an <code>INSERT ... SELECT</code> for every update that no longer has a current row (changed or brand new).',check='SELECT customer_id, city, segment, valid_from, valid_to, is_current FROM dim_customer ORDER BY customer_id, valid_from')
add('islands','de',3,'Downtime episodes (gaps and islands)','<p><code>machine_status</code> has one reading per machine every 10 minutes. A downtime episode is a run of consecutive <code>DOWN</code> readings. Return <code>machine_id</code>, <code>started</code> (first DOWN reading), <code>ended</code> (last DOWN reading), <code>readings</code> and <code>minutes</code> (readings × 10), sorted by machine and start.</p>',
"""with s as (
  select machine_id, ts, status,
         row_number() over (partition by machine_id order by ts)
       - row_number() over (partition by machine_id, status order by ts) as grp
  from machine_status
)
select machine_id, min(ts) as started, max(ts) as ended, count(*) as readings, count(*) * 10 as minutes
from s
where status = 'DOWN'
group by machine_id, grp
order by machine_id, started;""",'The classic trick: the difference between a row number over all readings and a row number within each status is constant inside a run. Group by it.')
add('sessions','de',3,'Sessionise clickstream events','<p>Split each user\'s <code>events</code> into sessions: a new session starts at a user\'s first event and whenever more than 30 minutes pass since their previous event. Return <code>user_id</code>, <code>session_no</code> (1, 2, … per user), <code>session_start</code>, <code>session_end</code> and <code>events</code>, sorted by user and session.</p>',
"""with e as (
  select user_id, event_time,
         case when lag(event_time) over (partition by user_id order by event_time) is null
                or (julianday(event_time)
                    - julianday(lag(event_time) over (partition by user_id order by event_time))) * 1440 > 30
              then 1 else 0 end as new_session
  from events
), s as (
  select *, sum(new_session) over (partition by user_id order by event_time rows unbounded preceding) as session_no
  from e
)
select user_id, session_no, min(event_time) as session_start, max(event_time) as session_end, count(*) as events
from s
group by user_id, session_no
order by user_id, session_no;""",'Flag a new session with <code>LAG()</code> and a gap test (<code>julianday</code> difference × 1440 gives minutes), then a running <code>SUM</code> of the flags numbers the sessions.')
add('delete-dupes','de',3,'Remove exact duplicates in place','<p>Delete exact duplicate rows from <code>raw_orders</code>, keeping one copy of each. Rows that differ in any column (for example a later <code>ingested_at</code>) must stay.</p>'+STATE.format(q='SELECT * FROM raw_orders ORDER BY order_id, ingested_at, status'),
"""delete from raw_orders
where rowid not in (
  select min(rowid) from raw_orders
  group by order_id, customer_id, order_date, status, amount, ingested_at
);""",'Every SQLite table has a hidden <code>rowid</code>. Keep the smallest rowid in each group of identical rows and delete the rest.',check='SELECT * FROM raw_orders ORDER BY order_id, ingested_at, status')

# ---------- verify with SQLite
seed = open('shop.sql').read()
for p in P:
    con = sqlite3.connect(':memory:'); con.executescript(seed)
    if p['check']:
        con.executescript(p['solution']); rows = con.execute(p['check']).fetchall()
    else:
        rows = con.execute(p['solution']).fetchall()
    assert rows, p['id']
    p['nrows'] = len(rows)
    print(p['id'], p['level'], len(rows), rows[:2])
json.dump(P, open('bank_sql_de.json', 'w'), indent=1)
print(len(P), 'problems')
