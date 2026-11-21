# Machine learning (scikit-learn) and manufacturing analytics problems in Python. All original.
import json
P = []
def add(id, skill, level, title, body, setup, solution, hint, check='expr', ordered=False, pkgs=('scikit-learn',)):
    P.append(dict(id='py-' + id, lang='py', skill=skill, level=level, title=title, body=body, setup=setup,
                  starter='# Write your code below. The value of your last line is checked.\n', solution=solution,
                  hint=hint, check=check, ordered=ordered, src='own', pkgs=list(pkgs)))
EXPR = '<p class="note">End with an expression; the value of your last line is checked.</p>'

IRIS = "from sklearn.datasets import load_iris\nfrom sklearn.model_selection import train_test_split\nX, y = load_iris(return_X_y=True)"
IRIS_SPLIT = IRIS + "\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)"
DIAB = "from sklearn.datasets import load_diabetes\nfrom sklearn.model_selection import train_test_split\nX, y = load_diabetes(return_X_y=True)\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)"
CANCER = "from sklearn.datasets import load_breast_cancer\nfrom sklearn.model_selection import train_test_split\nX, y = load_breast_cancer(return_X_y=True)\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)"
WINE = "from sklearn.datasets import load_wine\nX, y = load_wine(return_X_y=True)"

SENSORS = """rng = np.random.RandomState(7)
n = 600
sensors = pd.DataFrame({
    'machine_id': rng.choice(['M1', 'M2', 'M3', 'M4'], n),
    'temp': rng.normal(70, 5, n).round(1),
    'vibration': rng.gamma(2.0, 0.5, n).round(3),
    'pressure': rng.normal(30, 3, n).round(2),
    'hours_since_service': rng.randint(0, 500, n),
})
risk = (0.04 * (sensors['temp'] - 70) + 1.5 * (sensors['vibration'] - 1)
        + 0.006 * (sensors['hours_since_service'] - 250)
        + 0.5 * (sensors['machine_id'] == 'M3'))
sensors['failure'] = (risk + rng.normal(0, 0.6, n) > 1.2).astype(int)
FEATURES = ['temp', 'vibration', 'pressure', 'hours_since_service']"""
SENSORS_SPLIT = SENSORS + "\nfrom sklearn.model_selection import train_test_split\nX_train, X_test, y_train, y_test = train_test_split(\n    sensors[FEATURES], sensors['failure'], test_size=0.3, random_state=0, stratify=sensors['failure'])"
SHAFTS = """rng = np.random.RandomState(3)
shafts = pd.DataFrame({'subgroup': np.repeat(np.arange(1, 26), 5),
                       'diameter': rng.normal(25.0, 0.012, 125).round(4)})
shafts.loc[shafts['subgroup'].between(18, 20), 'diameter'] += 0.025   # a tool shift
LSL, USL = 24.95, 25.05
A2 = 0.577   # control chart constant for subgroups of 5"""
TEMPS = """rng = np.random.RandomState(11)
idx = pd.date_range('2025-03-03 00:00', periods=288, freq='5min')
temps = pd.Series(70 + np.sin(np.arange(288) / 30) * 2 + rng.normal(0, 0.4, 288), index=idx).round(2)
temps.iloc[[60, 150, 151, 240]] += [6.0, 5.0, 4.5, 7.0]   # spikes"""
OEE = """oee_log = pd.DataFrame({
    'machine': ['CNC1'] * 3 + ['CNC2'] * 3 + ['Press1'] * 3,
    'planned_min': [480] * 9,
    'downtime_min': [35, 50, 20, 90, 60, 75, 15, 25, 10],
    'ideal_cycle_s': [30] * 6 + [12] * 3,
    'total_count': [780, 760, 820, 640, 700, 650, 2100, 2050, 2180],
    'good_count': [765, 741, 806, 610, 676, 630, 2080, 2021, 2166],
})"""
HOUSES = """houses = pd.DataFrame({
    'city': ['Austin', 'Austin', 'Denver', 'Denver', 'Boston', 'Boston', 'Austin', 'Denver', 'Boston', 'Austin', 'Denver', 'Boston'],
    'sqft': [1400, 2100, 1600, 2500, 1200, 1900, 1750, 1300, 2300, 2600, 2000, 1500],
    'beds': [3, 4, 3, 4, 2, 3, 3, 2, 4, 5, 3, 3],
    'price': [410, 590, 450, 690, 520, 760, 480, 380, 880, 700, 560, 610],   # thousands of dollars
})
new_house = pd.DataFrame({'city': ['Denver'], 'sqft': [1800], 'beds': [3]})"""

