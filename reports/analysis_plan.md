# Analysis plan

## Scope and research question

This completed undergraduate project asks how recorded socioeconomic, health-system, and vaccination measures are associated with national life expectancy, and how pooled cross-country patterns change when estimates rely on within-country variation and common year shocks are controlled. It is an associational panel-data study, not a causal design.

## Data and audit decisions

- Raw data: 2,938 country-year observations, 193 countries, 2000–2015.
- Country and year uniquely identify rows; 183 countries have 16 observations and ten have one.
- Original values are preserved. Analysis copies, anomaly flags, and review classifications are separate.
- No arbitrary imputation, winsorization, or automatic deletion is used.
- The four main models use one common complete-case sample. Included-versus-excluded diagnostics are reported rather than assuming missingness is ignorable.

## Primary specification

The main two-way fixed-effects specification is:

`Life expectancy_it = country FE + year FE + Schooling_it + log(1 + GDP_it) + Total expenditure_it + Polio_it + error_it`

The same regressor set and common sample are used for pooled OLS, year fixed effects, country fixed effects, and country-plus-year fixed effects. Pooled models use HC1 standard errors; fixed-effects models use country-clustered standard errors.

GDP retains its neutral source label because the merged-file metadata do not verify “GDP per capita.” The exact total-expenditure denominator also remains unresolved. Polio is interpreted as three-dose coverage among one-year-olds, consistent with WHO metadata.

The contemporaneous HIV/AIDS field was removed from the primary specification after provenance review connected it to a WHO cause-specific mortality indicator measured in deaths per 1,000 live births. Its earlier use created direct conceptual overlap with the mortality-based outcome. It remains only as a labeled supplementary result. Adult mortality, infant deaths, and under-five deaths remain excluded for the same general outcome-overlap reason.

## Focused sensitivity analyses

1. Exclude clearly invalid, then invalid-plus-unresolved rows.
2. Vary the GDP transformation and omit variables with uncertain definitions.
3. Replace overlapping development or vaccination measures; examine polio and diphtheria jointly.
4. Exclude pooled Cook's-distance flags and estimate developed/developing subgroups.
5. Estimate a one-year-lagged TWFE model using only genuine adjacent-year lags.
6. Recalculate TWFE uncertainty with country-and-year two-way clustering as a limited sensitivity check; only 16 year clusters are available.
7. Compare the main complete cases with excluded observations using means, proportions, and standardized differences.

These checks were chosen for specific methodological questions, not by p-values. The former redundant specification that reproduced the baseline sample and coefficients was removed.

## Interpretation boundary

Coefficient changes from pooled OLS to TWFE are the central comparison. Fixed effects reduce time-invariant country confounding and common year shocks but do not solve reverse causality, time-varying confounding, measurement error, or complete-case selection. Lagging improves temporal ordering only. All conclusions remain associations.
