# Robustness and sensitivity results

The analysis now separates coefficient/sample sensitivity, inference sensitivity, temporal ordering, and the conceptually overlapping HIV/AIDS mortality field. These checks assess robustness; none turns the observational design into a causal one.

## 1. Sample and data-rule sensitivity

- Main complete-case sample: 2,319 observations.
- Excluding clearly invalid rows: 2,301 observations.
- Excluding clearly invalid and unresolved rows: 2,266 observations.
- R4–R9 vary transformation or covariate choice; R10 removes pooled Cook's-distance flags; R11–R12 examine status subgroups.

Relative coefficient ranges for the core sample/subgroup checks are:

| variable          |   relative_range_to_main_abs_coefficient |
|:------------------|-----------------------------------------:|
| schooling         |                                    3.986 |
| log1p_gdp         |                                    3.81  |
| total_expenditure |                                    1.658 |
| polio             |                                    2.758 |

## 2. Alternative inference

I1 keeps the preferred two-way fixed-effects point specification but clusters by country and year. Point estimates are unchanged by construction; standard errors change. For example, the schooling SE is 0.1228 with country clustering and 0.1165 with two-way clustering. The year dimension contains only 16 clusters, so the two-way-cluster result is a limited sensitivity check rather than a definitive small-cluster correction.

## 3. One-year-lagged model

L1 regresses current life expectancy on one-year lags of the four preferred covariates with country and year fixed effects and country-clustered standard errors. Lags are created after sorting by country and year and only when the preceding observation is exactly one calendar year earlier. It uses 2,317 observations from 157 countries. Exact estimates are in `tables/lagged_model_results.csv`. Temporal ordering is improved, but reverse causality, time-varying confounding, measurement error, and slow-moving trends remain.

## 4. Contemporaneous HIV/AIDS mortality field

S1 is a labeled supplementary overlap check. The HIV/AIDS field belongs to a contemporaneous cause-specific mortality-rate family and is therefore not interpreted as an independent determinant of life expectancy. Its strong negative coefficient is unsurprising and is not a headline substantive finding.

Exact coefficients, uncertainty estimates, formulas, sample sizes, and flag-removal counts are in `tables/robustness_results.csv`, `tables/robustness_sample_summary.csv`, and `tables/model_sample_summary.csv`.
