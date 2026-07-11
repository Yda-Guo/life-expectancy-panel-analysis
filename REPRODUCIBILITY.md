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
6. `robustness.py` estimates 14 focused two-way fixed-effects checks and writes robustness result/sample tables and `reports/robustness_results.md`.

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
dfb73be2ab34f2b0df09a33e9e02e4bc86ccbd2a07c72eddc3e0c3661a0ad066
```

The verified processed Git blob is `3d3cb0b0cc4f1e97fa9f194d555ec4acf62a8c2a`; rerunning the deterministic cleaning script should reproduce its contents under the verified environment.

## Known limitations

- GDP and total-expenditure definitions remain unresolved in the supplied metadata.
- The workflow uses complete-case samples rather than a general missing-data estimator.
- Flagged unusual and unresolved observations remain unless an explicit robustness sample excludes them.
- Fixed effects do not resolve reverse causality, time-varying omitted variables, or measurement error.
- Subgroup estimates may be unstable because they use fewer countries and clusters.