# ---------- Supervised learning
add('ml-split','ml',1,'Train/test split',f'<p>Split the iris data into train and test sets with 25% for testing, <code>random_state=0</code>, stratified on <code>y</code>. Name them <code>X_train, X_test, y_train, y_test</code> and end with <code>(X_train.shape, X_test.shape)</code>.</p>'+EXPR,IRIS,
    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)\n(X_train.shape, X_test.shape)",'<code>train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)</code> returns four arrays in that order.')
add('ml-knn','ml',1,'k-nearest neighbours','<p>Fit a <code>KNeighborsClassifier(n_neighbors=5)</code> on the training set and return its accuracy on the test set, rounded to 3 decimals.</p>'+EXPR,IRIS_SPLIT,
    "from sklearn.neighbors import KNeighborsClassifier\nmodel = KNeighborsClassifier(n_neighbors=5).fit(X_train, y_train)\nround(model.score(X_test, y_test), 3)",'For classifiers, <code>model.score(X_test, y_test)</code> is accuracy.')
add('ml-linreg','ml',1,'Linear regression R²','<p>Fit a <code>LinearRegression</code> on the diabetes training set and return R² on the test set, rounded to 3 decimals.</p>'+EXPR,DIAB,
    "from sklearn.linear_model import LinearRegression\nmodel = LinearRegression().fit(X_train, y_train)\nround(model.score(X_test, y_test), 3)",'For regressors, <code>model.score()</code> returns R².')
add('ml-confusion','ml',2,'Confusion matrix','<p>Fit <code>LogisticRegression(max_iter=5000)</code> on the breast cancer training set and return the confusion matrix of its test predictions (a 2×2 array).</p>'+EXPR,CANCER,
    "from sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import confusion_matrix\nmodel = LogisticRegression(max_iter=5000).fit(X_train, y_train)\nconfusion_matrix(y_test, model.predict(X_test))",'<code>confusion_matrix(y_true, y_pred)</code>; rows are true classes, columns predicted.')
add('ml-prf','ml',2,'Precision, recall and F1','<p>With the same model as above (<code>LogisticRegression(max_iter=5000)</code> on the breast cancer split), return a tuple of precision, recall and F1 for class 1 on the test set, each rounded to 3 decimals.</p>'+EXPR,CANCER,
    "from sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import precision_score, recall_score, f1_score\npred = LogisticRegression(max_iter=5000).fit(X_train, y_train).predict(X_test)\n(round(precision_score(y_test, pred), 3), round(recall_score(y_test, pred), 3), round(f1_score(y_test, pred), 3))",'<code>precision_score</code>, <code>recall_score</code> and <code>f1_score</code> default to the positive class 1.')
add('ml-rmse','ml',2,'Regularised regression RMSE','<p>Fit <code>Ridge(alpha=1.0)</code> on the diabetes training set and return the test RMSE (root mean squared error), rounded to 2 decimals.</p>'+EXPR,DIAB,
    "from sklearn.linear_model import Ridge\nfrom sklearn.metrics import mean_squared_error\npred = Ridge(alpha=1.0).fit(X_train, y_train).predict(X_test)\nround(float(np.sqrt(mean_squared_error(y_test, pred))), 2)",'RMSE is <code>np.sqrt(mean_squared_error(y_test, pred))</code>.')
