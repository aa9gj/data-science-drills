# Credits

This project stands on generously licensed teaching material and open-source software. Thank you to everyone below.

## Question sources

### SQL: PostgreSQL Exercises

- **Work:** PostgreSQL Exercises, https://pgexercises.com (source: https://github.com/AlisdairO/pgexercises)
- **Author:** Alisdair Owens
- **License:** questions and explanations: [CC BY-SA 3.0 US](https://creativecommons.org/licenses/by-sa/3.0/us/); database and site code: BSD 2-Clause (reproduced below)
- **Used for:** 58 SQL problems in the skills Retrieving data, Joins & subqueries, Aggregation, Window functions & recursion, Text functions, and Dates & times. Also the club database in `data/club.sql.txt`.
- **Changes:** converted the database from PostgreSQL to SQLite; removed the `cd.` schema (queries that still use it work); rewrote 18 reference queries that relied on PostgreSQL-only features (`EXTRACT`, `DATE_TRUNC`, intervals, `generate_series`, `ROLLUP`, `LPAD`, `TRANSLATE`, regex) using SQLite functions, and rewrote the matching question text and hints; dropped three questions about PostgreSQL's timestamp and interval types and the data-modification category; assigned difficulty levels; added SQLite notes to some explanations.

```
Copyright (c) 2013-2014, Alisdair Owens
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

### Python: 100 pandas puzzles

- **Work:** 100 pandas puzzles, https://github.com/ajcr/100-pandas-puzzles
- **Author:** Alex Riley and contributors
- **License:** MIT (reproduced below)
- **Used for:** 42 pandas problems in the skills Selecting & filtering, Changing data, Grouping & sorting, Cleaning messy data, Dates & time series, and MultiIndex.
- **Changes:** reworded puzzles as self-contained tasks; moved the data setup into code that runs before your answer; replaced APIs removed in pandas 2 (`sum(level=...)`, `resample('M')`, `is_lexsorted`); rewrote solutions that relied on chained assignment; fixed small inconsistencies in puzzle text; changed one filter threshold so it returns rows; assigned difficulty levels.

```
MIT License

Copyright (c) 2018 Alex Riley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### R: Software Carpentry, R for Reproducible Scientific Analysis

- **Work:** Software Carpentry: R for Reproducible Scientific Analysis, https://swcarpentry.github.io/r-novice-gapminder/ (source: https://github.com/swcarpentry/r-novice-gapminder)
- **Authors:** The Carpentries and the lesson's contributors. Cite as: Naupaka Zimmerman, Greg Wilson, Raniere Silva, Scott Ritchie, François Michonneau, Jeffrey Oliver, … Yuka Takemon. (2019). *Software Carpentry: R for Reproducible Scientific Analysis*. Zenodo. https://doi.org/10.5281/zenodo.3265164
- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Used for:** 22 R problems built from the lesson's challenges on vectors, subsetting, data frames, control flow, functions, vectorisation, dplyr and tidyr.
- **Changes:** reworded challenges as self-contained tasks with an automatic check; asked for named results where a challenge had several parts; specified exact output formats for loop exercises; replaced discussion questions with coding tasks; assigned difficulty levels.

### R data: gapminder

- `data/gapminder.csv` is `gapminder_data.csv` from the Software Carpentry lesson above (CC BY 4.0), based on data from the [Gapminder Foundation](https://www.gapminder.org) (CC BY 4.0).

### SAS: SAS Programming for R Users

- **Work:** SAS Programming for R Users (course notes and exercise programs), https://github.com/sascommunities/sas-prog-for-r-users
- **Author:** SAS Institute Inc. (Copyright 2016 SAS Institute Inc.)
- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Used for:** 19 SAS problems adapted from the course exercises in chapters 2 to 6 (creating and importing data, formats and labels, new variables and functions, subsetting and stacking tables, DO loops and simulation, plotting, summary procedures, macro variables, regression and ANOVA).
- **Changes:** reworded exercises as self-contained tasks; pointed them at `sashelp` tables and the WORK library instead of the course's `sp4r` library and data files; substituted `sashelp.cars` for course datasets in some exercises; combined or split multi-part exercises; assigned difficulty levels.

SAS is a registered trademark of SAS Institute Inc.

### Original problems

All other problems are original to this project: the SQL advanced analytics and data engineering sets (with the synthetic warehouse made by `tools/gen_shop.py`); the scikit-learn and manufacturing problems in Python; the statistics, regression and manufacturing problems in R and SAS; and a few others marked "original" in the app. They use built-in datasets from R (`mtcars`, `airquality`, `ToothGrowth`, `PlantGrowth`, `sleep`, `cars`), SAS (`sashelp`) and scikit-learn (iris, wine, breast cancer and diabetes, which ship with scikit-learn), or synthetic data generated with a fixed seed.

## Software

The app runs entirely in the browser using:

- [sql.js](https://sql.js.org): SQLite compiled to JavaScript (MIT)
- [Pyodide](https://pyodide.org): Python in WebAssembly (MPL-2.0), with [pandas](https://pandas.pydata.org), [NumPy](https://numpy.org), [SciPy](https://scipy.org) and [scikit-learn](https://scikit-learn.org) (BSD 3-Clause)
- [webR](https://docs.r-wasm.org/webr/latest/): R in WebAssembly (webR binaries GPL-3; supporting code MIT), with [dplyr](https://dplyr.tidyverse.org) and [tidyr](https://tidyr.tidyverse.org) (MIT)
- [Anthropic TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript) (MIT), loaded only if you add an API key
- [Instrument Sans](https://fonts.google.com/specimen/Instrument+Sans) and [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) (SIL Open Font License)

These are loaded from public CDNs and are not redistributed in this repository.
