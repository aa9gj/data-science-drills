# Generates the synthetic "shop" warehouse used by the advanced / data engineering SQL problems.
# Everything is deterministic (seeded) so expected answers never change.
import random, datetime as dt, json

R = random.Random(3)
cities = ['Austin', 'Chicago', 'Denver', 'Seattle', 'Boston', None]
first = ['Ava','Liam','Mia','Noah','Zoe','Eli','Ivy','Owen','Lena','Kai','Nora','Ezra','Ruby','Theo','Maya','Leo','Iris','Finn','Cora','Jude','Ada','Max','Lila','Sam']
last = ['Reed','Shah','Kim','Lopez','Ng','Ford','Diaz','Bell','Park','Cole','Hart','Wu']
cust = []
for i in range(1, 25):
    nm = f"{first[i-1]} {R.choice(last)}"
    city = R.choice(cities) if i % 7 else None
    seg = R.choice(['Consumer', 'Consumer', 'Business'])
    sd = dt.date(2024, 1, 1) + dt.timedelta(days=R.randint(0, 330))
    cust.append((i, nm, city, seg, sd.isoformat()))
prods = [(1,'Trail Shoes','Footwear',89.0),(2,'Running Socks','Apparel',12.5),(3,'Rain Jacket','Apparel',140.0),(4,'Water Bottle','Gear',18.0),(5,'Headlamp','Gear',35.0),(6,'Hiking Boots','Footwear',165.0),(7,'Fleece','Apparel',60.0),(8,'Daypack','Gear',75.0),(9,'Sandals','Footwear',45.0),(10,'Trekking Poles','Gear',95.0)]
price = {p[0]: p[3] for p in prods}
orders, items, oid = [], [], 1
active = [c for c in cust if c[0] not in (5, 13, 21)]          # three customers never order
for c in active:
    n = R.choice([1, 1, 2, 2, 3, 4, 5])
    sd = dt.date.fromisoformat(c[4])
    for _ in range(n):
        od = sd + dt.timedelta(days=R.randint(1, 300))
        if od > dt.date(2025, 6, 30): od = dt.date(2025, 6, 30) - dt.timedelta(days=R.randint(0, 40))
        st = R.choices(['completed', 'returned', 'cancelled'], [8, 1, 1])[0]
        orders.append((oid, c[0], od.isoformat(), st))
        for p in R.sample(prods, R.choice([1, 1, 2, 3])):
            items.append((oid, p[0], R.choice([1, 1, 1, 2, 3])))
        oid += 1
items += [(7, 99, 1), (31, 98, 2)]                               # orphans: products that don't exist
amount = {}
for o, p, q in items:
    amount[o] = round(amount.get(o, 0) + q * price.get(p, 0), 2)

# raw_orders: every order ingested once, ~15% re-ingested later with a status change, plus a few exact duplicates
raw = []
for o in orders:
    t0 = dt.datetime.fromisoformat(o[2] + 'T23:00:00')
    raw.append((o[0], o[1], o[2], 'placed' if o[3] != 'cancelled' else 'cancelled', amount.get(o[0], 0.0), t0.isoformat(sep=' ')))
    if R.random() < 0.15 or o[3] == 'returned':
        raw.append((o[0], o[1], o[2], o[3] if o[3] != 'cancelled' else 'cancelled', amount.get(o[0], 0.0), (t0 + dt.timedelta(days=R.randint(1, 9), hours=3)).isoformat(sep=' ')))
for o in R.sample(orders, 4):
    first_row = next(r for r in raw if r[0] == o[0])
    raw.append(first_row)                                        # exact duplicate row (re-sent file)
raw.sort(key=lambda r: (r[5], r[0]))

# dim_customer as SCD type 2: a few customers moved in 2025
moves = {3: ('Seattle', '2025-02-01'), 8: ('Denver', '2025-03-15'), 11: ('Chicago', '2025-01-10'), 17: ('Austin', '2025-04-20')}
dim, key = [], 1
for c in cust:
    if c[0] in moves:
        new_city, d = moves[c[0]]
        dim.append((key, c[0], c[2], c[3], c[4], d, 0)); key += 1
        dim.append((key, c[0], new_city, c[3], d, '9999-12-31', 1)); key += 1
    else:
        dim.append((key, c[0], c[2], c[3], c[4], '9999-12-31', 1)); key += 1

# staged changes for an SCD2 load on 2025-07-01: two moves, one segment change, one no-op, one new customer
cust_updates = [(4, 'Austin', 'Business', '2025-07-01'), (9, 'Boston', 'Consumer', '2025-07-01'),
                (12, 'Seattle', 'Business', '2025-07-01'), (15, 'Denver', 'Business', '2025-07-01'),
                (25, 'Chicago', 'Consumer', '2025-07-01')]

