# Determinants of Life Expectancy: A Panel Data Analysis

Life expectancy reflects economic conditions, education, healthcare systems, disease burden, and many other features of a country. This project examines how several of these measures are associated with national life expectancy using country-year panel data. Its central question is not only whether countries differ from one another, but whether changes within the same country are associated with changes in life expectancy after accounting for common year shocks.

The project follows the analysis from raw-data auditing through cleaning, descriptive exploration, model diagnostics, regression, and robustness checks. It is an observational study: every result is interpreted as an association, not as evidence of a causal effect.

## Data and scope

The repository documentation identifies the source as the Kaggle Life Expectancy (WHO) dataset. The raw data contain:

- Raw observations: 2,938
- Countries: 193
- Years: 2000–2015
- Unit of observation: country-year
- Main outcome: life expectancy

Country and year uniquely identify each observation, but the panel is unbalanced: most countries have all 16 years while ten countries appear only once. The raw dataset is preserved at `data/raw/life_expectancy.csv`; the reproducibly generated, audit-flagged dataset is `data/processed/life_expectancy_clean.csv`.

The audit found no duplicate country-year keys or exact duplicate rows. Missingness and suspicious values are documented rather than hidden: raw values remain intact, clearly invalid values are set to missing only in analysis copies, and unusual or unresolved observations retain explicit flags. GDP and total-expenditure definitions remain unresolved in the supplied metadata and are therefore described conservatively.

## Analytical approach

The main analysis uses one common complete-case sample of 2,319 observations from 157 countries over 2000–2015. Keeping the sample fixed makes changes across model specifications easier to interpret. Four models are compared:

1. Pooled OLS with HC1 heteroskedasticity-robust standard errors.
2. Pooled OLS with year fixed effects and HC1 standard errors.
3. Country fixed effects with standard errors clustered by country.
4. Country and year fixed effects with standard errors clustered by country.

The primary covariates are schooling, `log(1 + GDP)`, total expenditure, polio vaccination coverage, and `log(1 + HIV/AIDS)`. The logarithmic transformations reduce the influence of strongly right-skewed values while retaining zeros. Adult mortality, infant deaths, and under-five deaths are not used as primary predictors because they are mortality outcomes or mechanically close to life expectancy.

Country fixed effects absorb persistent differences between countries, while year fixed effects absorb shocks shared across countries in a given year. Country-clustered standard errors allow observations from the same country to remain correlated over time. These choices strengthen the comparison, but they do not eliminate reverse causality, time-varying omitted variables, measurement error, or missing-data selection.

## What the analysis finds

In pooled models, schooling, recorded GDP, total expenditure, and polio coverage have sizeable positive associations with life expectancy. Those estimates become much smaller after country and year fixed effects are introduced, suggesting that persistent differences between countries account for much of the pooled pattern.

The two-way fixed-effects estimates are:

| Variable | Coefficient | 95% confidence interval | p-value |
|---|---:|---:|---:|
| Schooling | 0.1450 | [-0.0547, 0.3448] | 0.155 |
| log(1 + GDP) | -0.0208 | [-0.0882, 0.0465] | 0.544 |
| Total expenditure | -0.0532 | [-0.1340, 0.0277] | 0.198 |
| Polio coverage | 0.0037 | [-0.0019, 0.0094] | 0.197 |
| log(1 + HIV/AIDS) | -4.1969 | [-5.2728, -3.1209] | <0.001 |

The transformed HIV/AIDS coefficient remains negative and approximately -4.1 to -4.3 across several focused robustness checks. By contrast, schooling and polio are more sensitive to the treatment of influential observations, and GDP, expenditure, and vaccination estimates depend more strongly on transformation and variable choice. Fourteen robustness specifications document these patterns in detail.

The clearest lesson is methodological: a strong cross-country association need not remain strong when identification comes from changes within countries. The estimates should still be read as conditional associations rather than causal effects.

## Explore the project

For a concise interpretation, begin with the [executive summary](reports/executive_summary.md). The [final report](reports/final_report.md) presents the full research design, results, diagnostics, robustness checks, and limitations. The [analysis notebook](notebooks/life_expectancy_analysis.ipynb) provides a guided path through the workflow, while the reusable implementation lives in `src/`.

Key supporting materials include:

- [Data audit](reports/data_audit.md)
- [Cleaning decisions](reports/data_cleaning_decisions.md)
- [Descriptive results](reports/descriptive_results.md)
- [Model diagnostics](reports/model_diagnostics.md)
- [Main model results](reports/model_results.md)
- [Robustness results](reports/robustness_results.md)
- [Generated figures](figures/) and [tables](tables/)

## Repository structure

```text
data/
  raw/                  Preserved source data
  processed/            Reproducibly generated, audit-flagged data
figures/                Descriptive and model diagnostic figures
notebooks/              Guided analysis notebook
reports/                Audit, cleaning, modeling, and final reports
src/                    Reusable analysis scripts
tables/                 Generated analytical tables
README.md               Project orientation
REPRODUCIBILITY.md       Detailed environment and execution guide
requirements.txt        Python dependencies
```

## Reproduce the analysis

Python 3.12 was used for verification.

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

Run the following commands from the repository root:

```bash
python src/data_audit.py --input data/raw/life_expectancy.csv
python src/data_cleaning.py
python src/descriptive_analysis.py
python src/model_diagnostics.py
python src/regression_models.py
python src/robustness.py
```

The scripts are deterministic and do not use random sampling or stochastic optimization. See the [reproducibility guide](REPRODUCIBILITY.md) for environment activation, expected outputs, data-integrity checks, and known limitations.

