# Executive Summary

## Research purpose

This undergraduate research project asks which socioeconomic, healthcare, and public-health measures are associated with national life expectancy and whether those associations remain after controlling for persistent country differences and common year shocks.

The project is designed as a transparent panel-data workflow rather than a causal study. It preserves the raw data, documents cleaning decisions, separates descriptive and model samples, compares pooled and fixed-effects estimators, and subjects the preferred specification to focused robustness checks.

## Data

The repository identifies the source as the Kaggle Life Expectancy (WHO) dataset. The raw file contains 2,938 country-year observations, 193 countries, and the years 2000–2015. Country and year uniquely identify each row. The panel is unbalanced: 183 countries have 16 years and ten countries have one year.

The main regression comparison uses 2,319 complete-case observations from 157 countries. The same sample is used for all four main models so coefficient changes are not driven only by sample composition.

Data auditing identified substantial missingness in population, Hepatitis B coverage, GDP, and total expenditure. A documented review classified 18 observations as clearly invalid, 62 as merely unusual, and 40 as unresolved. Original values remain preserved. Only analysis-copy values are set to missing when an internally documented rule identifies a clearly invalid observation; no external values are invented.

## Methods

The main outcome is life expectancy. The parsimonious specification includes schooling, log(1 + GDP), total expenditure, polio vaccination coverage, and log(1 + HIV/AIDS). GDP retains its neutral name because the supplied documentation does not establish that it is GDP per capita.

Four models are compared:

1. Pooled OLS with heteroskedasticity-robust standard errors.
2. Pooled OLS with year fixed effects.
3. Country fixed effects with country-clustered standard errors.
4. Country and year fixed effects with country-clustered standard errors.

Country fixed effects remove time-invariant differences between countries. Year fixed effects absorb shocks common across countries in a year. Country clustering allows residual dependence within a country over time. These methods strengthen the descriptive comparison but do not create a causal design.

Adult mortality, infant deaths, and under-five deaths are excluded from the primary specification because they are mortality outcomes or mechanically close to life expectancy. Development status is omitted from country fixed-effects models because it is time-invariant. Schooling and income composition are not used together in the primary model because they overlap conceptually and have a correlation of 0.794. Polio and diphtheria coverage are examined as alternatives because their correlation is 0.681.

## Main findings

In pooled OLS, schooling, recorded GDP, expenditure, and polio coverage all have positive associations with life expectancy. These estimates decline substantially after country and year fixed effects are included:

| Variable | Pooled OLS | Two-way fixed effects | Two-way p-value |
|---|---:|---:|---:|
| Schooling | 1.1561 | 0.1450 | 0.155 |
| log(1 + GDP) | 0.7786 | -0.0208 | 0.544 |
| Total expenditure | 0.1182 | -0.0532 | 0.198 |
| Polio coverage | 0.0283 | 0.0037 | 0.197 |
| log(1 + HIV/AIDS) | -6.2627 | -4.1969 | <0.001 |

The attenuation suggests that persistent cross-country differences explain much of the pooled association for schooling, GDP, expenditure, and polio. Statistical insignificance in the two-way model does not prove that the corresponding true associations are zero.

The transformed HIV/AIDS coefficient remains negative and comparatively stable. It is approximately -4.1 to -4.3 when flagged rows are treated differently, GDP or expenditure is omitted, or influential pooled observations are excluded. This is the most stable empirical pattern, but it remains an association rather than evidence of causation.

## Diagnostics and robustness

The maximum VIF among the main regressors is 2.06. The pooled Breusch–Pagan test has a p-value of approximately 2.53 × 10^-16, supporting heteroskedasticity-robust inference. The two-way fixed-effects residual lag-1 correlation within countries is 0.452, supporting country-clustered inference. A Cook's-distance rule flags 135 pooled observations; they are retained in the main model and excluded only in a sensitivity check.

Fourteen focused robustness specifications examine flag treatment, specification-specific samples, transformations, GDP omission, alternative development and vaccination measures, expenditure omission, influential observations, and developed/developing subgroups.

Schooling and polio become larger when influential observations are excluded. GDP, expenditure, and vaccination estimates depend on transformation and variable choice. Including polio and diphtheria together attenuates polio. The developed-country HIV/AIDS estimate changes sign and should not receive substantive interpretation.

## Limitations and next steps

The study is observational and subject to reverse causality, omitted time-varying confounders, measurement error, complete-case selection, unresolved data definitions, possible data-entry errors, limited within-country variation, a relatively short time period, serial dependence, and potentially lagged or nonlinear relationships. Country fixed effects control for time-invariant characteristics but do not solve every endogeneity problem.

The next research steps should be to verify GDP and expenditure definitions against authoritative metadata, validate suspicious values, study lagged and nonlinear relationships, test alternative missing-data approaches, and identify a credible causal design if causal questions are pursued. For evaluating the work as an undergraduate research project, the strongest contribution is the reproducible workflow and the disciplined distinction between pooled cross-country patterns and within-country associations.
