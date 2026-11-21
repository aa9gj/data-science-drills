# pandas problems. Most are adapted from "100 pandas puzzles" by Alex Riley (MIT);
# the statistics set is original. Writes bank_py.json.
import json

ANIMALS = """data = {'animal': ['cat', 'cat', 'snake', 'dog', 'dog', 'cat', 'snake', 'cat', 'dog', 'dog'],
        'age': [2.5, 3, 0.5, np.nan, 5, 2, 4.5, np.nan, 7, 3],
        'visits': [1, 3, 2, 3, 2, 3, 1, 1, 2, 1],
        'priority': ['yes', 'yes', 'no', 'yes', 'no', 'no', 'no', 'yes', 'no', 'no']}
labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
df = pd.DataFrame(data, index=labels)"""

FLIGHTS = """df = pd.DataFrame({'From_To': ['LoNDon_paris', 'MAdrid_miLAN', 'londON_StockhOlm',
                               'Budapest_PaRis', 'Brussels_londOn'],
                   'FlightNumber': [10045, np.nan, 10065, np.nan, 10085],
                   'RecentDelays': [[23, 47], [], [24, 43, 87], [13], [67, 32]],
                   'Airline': ['KLM(!)', '<Air France> (12)', '(British Airways. )',
                               '12. Air France', '"Swiss Air"']})"""
F38 = "df['FlightNumber'] = df['FlightNumber'].interpolate().astype(int)"
F39 = "temp = df['From_To'].str.split('_', expand=True)\ntemp.columns = ['From', 'To']"
F40 = "temp['From'] = temp['From'].str.capitalize()\ntemp['To'] = temp['To'].str.capitalize()"
F41 = "df = df.drop('From_To', axis=1).join(temp)"
F42 = "df['Airline'] = df['Airline'].str.extract(r'([a-zA-Z\\s]+)', expand=False).str.strip()"

BDAYS = "dti = pd.date_range(start='2015-01-01', end='2015-12-31', freq='B')\ns = pd.Series(np.random.rand(len(dti)), index=dti)"
MULTI = "letters = ['A', 'B', 'C']\nnumbers = list(range(10))\nmi = pd.MultiIndex.from_product([letters, numbers])\ns = pd.Series(np.random.rand(30), index=mi)"

PATIENTS = """rng = np.random.RandomState(42)
n = 40
patients = pd.DataFrame({
    'patient_id': range(101, 101 + n),
    'age': rng.randint(25, 80, n),
    'sex': rng.choice(['F', 'M'], n),
    'treatment': rng.choice(['A', 'B'], n),
    'bmi': rng.normal(27, 4, n).round(1),
    'sbp': rng.normal(132, 15, n).round(0),
})
patients.loc[[3, 11, 27], 'bmi'] = np.nan
patients['improved'] = (rng.rand(n) < np.where(patients['treatment'] == 'B', 0.65, 0.4)).astype(int)"""

P = []
def add(id, skill, level, title, body, setup, solution, hint, check='expr', ordered=False, starter='', src='ajcr'):
    P.append(dict(id='py-' + id, lang='py', skill=skill, level=level, title=title, body=body, setup=setup,
                  starter=starter or '# Write your code below. The value of your last line is checked.\n',
                  solution=solution, hint=hint, check=check, ordered=ordered, src=src))

EXPR = '<p class="note">End with an expression; the value of your last line is checked.</p>'
def VAR(v): return f'<p class="note">Your updated <code>{v}</code> is checked after your code runs.</p>'

