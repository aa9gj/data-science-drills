# Data Science Drills

Adaptive coding practice for data science in **SQL, Python, R and SAS**, in a single web page. You write real code and it is checked in your browser. The difficulty adjusts to how you're doing: a mistake gets you an easier question, and a clean solve moves you up a level. Practise one skill at a time, or take a mixed session across skills and languages.

**Try it:** https://aa9gj.github.io/data-science-drills/

Nothing to install and no account needed. Your progress is saved in your own browser.

## What's inside

244 problems in 33 skills, each with three levels: 1 Foundations, 2 Practice, 3 Challenge.

| Language | Problems | Skills | How answers are checked |
|---|---|---|---|
| SQL | 81 | Retrieving data, joins & subqueries, aggregation, window functions & recursion, text, dates, **advanced analytics**, **data engineering** | Your query runs on SQLite ([sql.js](https://sql.js.org)). It's compared with the expected rows, or with the resulting table contents for tasks that change data. |
| Python | 74 | pandas selecting, changing, grouping, cleaning, time series, MultiIndex, statistics, **supervised learning**, **pipelines & tuning**, **clustering & reduction**, **manufacturing analytics** | Your code runs in Python with pandas and scikit-learn ([Pyodide](https://pyodide.org)). The value of your last line, or a named variable, is compared with the expected value. |
| R | 49 | Vectors & subsetting, data frames, dplyr & tidyr, functions & loops, **statistics**, **regression models**, **manufacturing & quality** | Your code runs in R with dplyr and tidyr ([webR](https://docs.r-wasm.org/webr/latest/)). It's compared by value or by printed output. |
| SAS | 40 | DATA step, creating variables, summaries & reports, PROC SQL, DO loops & simulation, **statistical procedures**, **manufacturing & quality** | SAS can't run in a browser. You compare your answer with the solution yourself, or turn on Claude checking (below). |

Some examples of the harder material:

- **SQL data engineering:** deduplicating re-ingested loads, upserts with `ON CONFLICT`, watermark-based incremental loads, applying a slowly changing dimension (type 2), point-in-time joins, gaps-and-islands downtime episodes, sessionising clickstreams, parsing JSON payloads, data quality and referential integrity checks.
- **SQL analytics:** date spines, pivots, medians without a MEDIAN function, cohort conversion, ordered funnels, cumulative revenue share.
- **Machine learning:** train/test splits, metrics, cross-validation, ROC AUC, fixing data leakage, pipelines with `ColumnTransformer`, grid search, feature importance, choosing model complexity, k-means, PCA, silhouette scores.
- **Manufacturing:** Cp/Cpk, X-bar and p-chart control limits, out-of-control subgroups, run rules, Pareto analysis, OEE, spike detection, predictive maintenance with imbalanced classes, anomaly detection with Isolation Forest, and the SAS/QC procedures `SHEWHART` and `CAPABILITY`.
- **Statistics:** confidence intervals, chi-square, paired and two-sample t-tests, ANOVA with Tukey HSD, nonparametric tests, linear and logistic regression, prediction intervals, cross-validated error, stepwise selection.

## How the adaptive part works

- Each skill has its own level from 1 to 3, shown as dots in the sidebar.
- **Solve a problem on the first try** (no hint, no solution) and you move up a level. A first-try solve at Level 3 marks the skill as mastered.
- **A wrong answer or showing the solution** drops that skill a level. The **Easier question** button gives you an unsolved problem one level down in the same skill.
- **Next problem** picks the next unsolved problem at your level, and moves on to the next skill once you've mastered one.
- Hints, full solutions and, for the SQL set, the original author's explanations are always available.

### Mixed practice

Practising one skill at a time is good for learning a technique; mixing skills is better for remembering when to use which one. **Mixed practice** in the sidebar starts a 10-problem session that switches between skills, within the current language or across **all languages**:

- Each problem comes from a different skill than the one before, at your current level for that skill.
- Skills you haven't mastered and skills where your level is lower come up more often.
- Mistakes work the same way as in normal practice: try again, take an easier question in the same skill, or skip. Your skill levels keep updating.
- At the end you get a summary of what you solved on the first try, after a retry, or not yet, by language and skill.
- Once everything in your scope is solved, mixed practice brings back problems that needed more than one try or the solution.

## Optional: Claude checking

Click **Claude checking** (top right) and paste an [Anthropic API key](https://console.anthropic.com/settings/keys) to:

- have Claude grade SAS answers (and any R or Python that can't run in your browser) by predicting the output and explaining what's wrong;
- have Claude write new problems at your level when a skill runs out, or an easier one after a mistake. New SQL, Python and R problems are kept only if their own solutions run correctly.

The key is stored only in your browser's local storage and sent only to `api.anthropic.com`. Requests use Claude Opus 5.5 and are billed to your Anthropic account. Remove it any time from the same panel. Everything else works without a key.

## Run it locally

The page loads its data files over HTTP, so open it through a local web server, not as a `file://` path:

```bash
git clone https://github.com/aa9gj/data-science-drills.git
cd data-science-drills
python3 -m http.server 8000
```

Then open http://localhost:8000. The first Python or R problem downloads its runtime from a public CDN (about 20 to 50 MB, cached by the browser afterwards).

## Project layout

```
index.html          the whole app: page, styles, engine and the question bank (generated)
data/               SQLite databases (as SQL text) and the gapminder CSV
tools/              everything needed to rebuild index.html
  build.py          runs the bank scripts, then assembles index.html
  sql_bank.py       PostgreSQL Exercises -> SQLite, with hand-ported date/string questions
  bank_sql_de.py    advanced analytics and data engineering SQL (verified against SQLite)
  gen_shop.py       generates the synthetic warehouse used by bank_sql_de.py
  bank_py.py        pandas problems
  bank_py_ml.py     scikit-learn and manufacturing problems
  bank_rsas.py      R and SAS problems (first set)
  bank_rsas2.py     R check modes, plus statistics, regression and manufacturing problems for R and SAS
  template.html, part_body.html, part_script.js, assemble2.py   page template and engine
```

To change or add problems, edit the relevant `bank_*.py` file and run `cd tools && python3 build.py`. Each problem is a small dictionary: language, skill, level (1 to 3), title, task text, optional setup code, starter code, hint, solution, and how to check it.

## Credits and license

The questions are adapted from four openly licensed sources, credited in full in [CREDITS.md](CREDITS.md):

- [PostgreSQL Exercises](https://pgexercises.com) by Alisdair Owens (CC BY-SA 3.0)
- [100 pandas puzzles](https://github.com/ajcr/100-pandas-puzzles) by Alex Riley (MIT)
- [Software Carpentry: R for Reproducible Scientific Analysis](https://swcarpentry.github.io/r-novice-gapminder/) (CC BY 4.0)
- [SAS Programming for R Users](https://github.com/sascommunities/sas-prog-for-r-users) by SAS Institute Inc. (CC BY 4.0)

Problems not marked as adapted are original.

- **Code** (the app and build tools) is under the [MIT License](LICENSE).
- **Question content** (problem text, solutions, hints and explanations) is under [CC BY-SA 4.0](LICENSE-CONTENT.md), as the share-alike terms of the SQL source require. Upstream notices are kept in CREDITS.md.

SAS is a registered trademark of SAS Institute Inc. This project is not affiliated with or endorsed by SAS Institute, The Carpentries or Anthropic.
