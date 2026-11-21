# Extends the R and SAS banks: check modes for running R in webR, plus new statistics,
# regression and manufacturing problems (original). Writes bank_r.json and bank_sas.json.
import json
base = json.load(open('bank_rsas.json'))
R = [p for p in base if p['lang'] == 'r']
S = [p for p in base if p['lang'] == 'sas']
byid = {p['id']: p for p in R}
GAP = '<p class="note"><code>gapminder</code> is loaded: one row per country and year, with columns <code>country</code>, <code>year</code>, <code>pop</code>, <code>continent</code>, <code>lifeExp</code>, <code>gdpPercap</code> (1,704 rows).</p>'

# How each existing R problem is checked when R runs in the browser:
#   last = value of the last expression, output = printed output, var:x / vars:a,b = objects, manual = no automatic check
modes = {'vec26':'last','meansd':'output','letters':'last','sub1':'last','sub2':'last','sub5':'last','seasia':'last','matrix':'last',
         'tail':'manual','popmil':'var:gapminder','six':'last','small':'var:gapminder_small','if2002':'manual',
         'cylsum':'last','bycountry':'last','sample2':'manual','long':'last','kelvin':'last','cv':'output','fahr':'last',
         'vecsum':'output','contloop':'output','fence':'last','countryloop':'output','cor':'last','ttest':'last','lm':'last'}
for k, m in modes.items(): byid['r-' + k]['rcheck'] = m

f = byid['r-fix']
f['body'] = '<p>Each line below has a bug. Fix all five and store the results in <code>q1</code> to <code>q5</code>.</p>' + GAP
f['starter'] = "# 1. Observations for the year 1957\nq1 <- gapminder[gapminder$year = 1957,]\n# 2. All columns except 1 through 4\nq2 <- gapminder[,-1:4]\n# 3. Rows where life expectancy is above 80\nq3 <- gapminder[gapminder$lifeExp > 80]\n# 4. First row, fourth and fifth columns\nq4 <- gapminder[1, 4, 5]\n# 5. Rows for the years 2002 and 2007\nq5 <- gapminder[gapminder$year == 2002 | 2007,]\n"
f['solution'] = "q1 <- gapminder[gapminder$year == 1957, ]\nq2 <- gapminder[, -c(1:4)]\nq3 <- gapminder[gapminder$lifeExp > 80, ]\nq4 <- gapminder[1, c(4, 5)]\nq5 <- gapminder[gapminder$year %in% c(2002, 2007), ]"
f['rcheck'] = 'vars:q1,q2,q3,q4,q5'
a = byid['r-africa']
a['body'] = '<p>With dplyr pipes, make a data frame <code>africa</code> with the African rows of <code>gapminder</code> and only the columns <code>year</code>, <code>country</code> and <code>lifeExp</code>, in that order. How many rows does it have?</p>' + GAP
a['solution'] = 'library(dplyr)\n\nafrica <- gapminder %>%\n  filter(continent == "Africa") %>%\n  select(year, country, lifeExp)\nnrow(africa)'
a['rcheck'] = 'var:africa'
b = byid['r-bycountry']
b['body'] = '<p>Calculate the average life expectancy per country (column <code>mean_lifeExp</code>). End with a data frame of just two rows: the countries with the shortest and the longest average.</p>' + GAP
c = byid['r-contloop']
c['body'] = '<p>Loop over the continents in <code>gapminder</code> (in the order <code>unique()</code> gives) and, for each, print a line with <code>cat()</code> in exactly this form:</p><pre>Average life expectancy in Asia is less than 50\nAverage life expectancy in Europe is greater than 50</pre>' + GAP
c['solution'] = 'threshold <- 50\nfor (cont in unique(gapminder$continent)) {\n  m <- mean(gapminder[gapminder$continent == cont, "lifeExp"])\n  if (m < threshold) {\n    cat("Average life expectancy in", cont, "is less than", threshold, "\\n")\n  } else {\n    cat("Average life expectancy in", cont, "is greater than", threshold, "\\n")\n  }\n}'
cl = byid['r-countryloop']
cl['body'] = '<p>Loop over each country in <code>gapminder</code> (in the order <code>unique()</code> gives) and print one line per country with <code>cat()</code>, using exactly one of these forms:</p><pre>Average life expectancy in X is less than 50\nAverage life expectancy in X is between 50 and 70\nAverage life expectancy in X is greater than 70</pre>' + GAP
t = byid['r-ttest']
t['body'] = '<p>Using the built-in <code>ToothGrowth</code> data, run a t-test comparing tooth <code>len</code> between the two supplement types (<code>supp</code>). End with a numeric vector of the t statistic and the p-value, rounded to 3 decimals.</p>'
t['solution'] = 'res <- t.test(len ~ supp, data = ToothGrowth)\nround(c(res$statistic, res$p.value), 3)'
lm = byid['r-lm']
lm.update(skill='models', level=2, body='<p>Fit a linear model of <code>mpg</code> on <code>wt</code> and <code>hp</code> using <code>mtcars</code>. End with a numeric vector of the three coefficients followed by the R-squared, all rounded to 3 decimals.</p>',
          solution='fit <- lm(mpg ~ wt + hp, data = mtcars)\nround(c(coef(fit), summary(fit)$r.squared), 3)', hint='<code>coef(fit)</code> for coefficients; <code>summary(fit)$r.squared</code> for R². Combine them with <code>c()</code>.')

