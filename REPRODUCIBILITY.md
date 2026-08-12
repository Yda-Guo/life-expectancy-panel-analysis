# Reproducibility Guide

## Environment

The verified environment used Python 3.12. The project dependencies are declared in `requirements.txt`:

- pandas
- matplotlib
- statsmodels
- tabulate

Create and activate an isolated environment from the repository root. For example:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

macOS or Linux:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Working directory

Run every command from the repository root—the directory containing `README.md`, `requirements.txt`, `src/`, `data/`, `tables/`, and `figures/`. All permanent scripts use repository-relative paths. Do not run them from `src/`.

## Ordered execution

```bash
python src/data_audit.py --input data/raw/life_expectancy.csv
python src/data_cleaning.py
python src/descriptive_analysis.py
python src/model_diagnostics.py
python src/regression_models.py
python src/robustness.py
```

## Expected outputs

1. `data_audit.py` checks dimensions, identifiers, balance, missingness, ranges, skewness, and suspicious within-country jumps. It writes `reports/data_audit.md` and audit tables.
2. `data_cleaning.py` creates `data/processed/life_expectancy_clean.csv`, records cleaning decisions, creates audit flags and transformations, and writes zero/missingness/sample tables. It verifies the raw SHA-256 before and after execution.
3. `descriptive_analysis.py` writes descriptive tables and figures, including life-expectancy distributions, year averages, status comparisons, representative trends, correlations, and within/between variation.
4. `model_diagnostics.py` writes the estimation-sample summary, candidate correlations, VIFs, and within/between variation, plus `reports/model_diagnostics.md`.
5. `regression_models.py` estimates the four main models, writes `tables/main_regression_results.csv` and model diagnostics, generates five model figures, and writes `reports/model_results.md`.
6. `robustness.py` estimates 12 focused coefficient/sample checks, one labeled mortality-overlap supplement, one alternative-inference check, and one one-year-lagged TWFE model. It writes robustness tables, `tables/lagged_model_results.csv`, and `reports/robustness_results.md`.

`model_diagnostics.py` also writes `tables/complete_case_selection_diagnostics.csv`, comparing membership in the actual current main sample without imputing missing covariates.

## Determinism

The scripts do not use random sampling, simulation, stochastic optimization, or random train/test splits. No random seed is required. Rows are sorted deterministically during cleaning. Numerical output may differ in insignificant final digits across operating systems or dependency versions, but the documented sample sizes and rounded results should match.

## Notebook

Start Jupyter from the repository root, then open:

```text
notebooks/life_expectancy_analysis.ipynb
```

The Notebook checks that `data/raw/life_expectancy.csv` is reachable from the current working directory and invokes the reusable scripts. Essential logic is maintained in `src/`; the Notebook is a guided presentation layer.

## Data protection

Do not edit or overwrite `data/raw/life_expectancy.csv`. All transformations belong in scripts and the processed dataset. The verified raw SHA-256 is:

```text
872125dd1dd0f9140fbead61df20585a815f5cf47db68f08bf54efaf87963b11
```

The SHA-256 above is calculated over the repository file bytes. `data_cleaning.py` and `regression_models.py` independently compare the raw file before and after their work; neither relies only on the documented value.

## Known limitations

- GDP units and the exact total-expenditure denominator remain unresolved in the merged-file metadata.
- The workflow uses complete-case samples rather than a general missing-data estimator.
- The included/excluded diagnostic describes selection but cannot establish that missingness is ignorable.
- Flagged unusual and unresolved observations remain unless an explicit robustness sample excludes them.
- Fixed effects do not resolve reverse causality, time-varying omitted variables, or measurement error.
- The lagged model improves temporal ordering but does not resolve endogeneity.
- Two-way clustering is a sensitivity check only because the panel has just 16 year clusters.
- Subgroup estimates may be unstable because they use fewer countries and clusters.
