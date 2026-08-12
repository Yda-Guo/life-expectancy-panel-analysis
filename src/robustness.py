"""Run focused sensitivity, inference, and one-year-lag panel checks."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from model_utils import MAIN_REGRESSORS, construct_sample, fit_model, load_model_data, tidy_result


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"
REPORT = ROOT / "reports/robustness_results.md"


def make_consecutive_lags(df: pd.DataFrame, variables: list[str]) -> tuple[pd.DataFrame, list[str]]:
    """Create lags only for adjacent country-years, never across a gap."""
    lagged = df.sort_values(["country", "year"]).copy()
    previous_year = lagged.groupby("country")["year"].shift(1)
    consecutive = lagged["year"].sub(previous_year).eq(1)
    lag_names = []
    for variable in variables:
        lag_name = f"lag1_{variable}"
        lagged[lag_name] = lagged.groupby("country")[variable].shift(1).where(consecutive)
        lag_names.append(lag_name)
    return lagged, lag_names


def validate_lags(source: pd.DataFrame, lagged: pd.DataFrame, variables: list[str]) -> None:
    """Fail fast if a nonconsecutive or cross-country lag enters estimation."""
    ordered = source.sort_values(["country", "year"])
    previous_year = ordered.groupby("country")["year"].shift(1)
    valid = ordered["year"].sub(previous_year).eq(1)
    for variable in variables:
        expected = ordered.groupby("country")[variable].shift(1).where(valid)
        actual = lagged.loc[ordered.index, f"lag1_{variable}"]
        if not actual.equals(expected):
            raise RuntimeError(f"Invalid one-year lag construction for {variable}")


def main() -> None:
    df = load_model_data()
    influence = pd.read_csv(TABLES / "pooled_influence_diagnostics.csv")
    influential_keys = set(map(tuple, influence.loc[influence["influential_rule_4_over_n"], ["country", "year"]].to_numpy()))
    influential_mask = pd.Series([(c, y) in influential_keys for c, y in zip(df.country, df.year)], index=df.index)

    checks = [
        ("R1_main_cleaned", MAIN_REGRESSORS, "main_cleaned", None, None),
        ("R2_exclude_clearly_invalid_rows", MAIN_REGRESSORS, "exclude_clearly_invalid", None, None),
        ("R3_exclude_invalid_and_unresolved", MAIN_REGRESSORS, "exclude_invalid_unresolved", None, None),
        ("R4_untransformed_gdp", ["schooling", "gdp_analysis", "total_expenditure", "polio"], "main_cleaned", None, None),
        ("R5_exclude_gdp", ["schooling", "total_expenditure", "polio"], "main_cleaned", None, None),
        ("R6_income_composition_replaces_schooling", ["income_composition_of_resources", "log1p_gdp", "total_expenditure", "polio"], "main_cleaned", None, None),
        ("R7_diphtheria_replaces_polio", ["schooling", "log1p_gdp", "total_expenditure", "diphtheria"], "main_cleaned", None, None),
        ("R8_polio_and_diphtheria", ["schooling", "log1p_gdp", "total_expenditure", "polio", "diphtheria"], "main_cleaned", None, None),
        ("R9_exclude_total_expenditure", ["schooling", "log1p_gdp", "polio"], "main_cleaned", None, None),
        ("R10_exclude_influential", MAIN_REGRESSORS, "main_cleaned", influential_mask, None),
        ("R11_developed_only", MAIN_REGRESSORS, "main_cleaned", None, "Developed"),
        ("R12_developing_only", MAIN_REGRESSORS, "main_cleaned", None, "Developing"),
        ("S1_add_contemporaneous_hiv_mortality", [*MAIN_REGRESSORS, "log1p_hiv_aids"], "main_cleaned", None, None),
    ]

    result_frames, sample_rows = [], []
    for name, regressors, flag_rule, influence_rule, status in checks:
        sample, info = construct_sample(
            df, regressors, exclude_single_year=True, flag_rule=flag_rule,
            influential_mask=influence_rule, status=status,
        )
        if sample["country"].nunique() < 10 or len(sample) < 100:
            sample_rows.append({"model": name, "status": "not_estimated_insufficient_sample", **info})
            continue
        result, formula = fit_model(sample, regressors, country_fe=True, year_fe=True, covariance="cluster_country")
        result_frames.append(tidy_result(
            result, name, regressors, sample, country_fe=True, year_fe=True,
            covariance="cluster_country",
        ))
        sample_rows.append({
            "model": name, "status": "estimated", "included_variables": "; ".join(regressors),
            **info, "country_fixed_effects": True, "year_fixed_effects": True,
            "standard_errors": "cluster_country", "formula": formula,
        })

    main_sample, main_info = construct_sample(df, MAIN_REGRESSORS, exclude_single_year=True)
    inference_result, inference_formula = fit_model(
        main_sample, MAIN_REGRESSORS, country_fe=True, year_fe=True,
        covariance="cluster_country_year",
    )
    result_frames.append(tidy_result(
        inference_result, "I1_two_way_cluster_country_year", MAIN_REGRESSORS, main_sample,
        country_fe=True, year_fe=True, covariance="cluster_country_year",
    ))
    sample_rows.append({
        "model": "I1_two_way_cluster_country_year", "status": "estimated",
        "included_variables": "; ".join(MAIN_REGRESSORS), **main_info,
        "country_fixed_effects": True, "year_fixed_effects": True,
        "standard_errors": "cluster_country_year", "formula": inference_formula,
    })

    lag_source, lag_regressors = make_consecutive_lags(df, MAIN_REGRESSORS)
    validate_lags(df, lag_source, MAIN_REGRESSORS)
    lag_sample, lag_info = construct_sample(lag_source, lag_regressors, exclude_single_year=True)
    lag_result, lag_formula = fit_model(
        lag_sample, lag_regressors, country_fe=True, year_fe=True, covariance="cluster_country",
    )
    lag_table = tidy_result(
        lag_result, "L1_one_year_lagged_two_way_fe", lag_regressors, lag_sample,
        country_fe=True, year_fe=True, covariance="cluster_country",
    )
    lag_table.to_csv(TABLES / "lagged_model_results.csv", index=False)
    sample_rows.append({
        "model": "L1_one_year_lagged_two_way_fe", "status": "estimated",
        "included_variables": "; ".join(lag_regressors), **lag_info,
        "country_fixed_effects": True, "year_fixed_effects": True,
        "standard_errors": "cluster_country", "formula": lag_formula,
    })

    results = pd.concat(result_frames, ignore_index=True)
    samples = pd.DataFrame(sample_rows)
    results.to_csv(TABLES / "robustness_results.csv", index=False)
    samples.to_csv(TABLES / "robustness_sample_summary.csv", index=False)
    main_samples = pd.read_csv(TABLES / "main_model_sample_summary.csv")
    pd.concat([main_samples, samples], ignore_index=True, sort=False).to_csv(TABLES / "model_sample_summary.csv", index=False)

    comparison = results.pivot(index="model", columns="variable", values="coefficient")
    comparison.to_csv(TABLES / "robustness_coefficient_comparison.csv")
    baseline = comparison.loc["R1_main_cleaned", MAIN_REGRESSORS]
    core = comparison.loc[[
        "R1_main_cleaned", "R2_exclude_clearly_invalid_rows", "R3_exclude_invalid_and_unresolved",
        "R10_exclude_influential", "R11_developed_only", "R12_developing_only",
    ], MAIN_REGRESSORS]
    relative_spread = ((core.max() - core.min()) / baseline.abs()).replace([np.inf], pd.NA)

    r1 = results.loc[results.model.eq("R1_main_cleaned")].set_index("variable")
    i1 = results.loc[results.model.eq("I1_two_way_cluster_country_year")].set_index("variable")
    report = f"""# Robustness and sensitivity results