def r(id, skill, level, title, body, solution, hint, rcheck='last', setup='', starter='', src='own'):
    R.append(dict(id='r-' + id, lang='r', skill=skill, level=level, title=title, body=body, setup=setup,
                  starter=starter, solution=solution, hint=hint, src=src, rcheck=rcheck))
END = '<p class="note">End with the value you want checked.</p>'

# ---------- Statistics
r('medianiqr','stats',1,'Robust summaries','<p><code>airquality$Ozone</code> has missing values. End with a vector of its median and its interquartile range, ignoring missing values.</p>'+END,
  'c(median(airquality$Ozone, na.rm = TRUE), IQR(airquality$Ozone, na.rm = TRUE))','Both functions take <code>na.rm = TRUE</code>.')
r('props','stats',1,'Proportions','<p>End with the proportion of cars with 4, 6 and 8 cylinders in <code>mtcars</code>, rounded to 3 decimals.</p>'+END,
  'round(prop.table(table(mtcars$cyl)), 3)','<code>prop.table(table(x))</code>.')
r('ci','stats',2,'Confidence interval','<p>End with the 95% confidence interval for the mean <code>mpg</code> in <code>mtcars</code> (a one-sample t interval), rounded to 2 decimals.</p>'+END,
  'round(t.test(mtcars$mpg)$conf.int, 2)','<code>t.test(x)$conf.int</code>.')
r('chisq','stats',2,'Chi-square test','<p>Test whether transmission (<code>am</code>) and engine shape (<code>vs</code>) are independent in <code>mtcars</code> with a chi-square test on their 2×2 table. End with the p-value rounded to 4 decimals.</p>'+END,
  'round(chisq.test(table(mtcars$am, mtcars$vs))$p.value, 4)','<code>chisq.test(table(a, b))</code> applies the continuity correction for 2×2 tables by default.')
r('paired','stats',2,'Paired t-test','<p>The built-in <code>sleep</code> data has the extra hours of sleep for 10 patients under two drugs (<code>group</code> 1 and 2). Run a <b>paired</b> t-test of group 1 against group 2 and end with the p-value rounded to 4 decimals.</p>'+END,
  'with(sleep, round(t.test(extra[group == 1], extra[group == 2], paired = TRUE)$p.value, 4))','Pass the two vectors and <code>paired = TRUE</code>.')
