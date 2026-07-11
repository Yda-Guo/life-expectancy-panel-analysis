"""Estimate the four pre-specified main regression models and diagnostics."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import het_breuschpagan

from model_utils import MAIN_REGRESSORS, construct_sample, fit_model, load_model_data, main_definitions, tidy_result


RAW = ROOT / "data/raw/life_expectancy.csv"
TABLES = ROOT / "tables"
FIGURES = ROOT / "figures"
REPORT = ROOT / "reports/model_results.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name: str) -> None:
    plt.tight_layout()
    plt.savefig(FIGURES / name, dpi=180, bbox_inches="tight")
    plt.close()


def main() -> None:
    before = sha256(RAW)
    df = load_model_data()
    common, info = construct_sample(df, MAIN_REGRESSORS, exclude_single_year=True)
    all_results, sample_rows, fitted = [], [], {}
    for definition in main_definitions():
        result, formula = fit_model(
            common, definition.regressors, country_fe=definition.country_fe,
            year_fe=definition.year_fe, covariance=definition.covariance,
        )
        fitted[definition.name] = result
        all_results.append(tidy_result(
            result, definition.name, definition.regressors, common,
            country_fe=definition.country_fe, year_fe=definition.year_fe,
            covariance=definition.covariance,
        ))
        sample_rows.append({
            "model": definition.name,
            "included_variables": "; ".join(definition.regressors),
            **info,
            "country_fixed_effects": definition.country_fe,
            "year_fixed_effects": definition.year_fe,
            "standard_errors": definition.covariance,
            "formula": formula,
        })
    results = pd.concat(all_results, ignore_index=True)
    samples = pd.DataFrame(sample_rows)
    results.to_csv(TABLES / "main_regression_results.csv", index=False)
    samples.to_csv(TABLES / "main_model_sample_summary.csv", index=False)
    samples.to_csv(TABLES / "model_sample_summary.csv", index=False)

    pooled = fitted["M1_pooled_ols"]
    influence = pooled.get_influence()
    cooks = influence.cooks_distance[0]
    influence_table = common[["country", "year", "life_expectancy"]].copy()
    influence_table["fitted"] = pooled.fittedvalues
    influence_table["residual"] = pooled.resid
    influence_table["studentized_residual"] = influence.resid_studentized_external
    influence_table["cooks_distance"] = cooks
    influence_table["influential_rule_4_over_n"] = cooks > 4 / len(common)
    influence_table.sort_values("cooks_distance", ascending=False).to_csv(TABLES / "pooled_influence_diagnostics.csv", index=False)

    bp = het_breuschpagan(pooled.resid, pooled.model.exog)
    pd.DataFrame([{"lm_statistic": bp[0], "lm_p_value": bp[1], "f_statistic": bp[2], "f_p_value": bp[3]}]).to_csv(TABLES / "pooled_heteroskedasticity_test.csv", index=False)

    plt.figure(figsize=(7, 4)); plt.hist(pooled.resid, bins=30, color="#4776A8", edgecolor="white"); plt.xlabel("Residual"); plt.title("Pooled OLS residual distribution"); save("pooled_residual_distribution.png")
    plt.figure(figsize=(7, 4)); plt.scatter(pooled.fittedvalues, pooled.resid, s=10, alpha=.45); plt.axhline(0, color="black", lw=1); plt.xlabel("Fitted life expectancy"); plt.ylabel("Residual"); plt.title("Pooled OLS residuals versus fitted"); save("pooled_residuals_vs_fitted.png")
    plt.figure(figsize=(8, 4)); plt.scatter(range(len(cooks)), cooks, s=8, alpha=.55); plt.axhline(4/len(common), color="red", ls="--", label="4/n"); plt.ylabel("Cook's distance"); plt.title("Pooled OLS influence diagnostic"); plt.legend(); save("pooled_cooks_distance.png")

    twfe = fitted["M4_two_way_fe"]
    plt.figure(figsize=(7, 4)); plt.scatter(twfe.fittedvalues, twfe.resid, s=10, alpha=.45); plt.axhline(0, color="black", lw=1); plt.xlabel("Fitted life expectancy"); plt.ylabel("Residual"); plt.title("Two-way FE residuals versus fitted"); save("twfe_residuals_vs_fitted.png")
    twfe_residuals = common[["country", "year"]].copy(); twfe_residuals["residual"] = twfe.resid
    twfe_residuals = twfe_residuals.sort_values(["country", "year"])
    lagged = twfe_residuals.groupby("country")["residual"].shift()
    residual_lag1_correlation = twfe_residuals["residual"].corr(lagged)
    twfe_residuals.assign(abs_residual=lambda x: x.residual.abs()).sort_values("abs_residual", ascending=False).to_csv(TABLES / "twfe_residual_diagnostics.csv", index=False)

    plot_data = results.copy()
    offsets = np.linspace(-.18, .18, 4)
    fig, ax = plt.subplots(figsize=(8, 6))
    variables = MAIN_REGRESSORS
    for offset, (model, group) in zip(offsets, plot_data.groupby("model", sort=False)):
        group = group.set_index("variable").loc[variables]
        y = np.arange(len(variables)) + offset
        ax.errorbar(group.coefficient, y, xerr=[group.coefficient-group.ci_lower_95, group.ci_upper_95-group.coefficient], fmt="o", capsize=3, label=model)
    ax.axvline(0, color="black", lw=1); ax.set_yticks(range(len(variables)), variables); ax.set_xlabel("Coefficient with 95% CI"); ax.set_title("Main regression coefficients"); ax.legend(fontsize=8); save("main_coefficient_plot.png")

    main_pivot = results.pivot(index="variable", columns="model", values="coefficient")
    report = f"""# Main regression results

