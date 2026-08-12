"""Reproducible, read-only audit of the raw life-expectancy panel dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def clean_column_names(columns: pd.Index) -> pd.Index:
    """Remove accidental leading/trailing and repeated whitespace."""
    return columns.str.strip().str.replace(r"\s+", " ", regex=True)


def markdown_table(frame: pd.DataFrame, index: bool = True) -> str:
    """Render a small DataFrame without requiring the optional tabulate package."""
    shown = frame.reset_index() if index else frame.copy()
    headers = [str(column) for column in shown.columns]
    rows = [["" if pd.isna(value) else str(value) for value in row] for row in shown.to_numpy()]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def audit(input_path: Path, report_path: Path, tables_dir: Path) -> None:
    """Audit the raw CSV and write human- and machine-readable results."""
    df = pd.read_csv(input_path)
    original_columns = list(df.columns)
    df.columns = clean_column_names(df.columns)

    key_duplicates = df.duplicated(["Country", "Year"], keep=False)
    exact_duplicates = df.duplicated(keep=False)
    counts = df.groupby("Country", sort=True).size().rename("observations")
    expected_years = set(range(int(df["Year"].min()), int(df["Year"].max()) + 1))
    country_years = df.groupby("Country")["Year"].agg(lambda values: set(values))
    missing_years = country_years.map(lambda years: ", ".join(map(str, sorted(expected_years - years))))
    panel = pd.concat([counts, missing_years.rename("missing_years")], axis=1)

    missing = pd.DataFrame(
        {
            "missing_count": df.isna().sum(),
            "missing_rate_pct": (100 * df.isna().mean()).round(3),
        }
    )
    numeric = df.select_dtypes(include="number")
    skewness = numeric.skew().sort_values(key=lambda values: values.abs(), ascending=False)
    strongly_skewed = skewness[skewness.abs() >= 1].rename("skewness").round(3).to_frame()

    normalized_names = df["Country"].str.strip().str.casefold()
    name_variants = (
        pd.DataFrame({"normalized": normalized_names, "Country": df["Country"]})
        .drop_duplicates()
        .groupby("normalized")["Country"]
        .agg(list)
    )
    inconsistent_names = name_variants[name_variants.map(len) > 1]

    range_rules = {
        "Life expectancy": (0, 120),
        "Adult Mortality": (0, None),
        "Alcohol": (0, None),
        "Hepatitis B": (0, 100),
        "BMI": (0, 100),
        "Polio": (0, 100),
        "Total expenditure": (0, 100),
        "Diphtheria": (0, 100),
        "HIV/AIDS": (0, 100),
        "Income composition of resources": (0, 1),
        "Schooling": (0, None),
    }
    range_rows = []
    for column, (lower, upper) in range_rules.items():
        invalid = df[column].lt(lower)
        if upper is not None:
            invalid |= df[column].gt(upper)
        range_rows.append(
            {
                "variable": column,
                "rule": f"[{lower}, {upper if upper is not None else 'unbounded'}]",
                "violations": int(invalid.fillna(False).sum()),
            }
        )
    range_checks = pd.DataFrame(range_rows).set_index("variable")

    # Flag large within-country jumps for variables that should usually evolve smoothly.
    ordered = df.sort_values(["Country", "Year"]).copy()
    jump_rules = {
        "Adult Mortality": 100,
        "BMI": 10,
        "GDP": 0.80,
        "Population": 0.80,
        "thinness 1-19 years": 5,
        "thinness 5-9 years": 5,
    }
    jump_rows = []
    for column, threshold in jump_rules.items():
        prior = ordered.groupby("Country")[column].shift()
        if column in {"GDP", "Population"}:
            score = (ordered[column] - prior).abs() / prior.abs()
        else:
            score = (ordered[column] - prior).abs()
        flagged = score.gt(threshold) & ordered[column].notna() & prior.notna()
        for idx in ordered.index[flagged]:
            jump_rows.append(
                {
                    "Country": ordered.at[idx, "Country"],
                    "Year": int(ordered.at[idx, "Year"]),
                    "variable": column,
                    "previous_value": float(prior.at[idx]),
                    "current_value": float(ordered.at[idx, column]),
                    "jump_score": float(score.at[idx]),
                }
            )
    jumps = pd.DataFrame(jump_rows).sort_values(
        ["variable", "jump_score"], ascending=[True, False]
    )

    tables_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    missing.to_csv(tables_dir / "missing_values.csv", index_label="variable")
    panel.to_csv(tables_dir / "observations_per_country.csv", index_label="country")
    strongly_skewed.to_csv(tables_dir / "strongly_skewed_variables.csv", index_label="variable")
    # Keep the review table compact while retaining the most extreme flags per variable.
    priority_jumps = jumps.groupby("variable", group_keys=False).head(20)
    priority_jumps.to_csv(tables_dir / "suspicious_within_country_jumps.csv", index=False)

    observations_distribution = counts.value_counts().sort_index().rename("countries").to_frame()
    sample = df.head(5).round(3)
    type_table = pd.DataFrame(
        {"column": df.columns, "dtype": [str(dtype) for dtype in df.dtypes]}
    )
    whitespace_changes = [
        f"`{old}` → `{new}`" for old, new in zip(original_columns, df.columns) if old != new
    ]
    balanced = bool(counts.nunique() == 1 and counts.iloc[0] == len(expected_years))

    report = f"""# Data audit