# ---------- Selecting & filtering
add('6','select',1,'First rows','<p>Return the first 3 rows of the DataFrame <code>df</code>.</p>'+EXPR,ANIMALS,'df.head(3)','<code>df.head(n)</code> or <code>df.iloc[:n]</code>.')
add('7','select',1,'Pick columns','<p>Select just the <code>animal</code> and <code>age</code> columns from <code>df</code>.</p>'+EXPR,ANIMALS,"df[['animal', 'age']]",'Pass a list of column names inside the brackets: <code>df[[...]]</code>.')
add('9','select',1,'Filter on a number','<p>Select only the rows where the number of <code>visits</code> is greater than 2.</p>'+EXPR,ANIMALS,"df[df['visits'] > 2]",'Build a boolean mask such as <code>df[\'visits\'] &gt; 2</code> and index <code>df</code> with it.')
add('8','select',2,'Rows by position','<p>Select the data in rows at positions <code>[3, 4, 8]</code> <em>and</em> in columns <code>[\'animal\', \'age\']</code>.</p>'+EXPR,ANIMALS,"df.iloc[[3, 4, 8]][['animal', 'age']]",'<code>iloc</code> selects by position; then pick the columns. Or use <code>df.loc[df.index[[3, 4, 8]], [...]]</code>.')
add('10','select',2,'Missing values','<p>Select the rows where the <code>age</code> is missing, i.e. it is <code>NaN</code>.</p>'+EXPR,ANIMALS,"df[df['age'].isna()]",'<code>Series.isna()</code> returns a boolean mask.')
add('11','select',2,'Two conditions','<p>Select the rows where the animal is a cat <em>and</em> the age is less than 3.</p>'+EXPR,ANIMALS,"df[(df['animal'] == 'cat') & (df['age'] < 3)]",'Combine masks with <code>&amp;</code>, and wrap each condition in parentheses.')
add('12','select',2,'Between two values','<p>Select the rows where the age is between 2 and 4 (inclusive).</p>'+EXPR,ANIMALS,"df[df['age'].between(2, 4)]",'<code>Series.between(low, high)</code> is inclusive by default.')
add('24','select',3,'Smallest column','<p><code>df</code> has 10 columns of random numbers. Which column has the smallest sum? Return that column\'s label.</p>'+EXPR,
    "df = pd.DataFrame(np.random.random(size=(5, 10)), columns=list('abcdefghij'))","df.sum().idxmin()",'<code>df.sum()</code> gives one total per column; <code>idxmin()</code> returns the label of the smallest.')
add('26','select',3,'Third missing value','<p>Each row of <code>df</code> has exactly 5 <code>NaN</code> values. For each row, find the <em>column</em> that holds the <em>third</em> NaN. You should get a Series of labels: <code>e, c, d, h, d</code>.</p>'+EXPR,
    """nan = np.nan
data = [[0.04,  nan,  nan, 0.25,  nan, 0.43, 0.71, 0.51,  nan,  nan],
        [ nan,  nan,  nan, 0.04, 0.76,  nan,  nan, 0.67, 0.76, 0.16],
        [ nan,  nan, 0.5 ,  nan, 0.31, 0.4 ,  nan,  nan, 0.24, 0.01],
        [0.49,  nan,  nan, 0.62, 0.73, 0.26, 0.85,  nan,  nan,  nan],
        [ nan,  nan, 0.41,  nan, 0.05,  nan, 0.61,  nan, 0.48, 0.68]]
df = pd.DataFrame(data, columns=list('abcdefghij'))""",
    "(df.isnull().cumsum(axis=1) == 3).idxmax(axis=1)",'Count NaNs cumulatively along each row with <code>isnull().cumsum(axis=1)</code>, then find where the count first equals 3 with <code>idxmax(axis=1)</code>.')

# ---------- Changing data
add('13','modify',1,'Change one value','<p>Change the age in row <code>\'f\'</code> to 1.5.</p>'+VAR('df'),ANIMALS,"df.loc['f', 'age'] = 1.5",'<code>df.loc[row_label, column] = value</code>.',check='var:df')
add('19','modify',1,'Yes/no to booleans','<p>The <code>priority</code> column contains <code>\'yes\'</code> and <code>\'no\'</code>. Replace it with booleans: <code>\'yes\'</code> becomes <code>True</code>, <code>\'no\'</code> becomes <code>False</code>.</p>'+VAR('df'),ANIMALS,"df['priority'] = df['priority'].map({'yes': True, 'no': False})",'<code>Series.map()</code> accepts a dictionary.',check='var:df')
add('20','modify',1,'Rename a category','<p>In the <code>animal</code> column, change the <code>\'snake\'</code> entries to <code>\'python\'</code>.</p>'+VAR('df'),ANIMALS,"df['animal'] = df['animal'].replace('snake', 'python')",'<code>Series.replace(old, new)</code>, then assign it back to the column.',check='var:df')
add('22','modify',2,'Drop repeated neighbours','<p><code>df</code> has a column <code>A</code> of integers. Filter out rows that contain the same integer as the row immediately above. You should be left with <code>1, 2, 3, 4, 5, 6, 7</code>.</p>'+EXPR,
    "df = pd.DataFrame({'A': [1, 2, 2, 3, 4, 5, 5, 5, 6, 7, 7]})","df.loc[df['A'].shift() != df['A']]",'<code>df[\'A\'].shift()</code> lines each value up with the one above it.')