add('ml-cv','ml',3,'Cross-validation','<p>Use 5-fold cross-validation to estimate the accuracy of <code>DecisionTreeClassifier(max_depth=3, random_state=0)</code> on the full wine data. Return the mean score rounded to 3 decimals.</p>'+EXPR,WINE,
    "from sklearn.tree import DecisionTreeClassifier\nfrom sklearn.model_selection import cross_val_score\nscores = cross_val_score(DecisionTreeClassifier(max_depth=3, random_state=0), X, y, cv=5)\nround(scores.mean(), 3)",'<code>cross_val_score(model, X, y, cv=5)</code> returns one score per fold.')
add('ml-auc','ml',3,'ROC AUC','<p>Build a pipeline of <code>StandardScaler</code> and <code>LogisticRegression()</code>, fit it on the breast cancer training set, and return the test ROC AUC using predicted probabilities for class 1, rounded to 4 decimals.</p>'+EXPR,CANCER,
    "from sklearn.pipeline import make_pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import roc_auc_score\nmodel = make_pipeline(StandardScaler(), LogisticRegression()).fit(X_train, y_train)\nround(roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]), 4)",'AUC needs scores, not labels: <code>predict_proba(X_test)[:, 1]</code>.')
add('ml-leak','ml',3,'Fix the data leak','<p>This code scales the data <i>before</i> splitting, so the test set leaks into the scaler:</p><pre><code>scaler = StandardScaler().fit(X)\nX_train, X_test, y_train, y_test = train_test_split(\n    scaler.transform(X), y, test_size=0.3, random_state=1, stratify=y)</code></pre><p>Rewrite it so you split first (same arguments, on the raw <code>X</code>) and fit <code>scaler</code> on the training data only. End with <code>scaler.mean_[:3].round(3)</code>.</p>'+EXPR,
    "from sklearn.datasets import load_breast_cancer\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.preprocessing import StandardScaler\nX, y = load_breast_cancer(return_X_y=True)",
    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1, stratify=y)\nscaler = StandardScaler().fit(X_train)\nX_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)\nscaler.mean_[:3].round(3)",'Swap the order: <code>train_test_split</code> on raw <code>X</code>, then <code>StandardScaler().fit(X_train)</code>.')

# ---------- Pipelines & tuning
add('mlp-pipeline','mlpipe',1,'Build a pipeline','<p>Create a <code>Pipeline</code> with steps <code>("scale", StandardScaler())</code> and <code>("clf", LogisticRegression(max_iter=1000))</code>, fit it on the breast cancer training set, and return test accuracy rounded to 3 decimals.</p>'+EXPR,CANCER,
    "from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\npipe = Pipeline([('scale', StandardScaler()), ('clf', LogisticRegression(max_iter=1000))])\npipe.fit(X_train, y_train)\nround(pipe.score(X_test, y_test), 3)",'A pipeline fits like a model: <code>pipe.fit(X_train, y_train)</code>, then <code>pipe.score(...)</code>.')
add('mlp-onehot','mlpipe',2,'Categorical features','<p>Predict house <code>price</code> from <code>city</code>, <code>sqft</code> and <code>beds</code>. Use a <code>ColumnTransformer</code> that one-hot encodes <code>city</code> (with <code>handle_unknown="ignore"</code>) and passes the numeric columns through, followed by <code>LinearRegression</code>. Fit on all of <code>houses</code> and return the predicted price for <code>new_house</code>, rounded to 1 decimal.</p>'+EXPR,HOUSES,
    "from sklearn.compose import ColumnTransformer\nfrom sklearn.preprocessing import OneHotEncoder\nfrom sklearn.pipeline import make_pipeline\nfrom sklearn.linear_model import LinearRegression\nprep = ColumnTransformer([('city', OneHotEncoder(handle_unknown='ignore'), ['city'])], remainder='passthrough')\nmodel = make_pipeline(prep, LinearRegression()).fit(houses[['city', 'sqft', 'beds']], houses['price'])\nround(float(model.predict(new_house)[0]), 1)",'<code>ColumnTransformer([("city", OneHotEncoder(...), ["city"])], remainder="passthrough")</code>, then chain it with the regressor.',pkgs=['scikit-learn'])
