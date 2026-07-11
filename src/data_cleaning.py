"""Create an auditable processed panel without modifying the raw CSV."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/life_expectancy.csv"
PROCESSED = ROOT / "data/processed/life_expectancy_clean.csv"
TABLES = ROOT / "tables"
REPORT = ROOT / "reports/data_cleaning_decisions.md"


def snake_case(value: str) -> str:
    value = re.sub(r"[^0-9A-Za-z]+", "_", value.strip()).strip("_")
    return value.lower()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def neighbor_values(df: pd.DataFrame, row_index: int, variable: str) -> tuple[float, float]:
    country = df.at[row_index, "country"]
    year = df.at[row_index, "year"]
    indexed = df.set_index(["country", "year"])[variable]
    previous = indexed.get((country, year - 1), np.nan)
    following = indexed.get((country, year + 1), np.nan)
    return previous, following


def classify_jump(variable: str, previous: float, current: float, following: float) -> tuple[str, str]:
    """Classify an internally isolated value; never introduce an external replacement."""
    adjacent = [value for value in (previous, following) if pd.notna(value)]
    if variable == "adult_mortality" and current < 10 and any(value > 100 for value in adjacent):
        return (
            "clearly_invalid",
            "Single-digit adult mortality is a decimal/digit-scale break from an adjacent value above 100; set only the analysis copy to missing.",
        )
    if variable == "bmi" and current < 10 and any(value > 25 for value in adjacent):
        return (
            "clearly_invalid",
            "Single-digit national BMI is a decimal/digit-scale break from an adjacent value above 25; set only the analysis copy to missing.",
        )
    if pd.notna(previous) and pd.notna(following):
        neighbor_mid = (previous + following) / 2
        if variable in {"gdp", "population", "adult_mortality"}:
            neighbors_agree = min(previous, following) > 0 and max(previous, following) / min(previous, following) <= 1.5
            isolated = neighbor_mid > 0 and (current / neighbor_mid < 0.2 or current / neighbor_mid > 5)
        elif variable == "bmi":
            neighbors_agree = abs(previous - following) <= 5
            isolated = abs(current - neighbor_mid) >= 10
        else:
            neighbors_agree = abs(previous - following) <= 3
            isolated = abs(current - neighbor_mid) >= 5
        if neighbors_agree and isolated:
            return (
                "clearly_invalid",
                "Isolated factor/decimal-scale break between two similar adjacent-year values; set only the analysis copy to missing.",
            )
    if variable in {"gdp", "population"}:
        return (
            "unresolved",
            "Large scale change may reflect a transcription, unit, or coverage issue; retain and flag pending source verification.",
        )
    return (
        "merely_unusual",
        "Abrupt change remains inside a broad logical range but is not isolated between two agreeing neighbors; retain and flag.",
    )


def main() -> None:
    raw_hash_before = sha256(RAW)
    df = pd.read_csv(RAW)
    df.columns = [snake_case(column) for column in df.columns]
    string_columns = df.columns[df.dtypes.astype(str).isin(["object", "str", "string"])]
    for column in string_columns:
        df[column] = df[column].str.strip()
    df = df.sort_values(["country", "year"]).reset_index(drop=True)

    duplicate_keys = int(df.duplicated(["country", "year"]).sum())
    if duplicate_keys:
        raise ValueError(f"Found {duplicate_keys} duplicate country-year keys")

    country_counts = df.groupby("country")["year"].transform("size")
    df["country_observation_count"] = country_counts
    df["country_has_two_plus_years"] = country_counts.ge(2)
    single_year = sorted(df.loc[~df["country_has_two_plus_years"], "country"].unique())

    flagged = pd.read_csv(TABLES / "suspicious_within_country_jumps.csv")
    flagged["variable_standardized"] = flagged["variable"].map(snake_case)
    review_rows = []
    for row in flagged.itertuples(index=False):
        variable = row.variable_standardized
        matches = df.index[(df["country"] == row.Country) & (df["year"] == row.Year)]
        if len(matches) != 1:
            raise ValueError(f"Could not uniquely locate {row.Country}, {row.Year}")
        idx = int(matches[0])
        previous, following = neighbor_values(df, idx, variable)
        classification, decision_rule = classify_jump(variable, previous, df.at[idx, variable], following)
        review_rows.append(
            {
                "country": row.Country,
                "year": int(row.Year),
                "variable": variable,
                "preceding_value": previous,
                "current_value": df.at[idx, variable],
                "following_value": following,
                "classification": classification,
                "action": "analysis_copy_set_missing" if classification == "clearly_invalid" else "retained_and_flagged",
                "decision_rule": decision_rule,
                "authoritative_replacement_source": "none",
            }
        )
    review = pd.DataFrame(review_rows).drop_duplicates(["country", "year", "variable"])
    review.to_csv(TABLES / "suspicious_value_review.csv", index=False)

    suspicious_variables = sorted(review["variable"].unique())
    df["suspicious_any_flag"] = False
    for variable in suspicious_variables:
        df[f"{variable}_suspicious_flag"] = False
        df[f"{variable}_analysis"] = df[variable]
    for row in review.itertuples(index=False):
        mask = df["country"].eq(row.country) & df["year"].eq(row.year)
        df.loc[mask, "suspicious_any_flag"] = True
        df.loc[mask, f"{row.variable}_suspicious_flag"] = True
        if row.classification == "clearly_invalid":
            df.loc[mask, f"{row.variable}_analysis"] = np.nan

    zero_variables = ["percentage_expenditure", "income_composition_of_resources", "schooling"]
    zero_rows = []
    for variable in zero_variables:
        flag = df[variable].eq(0)
        df[f"{variable}_zero_flag"] = flag
        if variable in {"income_composition_of_resources", "schooling"}:
            classification = "likely_encoded_missingness"
            rationale = "A literal zero is substantively doubtful and is concentrated in specific developing-country periods; retained pending source verification."
        else:
            classification = "unresolved"
            rationale = "Zeros are widespread and heavily concentrated in 2015, but the supplied documentation does not establish a missing-value code."
        for idx in df.index[flag]:
            zero_rows.append(
                {
                    "variable": variable,
                    "country": df.at[idx, "country"],
                    "year": int(df.at[idx, "year"]),
                    "status": df.at[idx, "status"],
                    "classification": classification,
                    "action": "retained_and_flagged",
                    "rationale": rationale,
                }
            )
    zero_review = pd.DataFrame(zero_rows)
    zero_review.to_csv(TABLES / "zero_value_review.csv", index=False)
    zero_review.groupby(["variable", "country"]).size().rename("zero_count").to_csv(TABLES / "zero_counts_by_country.csv")
    zero_review.groupby(["variable", "year"]).size().rename("zero_count").to_csv(TABLES / "zero_counts_by_year.csv")

    missing_long = df.melt(
        id_vars=["country", "year", "status"],
        value_vars=[column for column in df.columns[:22] if column not in {"country", "year", "status"}],
        var_name="variable",
        value_name="value",
    )
    missing_long["is_missing"] = missing_long["value"].isna()
    missing_long.groupby(["variable", "country"])["is_missing"].agg(["sum", "mean"]).rename(columns={"sum": "missing_count", "mean": "missing_rate"}).to_csv(TABLES / "missingness_by_country.csv")
    missing_long.groupby(["variable", "year"])["is_missing"].agg(["sum", "mean"]).rename(columns={"sum": "missing_count", "mean": "missing_rate"}).to_csv(TABLES / "missingness_by_year.csv")
    missing_long.groupby(["variable", "status"])["is_missing"].agg(["sum", "mean"]).rename(columns={"sum": "missing_count", "mean": "missing_rate"}).to_csv(TABLES / "missingness_by_status.csv")

    transform_sources = {
        "gdp": "gdp_analysis",
        "hiv_aids": "hiv_aids",
        "population": "population_analysis",
        "measles": "measles",
        "infant_deaths": "infant_deaths",
        "under_five_deaths": "under_five_deaths",
        "percentage_expenditure": "percentage_expenditure",
    }
    for output, source in transform_sources.items():
        if (df[source].dropna() < 0).any():
            raise ValueError(f"Negative values prevent log1p transformation of {source}")
        df[f"log1p_{output}"] = np.log1p(df[source])

    specifications = {
        "spec_1_schooling_gdp": ["life_expectancy", "schooling", "gdp_analysis", "total_expenditure", "polio", "hiv_aids"],
        "spec_2_development_index": ["life_expectancy", "income_composition_of_resources", "total_expenditure", "polio", "hiv_aids"],
        "spec_3_health_education": ["life_expectancy", "schooling", "total_expenditure", "polio", "alcohol", "bmi_analysis", "hiv_aids"],
    }
    sample_rows = []
    for name, variables in specifications.items():
        flag = df[variables].notna().all(axis=1)
        df[f"complete_case_{name}"] = flag
        sample_rows.append(
            {
                "specification": name,
                "variables": "; ".join(variables),
                "observations": int(flag.sum()),
                "countries": int(df.loc[flag, "country"].nunique()),
                "countries_with_two_plus_observations": int(df.loc[flag].groupby("country").size().ge(2).sum()),
            }
        )
    samples = pd.DataFrame(sample_rows)
    samples.to_csv(TABLES / "candidate_specification_samples.csv", index=False)

    PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED, index=False)
    raw_hash_after = sha256(RAW)
    if raw_hash_before != raw_hash_after:
        raise RuntimeError("Raw file changed during cleaning")

    class_counts = review["classification"].value_counts().to_dict()
    zero_counts = zero_review.groupby("variable").size().to_dict()
    report = f"""# Data-cleaning decisions