add('23','modify',2,'Center each row','<p>Given a DataFrame of random values, subtract the row mean from each element in the row.</p>'+EXPR,
    "df = pd.DataFrame(np.random.random(size=(5, 3)))","df.sub(df.mean(axis=1), axis=0)",'<code>df.mean(axis=1)</code> gives row means. <code>df.sub(..., axis=0)</code> subtracts them row by row.')
add('29','modify',3,'Distance to the previous zero','<p>For each value in column <code>X</code>, count the distance back to the previous zero (or to the start of the Series, whichever is closer). Store it in a new column <code>Y</code>. The values should be <code>[1, 2, 0, 1, 2, 3, 4, 0, 1, 2]</code>.</p>'+VAR('df'),
    "df = pd.DataFrame({'X': [7, 2, 0, 3, 4, 2, 5, 0, 3, 4]})",
    "izero = np.r_[-1, (df['X'] == 0).values.nonzero()[0]]  # positions of zeros\nidx = np.arange(len(df))\ndf['Y'] = idx - izero[np.searchsorted(izero - 1, idx) - 1]",
    'One approach: group with <code>(df[\'X\'] == 0).cumsum()</code>, number rows with <code>cumcount()</code>, then add 1 to the rows before the first zero.',check='var:df')
add('31','modify',3,'Patch negatives with the group mean','<p>Create a column <code>patched_vals</code> that keeps each value in <code>vals</code>, but replaces negative values with the mean of the non-negative values in the same group (<code>grps</code>). For group A that mean is 13.6.</p>'+VAR('df'),
    'df = pd.DataFrame({"vals": np.random.RandomState(31).randint(-30, 30, size=15),\n                   "grps": np.random.RandomState(31).choice(["A", "B"], 15)})',
    "pos_mean = df[df['vals'] >= 0].groupby('grps')['vals'].mean()\ndf['patched_vals'] = df['vals'].where(df['vals'] >= 0, df['grps'].map(pos_mean))",
    'Compute the per-group mean of the non-negative values, map it onto each row with <code>df[\'grps\'].map(...)</code>, and use <code>Series.where()</code> to swap it in where the value is negative.',check='var:df')

# ---------- Grouping & sorting
add('14','group',1,'Total visits','<p>Calculate the sum of all <code>visits</code> in <code>df</code>.</p>'+EXPR,ANIMALS,"df['visits'].sum()",'Select the column, then call <code>.sum()</code>.')
add('17','group',1,'Count each animal','<p>Count the number of each type of animal in <code>df</code>.</p>'+EXPR,ANIMALS,"df['animal'].value_counts()",'<code>Series.value_counts()</code>.')
add('15','group',1,'Mean age by animal','<p>Calculate the mean age for each different animal in <code>df</code>.</p>'+EXPR,ANIMALS,"df.groupby('animal')['age'].mean()",'<code>df.groupby(\'animal\')[\'age\']</code> then an aggregation.')
add('18','group',2,'Sort by two columns','<p>Sort <code>df</code> by <code>age</code> in <em>descending</em> order, then by <code>visits</code> in <em>ascending</em> order. Row <code>i</code> should be first and row <code>d</code> last.</p>'+EXPR,ANIMALS,"df.sort_values(by=['age', 'visits'], ascending=[False, True])",'<code>sort_values</code> takes a list for both <code>by</code> and <code>ascending</code>.',ordered=True)
add('21','group',2,'Pivot table','<p>For each animal type and each number of visits, find the mean age. Each row is an animal, each column is a number of visits, and the values are mean ages.</p>'+EXPR,ANIMALS,"df.pivot_table(index='animal', columns='visits', values='age', aggfunc='mean')",'<code>df.pivot_table(index=..., columns=..., values=..., aggfunc=\'mean\')</code>.')
add('25','group',2,'Count unique rows','<p>How many rows of <code>df</code> are unique, ignoring every row that has a duplicate anywhere in the table? Return the count.</p>'+EXPR,
    "df = pd.DataFrame(np.random.randint(0, 2, size=(10, 3)))","len(df.drop_duplicates(keep=False))",'<code>drop_duplicates(keep=False)</code> removes every copy of a duplicated row.')
