# Main regression results

All estimates are associational. The four models use the same 2,319-observation sample from 157 countries (2000–2015).

## Specifications

1. Pooled OLS with HC1 heteroskedasticity-robust standard errors.
2. Pooled OLS plus year fixed effects with HC1 standard errors.
3. Country fixed effects with standard errors clustered by country.
4. Country and year two-way fixed effects with standard errors clustered by country.

Each model includes schooling, `log1p_gdp`, total expenditure, and polio coverage. Country/year dummy coefficients are omitted from the main table. The contemporaneous HIV/AIDS field is excluded because authoritative WHO metadata identify the underlying indicator family as cause-specific mortality (deaths per 1,000 live births), creating direct outcome overlap with life expectancy.

## Coefficient interpretation

- Schooling: coefficient is the estimated difference in life-expectancy years associated with one additional schooling unit, holding included controls fixed.
- Total expenditure: coefficient is the estimated difference in life-expectancy years associated with a one-unit increase in the recorded expenditure measure; its exact definition remains unresolved.
- Polio: coefficient corresponds to a one-percentage-point increase in recorded vaccination coverage.
- For `log1p_gdp`, the coefficient is a semi-elasticity with respect to `log(1 + GDP)`. Away from zero, a 1% increase in GDP is approximately associated with 0.01 times the coefficient in life-expectancy years.
- Pooled estimates combine cross-country and within-country differences. Fixed-effects estimates describe within-country associations after removing time-invariant country differences.

## Observed estimates

| variable          |   M1_pooled_ols |   M2_pooled_year_fe |   M3_country_fe |   M4_two_way_fe |
|:------------------|----------------:|--------------------:|----------------:|----------------:|
| log1p_gdp         |          1.0492 |              1.0571 |          0.1618 |         -0.0157 |
| polio             |          0.0617 |              0.0625 |          0.0106 |          0.0049 |
| schooling         |          1.6878 |              1.688  |          0.924  |          0.134  |
| total_expenditure |         -0.1003 |             -0.1054 |          0.0272 |         -0.0337 |

Schooling changes from 1.688 in pooled OLS to 0.134 in the two-way model. The `log1p_gdp` estimate changes from 1.049 to -0.016; total expenditure changes from -0.100 to -0.034; and polio changes from 0.0617 to 0.0049. These attenuations and sign changes show that pooled cross-country associations differ substantially from within-country associations after country and year controls.

Full coefficients, robust/clustered standard errors, confidence intervals, p-values, sample metadata, and fit statistics are saved in `tables/main_regression_results.csv`.

## Diagnostics

- Breusch–Pagan LM p-value: 1.924e-33; robust standard errors are retained. This test does not prove the model is correctly specified.
- Pooled observations above Cook's-distance 4/n rule: 145. They are not automatically removed; a documented sensitivity check is reported separately.
- Clustered standard errors are used for both country fixed-effects specifications because repeated observations within countries may have dependent residuals.
- The two-way-FE residual lag-1 correlation within countries is 0.540, supporting the decision to allow within-country residual dependence through country-clustered standard errors. This diagnostic does not prove the covariance specification is correct.