add('mlp-grid','mlpipe',2,'Grid search','<p>Split the wine data (25% test, <code>random_state=0</code>, stratified). Tune a pipeline of <code>StandardScaler</code> and <code>KNeighborsClassifier</code> over <code>n_neighbors</code> in <code>[1, 3, 5, 7, 9, 11]</code> with <code>GridSearchCV(cv=5)</code> on the training set. Name the KNN step <code>knn</code> and return <code>best_params_</code>.</p>'+EXPR,
    WINE+"\nfrom sklearn.model_selection import train_test_split\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)",
    "from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.neighbors import KNeighborsClassifier\nfrom sklearn.model_selection import GridSearchCV\npipe = Pipeline([('scale', StandardScaler()), ('knn', KNeighborsClassifier())])\ngrid = GridSearchCV(pipe, {'knn__n_neighbors': [1, 3, 5, 7, 9, 11]}, cv=5).fit(X_train, y_train)\ngrid.best_params_",'Parameters of a pipeline step are named <code>step__param</code>, e.g. <code>knn__n_neighbors</code>.')
add('mlp-importance','mlpipe',3,'Feature importance','<p>Fit <code>RandomForestClassifier(n_estimators=200, random_state=0)</code> on the training split of the breast cancer data (as a DataFrame). Return a list of the names of the 3 most important features, most important first.</p>'+EXPR,
    "from sklearn.datasets import load_breast_cancer\nfrom sklearn.model_selection import train_test_split\ndata = load_breast_cancer(as_frame=True)\nX_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.25, random_state=0, stratify=data.target)",
    "from sklearn.ensemble import RandomForestClassifier\nrf = RandomForestClassifier(n_estimators=200, random_state=0).fit(X_train, y_train)\npd.Series(rf.feature_importances_, index=X_train.columns).nlargest(3).index.tolist()",'<code>rf.feature_importances_</code> lines up with <code>X_train.columns</code>; put them in a Series and take <code>nlargest(3)</code>.',ordered=True)
add('mlp-degree','mlpipe',3,'Choose model complexity','<p>For polynomial degrees 1 to 5, score a pipeline of <code>PolynomialFeatures(degree)</code> and <code>LinearRegression</code> with 5-fold cross-validation using <code>scoring="neg_mean_squared_error"</code> and <code>KFold(5, shuffle=True, random_state=0)</code>. Return the degree with the best (highest) mean score.</p>'+EXPR,
    "rng = np.random.RandomState(5)\nx = np.sort(rng.uniform(-3, 3, 80)).reshape(-1, 1)\ny = 0.5 * x[:, 0] ** 3 - x[:, 0] + rng.normal(0, 1.5, 80)",
    "from sklearn.pipeline import make_pipeline\nfrom sklearn.preprocessing import PolynomialFeatures\nfrom sklearn.linear_model import LinearRegression\nfrom sklearn.model_selection import cross_val_score, KFold\ncv = KFold(5, shuffle=True, random_state=0)\nscores = {d: cross_val_score(make_pipeline(PolynomialFeatures(d), LinearRegression()), x, y, cv=cv, scoring='neg_mean_squared_error').mean() for d in range(1, 6)}\nmax(scores, key=scores.get)",'Loop over degrees, store the mean CV score of each, and pick the key with the largest value.')

# ---------- Clustering & dimensionality reduction
add('un-kmeans','unsup',1,'k-means clusters','<p>Run <code>KMeans(n_clusters=3, n_init=10, random_state=0)</code> on the iris features and return the cluster sizes as a sorted list (smallest first).</p>'+EXPR,IRIS,
    "from sklearn.cluster import KMeans\nlabels = KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(X)\nsorted(np.bincount(labels).tolist())",'<code>fit_predict</code> returns labels; <code>np.bincount</code> counts them.')