add('27','group',3,'Sum of the top three','<p>For each group in <code>grps</code>, find the sum of the three greatest values in <code>vals</code>. You should get <code>a 409, b 156, c 345</code>.</p>'+EXPR,
    "df = pd.DataFrame({'grps': list('aaabbcaabcccbbc'),\n                   'vals': [12, 345, 3, 1, 45, 14, 4, 52, 54, 23, 235, 21, 57, 3, 87]})",
    "df.groupby('grps')['vals'].nlargest(3).groupby(level=0).sum()",'<code>nlargest(3)</code> per group, then sum again by the group level of the index.')
add('28','group',3,'Sum by bins','<p>Column <code>A</code> holds integers from 1 to 100. For each group of 10 consecutive integers in <code>A</code>, i.e. <code>(0, 10]</code>, <code>(10, 20]</code>, …, calculate the sum of the matching values in <code>B</code>. Return a Series.</p>'+EXPR,
    'df = pd.DataFrame(np.random.RandomState(8765).randint(1, 101, size=(100, 2)), columns=["A", "B"])',
    "df.groupby(pd.cut(df['A'], np.arange(0, 101, 10)), observed=False)['B'].sum()",'<code>pd.cut(df[\'A\'], np.arange(0, 101, 10))</code> makes the bins; group by it.')
add('32','group',3,'Rolling mean by group','<p>Compute a rolling mean with window size 3 within each <code>group</code>, ignoring NaN values (a window of <code>3, NaN, 3</code> has mean 3). Return a Series in the original row order: <code>1.0, 1.5, 3.0, 3.0, 1.67, 3.0, 3.0, 2.0, 3.67, 2.0, 4.5, 4.0</code>.</p>'+EXPR,
    "df = pd.DataFrame({'group': list('aabbabbbabab'),\n                   'value': [1, 2, 3, np.nan, 2, 3, np.nan, 1, 7, 3, np.nan, 8]})",
    "g1 = df.groupby('group')['value']\ng2 = df.fillna(0).groupby('group')['value']\ns = g2.rolling(3, min_periods=1).sum() / g1.rolling(3, min_periods=1).count()\ns.reset_index(level=0, drop=True).sort_index()",
    'Divide a rolling <em>sum</em> (NaN filled with 0) by a rolling <em>count</em> of non-missing values, both with <code>min_periods=1</code>.',ordered=True)

# ---------- Dates & time series
add('33','time',1,'Business days','<p>Create a DatetimeIndex called <code>dti</code> that contains each business day of 2015.</p>'+VAR('dti'),'',"dti = pd.date_range(start='2015-01-01', end='2015-12-31', freq='B')",'<code>pd.date_range(start, end, freq=\'B\')</code>.',check='var:dti',ordered=True)
add('34','time',1,'Wednesdays only','<p><code>s</code> is a Series of random numbers indexed by every business day of 2015. Find the sum of the values in <code>s</code> for every Wednesday.</p>'+EXPR,BDAYS,"s[s.index.weekday == 2].sum()",'<code>s.index.weekday</code> is 0 for Monday, so Wednesday is 2.')
add('35','time',2,'Monthly means','<p>For each calendar month in <code>s</code>, find the mean of the values. Label each month by its last day.</p>'+EXPR,BDAYS,"s.resample('ME').mean()",'<code>s.resample(\'ME\').mean()</code>. In pandas 2.2, <code>\'ME\'</code> means month end.',ordered=True)
add('37','time',2,'Third Thursdays','<p>Create a DatetimeIndex of the third Thursday in each month for 2015 and 2016.</p>'+EXPR,'',"pd.date_range('2015-01-01', '2016-12-31', freq='WOM-3THU')",'The frequency alias <code>\'WOM-3THU\'</code> means week-of-month 3, Thursday.',ordered=True)
add('36','time',3,'Best day per four months','<p>For each group of four consecutive calendar months in <code>s</code>, find the date on which the highest value occurred.</p>'+EXPR,BDAYS,"s.groupby(pd.Grouper(freq='4ME')).idxmax()",'Group with <code>pd.Grouper(freq=\'4ME\')</code>, then use <code>idxmax()</code>.',ordered=True)