product_updates = [(2, 'Running Socks', 'Apparel', 13.5), (6, 'Hiking Boots', 'Footwear', 159.0),
                   (11, 'Camp Stove', 'Gear', 64.0), (12, 'Sun Hat', 'Apparel', 22.0)]

# machine_status: 3 machines, a reading every 10 minutes on 2025-03-03 06:00-17:50
status = []
down = {'M1': [(14, 18), (40, 43)], 'M2': [(5, 6), (20, 31), (60, 64)], 'M3': []}
for m in ['M1', 'M2', 'M3']:
    for k in range(72):
        ts = dt.datetime(2025, 3, 3, 6, 0) + dt.timedelta(minutes=10 * k)
        s = 'DOWN' if any(a <= k <= b for a, b in down[m]) else 'RUN'
        if m == 'M3' and k in (30, 31): s = 'IDLE'
        status.append((m, ts.isoformat(sep=' '), s))

# events: web events for 6 users on 2025-06-10/11 (sessionisation and funnels)
events, eid = [], 1
for u in range(1, 7):
    t = dt.datetime(2025, 6, 10, 8 + u, 0)
    for s in range(R.choice([2, 3])):
        n = R.randint(2, 5)
        for j in range(n):
            et = 'view' if j < n - 2 else R.choice(['view', 'add_to_cart'])
            if j == n - 1 and R.random() < 0.5: et = 'purchase'
            events.append((eid, u, t.isoformat(sep=' '), et)); eid += 1
            t += dt.timedelta(minutes=R.randint(1, 12))
        t += dt.timedelta(minutes=R.randint(35, 300))
# make sure funnel steps exist in order for some users
events.sort(key=lambda e: (e[1], e[2]))

raw_json = []
for e in events[:30]:
    payload = {'user': {'id': e[1], 'tier': 'gold' if e[1] % 3 == 0 else 'standard'}, 'event': e[3], 'ts': e[2],
               'device': R.choice(['ios', 'android', 'web']), 'cart_value': round(R.uniform(10, 200), 2) if e[3] != 'view' else None}
    raw_json.append((e[0], json.dumps(payload)))

fact_orders = [(o[0], o[2], amount.get(o[0], 0.0)) for o in orders if o[3] == 'completed' and o[2] <= '2025-05-31']

q = lambda v: 'NULL' if v is None else (f"'{v}'" if isinstance(v, str) else repr(v))
row = lambda t: '(' + ','.join(q(x) for x in t) + ')'
def table(ddl, name, rows):
    return [ddl, f"INSERT INTO {name} VALUES " + ','.join(row(r) for r in rows) + ';']
out = []
out += table("CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT, city TEXT, segment TEXT, signup_date TEXT);", 'customers', cust)
out += table("CREATE TABLE products (product_id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT, price REAL);", 'products', prods)
out += table("CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, order_date TEXT, status TEXT);", 'orders', orders)
out += table("CREATE TABLE order_items (order_id INTEGER, product_id INTEGER, quantity INTEGER);", 'order_items', items)
out += table("CREATE TABLE raw_orders (order_id INTEGER, customer_id INTEGER, order_date TEXT, status TEXT, amount REAL, ingested_at TEXT);", 'raw_orders', raw)
out += table("CREATE TABLE dim_customer (customer_key INTEGER PRIMARY KEY, customer_id INTEGER, city TEXT, segment TEXT, valid_from TEXT, valid_to TEXT, is_current INTEGER);", 'dim_customer', dim)
out += table("CREATE TABLE customer_updates (customer_id INTEGER, city TEXT, segment TEXT, updated_on TEXT);", 'customer_updates', cust_updates)
out += table("CREATE TABLE product_updates (product_id INTEGER, name TEXT, category TEXT, price REAL);", 'product_updates', product_updates)
out += table("CREATE TABLE machine_status (machine_id TEXT, ts TEXT, status TEXT);", 'machine_status', status)
out += table("CREATE TABLE events (event_id INTEGER PRIMARY KEY, user_id INTEGER, event_time TEXT, event_type TEXT);", 'events', events)
out += table("CREATE TABLE raw_events_json (event_id INTEGER PRIMARY KEY, payload TEXT);", 'raw_events_json', raw_json)
out += table("CREATE TABLE fact_orders (order_id INTEGER PRIMARY KEY, order_date TEXT, amount REAL);", 'fact_orders', fact_orders)
open('shop.sql', 'w').write('\n'.join(out))
print({'customers': len(cust), 'orders': len(orders), 'items': len(items), 'raw_orders': len(raw), 'dim': len(dim),
       'status': len(status), 'events': len(events), 'json': len(raw_json), 'fact': len(fact_orders)})