add('un-pca','unsup',2,'Principal components','<p>Standardise the iris features, then fit <code>PCA(n_components=2)</code>. Return <code>explained_variance_ratio_</code> rounded to 3 decimals.</p>'+EXPR,IRIS,
    "from sklearn.preprocessing import StandardScaler\nfrom sklearn.decomposition import PCA\npca = PCA(n_components=2).fit(StandardScaler().fit_transform(X))\npca.explained_variance_ratio_.round(3)",'Scale first (<code>StandardScaler().fit_transform(X)</code>), then fit PCA.')
add('un-silhouette','unsup',3,'Pick k by silhouette','<p>Standardise the wine features. For k from 2 to 6, fit <code>KMeans(n_clusters=k, n_init=10, random_state=0)</code> and compute the silhouette score. Return the k with the highest score.</p>'+EXPR,WINE,
    "from sklearn.preprocessing import StandardScaler\nfrom sklearn.cluster import KMeans\nfrom sklearn.metrics import silhouette_score\nXs = StandardScaler().fit_transform(X)\nscores = {k: silhouette_score(Xs, KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(Xs)) for k in range(2, 7)}\nmax(scores, key=scores.get)",'<code>silhouette_score(X, labels)</code>; higher is better.')

# ---------- Manufacturing analytics
add('mfg-rate','mfg',1,'Failure rate by machine','<p><code>sensors</code> holds 600 sensor snapshots from four machines, with <code>failure</code> = 1 when the machine failed within the next shift. Return the failure rate (share of snapshots with a failure) for each <code>machine_id</code>, rounded to 3 decimals.</p>'+EXPR,SENSORS,
    "sensors.groupby('machine_id')['failure'].mean().round(3)",'The mean of a 0/1 column is a rate.',pkgs=())
add('mfg-cpk','mfg',1,'Process capability','<p>Using all 125 shaft <code>diameter</code>s and the spec limits <code>LSL</code>, <code>USL</code>, compute Cp = (USL − LSL) / 6σ and Cpk = min(USL − μ, μ − LSL) / 3σ, with σ the sample standard deviation. Return <code>(Cp, Cpk)</code>, each rounded to 3 decimals.</p>'+EXPR,SHAFTS,
    "mu = shafts['diameter'].mean()\nsigma = shafts['diameter'].std()\ncp = (USL - LSL) / (6 * sigma)\ncpk = min(USL - mu, mu - LSL) / (3 * sigma)\n(round(cp, 3), round(cpk, 3))",'pandas <code>.std()</code> is the sample standard deviation (ddof=1); numpy\'s <code>np.std</code> is not, by default.',pkgs=())
add('mfg-xbar','mfg',2,'X-bar chart limits','<p>For the shaft data (subgroups of 5), compute the subgroup means and ranges. The centre line is the mean of the subgroup means; the limits are CL ± A2 × R̄, where R̄ is the mean range. Return <code>(LCL, CL, UCL)</code>, each rounded to 4 decimals.</p>'+EXPR,SHAFTS,
    "g = shafts.groupby('subgroup')['diameter']\nmeans, ranges = g.mean(), g.max() - g.min()\ncl, rbar = means.mean(), ranges.mean()\n(round(cl - A2 * rbar, 4), round(cl, 4), round(cl + A2 * rbar, 4))",'Group by subgroup; range is <code>max - min</code>.',pkgs=())
add('mfg-ooc','mfg',2,'Out-of-control subgroups','<p>Using the X-bar limits from the shaft data (CL ± A2 × R̄), return a list of the subgroup numbers whose mean falls outside the limits, in order.</p>'+EXPR,SHAFTS,
    "g = shafts.groupby('subgroup')['diameter']\nmeans, ranges = g.mean(), g.max() - g.min()\ncl, rbar = means.mean(), ranges.mean()\nmeans[(means > cl + A2 * rbar) | (means < cl - A2 * rbar)].index.tolist()",'Compute the limits, then filter the means Series with a boolean mask and take its index.',ordered=True,pkgs=())