r('anova','stats',3,'One-way ANOVA','<p>Using <code>PlantGrowth</code>, fit a one-way ANOVA of <code>weight</code> by <code>group</code>. End with a vector of the F statistic and its p-value, rounded to 4 decimals.</p>'+END,
  'fit <- aov(weight ~ group, data = PlantGrowth)\ns <- summary(fit)[[1]]\nround(c(s[["F value"]][1], s[["Pr(>F)"]][1]), 4)','<code>summary(aov(...))[[1]]</code> is a table with columns <code>"F value"</code> and <code>"Pr(&gt;F)"</code>.')
r('tukey','stats',3,'Post-hoc comparisons','<p>After the PlantGrowth ANOVA, run Tukey\'s HSD. End with the adjusted p-value for the comparison <code>trt2-trt1</code>, rounded to 4 decimals.</p>'+END,
  'tk <- TukeyHSD(aov(weight ~ group, data = PlantGrowth))\nround(tk$group["trt2-trt1", "p adj"], 4)','<code>TukeyHSD(fit)$group</code> is a matrix with rows like <code>"trt2-trt1"</code>.')
# ---------- Regression models
r('slope','models',1,'Simple regression slope','<p>Using the built-in <code>cars</code> data, fit <code>dist ~ speed</code> and end with the slope rounded to 3 decimals.</p>'+END,
  'fit <- lm(dist ~ speed, data = cars)\nround(coef(fit)[["speed"]], 3)','<code>coef(fit)</code> is a named vector.')
r('predict','models',2,'Prediction interval','<p>With the same <code>dist ~ speed</code> model, end with the predicted stopping distance at speed 21 and its 95% <b>prediction</b> interval (fit, lower, upper), rounded to 2 decimals.</p>'+END,
  'fit <- lm(dist ~ speed, data = cars)\nround(predict(fit, data.frame(speed = 21), interval = "prediction"), 2)','<code>predict(fit, newdata, interval = "prediction")</code>.')
r('glm','models',2,'Logistic regression','<p>Fit a logistic regression of <code>am</code> (manual transmission) on <code>wt</code> and <code>hp</code> using <code>mtcars</code>. End with the coefficients rounded to 3 decimals.</p>'+END,
  'fit <- glm(am ~ wt + hp, data = mtcars, family = binomial)\nround(coef(fit), 3)','<code>glm(..., family = binomial)</code>.')
r('glmprob','models',3,'Predicted probability','<p>Using the logistic model of <code>am</code> on <code>wt</code> and <code>hp</code>, end with the predicted probability of a manual transmission for a car with <code>wt = 2.5</code> and <code>hp = 120</code>, rounded to 3 decimals.</p>'+END,
  'fit <- glm(am ~ wt + hp, data = mtcars, family = binomial)\nround(predict(fit, data.frame(wt = 2.5, hp = 120), type = "response"), 3)','<code>type = "response"</code> returns probabilities instead of log-odds.')
r('cvrmse','models',3,'Cross-validated RMSE','<p>Estimate the out-of-sample error of <code>lm(mpg ~ wt + hp)</code> on <code>mtcars</code> with 5-fold cross-validation. Run <code>set.seed(42)</code>, then assign folds with <code>folds &lt;- sample(rep(1:5, length.out = nrow(mtcars)))</code>. For each fold, fit on the other folds and predict the held-out rows. End with the RMSE over all held-out predictions, rounded to 3 decimals.</p>'+END,
  'set.seed(42)\nfolds <- sample(rep(1:5, length.out = nrow(mtcars)))\npred <- numeric(nrow(mtcars))\nfor (k in 1:5) {\n  fit <- lm(mpg ~ wt + hp, data = mtcars[folds != k, ])\n  pred[folds == k] <- predict(fit, mtcars[folds == k, ])\n}\nround(sqrt(mean((pred - mtcars$mpg)^2)), 3)','Fill a prediction vector fold by fold, then compute <code>sqrt(mean((pred - actual)^2))</code> once at the end.')