All estimates are associational. The four models use the same {len(common):,}-observation sample from {common['country'].nunique()} countries ({common['year'].min()}–{common['year'].max()}).

## Specifications

1. Pooled OLS with HC1 heteroskedasticity-robust standard errors.
2. Pooled OLS plus year fixed effects with HC1 standard errors.
3. Country fixed effects with standard errors clustered by country.
4. Country and year two-way fixed effects with standard errors clustered by country.

Each model includes schooling, `log1p_gdp`, total expenditure, polio coverage, and `log1p_hiv_aids`. Country/year dummy coefficients are omitted from the main table.

## Coefficient interpretation

- Schooling: coefficient is the estimated difference in life-expectancy years associated with one additional schooling unit, holding included controls fixed.
- Total expenditure: coefficient is the estimated difference in life-expectancy years associated with a one-unit increase in the recorded expenditure measure; its exact definition remains unresolved.
- Polio: coefficient corresponds to a one-percentage-point increase in recorded vaccination coverage.
- For `log1p_gdp` and `log1p_hiv_aids`, the coefficient is a semi-elasticity with respect to `log(1 + X)`. Away from zero, a 1% increase in X is approximately associated with 0.01 times the coefficient in life-expectancy years.
- Pooled estimates combine cross-country and within-country differences. Fixed-effects estimates describe within-country associations after removing time-invariant country differences.

## Observed estimates

{main_pivot.round(4).to_markdown()}

Schooling changes from {main_pivot.loc['schooling', 'M1_pooled_ols']:.3f} in pooled OLS to {main_pivot.loc['schooling', 'M4_two_way_fe']:.3f} in the two-way model. The `log1p_gdp` estimate changes from {main_pivot.loc['log1p_gdp', 'M1_pooled_ols']:.3f} to {main_pivot.loc['log1p_gdp', 'M4_two_way_fe']:.3f}; total expenditure changes from {main_pivot.loc['total_expenditure', 'M1_pooled_ols']:.3f} to {main_pivot.loc['total_expenditure', 'M4_two_way_fe']:.3f}; and polio changes from {main_pivot.loc['polio', 'M1_pooled_ols']:.4f} to {main_pivot.loc['polio', 'M4_two_way_fe']:.4f}. These attenuations and sign changes show that pooled cross-country associations differ substantially from within-country associations after country and year controls. `log1p_hiv_aids` remains negative in all four models, changing from {main_pivot.loc['log1p_hiv_aids', 'M1_pooled_ols']:.3f} to {main_pivot.loc['log1p_hiv_aids', 'M4_two_way_fe']:.3f}.

Full coefficients, robust/clustered standard errors, confidence intervals, p-values, sample metadata, and fit statistics are saved in `tables/main_regression_results.csv`.

## Diagnostics

- Breusch–Pagan LM p-value: {bp[1]:.4g}; robust standard errors are retained. This test does not prove the model is correctly specified.
- Pooled observations above Cook's-distance 4/n rule: {int((cooks > 4/len(common)).sum())}. They are not automatically removed; a documented sensitivity check is reported separately.
- Clustered standard errors are used for both country fixed-effects specifications because repeated observations within countries may have dependent residuals.
- The two-way-FE residual lag-1 correlation within countries is {residual_lag1_correlation:.3f}, supporting the decision to allow within-country residual dependence through country-clustered standard errors. This diagnostic does not prove the covariance specification is correct.
"""
    REPORT.write_text(report, encoding="utf-8")
    after = sha256(RAW)
    if before != after:
        raise RuntimeError("Raw CSV changed while estimating models")
    print(f"Estimated four models on {len(common):,} observations from {common['country'].nunique()} countries")
    print(main_pivot.round(4).to_string())


if __name__ == "__main__":
    main()