add('mfg-spike','mfg',2,'Detect temperature spikes','<p><code>temps</code> is a 5-minute temperature series. Flag a reading as a spike when it exceeds the mean of the <b>previous</b> 12 readings plus 3 times their standard deviation. Return the number of spikes.</p>'+EXPR,TEMPS,
    "roll = temps.rolling(12)\nlimit = (roll.mean() + 3 * roll.std()).shift(1)\nint((temps > limit).sum())",'<code>temps.rolling(12).mean()</code> includes the current reading; <code>.shift(1)</code> makes it use only earlier ones.',pkgs=())
add('mfg-pm','mfg',2,'Predictive maintenance model','<p>Train <code>RandomForestClassifier(n_estimators=200, random_state=0)</code> to predict <code>failure</code> from the four sensor features, using the split in the setup. Return the recall on the test set (the share of real failures the model catches), rounded to 3 decimals.</p>'+EXPR,SENSORS_SPLIT,
    "from sklearn.ensemble import RandomForestClassifier\nfrom sklearn.metrics import recall_score\nrf = RandomForestClassifier(n_estimators=200, random_state=0).fit(X_train, y_train)\nround(recall_score(y_test, rf.predict(X_test)), 3)",'Fit on <code>X_train, y_train</code>; <code>recall_score(y_test, predictions)</code>.')
add('mfg-balanced','mfg',3,'Rare failures and class weights','<p>Failures are rare, so a plain model can miss them. Fit two pipelines of <code>StandardScaler</code> and <code>LogisticRegression</code>: one default, one with <code>class_weight="balanced"</code>. Return <code>(recall_default, recall_balanced)</code> on the test set, each rounded to 3 decimals.</p>'+EXPR,SENSORS_SPLIT,
    "from sklearn.pipeline import make_pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import recall_score\nplain = make_pipeline(StandardScaler(), LogisticRegression()).fit(X_train, y_train)\nbal = make_pipeline(StandardScaler(), LogisticRegression(class_weight='balanced')).fit(X_train, y_train)\n(round(recall_score(y_test, plain.predict(X_test)), 3), round(recall_score(y_test, bal.predict(X_test)), 3))",'<code>LogisticRegression(class_weight="balanced")</code> reweights classes by their inverse frequency.')
add('mfg-anomaly','mfg',3,'Unsupervised anomaly detection','<p>Fit <code>IsolationForest(contamination=0.02, random_state=0)</code> on <code>temp</code>, <code>vibration</code> and <code>pressure</code>. Return a list of the <code>sensors</code> index labels it flags as anomalies (prediction −1), in order.</p>'+EXPR,SENSORS,
    "from sklearn.ensemble import IsolationForest\ncols = ['temp', 'vibration', 'pressure']\npred = IsolationForest(contamination=0.02, random_state=0).fit_predict(sensors[cols])\nsensors.index[pred == -1].tolist()",'<code>fit_predict</code> returns 1 for normal points and −1 for anomalies.',ordered=True)
add('mfg-oee','mfg',3,'Overall equipment effectiveness','<p><code>oee_log</code> has three shifts per machine. Sum each machine\'s shifts first, then compute availability = (planned − downtime) / planned, performance = ideal_cycle_s × total_count / (run minutes × 60), quality = good_count / total_count, and OEE = availability × performance × quality. Return OEE per machine as a Series rounded to 3 decimals, highest first.</p>'+EXPR,OEE,
    "m = oee_log.groupby('machine').agg(planned=('planned_min', 'sum'), down=('downtime_min', 'sum'),\n                                     cycle=('ideal_cycle_s', 'first'), total=('total_count', 'sum'), good=('good_count', 'sum'))\nrun = m['planned'] - m['down']\noee = (run / m['planned']) * (m['cycle'] * m['total'] / (run * 60)) * (m['good'] / m['total'])\noee.round(3).sort_values(ascending=False)",'Aggregate with <code>groupby().agg()</code> first; the ideal cycle time is constant per machine.',ordered=True,pkgs=())

json.dump(P, open('bank_py_ml.json', 'w'), indent=1)
from collections import Counter
print(len(P), sorted(Counter((p['skill'], p['level']) for p in P).items()))
