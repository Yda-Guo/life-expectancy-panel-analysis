# Determinants of Life Expectancy: A Panel Data Analysis

## 1. Abstract

This study examines how socioeconomic, healthcare, and public-health measures are associated with national life expectancy in a country-year panel covering 193 countries from 2000 through 2015. The preferred regression comparison uses a common complete-case sample of 2,319 observations from 157 countries. Pooled ordinary least squares (OLS), pooled OLS with year fixed effects, country fixed effects, and country-and-year two-way fixed effects are compared. In pooled models, schooling, recorded GDP, total expenditure, and polio vaccination coverage have sizeable positive associations with life expectancy. These estimates decline substantially after country and year fixed effects are introduced, suggesting that much of the pooled association reflects persistent cross-country differences. In the preferred two-way model, the coefficients are 0.1450 for schooling, -0.0208 for log(1 + GDP), -0.0532 for total expenditure, 0.0037 for polio coverage, and -4.1969 for log(1 + HIV/AIDS). Only the transformed HIV/AIDS association remains comparatively stable across the main and several robustness specifications. The analysis is observational and associational; it does not establish causality.

## 2. Introduction

Life expectancy summarizes mortality conditions across the life course and varies substantially across countries and time. Differences may reflect economic resources, education, healthcare systems, vaccination coverage, disease burden, institutions, and other conditions. A country-year panel makes it possible to distinguish pooled cross-country patterns from associations based on changes within the same country.

This distinction matters. Countries with high schooling or income measures may also differ in many persistent ways that are difficult to observe directly. Country fixed effects remove time-invariant differences, while year fixed effects absorb shocks shared across countries in a given year. The resulting estimates address a narrower question than pooled OLS: whether changes in recorded explanatory variables within a country are associated with changes in its life expectancy, conditional on included controls.

## 3. Research Question

Which socioeconomic, healthcare, and public-health factors are associated with changes in national life expectancy, and how do those associations change after controlling for country and year fixed effects?

The analysis focuses on schooling, transformed GDP, total expenditure, polio vaccination coverage, and transformed HIV/AIDS. Alternative development and vaccination measures are examined through diagnostics and robustness checks rather than added automatically.

## 4. Data and Variable Definitions

The source file is identified in the repository as the Kaggle Life Expectancy (WHO) dataset. The raw data contain 2,938 observations and 22 original variables. Each observation represents a country-year. The data cover 193 countries and the years 2000–2015. Country and year uniquely identify observations. The panel is unbalanced: 183 countries have 16 observations and ten countries have one observation each.

The outcome is recorded life expectancy in years. The primary explanatory variables are:

- **Schooling:** recorded schooling measure; the supplied documentation does not provide a more precise unit definition.
- **GDP:** retained under its original neutral name because the supplied documentation does not verify that it is GDP per capita. The model uses `log(1 + GDP)` because the variable is nonnegative and strongly right-skewed.
- **Total expenditure:** recorded expenditure measure; its exact definition remains unresolved.
- **Polio:** recorded vaccination coverage, interpreted as percentage-point units.
- **HIV/AIDS:** recorded HIV/AIDS measure. The model uses `log(1 + HIV/AIDS)` because the observed distribution is strongly right-skewed and nonnegative.

Adult mortality, infant deaths, and under-five deaths are excluded from the primary specification because they are mortality outcomes or mechanically close to life expectancy. Including them would blur the distinction between predictors and alternative measures or components of the outcome. Development status is not included in country fixed-effects models because it is time-invariant within countries in these data and is therefore absorbed by country fixed effects.

Schooling and income composition of resources are not included together in the primary specification. They are conceptually overlapping development measures and have a correlation of 0.794. Polio and diphtheria coverage are also related (correlation 0.681), so they are treated as alternative vaccination measures and included together only in a specific collinearity sensitivity check.

## 5. Data Quality and Cleaning

The reproducible cleaning process standardizes column names to snake case in the processed dataset, trims strings, sorts observations by country and year, and preserves the raw values. The raw CSV is never overwritten. The processed dataset contains 2,938 rows and 50 columns, including audit flags, analysis copies, transformations, and complete-case indicators.

The audit found no duplicate country-year keys or exact duplicate rows. Missingness is highest in population (22.192%), Hepatitis B coverage (18.822%), GDP (15.248%), and total expenditure (7.692%). No global mean imputation, winsorization, or automatic outlier deletion is used.

The suspicious-value review classifies 120 observations: 18 clearly invalid, 62 merely unusual, and 40 unresolved. Original standardized variables retain their recorded values. For a clearly invalid value, only the corresponding `_analysis` copy is set to missing; no replacement value is invented. Unusual and unresolved observations remain present and flagged. Zeros in percentage expenditure remain unresolved, while zeros in income composition of resources and schooling are classified as likely encoded missingness; all zeros remain retained and flagged. Full decisions appear in [`data_cleaning_decisions.md`](data_cleaning_decisions.md) and [`suspicious_value_review.csv`](../tables/suspicious_value_review.csv).