## Observed facts

- Raw SHA-256 before and after cleaning: `{raw_hash_before}` (unchanged).
- Processed rows: {len(df):,}; country-year duplicates: {duplicate_keys}.
- Columns are standardized to snake_case only in the processed dataset.
- Strings are trimmed and observations are sorted by country and year.
- Ten single-year countries are retained: {', '.join(single_year)}.
- Suspicious-value classifications: {class_counts}.
- Zero counts: {zero_counts}.

## Cleaning decisions

- Original standardized variables preserve the raw values. Separate `_analysis` columns set only internally clear isolated scale breaks to missing; no replacement values are introduced.
- Every reviewed jump retains an explicit flag. Unresolved and merely unusual observations remain unchanged.
- `percentage_expenditure` zeros are classified as unresolved. `income_composition_of_resources` and `schooling` zeros are classified as likely encoded missingness. All remain present and are flagged.
- No global mean imputation, winsorization, automatic outlier deletion, or rowwise complete-case deletion is applied to the general cleaned dataset.
- `log1p` copies are created for nonnegative, strongly right-skewed variables; originals remain available.
- Candidate complete-case flags are separate and specification-specific.

## Unresolved questions

- Validate every clearly invalid internal-consistency flag and all unresolved values against an authoritative source before final modeling.
- Confirm the definitions and units of GDP and expenditure measures; the supplied documents do not verify that GDP is per capita.
- Determine whether recorded zeros are genuine or missing-value codes.
- Approve the candidate variable sets and treatment of single-year countries before regression work.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(f"Wrote {PROCESSED.relative_to(ROOT)} with {len(df):,} rows and {len(df.columns)} columns")
    print(f"Suspicious review rows: {len(review)}; raw SHA-256 unchanged: {raw_hash_after}")
    print(samples[["specification", "observations", "countries"]].to_string(index=False))


if __name__ == "__main__":
    main()
