# Determinants of Life Expectancy: A Panel Data Analysis

This undergraduate project studies how recorded socioeconomic and health-system measures are associated with national life expectancy in a country-year panel. Its main lesson is methodological: associations that look large across countries can shrink sharply when the comparison instead uses changes within the same country and controls for common year shocks.

Every result is associational. Fixed effects, clustering, and lagging improve the comparison but do not establish causality.

## Data and methodological correction

The Kaggle **Life Expectancy (WHO)** file contains 2,938 observations for 193 countries in 2000–2015. Kaggle says the merged health data originate from WHO GHO and economic data from the United Nations. The raw file is preserved; cleaning creates separate analysis copies and flags, without arbitrary imputation, winsorization, or automatic outlier deletion.

Metadata review changed the primary model. The source `HIV/AIDS` field belongs to a WHO cause-specific mortality indicator family measured as deaths per 1,000 live births. Because life expectancy is itself mortality-based, treating contemporaneous HIV/AIDS mortality as an independent determinant created direct conceptual outcome overlap. It is now excluded from the main model and retained only as a labeled supplementary check. The [data dictionary](data_dictionary.md) records sources, units, and remaining ambiguities; in particular, the merged metadata do not establish that `GDP` is GDP per capita or identify the exact denominator for `Total expenditure`.

## Analytical approach

Four models use the same complete-case sample of 2,319 observations from 157 countries:

1. Pooled OLS with HC1 standard errors.
2. Pooled OLS with year fixed effects and HC1 standard errors.
3. Country fixed effects with country-clustered standard errors.
4. Country and year fixed effects with country-clustered standard errors.

The primary covariates are schooling, `log(1 + GDP)`, total expenditure, and polio three-dose vaccination coverage. Adult mortality, infant deaths, and under-five deaths also remain excluded because they are mortality outcomes or mechanically close to life expectancy.

## Main result

The positive pooled associations for schooling, GDP, and polio become much smaller in the two-way fixed-effects model:

| Variable | Pooled OLS | TWFE | TWFE 95% CI | p-value |
|---|---:|---:|---:|---:|
| Schooling | 1.6878 | 0.1340 | [-0.1068, 0.3748] | 0.275 |
| log(1 + GDP) | 1.0492 | -0.0157 | [-0.0886, 0.0571] | 0.672 |
| Total expenditure | -0.1003 | -0.0337 | [-0.1216, 0.0542] | 0.452 |
| Polio coverage | 0.0617 | 0.0049 | [-0.0017, 0.0115] | 0.145 |

For example, a one-unit increase in the recorded schooling measure is associated with 1.69 more life-expectancy years in pooled data, but only 0.13 years within countries after country and year controls; the TWFE interval ranges from -0.11 to 0.37 years. For `log(1 + GDP)`, the effect of a change from (x_0) to (x_1) is the coefficient times `log((1+x1)/(1+x0))`; the familiar 1% approximation is only reasonable away from zero.

Focused checks add:

- a one-year-lagged TWFE model (2,317 observations, 157 countries), whose estimates remain small and uncertain;
- a complete-case diagnostic showing similar mean life expectancy but a later year composition among excluded rows (mean year 2009.40 versus 2007.02; standardized difference -0.50);
- country-and-year two-way clustered standard errors as a sensitivity check, with an explicit warning that only 16 year clusters are available;
- 12 nonredundant coefficient/sample checks, plus a separately labeled HIV/AIDS mortality-overlap result.

## Explore and reproduce

Start with the [executive summary](reports/executive_summary.md), then the [final report](reports/final_report.md). The [notebook](notebooks/life_expectancy_analysis.ipynb) is a guided execution layer; reusable logic is in `src/`.

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python src/data_audit.py --input data/raw/life_expectancy.csv
python src/data_cleaning.py
python src/descriptive_analysis.py
python src/model_diagnostics.py
python src/regression_models.py
python src/robustness.py
```

Key generated outputs include [main regression results](tables/main_regression_results.csv), [lagged results](tables/lagged_model_results.csv), [complete-case diagnostics](tables/complete_case_selection_diagnostics.csv), and [robustness results](tables/robustness_results.csv). See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for detailed checks and limitations.

```text
data/        Preserved raw data and reproducibly generated processed data
figures/     Descriptive and model diagnostic figures
notebooks/   Guided presentation / execution layer
reports/     Audit, methods, results, and interpretation
src/         Reusable analysis scripts
tables/      Generated analytical tables
```
