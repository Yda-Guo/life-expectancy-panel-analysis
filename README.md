# Determinants of Life Expectancy: A Panel Data Analysis

## Project overview

This undergraduate statistics project studies how socioeconomic, healthcare, and public-health measures are associated with national life expectancy. It uses country-year panel data and compares pooled cross-country associations with within-country fixed-effects estimates.

The analysis is observational. It does not claim that the included variables cause changes in life expectancy.

## Research question

Which socioeconomic, healthcare, and public-health factors are associated with changes in national life expectancy, and how do those associations change after controlling for country and year fixed effects?

## Data

Source: Kaggle, Life Expectancy (WHO), as identified in the supplied project documentation.

- Raw observations: 2,938
- Countries: 193
- Years: 2000–2015
- Unit of observation: country-year
- Main outcome: life expectancy

The raw dataset is `data/raw/life_expectancy.csv`. It must not be edited. The processed, audit-flagged dataset is `data/processed/life_expectancy_clean.csv`.

## Repository structure

```text
data/
  raw/                  Original source data; never overwritten
  processed/            Reproducibly generated cleaned data
figures/                Descriptive and model diagnostic figures
notebooks/              Guided analysis Notebook
reports/                Audit, cleaning, modeling, and final reports
src/                    Reusable analysis scripts
tables/                 Generated analytical tables
README.md               Project orientation
REPRODUCIBILITY.md       Detailed environment and execution guide
requirements.txt        Python dependencies
```

## Empirical methods

The main comparison uses one complete-case sample of 2,319 observations from 157 countries over 2000–2015. It estimates:

1. Pooled OLS with HC1 robust standard errors.
2. Pooled OLS with year fixed effects and HC1 standard errors.
3. Country fixed effects with country-clustered standard errors.
4. Country and year fixed effects with country-clustered standard errors.

The primary covariates are schooling, `log(1 + GDP)`, total expenditure, polio vaccination coverage, and `log(1 + HIV/AIDS)`. GDP is not labeled per capita because that definition is not verified by the supplied documentation.

## Main findings

In pooled models, schooling, recorded GDP, total expenditure, and polio coverage have sizeable positive associations with life expectancy. Their estimates decline substantially after country and year fixed effects are introduced, indicating that persistent cross-country differences account for much of the pooled association.

In the two-way fixed-effects model, the estimates are:

- schooling: 0.1450 (p = 0.155);
- log(1 + GDP): -0.0208 (p = 0.544);
- total expenditure: -0.0532 (p = 0.198);
- polio: 0.0037 (p = 0.197);
- log(1 + HIV/AIDS): -4.1969 (p < 0.001).

The transformed HIV/AIDS coefficient remains approximately -4.1 to -4.3 across several focused robustness checks. This is an association, not a causal estimate.

## Limitations

The project is limited by its observational design, possible reverse causality, omitted time-varying confounders, measurement error, missing-data selection, possible data-entry errors, unresolved GDP and expenditure definitions, limited within-country variation, short time coverage, and potentially lagged or nonlinear relationships. Country fixed effects control for time-invariant country characteristics but do not establish causality.

## Environment setup

Python 3.12 was used for verification.

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

See [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for activation commands, expected outputs, and data-integrity details.

## Reproduction commands

Run from the repository root in this order:

```bash
python src/data_audit.py --input data/raw/life_expectancy.csv
python src/data_cleaning.py
python src/descriptive_analysis.py
python src/model_diagnostics.py
python src/regression_models.py
python src/robustness.py
```

## Key outputs

- Final report: [`reports/final_report.md`](reports/final_report.md)
- Executive summary: [`reports/executive_summary.md`](reports/executive_summary.md)
- Notebook: [`notebooks/life_expectancy_analysis.ipynb`](notebooks/life_expectancy_analysis.ipynb)
- Figures: [`figures/`](figures/)
- Tables: [`tables/`](tables/)
- Model results: [`reports/model_results.md`](reports/model_results.md)
- Robustness results: [`reports/robustness_results.md`](reports/robustness_results.md)
