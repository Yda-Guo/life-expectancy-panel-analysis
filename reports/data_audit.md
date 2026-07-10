# Data audit

Generated from `../work/life_expectancy.csv`. The script reads but never writes to the raw file.

## Observed facts

- Dimensions: **2,938 observations × 22 variables**.
- Countries: **193**.
- Years: **2000–2015** (16 distinct years).
- Duplicate country–year keys: **0 rows**.
- Exact duplicate rows: **0 rows**.
- Balanced panel: **no**.
- Country-name whitespace/case collisions: **0**.
- Header whitespace normalized in memory: `Life expectancy ` → `Life expectancy`, `Measles ` → `Measles`, ` BMI ` → `BMI`, `under-five deaths ` → `under-five deaths`, `Diphtheria ` → `Diphtheria`, ` HIV/AIDS` → `HIV/AIDS`, ` thinness  1-19 years` → `thinness 1-19 years`, ` thinness 5-9 years` → `thinness 5-9 years`.

### Observations per country

| observations | countries |
| --- | --- |
| 1 | 10 |
| 16 | 183 |

The complete country-level table is in `tables/observations_per_country.csv`.

### Columns and inferred data types

| column | dtype |
| --- | --- |
| Country | str |
| Year | int64 |
| Status | str |
| Life expectancy | float64 |
| Adult Mortality | float64 |
| infant deaths | int64 |
| Alcohol | float64 |
| percentage expenditure | float64 |
| Hepatitis B | float64 |
| Measles | int64 |
| BMI | float64 |
| under-five deaths | int64 |
| Polio | float64 |
| Total expenditure | float64 |
| Diphtheria | float64 |
| HIV/AIDS | float64 |
| GDP | float64 |
| Population | float64 |
| thinness 1-19 years | float64 |
| thinness 5-9 years | float64 |
| Income composition of resources | float64 |
| Schooling | float64 |

### First five observations

| Country | Year | Status | Life expectancy | Adult Mortality | infant deaths | Alcohol | percentage expenditure | Hepatitis B | Measles | BMI | under-five deaths | Polio | Total expenditure | Diphtheria | HIV/AIDS | GDP | Population | thinness 1-19 years | thinness 5-9 years | Income composition of resources | Schooling |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Afghanistan | 2015 | Developing | 65.0 | 263.0 | 62 | 0.01 | 71.28 | 65.0 | 1154 | 19.1 | 83 | 6.0 | 8.16 | 65.0 | 0.1 | 584.259 | 33736494.0 | 17.2 | 17.3 | 0.479 | 10.1 |
| Afghanistan | 2014 | Developing | 59.9 | 271.0 | 64 | 0.01 | 73.524 | 62.0 | 492 | 18.6 | 86 | 58.0 | 8.18 | 62.0 | 0.1 | 612.697 | 327582.0 | 17.5 | 17.5 | 0.476 | 10.0 |
| Afghanistan | 2013 | Developing | 59.9 | 268.0 | 66 | 0.01 | 73.219 | 64.0 | 430 | 18.1 | 89 | 62.0 | 8.13 | 64.0 | 0.1 | 631.745 | 31731688.0 | 17.7 | 17.7 | 0.47 | 9.9 |
| Afghanistan | 2012 | Developing | 59.5 | 272.0 | 69 | 0.01 | 78.184 | 67.0 | 2787 | 17.6 | 93 | 67.0 | 8.52 | 67.0 | 0.1 | 669.959 | 3696958.0 | 17.9 | 18.0 | 0.463 | 9.8 |
| Afghanistan | 2011 | Developing | 59.2 | 275.0 | 71 | 0.01 | 7.097 | 68.0 | 3013 | 17.2 | 97 | 68.0 | 7.87 | 68.0 | 0.1 | 63.537 | 2978599.0 | 18.2 | 18.2 | 0.454 | 9.5 |

### Missing values