## 6. Descriptive Analysis

Across available observations, mean life expectancy is 69.22 years, the median is 72.10, and the observed range is 36.3 to 89.0 years. Mean life expectancy increases from 66.75 in 2000 to 71.62 in 2015. Developed observations average 79.20 years, compared with 67.11 years among developing observations. These are descriptive comparisons and may reflect many differences beyond development status.

The distribution and time pattern are shown in [`life_expectancy_distribution.png`](../figures/life_expectancy_distribution.png) and [`average_life_expectancy_by_year.png`](../figures/average_life_expectancy_by_year.png). Representative country trends, selected transparently using the 10th, 50th, and 90th percentiles of country-level mean life expectancy among complete panels, are in [`representative_country_trends.png`](../figures/representative_country_trends.png). Detailed descriptive tables are stored in [`summary_statistics.csv`](../tables/summary_statistics.csv), [`life_expectancy_by_year.csv`](../tables/life_expectancy_by_year.csv), and [`life_expectancy_by_status.csv`](../tables/life_expectancy_by_status.csv).

## 7. Empirical Methodology

The preferred specification is

\[
LE_{it} = \alpha_i + \lambda_t + \beta_1 Schooling_{it}
+ \beta_2 \log(1+GDP_{it}) + \beta_3 Expenditure_{it}
+ \beta_4 Polio_{it} + \beta_5 \log(1+HIV/AIDS_{it}) + \varepsilon_{it},
\]

where \(LE_{it}\) is life expectancy for country \(i\) in year \(t\), \(\alpha_i\) denotes country fixed effects, and \(\lambda_t\) denotes year fixed effects.

Four models are estimated on the same complete-case sample of 2,319 observations from 157 countries over 2000–2015:

1. Pooled OLS with HC1 heteroskedasticity-robust standard errors.
2. Pooled OLS with year fixed effects and HC1 standard errors.
3. Country fixed effects with standard errors clustered by country.
4. Country and year two-way fixed effects with standard errors clustered by country.

Using a common sample makes coefficient changes across the four models interpretable as changes in specification rather than changes caused only by sample composition. The ten single-year countries provide no within-country identifying variation and do not enter the common fixed-effects sample.

Country fixed effects control for observed and unobserved country characteristics that do not change over time. Year fixed effects control for common annual shocks. Country-clustered standard errors allow residuals to be dependent within countries over time. Fixed effects do not control for omitted time-varying confounders and do not establish causality.

## 8. Main Regression Results

The verified two-way fixed-effects estimates are:

| Variable | Coefficient | 95% confidence interval | p-value |
|---|---:|---:|---:|
| Schooling | 0.1450 | [-0.0547, 0.3448] | 0.155 |
| log(1 + GDP) | -0.0208 | [-0.0882, 0.0465] | 0.544 |
| Total expenditure | -0.0532 | [-0.1340, 0.0277] | 0.198 |
| Polio coverage | 0.0037 | [-0.0019, 0.0094] | 0.197 |
| log(1 + HIV/AIDS) | -4.1969 | [-5.2728, -3.1209] | <0.001 |

Schooling is associated with 1.156 additional life-expectancy years per recorded schooling unit in pooled OLS, but the estimate falls to 0.145 in the two-way model. The GDP estimate changes from 0.779 to -0.021, total expenditure from 0.118 to -0.053, and polio from 0.0283 to 0.0037. These attenuations and sign changes indicate that much of the pooled association reflects persistent cross-country differences rather than changes within countries after common year shocks are controlled.

The transformed HIV/AIDS coefficient remains negative in all four main models, changing from -6.263 in pooled OLS to -4.197 in the two-way model. Away from zero, a 1% increase in a variable entered as `log(1 + X)` is approximately associated with 0.01 times its coefficient in life-expectancy years. Statistical insignificance for schooling, GDP, expenditure, and polio in the two-way model does not prove that their true associations are zero; the estimates remain uncertain within the reported confidence intervals.

The complete result table—including robust or clustered standard errors, confidence intervals, p-values, sample metadata, and fit statistics—is [`main_regression_results.csv`](../tables/main_regression_results.csv). A compact visual comparison is [`main_coefficient_plot.png`](../figures/main_coefficient_plot.png).

## 9. Model Diagnostics

The maximum VIF among the five main regressors is 2.06, which does not indicate severe linear dependence in the pooled regressor matrix. VIF is not a direct diagnostic for collinearity after fixed-effect demeaning. The schooling–income-composition correlation is 0.794, supporting the decision not to include both in the primary model. The polio–diphtheria correlation is 0.681, motivating alternative and joint vaccination specifications.

The pooled Breusch–Pagan test has a p-value of approximately \(2.53 \times 10^{-16}\), indicating strong evidence of heteroskedastic residual variance under that test and supporting heteroskedasticity-robust inference. The two-way fixed-effects residual lag-1 within-country correlation is 0.452, supporting inference that permits residual dependence within countries. These diagnostics motivate robust and country-clustered standard errors but do not prove that the models are correctly specified.

