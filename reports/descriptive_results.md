# Descriptive results

No regression models are estimated here, and all statements are descriptive rather than causal.

## Observed facts

- The processed dataset contains 2,938 rows and 193 countries.
- Mean life expectancy is 69.22 years (median 72.10; observed range 36.3–89.0).
- Annual mean life expectancy changes from 66.75 in 2000 to 71.62 in 2015.
- Mean life expectancy by status is {'Developed': 79.2, 'Developing': 67.11}.
- Representative countries were selected among countries with all 16 years by choosing the country closest to the 10th, 50th, and 90th percentiles of country-level mean life expectancy: {'lower': 'Burundi', 'middle': 'Libya', 'upper': 'Luxembourg'}.
- Candidate complete-case samples are {'spec_1_schooling_gdp': 2319, 'spec_2_development_index': 2574, 'spec_3_health_education': 2552}.
- Zero-value classifications are {'income_composition_of_resources': 130, 'percentage_expenditure': 611, 'schooling': 28}.

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
