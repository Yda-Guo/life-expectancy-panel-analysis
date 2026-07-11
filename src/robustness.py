"""Run focused two-way fixed-effects robustness and sensitivity checks."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from model_utils import MAIN_REGRESSORS, construct_sample, fit_model, load_model_data, tidy_result


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"
REPORT = ROOT / "reports/robustness_results.md"


def main() -> None:
    df = load_model_data()
    influence = pd.read_csv(TABLES / "pooled_influence_diagnostics.csv")
    influential_keys = set(map(tuple, influence.loc[influence["influential_rule_4_over_n"], ["country", "year"]].to_numpy()))
    influential_mask = pd.Series([(c, y) in influential_keys for c, y in zip(df.country, df.year)], index=df.index)

    checks = [
        ("R1_main_cleaned", MAIN_REGRESSORS, "main_cleaned", True, None, None),
        ("R2_exclude_clearly_invalid_rows", MAIN_REGRESSORS, "exclude_clearly_invalid", True, None, None),
        ("R3_exclude_invalid_and_unresolved", MAIN_REGRESSORS, "exclude_invalid_unresolved", True, None, None),
        ("R4_specification_specific_sample", MAIN_REGRESSORS, "main_cleaned", False, None, None),
        ("R5_untransformed_gdp", ["schooling", "gdp_analysis", "total_expenditure", "polio", "log1p_hiv_aids"], "main_cleaned", True, None, None),
        ("R6_untransformed_hiv", ["schooling", "log1p_gdp", "total_expenditure", "polio", "hiv_aids"], "main_cleaned", True, None, None),
        ("R7_exclude_gdp", ["schooling", "total_expenditure", "polio", "log1p_hiv_aids"], "main_cleaned", True, None, None),
        ("R8_income_composition_replaces_schooling", ["income_composition_of_resources", "log1p_gdp", "total_expenditure", "polio", "log1p_hiv_aids"], "main_cleaned", True, None, None),
        ("R9_diphtheria_replaces_polio", ["schooling", "log1p_gdp", "total_expenditure", "diphtheria", "log1p_hiv_aids"], "main_cleaned", True, None, None),
        ("R10_polio_and_diphtheria", ["schooling", "log1p_gdp", "total_expenditure", "polio", "diphtheria", "log1p_hiv_aids"], "main_cleaned", True, None, None),
        ("R11_exclude_total_expenditure", ["schooling", "log1p_gdp", "polio", "log1p_hiv_aids"], "main_cleaned", True, None, None),
        ("R12_exclude_influential", MAIN_REGRESSORS, "main_cleaned", True, influential_mask, None),
        ("R13_developed_only", MAIN_REGRESSORS, "main_cleaned", True, None, "Developed"),
        ("R14_developing_only", MAIN_REGRESSORS, "main_cleaned", True, None, "Developing"),
    ]

    result_frames, sample_rows = [], []
    for name, regressors, flag_rule, exclude_single, influence_mask, status in checks:
        sample, info = construct_sample(
            df, regressors, exclude_single_year=exclude_single, flag_rule=flag_rule,
            influential_mask=influence_mask, status=status,
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
    results = pd.concat(result_frames, ignore_index=True)
    samples = pd.DataFrame(sample_rows)
    results.to_csv(TABLES / "robustness_results.csv", index=False)
    samples.to_csv(TABLES / "robustness_sample_summary.csv", index=False)
    main_samples = pd.read_csv(TABLES / "main_model_sample_summary.csv")
    pd.concat([main_samples, samples], ignore_index=True, sort=False).to_csv(TABLES / "model_sample_summary.csv", index=False)

    main = results.loc[results.model.eq("R1_main_cleaned")].set_index("variable")["coefficient"]
    comparison = results.pivot(index="model", columns="variable", values="coefficient")
    comparison.to_csv(TABLES / "robustness_coefficient_comparison.csv")
    same_variable_checks = comparison[[column for column in MAIN_REGRESSORS if column in comparison]].copy()
    relative_spread = ((same_variable_checks.max() - same_variable_checks.min()) / main.abs()).replace([float("inf")], pd.NA)

    report = f"""# Robustness results

All checks estimate country and year two-way fixed effects with country-clustered standard errors. They address specific sample, transformation, definition, collinearity, and influence concerns; they are not selected by p-values.

## Sample and flag sensitivity

- Main cleaned sample: {int(samples.loc[samples.model.eq('R1_main_cleaned'), 'observations'].iloc[0]):,} observations.
- Excluding all clearly invalid rows: {int(samples.loc[samples.model.eq('R2_exclude_clearly_invalid_rows'), 'observations'].iloc[0]):,} observations.
- Excluding clearly invalid and unresolved rows: {int(samples.loc[samples.model.eq('R3_exclude_invalid_and_unresolved'), 'observations'].iloc[0]):,} observations.
- The 62 merely unusual retained observations are not automatically deleted.
- Specification-specific main-variable sample including single-year countries: {int(samples.loc[samples.model.eq('R4_specification_specific_sample'), 'observations'].iloc[0]):,} observations. Single-year countries provide no within-country identifying variation even when present.

## Focused checks

- GDP transformation: compare R1 with R5.
- HIV/AIDS transformation: compare R1 with R6.
- GDP definition/missingness: R7 excludes GDP.
- Development-measure overlap: R8 replaces schooling with income composition.
- Vaccination choice/collinearity: R9 replaces polio with diphtheria; R10 includes both.
- Expenditure-definition ambiguity: R11 omits total expenditure.
- Influence: R12 excludes pooled observations with Cook's distance above 4/n.
- Heterogeneity: R13 and R14 estimate developed and developing samples separately when sample size permits.

## Stability guide

Relative coefficient ranges across checks using the same variables are:

{relative_spread.rename('relative_range_to_main_abs_coefficient').round(3).to_frame().to_markdown()}

- Flag handling is stable: R1–R3 produce very similar coefficients, including `log1p_hiv_aids` estimates between {comparison.loc[['R1_main_cleaned','R2_exclude_clearly_invalid_rows','R3_exclude_invalid_and_unresolved'], 'log1p_hiv_aids'].min():.3f} and {comparison.loc[['R1_main_cleaned','R2_exclude_clearly_invalid_rows','R3_exclude_invalid_and_unresolved'], 'log1p_hiv_aids'].max():.3f}.
- `log1p_hiv_aids` is also similar in the main, no-GDP, no-expenditure, and influential-observation checks. The developed-only estimate changes sign, so subgroup interpretation is sensitive and unresolved.
- Schooling and polio are sensitive to the influential-observation rule: both estimates become larger in R12. This rule removes many observations and is a sensitivity check, not a preferred specification.
- GDP, expenditure, and vaccination coefficients are generally small in the two-way models and depend on transformation or variable selection. Including polio and diphtheria together further attenuates the polio estimate.

Large ranges indicate sensitivity to specification or sample choices, not evidence of a causal effect. Exact coefficients, confidence intervals, p-values, samples, and fit statistics are in `tables/robustness_results.csv` and `tables/robustness_sample_summary.csv`.

## Remaining uncertainty

- GDP units and the total-expenditure definition remain unresolved.
- Unresolved flagged values are retained except in the explicit strict sample.
- Developed-country estimates may have limited within-country variation and relatively few country clusters.
- Robustness checks assess stability but cannot create a causal research design.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(f"Estimated {samples.status.eq('estimated').sum()} focused robustness specifications")
    print(samples[["model", "observations", "countries", "status"]].to_string(index=False))


if __name__ == "__main__":
    main()