# ---------- Manufacturing & quality
SHAFTS_R = """set.seed(7)
shafts <- data.frame(subgroup = rep(1:25, each = 5),
                     diameter = round(rnorm(125, mean = 25.00, sd = 0.012), 4))
shifted <- shafts$subgroup %in% 18:20
shafts$diameter[shifted] <- shafts$diameter[shifted] + 0.025   # a tool shift
LSL <- 24.95; USL <- 25.05
A2 <- 0.577   # control chart constant for subgroups of 5"""
DEFECTS_R = """defects <- data.frame(
  line = rep(c("A", "B", "C"), each = 6),
  day = rep(rep(1:3, each = 2), times = 3),
  shift = rep(c("Day", "Night"), times = 9),
  units = c(520, 480, 510, 470, 530, 490, 600, 580, 610, 590, 605, 575, 450, 430, 460, 440, 455, 445),
  defective = c(12, 19, 10, 22, 14, 18, 9, 11, 8, 12, 10, 13, 20, 26, 18, 41, 22, 24)
)"""
CAUSES_R = 'causes <- rep(c("scratch", "dent", "misalign", "porosity", "burr", "other"),\n              times = c(48, 31, 17, 12, 6, 4))'
OEE_R = """oee_log <- data.frame(
  machine = rep(c("CNC1", "CNC2", "Press1"), each = 3),
  planned_min = 480,
  downtime_min = c(35, 50, 20, 90, 60, 75, 15, 25, 10),
  ideal_cycle_s = rep(c(30, 30, 12), each = 3),
  total_count = c(780, 760, 820, 640, 700, 650, 2100, 2050, 2180),
  good_count = c(765, 741, 806, 610, 676, 630, 2080, 2021, 2166)
)"""
r('defrate','mfg',1,'Defect rate by line','<p><code>defects</code> records units produced and defective units per line, day and shift. With dplyr, end with a data frame of <code>line</code> and <code>rate</code> (total defective ÷ total units), rounded to 4 decimals.</p>'+END,
  'library(dplyr)\ndefects %>%\n  group_by(line) %>%\n  summarise(rate = round(sum(defective) / sum(units), 4))','Sum first, then divide: <code>sum(defective) / sum(units)</code>. Averaging per-row rates gives a different answer.',setup=DEFECTS_R)
r('cpk','mfg',1,'Process capability','<p>Using all shaft <code>diameter</code>s and the spec limits <code>LSL</code> and <code>USL</code>, compute Cp = (USL − LSL) / 6σ and Cpk = min(USL − μ, μ − LSL) / 3σ, with σ the sample standard deviation. End with <code>c(Cp, Cpk)</code> rounded to 3 decimals.</p>'+END,
  'mu <- mean(shafts$diameter)\ns <- sd(shafts$diameter)\nround(c((USL - LSL) / (6 * s), min(USL - mu, mu - LSL) / (3 * s)), 3)','<code>sd()</code> is the sample standard deviation.',setup=SHAFTS_R)
r('pareto','mfg',2,'Pareto of defect causes','<p><code>causes</code> lists the cause of every defect found this month. End with a data frame of <code>cause</code>, <code>n</code> and <code>cum_pct</code> (cumulative percent of all defects, rounded to 1), sorted from most to least frequent.</p>'+END,
  'tab <- sort(table(causes), decreasing = TRUE)\ndata.frame(cause = names(tab), n = as.integer(tab), cum_pct = round(100 * cumsum(tab) / sum(tab), 1))','<code>sort(table(x), decreasing = TRUE)</code>, then <code>cumsum()</code>.',setup=CAUSES_R)
r('xbar','mfg',2,'X-bar chart limits','<p>Compute each subgroup\'s mean and range for the shaft data. The centre line is the mean of the subgroup means; the limits are CL ± A2 × R̄ (R̄ = mean range). End with <code>c(LCL, CL, UCL)</code> rounded to 4 decimals.</p>'+END,
  'means <- tapply(shafts$diameter, shafts$subgroup, mean)\nranges <- tapply(shafts$diameter, shafts$subgroup, function(x) diff(range(x)))\ncl <- mean(means); rbar <- mean(ranges)\nround(c(cl - A2 * rbar, cl, cl + A2 * rbar), 4)','<code>tapply(values, groups, fun)</code> gives one value per subgroup; <code>diff(range(x))</code> is the range.',setup=SHAFTS_R)
