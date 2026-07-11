# Robustness results

All checks estimate country and year two-way fixed effects with country-clustered standard errors. They address specific sample, transformation, definition, collinearity, and influence concerns; they are not selected by p-values.

## Sample and flag sensitivity

- Main cleaned sample: 2,319 observations.
- Excluding all clearly invalid rows: 2,301 observations.
- Excluding clearly invalid and unresolved rows: 2,266 observations.
- The 62 merely unusual retained observations are not automatically deleted.
- Specification-specific main-variable sample including single-year countries: 2,319 observations. Single-year countries provide no within-country identifying variation even when present.

## Focused checks

- GDP transformation: compare R1 with R5.
- HIV/AIDS transformation: compare R1 with R6.
- GDP definition/missingness: R7 excludes GDP.
- Development-measure overlap: R8 replaces schooling with income composition.
- Vaccination choice/collinearity: R9 replaces polio with diphtheria; R10 includes both.
- Expenditure-definition ambiguity: R11 omits total expenditure.
- Influence: R12 excludes pooled observations with Cook's distance above 4/n.
- Heterogeneity: R13 and R14 estimate developed and developing samples separately when sample size permits.

## Stability guide

Relative coefficient ranges across checks using the same variables are:

| variable          |   relative_range_to_main_abs_coefficient |
|:------------------|-----------------------------------------:|
| schooling         |                                    2.954 |
| log1p_gdp         |                                    3.643 |
| total_expenditure |                                    1.651 |
| polio             |                                    4.329 |
| log1p_hiv_aids    |                                    2.823 |

- Flag handling is stable: R1–R3 produce very similar coefficients, including `log1p_hiv_aids` estimates between -4.197 and -4.125.
- `log1p_hiv_aids` is also similar in the main, no-GDP, no-expenditure, and influential-observation checks. The developed-only estimate changes sign, so subgroup interpretation is sensitive and unresolved.
- Schooling and polio are sensitive to the influential-observation rule: both estimates become larger in R12. This rule removes many observations and is a sensitivity check, not a preferred specification.
- GDP, expenditure, and vaccination coefficients are generally small in the two-way models and depend on transformation or variable selection. Including polio and diphtheria together further attenuates the polio estimate.

Large ranges indicate sensitivity to specification or sample choices, not evidence of a causal effect. Exact coefficients, confidence intervals, p-values, samples, and fit statistics are in `tables/robustness_results.csv` and `tables/robustness_sample_summary.csv`.

## Remaining uncertainty

- GDP units and the total-expenditure definition remain unresolved.
- Unresolved flagged values are retained except in the explicit strict sample.
- Developed-country estimates may have limited within-country variation and relatively few country clusters.
- Robustness checks assess stability but cannot create a causal research design.