# ---------- Cleaning messy data
add('38','clean',1,'Fill missing flight numbers','<p>Some values in <code>FlightNumber</code> are missing. The numbers increase by 10 each row, so 10055 and 10075 belong in the gaps. Fill them in and make the column an integer column.</p>'+VAR('df'),FLIGHTS,F38,'<code>interpolate()</code> fills the gaps linearly; then <code>astype(int)</code>.',check='var:df')
add('39','clean',1,'Split a column','<p>Split each string in <code>From_To</code> on the underscore to make a new DataFrame called <code>temp</code>, with columns named <code>From</code> and <code>To</code>.</p>'+VAR('temp'),FLIGHTS+'\n'+F38,F39,'<code>df[\'From_To\'].str.split(\'_\', expand=True)</code> returns a DataFrame.',check='var:temp')
add('40','clean',2,'Fix capitalisation','<p>The city names in <code>temp</code> have mixed capitalisation. Standardise them so only the first letter is uppercase (<code>"londON"</code> becomes <code>"London"</code>).</p>'+VAR('temp'),FLIGHTS+'\n'+F38+'\n'+F39,F40,'<code>.str.capitalize()</code> on each column.',check='var:temp')
add('41','clean',2,'Replace a column with two','<p>Delete the <code>From_To</code> column from <code>df</code> and attach the <code>temp</code> DataFrame in its place.</p>'+VAR('df'),FLIGHTS+'\n'+F38+'\n'+F39+'\n'+F40,F41,'<code>df.drop(\'From_To\', axis=1)</code>, then <code>.join(temp)</code>.',check='var:df')
add('42','clean',3,'Extract clean names','<p>The <code>Airline</code> column has stray punctuation and numbers around the names. Pull out just the airline name, e.g. <code>\'(British Airways. )\'</code> becomes <code>\'British Airways\'</code>.</p>'+VAR('df'),FLIGHTS+'\n'+F38+'\n'+F39+'\n'+F40+'\n'+F41,F42,'<code>.str.extract(r\'([a-zA-Z\\s]+)\', expand=False)</code>, then <code>.str.strip()</code>.',check='var:df')
add('43','clean',3,'Expand a list column','<p><code>RecentDelays</code> holds lists. Expand them so each first value is in its own column, each second value in another, and so on (NaN where there is no value). Name the columns <code>delay_1</code>, <code>delay_2</code>, … and replace <code>RecentDelays</code> in <code>df</code> with them.</p>'+VAR('df'),FLIGHTS+'\n'+F38+'\n'+F39+'\n'+F40+'\n'+F41+'\n'+F42,
    "delays = df['RecentDelays'].apply(pd.Series)\ndelays.columns = [f'delay_{n}' for n in range(1, len(delays.columns) + 1)]\ndf = df.drop('RecentDelays', axis=1).join(delays)",
    '<code>df[\'RecentDelays\'].apply(pd.Series)</code> turns the lists into columns.',check='var:df')