r('ooc','mfg',2,'Out-of-control subgroups','<p>Using the X-bar limits for the shaft data, end with an integer vector of the subgroups whose mean falls outside the limits.</p>'+END,
  'means <- tapply(shafts$diameter, shafts$subgroup, mean)\nranges <- tapply(shafts$diameter, shafts$subgroup, function(x) diff(range(x)))\ncl <- mean(means); rbar <- mean(ranges)\nas.integer(names(means)[means > cl + A2 * rbar | means < cl - A2 * rbar])','The names of the <code>tapply</code> result are the subgroup numbers.',setup=SHAFTS_R)
r('pchart','mfg',3,'p-chart with varying sample sizes','<p>Treat each row of <code>defects</code> as a sample. With p̄ = total defective ÷ total units, each row\'s limits are p̄ ± 3·√(p̄(1 − p̄)/n), with the lower limit floored at 0. End with a data frame of the out-of-control rows: <code>line</code>, <code>day</code>, <code>shift</code> and <code>p</code> (rounded to 4).</p>'+END,
  'pbar <- sum(defects$defective) / sum(defects$units)\np <- defects$defective / defects$units\nse <- sqrt(pbar * (1 - pbar) / defects$units)\nout <- p > pbar + 3 * se | p < pmax(0, pbar - 3 * se)\ndata.frame(line = defects$line[out], day = defects$day[out], shift = defects$shift[out], p = round(p[out], 4))','Compute p̄ once, then vectorised limits per row using each row\'s <code>units</code>.',setup=DEFECTS_R)
r('runs','mfg',3,'Run rule: eight on one side','<p>A common control chart rule flags a process when 8 consecutive subgroup means fall on the same side of the centre line. In this version of the shaft data the process also drifts upward from subgroup 12. Using the mean of all subgroup means as the centre line, end with the subgroup number at which the first such run reaches its 8th point, or <code>NA</code> if there is none.</p>'+END,
  'means <- tapply(shafts$diameter, shafts$subgroup, mean)\nside <- sign(means - mean(means))\nruns <- rle(as.vector(side))\nends <- cumsum(runs$lengths)\nk <- which(runs$lengths >= 8)[1]\nif (is.na(k)) NA else ends[k] - runs$lengths[k] + 8','<code>rle()</code> finds runs of equal values; <code>cumsum(lengths)</code> gives where each run ends.',setup=SHAFTS_R+'\ndrift <- shafts$subgroup >= 12\nshafts$diameter[drift] <- shafts$diameter[drift] + 0.015   # slow upward drift')
r('oee','mfg',3,'Overall equipment effectiveness','<p>Sum each machine\'s three shifts in <code>oee_log</code>, then compute availability = (planned − downtime) / planned, performance = ideal_cycle_s × total / (run minutes × 60), quality = good / total and oee = the product of the three. End with a data frame of <code>machine</code>, <code>availability</code>, <code>performance</code>, <code>quality</code>, <code>oee</code>, rounded to 3 and sorted by oee, highest first.</p>'+END,
  'library(dplyr)\noee_log %>%\n  group_by(machine) %>%\n  summarise(planned = sum(planned_min), down = sum(downtime_min), cycle = first(ideal_cycle_s),\n            total = sum(total_count), good = sum(good_count)) %>%\n  mutate(run = planned - down,\n         availability = run / planned,\n         performance = cycle * total / (run * 60),\n         quality = good / total,\n         oee = availability * performance * quality) %>%\n  arrange(desc(oee)) %>%\n  transmute(machine, availability = round(availability, 3), performance = round(performance, 3),\n            quality = round(quality, 3), oee = round(oee, 3))','<code>summarise()</code> the shifts first, then <code>mutate()</code> the three ratios.',setup=OEE_R)

# ================= SAS
def s(id, skill, level, title, body, solution, hint, starter='', src='own'):
    S.append(dict(id='sas-' + id, lang='sas', skill=skill, level=level, title=title, body=body, starter=starter,
                  solution=solution, hint=hint, src=src))
