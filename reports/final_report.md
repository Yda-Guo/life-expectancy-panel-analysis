# Determinants of Life Expectancy: A Panel Data Analysis

## 1. Abstract

This study compares pooled cross-country and within-country associations between national life expectancy and schooling, recorded GDP, health expenditure, and polio vaccination coverage. The panel has 2,938 country-years for 193 countries in 2000–2015; the common main estimation sample has 2,319 observations from 157 countries. Positive pooled associations for schooling, GDP, and polio shrink sharply in the country-and-year fixed-effects model. The preferred TWFE estimates are 0.1340 for schooling, -0.0157 for `log(1 + GDP)`, -0.0337 for total expenditure, and 0.0049 for polio, with all 95% confidence intervals crossing zero. A metadata review also corrected the earlier use of contemporaneous HIV/AIDS mortality as an independent predictor. The results are associational and do not establish causality.

## 2. Research question and contribution

How do associations between life expectancy and selected socioeconomic or health-system measures change after controlling for time-invariant country characteristics and common year shocks?

The project's main contribution is a transparent comparison. Pooled OLS combines cross-country and within-country information. Country fixed effects ask whether changes within a country are associated with changes in life expectancy; year fixed effects additionally remove shocks common to all countries. Large differences between these estimates reveal how strongly pooled patterns can depend on persistent country differences.

## 3. Data, provenance, and variable definitions

The distributed Kaggle **Life Expectancy (WHO)** file contains 2,938 observations and 22 original columns. Country-year keys are unique. The panel covers 193 countries in 2000–2015; 183 countries have 16 rows and ten have one. Kaggle states that health fields came from WHO GHO and economic fields from the United Nations, but it does not provide a versioned, field-level lineage for the merged file.

The outcome is life expectancy in years. The main covariates are:

- **Schooling:** recorded years of schooling; exact construction and age group are not traceable from the merged metadata.
- **GDP:** retained under its neutral name. The metadata do not establish total versus per-capita GDP, currency basis, or price year. The model uses `log(1 + GDP)` because the recorded values are nonnegative and strongly skewed.
- **Total expenditure:** a recorded percentage-like health-expenditure field. WHO publishes multiple expenditure indicators, but Kaggle does not identify the exact denominator used here.
- **Polio:** percentage of one-year-olds receiving three doses of polio-containing vaccine, consistent with WHO Pol3 metadata.

The field-level evidence and URLs are recorded in [`data_dictionary.md`](../data_dictionary.md).

### HIV/AIDS methodological correction

The source `HIV/AIDS` column belongs to the WHO cause-specific mortality family reported as deaths per 1,000 live births. Kaggle's lack of an upstream series ID prevents reconstructing every fine detail, but the mortality nature and unit family are clear enough for the modeling decision. Because life expectancy is constructed from mortality, the contemporaneous HIV/AIDS field overlaps directly with the outcome. It is excluded from the primary explanatory specification and appears only in a labeled supplementary model. Its large negative coefficient is not interpreted as evidence about an independent determinant.

Adult mortality, infant deaths, and under-five deaths remain excluded for the same broad outcome-overlap reason. Income composition and diphtheria coverage appear only in alternative-measure checks.

## 4. Data quality and cleaning

The workflow standardizes names, trims strings, sorts country-years, and creates transformations, review classifications, and analysis copies while preserving raw values. No global mean imputation, winsorization, or automatic outlier deletion is used. Clearly invalid values are set to missing only in separate analysis copies; merely unusual and unresolved records remain flagged. The raw file is checked before and after processing.

Missingness is highest in population (652 rows), hepatitis B (553), GDP (448), and total expenditure (226). Full audit and decisions appear in [`data_audit.md`](data_audit.md) and [`data_cleaning_decisions.md`](data_cleaning_decisions.md).

## 5. Empirical methodology

The preferred specification is

\[
LE_{it}=\alpha_i+\lambda_t+\beta_1Schooling_{it}+\beta_2\log(1+GDP_{it})
+\beta_3Expenditure_{it}+\beta_4Polio_{it}+\varepsilon_{it}.
\]

Four models use the same 2,319 complete cases from 157 countries in 2000–2015:

1. Pooled OLS, HC1 standard errors.
2. Pooled OLS with year fixed effects, HC1 standard errors.
3. Country fixed effects, country-clustered standard errors.
4. Country and year fixed effects, country-clustered standard errors.

The common sample prevents specification comparisons from being driven merely by sample changes. Country clustering permits arbitrary residual dependence over time within a country. Fixed effects do not control for omitted time-varying variables and do not establish causality.

For `log(1 + GDP)`, a change from recorded value \(x_0\) to \(x_1\) corresponds to \(\beta[\log(1+x_1)-\log(1+x_0)]\) life-expectancy years. A constant-percent approximation is not exact, especially near zero.

## 6. Main results

| Variable | Pooled OLS | TWFE | TWFE SE | TWFE 95% CI | p-value |
|---|---:|---:|---:|---:|---:|
| Schooling | 1.6878 | 0.1340 | 0.1228 | [-0.1068, 0.3748] | 0.275 |
| log(1 + GDP) | 1.0492 | -0.0157 | 0.0372 | [-0.0886, 0.0571] | 0.672 |
| Total expenditure | -0.1003 | -0.0337 | 0.0449 | [-0.1216, 0.0542] | 0.452 |
| Polio coverage | 0.0617 | 0.0049 | 0.0034 | [-0.0017, 0.0115] | 0.145 |

