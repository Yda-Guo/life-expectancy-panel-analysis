# Main regression results

All estimates are associational. The four models use the same 2,319-observation sample from 157 countries (2000–2015).

## Specifications

1. Pooled OLS with HC1 heteroskedasticity-robust standard errors.
2. Pooled OLS plus year fixed effects with HC1 standard errors.
3. Country fixed effects with standard errors clustered by country.
4. Country and year two-way fixed effects with standard errors clustered by country.

Each model includes schooling, `log1p_gdp`, total expenditure, polio coverage, and `log1p_hiv_aids`. Country/year dummy coefficients are omitted from the main table.

## Coefficient interpretation

- Schooling: coefficient is the estimated difference in life-expectancy years associated with one additional schooling unit, holding included controls fixed.
- Total expenditure: coefficient is the estimated difference in life-expectancy years associated with a one-unit increase in the recorded expenditure measure; its exact definition remains unresolved.
- Polio: coefficient corresponds to a one-percentage-point increase in recorded vaccination coverage.
- For `log1p_gdp` and `log1p_hiv_aids`, the coefficient is a semi-elasticity with respect to `log(1 + X)`. Away from zero, a 1% increase in X is approximately associated with 0.01 times the coefficient in life-expectancy years.
- Pooled estimates combine cross-country and within-country differences. Fixed-effects estimates describe within-country associations after removing time-invariant country differences.

## Observed estimates

| variable          |   M1_pooled_ols |   M2_pooled_year_fe |   M3_country_fe |   M4_two_way_fe |
|:------------------|----------------:|--------------------:|----------------:|----------------:|
| log1p_gdp         |          0.7786 |              0.7874 |          0.0991 |         -0.0208 |
| log1p_hiv_aids    |         -6.2627 |             -6.2638 |         -5.533  |         -4.1969 |
| polio             |          0.0283 |              0.0283 |          0.0076 |          0.0037 |
| schooling         |          1.1561 |              1.1605 |          0.6828 |          0.145  |
| total_expenditure |          0.1182 |              0.1199 |         -0.0216 |         -0.0532 |

Schooling changes from 1.156 in pooled OLS to 0.145 in the two-way model. The `log1p_gdp` estimate changes from 0.779 to -0.021; total expenditure changes from 0.118 to -0.053; and polio changes from 0.0283 to 0.0037. These attenuations and sign changes show that pooled cross-country associations differ substantially from within-country associations after country and year controls. `log1p_hiv_aids` remains negative in all four models, changing from -6.263 to -4.197.

Full coefficients, robust/clustered standard errors, confidence intervals, p-values, sample metadata, and fit statistics are saved in `tables/main_regression_results.csv`.

## Diagnostics

- Breusch–Pagan LM p-value: 2.528e-16; robust standard errors are retained. This test does not prove the model is correctly specified.
- Pooled observations above Cook's-distance 4/n rule: 135. They are not automatically removed; a documented sensitivity check is reported separately.
- Clustered standard errors are used for both country fixed-effects specifications because repeated observations within countries may have dependent residuals.
- The two-way-FE residual lag-1 correlation within countries is 0.452, supporting the decision to allow within-country residual dependence through country-clustered standard errors. This diagnostic does not prove the covariance specification is correct.