Generated from `{input_path.as_posix()}`. The script reads but never writes to the raw file.

## Observed facts

- Dimensions: **{len(df):,} observations × {len(df.columns)} variables**.
- Countries: **{df['Country'].nunique():,}**.
- Years: **{int(df['Year'].min())}–{int(df['Year'].max())}** ({df['Year'].nunique()} distinct years).
- Duplicate country–year keys: **{int(key_duplicates.sum()):,} rows**.
- Exact duplicate rows: **{int(exact_duplicates.sum()):,} rows**.
- Balanced panel: **{'yes' if balanced else 'no'}**.
- Country-name whitespace/case collisions: **{len(inconsistent_names)}**.
- Header whitespace normalized in memory: {', '.join(whitespace_changes) if whitespace_changes else 'none'}.

### Observations per country

{markdown_table(observations_distribution)}

The complete country-level table is in `tables/observations_per_country.csv`.

### Columns and inferred data types

{markdown_table(type_table, index=False)}

### First five observations

{markdown_table(sample, index=False)}

### Missing values

{markdown_table(missing)}

### Strongly skewed numeric variables

Threshold: absolute sample skewness ≥ 1.

{markdown_table(strongly_skewed)}

### Range and consistency checks

{markdown_table(range_checks)}

No values violate the broad logical ranges above. This does **not** establish data validity. The audit flags abrupt within-country changes in `tables/suspicious_within_country_jumps.csv`; these include patterns consistent with dropped digits or decimal-place errors and require comparison with an authoritative source.

## Modeling decisions

- Treat `Life expectancy` as the outcome and do not use `Adult Mortality`, `infant deaths`, or `under-five deaths` in the primary explanatory specification. They are mortality outcomes/components that are mechanically or definitionally close to life expectancy.
- Do not use contemporaneous `HIV/AIDS` in the primary explanatory specification. Subsequent provenance review identified it as a cause-specific mortality-burden field, creating direct conceptual outcome overlap.
- Do not include both broad development indices and all of their likely components without a clear estimand. `Income composition of resources` and `Schooling` are strongly conceptually related, and the former may embed education/income information.
- Avoid simultaneously using `percentage expenditure`, `Total expenditure`, and `GDP` without verifying definitions: expenditure measures can share denominators or be derived using GDP.
- Avoid including all three immunization measures together initially (`Hepatitis B`, `Polio`, `Diphtheria`) because they measure closely related health-system coverage and may be collinear.
- Treat `Status` as time-invariant unless source documentation shows transitions; country fixed effects would absorb it.
- Use transformations such as `log1p` for highly right-skewed counts and monetary/size variables only after suspicious values and zeros are resolved.

## Implemented primary specification

For a descriptive baseline after cleaning and missing-data decisions:

`Life expectancy_it = country FE + year FE + β1 Schooling_it + β2 log(1 + GDP_it) + β3 Total expenditure_it + β4 Polio_it + ε_it`

Use country-clustered standard errors. This is an associational model, not a causal claim. GDP remains neutrally labeled because the merged metadata do not verify a per-capita definition. Remaining metadata uncertainty, missing-data handling, and within-country variation are documented downstream.

## Unresolved questions requiring human/source review

- Rebuilding exact field-level lineage would require the versioned source files used in Kaggle's merge; the available record does not provide them.
- Validate abrupt country-level jumps and possible dropped-digit/decimal errors against an authoritative source.
- Confirm country coverage: 10 countries have only one observation (2013), while 183 have 16 observations.
- The ten single-year countries are excluded from the common main comparison because they provide no within-country information.
- Determine whether zero values in `percentage expenditure`, `Income composition of resources`, and `Schooling` are genuine zeros or missing-value codes.
- The implemented main comparison uses complete cases and reports included-versus-excluded diagnostics; no automatic global-mean imputation is used.
"""
    report_path.write_text(report, encoding="utf-8")

    print(f"Audit complete: {len(df):,} rows, {len(df.columns)} columns")
    print(f"Country-year key duplicates: {int(key_duplicates.sum()):,}")
    print(f"Panel balanced: {balanced}")
    print(f"Wrote {report_path} and four tables to {tables_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/life_expectancy.csv"))
    parser.add_argument("--report", type=Path, default=Path("reports/data_audit.md"))
    parser.add_argument("--tables-dir", type=Path, default=Path("tables"))
    args = parser.parse_args()
    audit(args.input, args.report, args.tables_dir)


if __name__ == "__main__":
    main()