The pooled Cook's-distance rule of 4/n flags 135 observations. They are retained in the preferred model and excluded only in an explicit sensitivity check. Diagnostic figures include [`pooled_residual_distribution.png`](../figures/pooled_residual_distribution.png), [`pooled_residuals_vs_fitted.png`](../figures/pooled_residuals_vs_fitted.png), [`pooled_cooks_distance.png`](../figures/pooled_cooks_distance.png), and [`twfe_residuals_vs_fitted.png`](../figures/twfe_residuals_vs_fitted.png).

## 10. Robustness and Sensitivity Analysis

Fourteen focused two-way fixed-effects specifications address flag treatment, complete-case construction, transformations, uncertain definitions, vaccination choice, influential observations, and subgroup heterogeneity. Sample sizes and formulas are in [`model_sample_summary.csv`](../tables/model_sample_summary.csv); coefficients and uncertainty estimates are in [`robustness_results.csv`](../tables/robustness_results.csv).

### Stable finding

The transformed HIV/AIDS coefficient remains approximately -4.1 to -4.3 when clearly invalid or unresolved rows are excluded, GDP is omitted, total expenditure is omitted, or pooled influential observations are excluded. Flag treatment is especially stable: the main, clearly-invalid-excluded, and stricter invalid-plus-unresolved samples produce transformed HIV/AIDS estimates from -4.197 to -4.125. This stability is associational and does not establish a causal relationship.

### Sensitive or inconclusive findings

- Schooling and polio estimates become larger after the 135 influential observations are excluded. This check leaves 2,184 observations from 156 countries and is not treated as the preferred model.
- GDP, expenditure, and vaccination estimates depend on transformation and variable selection.
- Including polio and diphtheria together attenuates the polio estimate.
- The developed-country HIV/AIDS estimate changes sign. The subgroup contains 420 observations from 28 countries, has limited relevant variation, and should not receive substantive interpretation.
- GDP units and the definition of total expenditure remain unresolved.

## 11. Limitations

This project has an observational, associational design. Reverse causality is possible: health conditions may affect schooling, economic measures, or public expenditure. Time-varying omitted variables—such as conflict, institutions, migration, environmental shocks, healthcare reforms, or changing data systems—may be associated with both the included regressors and life expectancy.

Measurement error is a serious concern. Several variables have unresolved definitions, and abrupt within-country jumps suggest possible digit, decimal, unit, or reporting inconsistencies. Missing data require complete-case selection, so the main sample may differ systematically from omitted country-years. Fixed effects cannot correct measurement error or selection automatically.

Some candidate variables have limited within-country movement relative to their cross-country variation. The 2000–2015 period is short for studying gradual demographic and institutional processes. Relationships may be lagged or nonlinear, while the reported models are contemporaneous and linear in their included transformations. Serial dependence remains present, although country-clustered standard errors address a broad class of within-country covariance patterns. Subgroup estimates rely on fewer countries and clusters and are correspondingly fragile.

Country fixed effects control for time-invariant country characteristics, but they do not solve every endogeneity problem and do not establish causality. The models also cannot determine whether statistically insignificant coefficients are truly zero.

## 12. Conclusion

Pooled regressions show strong associations between life expectancy and several development and health-system measures. After controlling for country and year fixed effects, the schooling, GDP, expenditure, and polio estimates become much smaller and are imprecisely estimated. This suggests that persistent differences between countries account for a substantial part of their pooled associations.

The negative association between transformed HIV/AIDS and life expectancy remains comparatively stable across the main and several robustness specifications. It is the most consistent empirical pattern in the project, but it remains observational. Future work should verify variable definitions against authoritative metadata, investigate reporting anomalies, consider lagged and nonlinear specifications, and develop a research design capable of addressing time-varying confounding and reverse causality.

## 13. Appendix

### A. Audit and cleaning trail

- [`data_audit.md`](data_audit.md)
- [`data_cleaning_decisions.md`](data_cleaning_decisions.md)
- [`missing_values.csv`](../tables/missing_values.csv)
- [`suspicious_value_review.csv`](../tables/suspicious_value_review.csv)
- [`zero_value_review.csv`](../tables/zero_value_review.csv)

### B. Descriptive outputs

- [`descriptive_results.md`](descriptive_results.md)
- [`summary_statistics.csv`](../tables/summary_statistics.csv)
- [`model_within_between_variation.csv`](../tables/model_within_between_variation.csv)
- [`model_candidate_correlations.csv`](../tables/model_candidate_correlations.csv)

### C. Model diagnostics and robustness

- [`model_diagnostics.md`](model_diagnostics.md)
- [`model_results.md`](model_results.md)
- [`robustness_results.md`](robustness_results.md)
- [`model_vif.csv`](../tables/model_vif.csv)
- [`pooled_heteroskedasticity_test.csv`](../tables/pooled_heteroskedasticity_test.csv)
- [`pooled_influence_diagnostics.csv`](../tables/pooled_influence_dia