HEART = '<p class="note"><code>sashelp.heart</code> is the Framingham Heart Study sample (5,209 rows) with columns including <code>Status</code> (Alive/Dead), <code>Sex</code>, <code>AgeAtStart</code>, <code>Cholesterol</code>, <code>Systolic</code>, <code>Smoking</code>.</p>'
SHAFTS_SAS = """data work.shafts;
   call streaminit(7);
   do subgroup = 1 to 25;
      do unit = 1 to 5;
         diameter = round(rand('normal', 25, 0.012), 0.0001);
         if 18 <= subgroup <= 20 then diameter = diameter + 0.025;
         output;
      end;
   end;
   drop unit;
run;
"""
s('univariate','stats',1,'Distribution and normality','<p>Use PROC UNIVARIATE to describe <code>Cholesterol</code> in <code>sashelp.heart</code>, request tests for normality, and draw a histogram with a fitted normal curve.</p>'+HEART,
  'proc univariate data=sashelp.heart normal;\n   var Cholesterol;\n   histogram Cholesterol / normal;\nrun;','The <code>NORMAL</code> option on the PROC statement adds the tests; <code>histogram var / normal;</code> overlays the curve.')
s('meanci','stats',1,'Means with confidence limits','<p>Use PROC MEANS to report N, mean and the 95% confidence limits of <code>MPG_Highway</code> for each <code>Origin</code> in <code>sashelp.cars</code>.</p>',
  'proc means data=sashelp.cars n mean clm;\n   class Origin;\n   var MPG_Highway;\nrun;','<code>CLM</code> requests two-sided confidence limits for the mean.')
s('freqchisq','stats',2,'Chi-square test of association','<p>Use PROC FREQ to test whether <code>Sex</code> and <code>Status</code> are associated in <code>sashelp.heart</code>. Show the two-way table with row percents only.</p>'+HEART,
  'proc freq data=sashelp.heart;\n   tables Sex*Status / chisq nocol nopercent;\nrun;','<code>tables a*b / chisq;</code>. <code>NOCOL NOPERCENT</code> leave only row percents.')
s('npar','stats',2,'Nonparametric comparison','<p>Use a Wilcoxon rank-sum test to compare <code>height</code> between the sexes in <code>sashelp.class</code>.</p>',
  'proc npar1way data=sashelp.class wilcoxon;\n   class sex;\n   var height;\nrun;','PROC NPAR1WAY with the <code>WILCOXON</code> option.')
s('logistic','stats',3,'Logistic regression','<p>Model the probability that <code>Status</code> is "Dead" in <code>sashelp.heart</code> from <code>AgeAtStart</code>, <code>Cholesterol</code> and <code>Sex</code> (reference level Female). Report odds ratios.</p>'+HEART,
  "proc logistic data=sashelp.heart;\n   class Sex(ref='Female') / param=ref;\n   model Status(event='Dead') = AgeAtStart Cholesterol Sex;\n   oddsratio Sex;\nrun;","<code>model Status(event='Dead') = ...;</code> sets which outcome is modelled. Put <code>Sex</code> in a <code>CLASS</code> statement with <code>ref=</code>.")
s('glmselect','stats',3,'Stepwise model selection','<p>Use PROC GLMSELECT on <code>sashelp.cars</code> to choose predictors of <code>MPG_Highway</code> from <code>Horsepower</code>, <code>Weight</code>, <code>EngineSize</code>, <code>Cylinders</code>, <code>Wheelbase</code> and <code>Length</code> with stepwise selection using significance level 0.05 to enter and to stay.</p>',
  'proc glmselect data=sashelp.cars;\n   model MPG_Highway = Horsepower Weight EngineSize Cylinders Wheelbase Length\n         / selection=stepwise(select=sl sle=0.05 sls=0.05);\nrun;','<code>selection=stepwise(select=sl sle=0.05 sls=0.05)</code> on the MODEL statement.')
