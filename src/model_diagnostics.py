"""Generate pre-model diagnostics for candidate regressors and the main sample."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

from model_utils import MAIN_REGRESSORS, construct_sample, load_model_data


TABLES = ROOT / "tables"
REPORT = ROOT / "reports/model_diagnostics.md"


def selection_diagnostics(df: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    """Compare main complete cases with excluded rows without redefining the sample."""
    included = df.index.isin(sample.index)
    rows = [{
        "diagnostic": "observations", "included_value": int(included.sum()),
        "excluded_value": int((~included).sum()), "difference": np.nan,
        "standardized_difference": np.nan, "included_nonmissing_n": int(included.sum()),
        "excluded_nonmissing_n": int((~included).sum()), "note": "Counts of country-year rows",
    }, {
        "diagnostic": "countries", "included_value": sample["country"].nunique(),
        "excluded_value": df.loc[~included, "country"].nunique(), "difference": np.nan,
        "standardized_difference": np.nan, "included_nonmissing_n": int(included.sum()),
        "excluded_nonmissing_n": int((~included).sum()), "note": "A country may appear in both groups",
    }]
    comparison = df.assign(developed=df["status"].eq("Developed").astype(float))
    for variable in ["life_expectancy", "developed", "year", *MAIN_REGRESSORS]:
        left = comparison.loc[included, variable].dropna()
        right = comparison.loc[~included, variable].dropna()
        pooled_sd = np.sqrt((left.var(ddof=1) + right.var(ddof=1)) / 2)
        difference = left.mean() - right.mean()
        rows.append({
            "diagnostic": variable, "included_value": left.mean(), "excluded_value": right.mean(),
            "difference": difference,
            "standardized_difference": difference / pooled_sd if pooled_sd else np.nan,
            "included_nonmissing_n": len(left), "excluded_nonmissing_n": len(right),
            "note": "Means use observed values; missingness-defining covariates are not imputed",
        })
    for year in sorted(df["year"].dropna().unique()):
        left_share = df.loc[included, "year"].eq(year).mean()
        right_share = df.loc[~included, "year"].eq(year).mean()
        rows.append({
            "diagnostic": f"year_share_{int(year)}", "included_value": left_share,
            "excluded_value": right_share, "difference": left_share - right_share,
            "standardized_difference": np.nan, "included_nonmissing_n": int(included.sum()),
            "excluded_nonmissing_n": int((~included).sum()),
            "note": "Share of observations within each membership group",
        })
    return pd.DataFrame(rows)


def main() -> None:
    df = load_model_data()
    sample, sample_info = construct_sample(df, MAIN_REGRESSORS, exclude_single_year=True)
    candidates = [
        "schooling", "income_composition_of_resources", "log1p_gdp", "gdp_analysis",
        "total_expenditure", "polio", "diphtheria", "log1p_hiv_aids", "hiv_aids", "bmi_analysis",
    ]

    summary = sample[["life_expectancy", *MAIN_REGRESSORS]].describe().T
    summary.to_csv(TABLES / "estimation_sample_summary_statistics.csv", index_label="variable")
    selection = selection_diagnostics(df, sample)
    selection.to_csv(TABLES / "complete_case_selection_diagnostics.csv", index=False)

    variation_rows = []
    for variable in candidates:
        valid = df[["country", variable]].dropna()
        country_means = valid.groupby("country")[variable].mean()
        within = valid[variable] - valid.groupby("country")[variable].transform("mean")
        variation_rows.append({
            "variable": variable,
            "observations": len(valid),
            "countries": valid["country"].nunique(),
            "overall_sd": valid[variable].std(),
            "between_country_sd": country_means.std(),
            "within_country_sd": within.std(),
            "within_to_overall_sd_ratio": within.std() / valid[variable].std(),
        })
    variation = pd.DataFrame(variation_rows)
    variation.to_csv(TABLES / "model_within_between_variation.csv", index=False)

    diagnostic_sample = df[["life_expectancy", *candidates]].dropna()
    correlations = diagnostic_sample.corr()
    correlations.to_csv(TABLES / "model_candidate_correlations.csv")

    vif_data = sm.add_constant(sample[MAIN_REGRESSORS].copy())
    vif_rows = [
        {"variable": column, "vif": variance_inflation_factor(vif_data.to_numpy(), position)}
        for position, column in enumerate(vif_data.columns)
        if column != "const"
    ]
    vif = pd.DataFrame(vif_rows)
    vif.to_csv(TABLES / "model_vif.csv", index=False)

    key_correlations = {
        "schooling_income_composition": correlations.loc["schooling", "income_composition_of_resources"],
        "schooling_log1p_gdp": correlations.loc["schooling", "log1p_gdp"],
        "income_composition_log1p_gdp": correlations.loc["income_composition_of_resources", "log1p_gdp"],
        "polio_diphtheria": correlations.loc["polio", "diphtheria"],
    }
    pd.DataFrame([key_correlations]).to_csv(TABLES / "key_model_correlations.csv", index=False)

    report = f"""# Model diagnostics