# ---------- MultiIndex
add('44','multi',1,'Build a MultiIndex','<p>Given the lists <code>letters</code> and <code>numbers</code>, construct a MultiIndex from the product of the two lists. Call it <code>mi</code>.</p>'+VAR('mi'),"letters = ['A', 'B', 'C']\nnumbers = list(range(10))","mi = pd.MultiIndex.from_product([letters, numbers])",'<code>pd.MultiIndex.from_product([...])</code>.',check='var:mi',ordered=True)
add('46','multi',1,'Select inner labels','<p><code>s</code> is a Series with a two-level MultiIndex. Select the labels <code>1</code>, <code>3</code> and <code>6</code> from the second level.</p>'+EXPR,MULTI,"s.loc[:, [1, 3, 6]]",'<code>s.loc[:, [1, 3, 6]]</code>: everything in the first level, a list in the second.',ordered=True)
add('47','multi',2,'Slice two levels','<p>Slice <code>s</code> up to label <code>\'B\'</code> in the first level and from label 5 onwards in the second level.</p>'+EXPR,MULTI,"s.loc[pd.IndexSlice[:'B', 5:]]",'<code>pd.IndexSlice[:\'B\', 5:]</code> describes a slice on each level.',ordered=True)
add('48','multi',2,'Sum by outer level','<p>Sum the values in <code>s</code> for each label in the first level. You should get totals for A, B and C.</p>'+EXPR,MULTI,"s.groupby(level=0).sum()",'<code>s.groupby(level=0).sum()</code>. (Older pandas allowed <code>s.sum(level=0)</code>, which has been removed.)')
add('49','multi',3,'Unstack instead','<p>Without using <code>groupby</code>, compute the sum of <code>s</code> for each label in the <em>second</em> level.</p>'+EXPR,MULTI,"s.unstack().sum(axis=0)",'<code>s.unstack()</code> turns the inner level into columns.')
add('50','multi',3,'Swap and sort levels','<p>Swap the two levels of the MultiIndex so the numbers come first, then sort the result by its index. Call the new Series <code>new_s</code>.</p>'+VAR('new_s'),MULTI,"new_s = s.swaplevel(0, 1).sort_index()",'<code>swaplevel(0, 1)</code>, then <code>sort_index()</code>.',check='var:new_s',ordered=True)

# ---------- Statistics (original)
add('st1','stats',1,'Average BMI','<p>The <code>patients</code> table holds 40 synthetic patients. Return the mean <code>bmi</code>, rounded to 2 decimals. Some BMIs are missing.</p>'+EXPR,PATIENTS,"round(patients['bmi'].mean(), 2)",'pandas skips NaN in <code>mean()</code> by default.',src='own')
add('st2','stats',1,'Share by sex','<p>Return the proportion of patients of each <code>sex</code> (values between 0 and 1).</p>'+EXPR,PATIENTS,"patients['sex'].value_counts(normalize=True)",'<code>value_counts(normalize=True)</code>.',src='own')
add('st3','stats',2,'Correlation','<p>Return the Pearson correlation between <code>age</code> and <code>sbp</code> (systolic blood pressure), rounded to 3 decimals.</p>'+EXPR,PATIENTS,"round(patients['age'].corr(patients['sbp']), 3)",'<code>Series.corr(other)</code> is Pearson by default.',src='own')
add('st4','stats',2,'Outcome by treatment','<p>Make a cross-tabulation of <code>treatment</code> (rows) by <code>improved</code> (columns) showing the proportion of each row, rounded to 3 decimals.</p>'+EXPR,PATIENTS,"pd.crosstab(patients['treatment'], patients['improved'], normalize='index').round(3)",'<code>pd.crosstab(rows, cols, normalize=\'index\')</code>.',src='own')
add('st5','stats',3,'Standardise a column','<p>Add a column <code>sbp_z</code> with the z-score of <code>sbp</code> (subtract the mean, divide by the sample standard deviation), rounded to 2 decimals.</p>'+VAR('patients'),PATIENTS,"patients['sbp_z'] = ((patients['sbp'] - patients['sbp'].mean()) / patients['sbp'].std()).round(2)",'<code>Series.std()</code> uses the sample standard deviation (ddof=1).',check='var:patients',src='own')
add('st6','stats',3,'Blood pressure by age band','<p>Group patients into age bands <code>&lt;40</code>, <code>40-59</code> and <code>60+</code> and return the mean <code>sbp</code> for each band, rounded to 1 decimal.</p>'+EXPR,PATIENTS,
    "bands = pd.cut(patients['age'], bins=[0, 40, 60, 120], right=False, labels=['<40', '40-59', '60+'])\npatients.groupby(bands, observed=False)['sbp'].mean().round(1)",
    '<code>pd.cut(..., bins=[0, 40, 60, 120], right=False, labels=[...])</code> makes the bands.',src='own',ordered=True)

json.dump(P, open('bank_py.json', 'w'), indent=1)
from collections import Counter
print(len(P), sorted(Counter((p['skill'], p['level']) for p in P).items()))