s('shafts','mfg',1,'Simulate process data','<p>Create <code>work.shafts</code> with 25 subgroups of 5 shaft diameters each, drawn from a normal distribution with mean 25 and standard deviation 0.012 (seed 7, rounded to 0.0001). Subgroups 18 to 20 have a tool shift: add 0.025 to their diameters. Then report the overall mean and standard deviation.</p>',
  SHAFTS_SAS+'\nproc means data=work.shafts mean std maxdec=4;\n   var diameter;\nrun;','Nested DO loops with <code>output;</code> inside; <code>rand(\'normal\', mean, sd)</code>.')
s('cpk','mfg',2,'Cp and Cpk','<p>Starting from <code>work.shafts</code> (code given), compute Cp = (USL − LSL) / 6σ and Cpk = min(USL − μ, μ − LSL) / 3σ with LSL = 24.95 and USL = 25.05. Use PROC MEANS with an OUTPUT statement, then a DATA step, and print the result.</p>',
  SHAFTS_SAS+'\nproc means data=work.shafts noprint;\n   var diameter;\n   output out=work.stats mean=mu std=sigma;\nrun;\n\ndata work.capability;\n   set work.stats;\n   lsl = 24.95; usl = 25.05;\n   cp = (usl - lsl) / (6 * sigma);\n   cpk = min(usl - mu, mu - lsl) / (3 * sigma);\nrun;\n\nproc print data=work.capability noobs;\n   var mu sigma cp cpk;\nrun;',
  '<code>output out=... mean=mu std=sigma;</code> writes one row of statistics you can compute with in a DATA step.',starter=SHAFTS_SAS)
s('xbar','mfg',2,'X-bar and R chart','<p>Draw X-bar and R control charts of <code>diameter</code> by <code>subgroup</code> for <code>work.shafts</code> (code given) and list any tests that are triggered.</p><p class="note">This uses PROC SHEWHART from SAS/QC.</p>',
  SHAFTS_SAS+'\nproc shewhart data=work.shafts;\n   xrchart diameter*subgroup / tests=1 to 8;\nrun;','<code>xrchart process*subgroup;</code> draws both charts. <code>tests=1 to 8</code> applies the Western Electric run tests.',starter=SHAFTS_SAS)
s('limits','mfg',3,'Control limits by hand','<p>Without SAS/QC: compute each subgroup\'s mean and range from <code>work.shafts</code> (code given), then the centre line CL = mean of subgroup means and limits CL ± 0.577 × R̄. Print the subgroups whose mean is outside the limits.</p>',
  SHAFTS_SAS+'\nproc means data=work.shafts noprint nway;\n   class subgroup;\n   var diameter;\n   output out=work.sub mean=xbar range=r;\nrun;\n\nproc sql;\n   select subgroup, xbar\n   from work.sub,\n        (select mean(xbar) as cl, mean(r) as rbar from work.sub)\n   where xbar > cl + 0.577 * rbar or xbar < cl - 0.577 * rbar\n   order by subgroup;\nquit;',
  'PROC MEANS with <code>class subgroup; output out= mean= range=;</code>, then join the per-subgroup table to a one-row summary in PROC SQL.',starter=SHAFTS_SAS)
DEF_SAS = """data work.defects;
   input line $ day shift $ units defective;
   datalines;
A 1 Day 520 12
A 1 Night 480 19
A 2 Day 510 10
A 2 Night 470 22
A 3 Day 530 14
A 3 Night 490 18
B 1 Day 600 9
B 1 Night 580 11
B 2 Day 610 8
B 2 Night 590 12
B 3 Day 605 10
B 3 Night 575 13
C 1 Day 450 20
C 1 Night 430 26
C 2 Day 460 18
C 2 Night 440 41
C 3 Day 455 22
C 3 Night 445 24
;
run;
"""
s('defrate','mfg',1,'Defect rate by line and shift','<p>Using <code>work.defects</code> (code given), use PROC SQL to report the total units, total defective and defect rate (formatted as a percent with 2 decimals) for each line and shift.</p>',
  DEF_SAS+'\nproc sql;\n   select line, shift, sum(units) as units, sum(defective) as defective,\n          sum(defective) / sum(units) as rate format=percent8.2\n   from work.defects\n   group by line, shift\n   order by line, shift;\nquit;','Divide the sums, not the row rates. <code>format=percent8.2</code> displays a percentage.',starter=DEF_SAS)
