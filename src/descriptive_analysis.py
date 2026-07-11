"""Generate descriptive tables, figures, and a traceable results report."""

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


DATA = ROOT / "data/processed/life_expectancy_clean.csv"
TABLES = ROOT / "tables"
FIGURES = ROOT / "figures"
REPORT = ROOT / "reports/descriptive_results.md"


def save_figure(name: str) -> None:
    plt.tight_layout()
    plt.savefig(FIGURES / name, dpi=180, bbox_inches="tight")
    plt.close()


def main() -> None:
    df = pd.read_csv(DATA)
    TABLES.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)

    original = [
        "country", "year", "status", "life_expectancy", "adult_mortality", "infant_deaths",
        "alcohol", "percentage_expenditure", "hepatitis_b", "measles", "bmi",
        "under_five_deaths", "polio", "total_expenditure", "diphtheria", "hiv_aids",
        "gdp", "population", "thinness_1_19_years", "thinness_5_9_years",
        "income_composition_of_resources", "schooling",
    ]
    summary = df[original].describe(include="all").T
    summary.to_csv(TABLES / "summary_statistics.csv", index_label="variable")

    missing = pd.DataFrame({"missing_count": df[original].isna().sum(), "missing_rate_pct": 100 * df[original].isna().mean()})
    missing.to_csv(TABLES / "missing_values_clean.csv", index_label="variable")
    missing.sort_values("missing_rate_pct")["missing_rate_pct"].plot.barh(figsize=(8, 7), color="#4776A8")
    plt.xlabel("Missing observations (%)")
    plt.ylabel("")
    plt.title("Missingness by variable")
    save_figure("missingness_by_variable.png")

    missing_year = df.groupby("year")[original[3:]].apply(lambda group: group.isna().mean().mean() * 100)
    missing_year.plot(figsize=(8, 4), marker="o", color="#B34E4E")
    plt.ylabel("Average cell missingness (%)")
    plt.title("Average missingness across numeric variables by year")
    save_figure("missingness_by_year.png")

    df["life_expectancy"].plot.hist(bins=25, figsize=(7, 4), color="#4C956C", edgecolor="white")
    plt.xlabel("Life expectancy")
    plt.title("Distribution of life expectancy")
    save_figure("life_expectancy_distribution.png")

    yearly = df.groupby("year")["life_expectancy"].agg(["mean", "count", "std"])
    yearly.to_csv(TABLES / "life_expectancy_by_year.csv")
    yearly["mean"].plot(figsize=(8, 4), marker="o", color="#2C5F8A")
    plt.ylabel("Mean life expectancy")
    plt.title("Average life expectancy by year")
    save_figure("average_life_expectancy_by_year.png")

    complete_countries = df.groupby("country").size().loc[lambda values: values.eq(16)].index
    country_means = df[df["country"].isin(complete_countries)].groupby("country")["life_expectancy"].mean().dropna().sort_values()
    percentiles = {"lower": 0.10, "middle": 0.50, "upper": 0.90}
    representatives = []
    for label, quantile in percentiles.items():
        target = country_means.quantile(quantile)
        country = (country_means - target).abs().idxmin()
        representatives.append({"selection_band": label, "country": country, "mean_life_expectancy": country_means[country], "target_quantile": quantile})
    representative_table = pd.DataFrame(representatives)
    representative_table.to_csv(TABLES / "representative_countries.csv", index=False)
    representative_names = representative_table["country"].tolist()
    trend = df[df["country"].isin(representative_names)].pivot(index="year", columns="country", values="life_expectancy")
    trend.to_csv(TABLES / "representative_country_trends.csv")
    trend.plot(figsize=(8, 5), marker="o")
    plt.ylabel("Life expectancy")
    plt.title("Life-expectancy trends: transparent percentile selection")
    save_figure("representative_country_trends.png")

    status = df.groupby("status")["life_expectancy"].agg(["mean", "median", "std", "count"])
    status.to_csv(TABLES / "life_expectancy_by_status.csv")
    status["mean"].plot.bar(figsize=(6, 4), color=["#4776A8", "#D98C4A"])
    plt.ylabel("Mean life expectancy")
    plt.xlabel("")
    plt.title("Life expectancy by development status")
    plt.xticks(rotation=0)
    save_figure("life_expectancy_by_status.png")

    candidates = ["life_expectancy", "schooling", "income_composition_of_resources", "gdp_analysis", "total_expenditure", "polio", "hiv_aids", "alcohol", "bmi_analysis"]
    correlations = df[candidates].corr()
    correlations.to_csv(TABLES / "candidate_correlations.csv")
    fig, ax = plt.subplots(figsize=(8, 7))
    image = ax.imshow(correlations, vmin=-1, vmax=1, cmap="coolwarm")
    ax.set_xticks(range(len(candidates)), [name.replace("_", " ") for name in candidates], rotation=60, ha="right")
    ax.set_yticks(range(len(candidates)), [name.replace("_", " ") for name in candidates])
    fig.colorbar(image, ax=ax, label="Pearson correlation")
    ax.set_title("Candidate-variable correlations")
    save_figure("candidate_correlations.png")

    variation_rows = []
    for variable in candidates:
        series = df[["country", variable]].dropna()
        country_means_for_var = series.groupby("country")[variable].mean()
        within = series[variable] - series.groupby("country")[variable].transform("mean")
        variation_rows.append({
            "variable": variable,
            "observations": len(series),
            "countries": series["country"].nunique(),
            "overall_sd": series[variable].std(),
            "between_country_sd": country_means_for_var.std(),
            "within_country_sd": within.std(),
        })
    variation = pd.DataFrame(variation_rows)
    variation.to_csv(TABLES / "within_between_variation.csv", index=False)

    samples = pd.read_csv(TABLES / "candidate_specification_samples.csv")
    zeros = pd.read_csv(TABLES / "zero_value_review.csv")
    zero_summary = zeros.groupby(["variable", "classification"]).size().rename("zero_count").reset_index()
    zero_summary.to_csv(TABLES / "zero_value_summary.csv", index=False)

    report = f"""# Descriptive results

No regression models are estimated here, and all statements are descriptive rather than causal.

## Observed facts

- The processed dataset contains {len(df):,} rows and {df['country'].nunique()} countries.
- Mean life expectancy is {df['life_expectancy'].mean():.2f} years (median {df['life_expectancy'].median():.2f}; observed range {df['life_expectancy'].min():.1f}–{df['life_expectancy'].max():.1f}).
- Annual mean life expectancy changes from {yearly.loc[2000, 'mean']:.2f} in 2000 to {yearly.loc[2015, 'mean']:.2f} in 2015.
- Mean life expectancy by status is {status['mean'].round(2).to_dict()}.
- Representative countries were selected among countries with all 16 years by choosing the country closest to the 10th, 50th, and 90th percentiles of country-level mean life expectancy: {representative_table[['selection_band', 'country']].set_index('selection_band')['country'].to_dict()}.
- Candidate complete-case samples are {samples.set_index('specification')['observations'].to_dict()}.
- Zero-value classifications are {zero_summary.set_index('variable')['zero_count'].to_dict()}.

## Interpretation boundaries

- Correlations and time trends describe associations only.
- Between-country variation is not interchangeable with within-country change. See `tables/within_between_variation.csv` before selecting fixed-effects covariates.
- The GDP definition is unverified in the supplied documentation; outputs retain the neutral name `gdp` and do not label it per capita.
- Suspicious unresolved values, zero-value ambiguity, and missingness may affect all descriptive summaries.

## Traceable outputs

- Distribution and trend tables: `tables/life_expectancy_by_year.csv`, `tables/life_expectancy_by_status.csv`, and `tables/representative_country_trends.csv`.
- Missingness: `tables/missing_values_clean.csv` plus country/year/status tables generated during cleaning.
- Correlations and variation: `tables/candidate_correlations.csv` and `tables/within_between_variation.csv`.
- Candidate samples: `tables/candidate_specification_samples.csv`.
- Figures are stored in `figures/` with matching descriptive names.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(f"Generated {len(list(FIGURES.glob('*.png')))} figures and descriptive tables")
    print(samples[["specification", "observations", "countries"]].to_string(index=False))


if __name__ == "__main__":
    main()
