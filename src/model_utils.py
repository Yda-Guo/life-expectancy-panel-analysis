"""Shared sample construction and regression helpers for the modeling stage."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/processed/life_expectancy_clean.csv"
REVIEW_PATH = ROOT / "tables/suspicious_value_review.csv"

OUTCOME = "life_expectancy"
MAIN_REGRESSORS = ["schooling", "log1p_gdp", "total_expenditure", "polio", "log1p_hiv_aids"]
DISPLAY_NAMES = {
    "schooling": "Schooling",
    "log1p_gdp": "log(1 + GDP)",
    "gdp_analysis": "GDP (untransformed analysis copy)",
    "total_expenditure": "Total expenditure",
    "polio": "Polio coverage",
    "diphtheria": "Diphtheria coverage",
    "log1p_hiv_aids": "log(1 + HIV/AIDS)",
    "hiv_aids": "HIV/AIDS",
    "income_composition_of_resources": "Income composition of resources",
    "bmi_analysis": "BMI (analysis copy)",
}


@dataclass(frozen=True)
class ModelDefinition:
    name: str
    regressors: list[str]
    country_fe: bool
    year_fe: bool
    covariance: str


def load_model_data() -> pd.DataFrame:
    """Load processed data and add row-level review classifications without altering it."""
    df = pd.read_csv(DATA_PATH)
    review = pd.read_csv(REVIEW_PATH)
    severity = {"merely_unusual": 1, "unresolved": 2, "clearly_invalid": 3}
    row_review = review.assign(severity=review["classification"].map(severity)).groupby(
        ["country", "year"], as_index=False
    ).agg(review_severity=("severity", "max"))
    df = df.merge(row_review, on=["country", "year"], how="left")
    df["review_severity"] = df["review_severity"].fillna(0).astype(int)
    df["row_clearly_invalid_flag"] = df["review_severity"].eq(3)
    df["row_unresolved_flag"] = df["review_severity"].eq(2)
    df["row_unusual_flag"] = df["review_severity"].eq(1)
    return df


def construct_sample(
    df: pd.DataFrame,
    regressors: list[str],
    *,
    exclude_single_year: bool = True,
    flag_rule: str = "main_cleaned",
    influential_mask: pd.Series | None = None,
    status: str | None = None,
) -> tuple[pd.DataFrame, dict[str, int | str | bool]]:
    """Create a transparent complete-case estimation sample and removal accounting."""
    working = df.copy()
    if status is not None:
        working = working.loc[working["status"].eq(status)].copy()
    start = len(working)
    single_year_mask = ~working["country_has_two_plus_years"].astype(bool)
    removed_single_year = int(single_year_mask.sum()) if exclude_single_year else 0
    if exclude_single_year:
        working = working.loc[~single_year_mask].copy()

    if flag_rule == "exclude_clearly_invalid":
        flag_mask = working["row_clearly_invalid_flag"]
    elif flag_rule == "exclude_invalid_unresolved":
        flag_mask = working["row_clearly_invalid_flag"] | working["row_unresolved_flag"]
    elif flag_rule == "main_cleaned":
        flag_mask = pd.Series(False, index=working.index)
    else:
        raise ValueError(f"Unknown flag rule: {flag_rule}")
    removed_flagged = int(flag_mask.sum())
    working = working.loc[~flag_mask].copy()

    required = [OUTCOME, *regressors]
    missing_mask = working[required].isna().any(axis=1)
    removed_missing = int(missing_mask.sum())
    working = working.loc[~missing_mask].copy()

    removed_influential = 0
    if influential_mask is not None:
        aligned = influential_mask.reindex(working.index, fill_value=False)
        removed_influential = int(aligned.sum())
        working = working.loc[~aligned].copy()

    summary = {
        "starting_observations": start,
        "observations": len(working),
        "countries": working["country"].nunique(),
        "year_start": int(working["year"].min()) if len(working) else np.nan,
        "year_end": int(working["year"].max()) if len(working) else np.nan,
        "removed_missing": removed_missing,
        "removed_invalid_rule": removed_flagged,
        "removed_single_year": removed_single_year,
        "removed_influential": removed_influential,
        "single_year_included": not exclude_single_year,
        "flag_rule": flag_rule,
    }
    return working, summary


def fit_model(
    data: pd.DataFrame,
    regressors: list[str],
    *,
    country_fe: bool,
    year_fe: bool,
    covariance: str,
):
    terms = list(regressors)
    if country_fe:
        terms.append("C(country)")
    if year_fe:
        terms.append("C(year)")
    formula = f"{OUTCOME} ~ " + " + ".join(terms)
    model = smf.ols(formula, data=data)
    if covariance == "HC1":
        result = model.fit(cov_type="HC1")
    elif covariance == "cluster_country":
        result = model.fit(
            cov_type="cluster",
            cov_kwds={"groups": data["country"], "use_correction": True},
        )
    else:
        result = model.fit()
    return result, formula


def tidy_result(
    result,
    model_name: str,
    regressors: list[str],
    data: pd.DataFrame,
    *,
    country_fe: bool,
    year_fe: bool,
    covariance: str,
) -> pd.DataFrame:
    ci = result.conf_int()
    rows = []
    for variable in regressors:
        rows.append(
            {
                "model": model_name,
                "variable": variable,
                "variable_label": DISPLAY_NAMES.get(variable, variable),
                "coefficient": result.params[variable],
                "std_error": result.bse[variable],
                "ci_lower_95": ci.loc[variable, 0],
                "ci_upper_95": ci.loc[variable, 1],
                "p_value": result.pvalues[variable],
                "observations": int(result.nobs),
                "countries": data["country"].nunique(),
                "year_start": int(data["year"].min()),
                "year_end": int(data["year"].max()),
                "country_fixed_effects": country_fe,
                "year_fixed_effects": year_fe,
                "standard_errors": covariance,
                "r_squared": result.rsquared,
                "adjusted_r_squared": result.rsquared_adj,
            }
        )
    return pd.DataFrame(rows)


def main_definitions() -> list[ModelDefinition]:
    return [
        ModelDefinition("M1_pooled_ols", MAIN_REGRESSORS, False, False, "HC1"),
        ModelDefinition("M2_pooled_year_fe", MAIN_REGRESSORS, False, True, "HC1"),
        ModelDefinition("M3_country_fe", MAIN_REGRESSORS, True, False, "cluster_country"),
        ModelDefinition("M4_two_way_fe", MAIN_REGRESSORS, True, True, "cluster_country"),
    ]
