"""Generate pre-model diagnostics for candidate regressors and the main sample."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

from model_utils import MAIN_REGRESSORS, construct_sample, load_model_data


TABLES = ROOT / "tables"
REPORT = ROOT / "reports/model_diagnostics.md"


def main() -> None:
    df = load_model_data()
    sample, sample_info = construct_sample(df, MAIN_REGRESSORS, exclude_single_year=True)
    candidates = [
        "schooling", "income_composition_of_resources", "log1p_gdp", "gdp_analysis",
        "total_expenditure", "polio", "diphtheria", "log1p_hiv_aids", "hiv_aids", "bmi_analysis",
    ]

    summary = sample[["life_expectancy", *MAIN_REGRESSORS]].describe().T
    summary.to_csv(TABLES / "estimation_sample_summary_statistics.csv", index_label="variable")

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

- The preferred parsimonious covariates are schooling, `log1p_gdp`, total expenditure, polio, and `log1p_hiv_aids`.
- GDP is not described as per capita because the supplied documentation does not verify that definition.
- Schooling, income composition, and GDP are not placed together in the primary model because they are conceptually overlapping development measures.
- Polio and diphtheria are compared in robustness checks; both are included together only as an explicit collinearity sensitivity check.
- Adult mortality, infant deaths, and under-five deaths are excluded from the primary specification because they are mortality outcomes or mechanically close to life expectancy.
- `status` is excluded from country fixed-effects models because it is time-invariant within countries in these data.
- Variable selection is based on definitions, missingness, within-country variation, and conceptual parsimony—not p-values.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(f"Diagnostics complete for {sample_info['observations']:,} observations and {sample_info['countries']} countries")
    print(vif.to_string(index=False))


if __name__ == "__main__":
    main()