s('pareto','mfg',2,'Pareto table','<p>Defect causes this month were: scratch 48, dent 31, misalign 17, porosity 12, burr 6, other 4. Enter these counts with DATALINES and use PROC FREQ to list the causes from most to least frequent with cumulative percents.</p>',
  'data work.causes;\n   input cause $ count;\n   datalines;\nscratch 48\ndent 31\nmisalign 17\nporosity 12\nburr 6\nother 4\n;\nrun;\n\nproc freq data=work.causes order=freq;\n   tables cause;\n   weight count;\nrun;','<code>WEIGHT count;</code> treats each row as that many observations; <code>ORDER=FREQ</code> sorts by frequency.')
s('capability','mfg',3,'Capability analysis procedure','<p>Use PROC CAPABILITY on <code>work.shafts</code> (code given) with spec limits 24.95 and 25.05 and target 25 to report capability indices and a histogram with the spec limits drawn.</p><p class="note">This uses PROC CAPABILITY from SAS/QC.</p>',
  SHAFTS_SAS+'\nproc capability data=work.shafts;\n   specs lsl=24.95 usl=25.05 target=25;\n   var diameter;\n   histogram diameter / normal;\nrun;','The <code>SPECS</code> statement sets the limits; the indices table appears automatically.',starter=SHAFTS_SAS)
s('oee','mfg',3,'OEE with PROC SQL','<p>Enter the machine log below with DATALINES. With PROC SQL, sum each machine\'s shifts and compute availability = (planned − downtime) / planned, performance = ideal_cycle_s × total / ((planned − downtime) × 60), quality = good / total and OEE = their product. Sort by OEE, highest first.</p><pre>CNC1 480 35 30 780 765\nCNC1 480 50 30 760 741\nCNC1 480 20 30 820 806\nCNC2 480 90 30 640 610\nCNC2 480 60 30 700 676\nCNC2 480 75 30 650 630\nPress1 480 15 12 2100 2080\nPress1 480 25 12 2050 2021\nPress1 480 10 12 2180 2166</pre>',
  'data work.oee_log;\n   input machine $ planned_min downtime_min ideal_cycle_s total_count good_count;\n   datalines;\nCNC1 480 35 30 780 765\nCNC1 480 50 30 760 741\nCNC1 480 20 30 820 806\nCNC2 480 90 30 640 610\nCNC2 480 60 30 700 676\nCNC2 480 75 30 650 630\nPress1 480 15 12 2100 2080\nPress1 480 25 12 2050 2021\nPress1 480 10 12 2180 2166\n;\nrun;\n\nproc sql;\n   select machine,\n          (sum(planned_min) - sum(downtime_min)) / sum(planned_min) as availability format=6.3,\n          max(ideal_cycle_s) * sum(total_count) / ((sum(planned_min) - sum(downtime_min)) * 60) as performance format=6.3,\n          sum(good_count) / sum(total_count) as quality format=6.3,\n          calculated availability * calculated performance * calculated quality as oee format=6.3\n   from work.oee_log\n   group by machine\n   order by oee desc;\nquit;','In PROC SQL, refer to a column you just computed with the <code>CALCULATED</code> keyword.')

json.dump(R, open('bank_r.json', 'w'), indent=1)
json.dump(S, open('bank_sas.json', 'w'), indent=1)
from collections import Counter
print('R', len(R), sorted(Counter((p['skill'], p['level']) for p in R).items()))
print('SAS', len(S), sorted(Counter((p['skill'], p['level']) for p in S).items()))
print('missing rcheck:', [p['id'] for p in R if 'rcheck' not in p])