| index | missing_count | missing_rate_pct |
| --- | --- | --- |
| Country | 0 | 0.0 |
| Year | 0 | 0.0 |
| Status | 0 | 0.0 |
| Life expectancy | 10 | 0.34 |
| Adult Mortality | 10 | 0.34 |
| infant deaths | 0 | 0.0 |
| Alcohol | 194 | 6.603 |
| percentage expenditure | 0 | 0.0 |
| Hepatitis B | 553 | 18.822 |
| Measles | 0 | 0.0 |
| BMI | 34 | 1.157 |
| under-five deaths | 0 | 0.0 |
| Polio | 19 | 0.647 |
| Total expenditure | 226 | 7.692 |
| Diphtheria | 19 | 0.647 |
| HIV/AIDS | 0 | 0.0 |
| GDP | 448 | 15.248 |
| Population | 652 | 22.192 |
| thinness 1-19 years | 34 | 1.157 |
| thinness 5-9 years | 34 | 1.157 |
| Income composition of resources | 167 | 5.684 |
| Schooling | 163 | 5.548 |

### Strongly skewed numeric variables

Threshold: absolute sample skewness ≥ 1.

| index | skewness |
| --- | --- |
| Population | 15.916 |
| infant deaths | 9.787 |
| under-five deaths | 9.495 |
| Measles | 9.441 |
| HIV/AIDS | 5.396 |
| percentage expenditure | 4.652 |
| GDP | 3.207 |
| Polio | -2.098 |
| Diphtheria | -2.073 |
| Hepatitis B | -1.931 |
| thinness 5-9 years | 1.777 |
| thinness 1-19 years | 1.711 |
| Adult Mortality | 1.174 |
| Income composition of resources | -1.144 |

### Range and consistency checks

| variable | rule | violations |
| --- | --- | --- |
| Life expectancy | [0, 120] | 0 |
| Adult Mortality | [0, unbounded] | 0 |
| Alcohol | [0, unbounded] | 0 |
| Hepatitis B | [0, 100] | 0 |
| BMI | [0, 100] | 0 |
| Polio | [0, 100] | 0 |
| Total expenditure | [0, 100] | 0 |
| Diphtheria | [0, 100] | 0 |
| HIV/AIDS | [0, 100] | 0 |
| Income composition of resources | [0, 1] | 0 |
| Schooling | [0, unbounded] | 0 |

No values violate the broad logical ranges above. This does **not** establish data validity. The audit flags abrupt within-country changes in `tables/suspicious_within_country_jumps.csv`; these include patterns consistent with dropped digits or decimal-place errors and require comparison with an authoritative source.

## Modeling decisions (not estimated here)

- Treat `Life expectancy` as the outcome and do not use `Adult Mortality`, `infant deaths`, or `under-five deaths` in the primary explanatory specification. They are mortality outcomes/components that are mechanically or definitionally close to life expectancy.
- Do not include both broad development indices and all of their likely components without a clear estimand. `Income composition of resources` and `Schooling` are strongly conceptually related, and the former may embed education/income information.
- Avoid simultaneously using `percentage expenditure`, `Total expenditure`, and `GDP` without verifying definitions: expenditure measures can share denominators or be derived using GDP.
- Avoid including all three immunization measures together initially (`Hepatitis B`, `Polio`, `Diphtheria`) because they measure closely related health-system coverage and may be collinear.
- Treat `Status` as time-invariant unless source documentation shows transitions; country fixed effects would absorb it.
- Use transformations such as `log1p` for highly right-skewed counts and monetary/size variables only after suspicious values and zeros are resolved.

## Proposed initial specification

For a descriptive baseline after cleaning and missing-data decisions:

`Life expectancy_it = country FE + year FE + β1 Schooling_it + β2 log(GDP per capita_it) + β3 Total expenditure_it + β4 Polio_it + β5 HIV/AIDS_it + ε_it`

Use country-clustered standard errors. This is an associational model, not a causal claim. Before estimation, verify that `GDP` is per capita, verify units for `Total expenditure` and `HIV/AIDS`, decide whether to use `Income composition of resources` instead of `Schooling`/GDP, document missing-data handling, and assess within-country variation.

## Unresolved questions requiring human/source review

- Confirm every variable definition and unit against the original WHO/Kaggle documentation.
- Validate abrupt country-level jumps and possible dropped-digit/decimal errors against an authoritative source.
- Confirm country coverage: 10 countries have only one observation (2013), while 183 have 16 observations.
- Decide whether the ten single-year countries belong in fixed-effects analyses; they provide no within-country information.
- Determine whether zero values in `percentage expenditure`, `Income composition of resources`, and `Schooling` are genuine zeros or missing-value codes.
- Choose a missing-data strategy; no automatic global-mean imputation is recommended.