The schooling estimate falls from 1.69 life-expectancy years per recorded schooling unit in pooled OLS to 0.13 years in TWFE. Its interval spans a modest negative association to 0.37 years. The GDP estimate falls from 1.05 per log unit to nearly zero and changes sign. The polio estimate falls from 0.0617 years per percentage point to 0.0049 years (about 0.049 years per ten points), with an interval from about -0.017 to 0.115 years per ten points. Total expenditure is smaller in magnitude in TWFE and also uncertain.

These differences are substantively larger than the distinction between “significant” and “not significant”: persistent cross-country characteristics explain much of the pooled schooling, GDP, and polio pattern. Exact estimates and model statistics are in [`main_regression_results.csv`](../tables/main_regression_results.csv).

## 7. Diagnostics and complete-case selection

The main-regressor maximum VIF is 1.90. The pooled Breusch–Pagan p-value is approximately \(1.92\times10^{-33}\), supporting heteroskedasticity-robust pooled inference. TWFE residual lag-one correlation is 0.540, supporting a covariance estimator that allows within-country dependence. The pooled Cook's-distance 4/n rule flags 145 observations; they are retained in the main analysis and removed only in sensitivity analysis.

The complete-case diagnostic compares the actual 2,319 included rows with 619 excluded rows. Observed mean life expectancy is similar (69.26 versus 69.11; standardized difference 0.02), as is polio coverage. Included rows have a slightly larger developed-country share (18.1% versus 14.9%). The largest observed difference is time composition: included rows average 2007.02, excluded rows 2009.40 (standardized difference -0.50). Observed-value standardized differences for the four main covariates range from approximately 0.00 to 0.19. Because missing values help define exclusion, covariate comparisons are explicitly conditional on availability. The diagnostic does not prove missingness is ignorable; generalization beyond the complete cases remains limited. See [`complete_case_selection_diagnostics.csv`](../tables/complete_case_selection_diagnostics.csv).

## 8. Focused sensitivity analyses

### Coefficient and sample sensitivity

Twelve TWFE checks examine invalid/unresolved flags, GDP transformation and omission, alternative development and vaccination measures, expenditure omission, pooled influence flags, and developed/developing subgroups. Detailed results are in [`robustness_results.csv`](../tables/robustness_results.csv).

### One-year-lagged TWFE

After sorting by country and year, lags are created only where the preceding row is exactly one calendar year earlier. The lagged model uses 2,317 observations from 157 countries (2001–2015):

| Lagged regressor | Coefficient | SE | 95% CI | p-value |
|---|---:|---:|---:|---:|
| Schooling (t-1) | 0.1019 | 0.1131 | [-0.1199, 0.3236] | 0.368 |
| log(1 + GDP) (t-1) | -0.0032 | 0.0381 | [-0.0779, 0.0714] | 0.932 |
| Total expenditure (t-1) | -0.0035 | 0.0447 | [-0.0910, 0.0841] | 0.938 |
| Polio (t-1) | 0.0049 | 0.0035 | [-0.0020, 0.0119] | 0.163 |

The estimates remain small and uncertain relative to the pooled associations. Lagging improves temporal ordering but does not eliminate reverse causality, omitted-variable bias, measurement error, or common trends. See [`lagged_model_results.csv`](../tables/lagged_model_results.csv).

### Alternative inference

Two-way clustering by country and year retains the exact TWFE point estimates. The alternative SEs are 0.1165 (schooling), 0.0353 (log GDP), 0.0378 (expenditure), and 0.0040 (polio), compared with primary country-clustered SEs of 0.1228, 0.0372, 0.0449, and 0.0034. The substantive conclusion remains one of small, uncertain TWFE associations. With only 16 year clusters, asymptotic justification in that dimension is weak, so this is a sensitivity check only; country clustering remains primary.

### Supplementary mortality-overlap model

The supplementary model `S1_add_contemporaneous_hiv_mortality` documents the contemporaneous mortality-overlap specification. It is not part of the main evidence and its HIV/AIDS coefficient is not interpreted as an independent determinant.

## 9. Limitations

The study remains vulnerable to reverse causality, omitted time-varying confounding, measurement error, ambiguous merged-file metadata, and complete-case selection. Fixed effects cannot solve these problems. Several variables move slowly within countries, the panel has only 16 years, linear/additive specifications may miss nonlinearities, and subgroup models have fewer clusters. Country clustering is asymptotic, while the alternative year dimension is especially small. The lagged specification does not create exogenous variation. No estimate should be read as a policy effect.

## 10. Conclusion

The strongest defensible finding is a comparison, not a single determinant: large pooled cross-country schooling, GDP, and polio associations become much smaller and more uncertain in within-country TWFE estimates. The contemporaneous HIV/AIDS mortality field is excluded from this interpretation because it directly overlaps conceptually with the outcome. All results remain subject to the observational limitations described above.

## Appendix: generated evidence

- Audit and cleaning: [`data_audit.md`](data_audit.md), [`data_cleaning_decisions.md`](data_cleaning_decisions.md)
- Main diagnostics/results: [`model_diagnostics.md`](model_diagnostics.md), [`model_results.md`](model_results.md)
- Sensitivity narrative: [`robustness_results.md`](robustness_results.md)
- Model samples: [`model_sample_summary.csv`](../tables/model_sample_summary.csv)
- Main estimates: [`main_regression_results.csv`](../tables/main_regression_results.csv)
- Lagged estimates: [`lagged_model_results.csv`](../tables/lagged_model_results.csv)
- Complete-case comparison: [`complete_case_selection_diagnostics.csv`](../tables/complete_case_selection_diagnostics.csv)
- Reproducibility: [`REPRODUCIBILITY.md`](../REPRODUCIBILITY.md)