## Observed sample facts

- The shared main comparison sample has {sample_info['observations']:,} observations from {sample_info['countries']} countries, covering {sample_info['year_start']}–{sample_info['year_end']}.
- Ten single-year countries are excluded from fixed-effects comparisons because they provide no within-country identifying variation.
- The 18 clearly invalid observations are represented by preserved original variables, row/variable flags, and `_analysis` copies in which only the affected analysis value is missing. The main model does not use adult mortality, infant deaths, or under-five deaths.

## Variation and overlap

- Within/between variation is saved in `tables/model_within_between_variation.csv`. Variables with a within-to-overall SD ratio below 0.25 should be treated as having relatively little within-country variation.
- Schooling–income composition correlation: {key_correlations['schooling_income_composition']:.3f}.
- Schooling–log(1 + GDP) correlation: {key_correlations['schooling_log1p_gdp']:.3f}.
- Income composition–log(1 + GDP) correlation: {key_correlations['income_composition_log1p_gdp']:.3f}.
- Polio–diphtheria correlation: {key_correlations['polio_diphtheria']:.3f}.
- Maximum VIF among the main non-fixed-effect regressors (with an intercept in the auxiliary regressions): {vif['vif'].max():.2f}. VIF is calculated on raw regressors and does not directly diagnose collinearity after fixed-effect demeaning.

## Modeling decisions

- The preferred parsimonious covariates are schooling, `log1p_gdp`, total expenditure, and polio.
- `HIV/AIDS` is retained only for descriptive/supplementary analysis because it is a contemporaneous mortality-rate measure, not an independent exposure.
- GDP is not described as per capita because the supplied documentation does not verify that definition.
- Schooling, income composition, and GDP are not placed together in the primary model because they are conceptually overlapping development measures.
- Polio and diphtheria are compared in robustness checks; both are included together only as an explicit collinearity sensitivity check.
- Adult mortality, infant deaths, and under-five deaths are excluded from the primary specification because they are mortality outcomes or mechanically close to life expectancy.
- `status` is excluded from country fixed-effects models because it is time-invariant within countries in these data.
- Variable selection is based on definitions, missingness, within-country variation, and conceptual parsimony—not p-values.

## Complete-case selection

The included-versus-excluded comparison is saved in `tables/complete_case_selection_diagnostics.csv`. It reports counts, outcome and developed-status differences, year composition, and observed-value comparisons for each main regressor. Covariate rows whose missingness helps define exclusion are explicitly conditional on observed values; no imputation is introduced. The largest absolute standardized difference among the outcome, status, year, and available covariate comparisons is {selection.loc[selection['standardized_difference'].notna(), 'standardized_difference'].abs().max():.2f}. These differences describe selection into the estimation sample and do not correct it.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(f"Diagnostics complete for {sample_info['observations']:,} observations and {sample_info['countries']} countries")
    print(vif.to_string(index=False))


if __name__ == "__main__":
    main()