The analysis now separates coefficient/sample sensitivity, inference sensitivity, temporal ordering, and the conceptually overlapping HIV/AIDS mortality field. These checks assess robustness; none turns the observational design into a causal one.

## 1. Sample and data-rule sensitivity

- Main complete-case sample: {int(samples.loc[samples.model.eq('R1_main_cleaned'), 'observations'].iloc[0]):,} observations.
- Excluding clearly invalid rows: {int(samples.loc[samples.model.eq('R2_exclude_clearly_invalid_rows'), 'observations'].iloc[0]):,} observations.
- Excluding clearly invalid and unresolved rows: {int(samples.loc[samples.model.eq('R3_exclude_invalid_and_unresolved'), 'observations'].iloc[0]):,} observations.
- R4–R9 vary transformation or covariate choice; R10 removes pooled Cook's-distance flags; R11–R12 examine status subgroups.

Relative coefficient ranges for the core sample/subgroup checks are:

{relative_spread.rename('relative_range_to_main_abs_coefficient').round(3).to_frame().to_markdown()}

## 2. Alternative inference

I1 keeps the preferred two-way fixed-effects point specification but clusters by country and year. Point estimates are unchanged by construction; standard errors change. For example, the schooling SE is {r1.loc['schooling', 'std_error']:.4f} with country clustering and {i1.loc['schooling', 'std_error']:.4f} with two-way clustering. The year dimension contains only {main_sample['year'].nunique()} clusters, so the two-way-cluster result is a limited sensitivity check rather than a definitive small-cluster correction.

## 3. One-year-lagged model

L1 regresses current life expectancy on one-year lags of the four preferred covariates with country and year fixed effects and country-clustered standard errors. Lags are created after sorting by country and year and only when the preceding observation is exactly one calendar year earlier. It uses {len(lag_sample):,} observations from {lag_sample['country'].nunique()} countries. Exact estimates are in `tables/lagged_model_results.csv`. Temporal ordering is improved, but reverse causality, time-varying confounding, measurement error, and slow-moving trends remain.

## 4. Contemporaneous HIV/AIDS mortality field

S1 is a labeled supplementary overlap check. The HIV/AIDS field belongs to a contemporaneous cause-specific mortality-rate family and is therefore not interpreted as an independent determinant of life expectancy. Its strong negative coefficient is unsurprising and is not a headline substantive finding.

Exact coefficients, uncertainty estimates, formulas, sample sizes, and flag-removal counts are in `tables/robustness_results.csv`, `tables/robustness_sample_summary.csv`, and `tables/model_sample_summary.csv`.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(f"Estimated {samples.status.eq('estimated').sum()} sensitivity specifications plus the lagged model")
    print(samples[["model", "observations", "countries", "status"]].to_string(index=False))


if __name__ == "__main__":
    main()
