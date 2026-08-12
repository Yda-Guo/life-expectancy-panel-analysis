# Data dictionary and provenance

Each row represents a country-year observation. The distributed file is the Kaggle **Life Expectancy (WHO)** dataset (2,938 rows, 22 source columns). Kaggle says its health fields were collected from the WHO Global Health Observatory (GHO), its economic fields from the United Nations, and the component files were merged. It does not provide field-level source identifiers or a versioned merge key, so the mappings below distinguish verified definitions from unresolved lineage.

Sources accessed 2026-08-12:

- Kaggle dataset record: <https://www.kaggle.com/datasets/kumarajarshi/life-expectancy-who>
- WHO GHO mortality data table, “Deaths per 1 000 live births”: <https://apps.who.int/gho/data/node.imr.MORT_200?lang=en>
- WHO GHO Polio (Pol3) indicator metadata: <https://www.who.int/data/gho/indicator-metadata-registry/imr-details/3451>
- WHO GHO health-expenditure indicator metadata: <https://www.who.int/data/gho/indicator-metadata-registry/imr-details/122>

## Identifiers and outcome

| Source column | Processed name | Meaning / unit | Verification status |
|---|---|---|---|
| Country | `country` | Country name | Supplied field; entity harmonization beyond whitespace/case was not independently verified. |
| Year | `year` | Calendar year | Supplied field. |
| Status | `status` | Developed / Developing label | Supplied field; classification system and vintage are not documented. |
| Life expectancy | `life_expectancy` | Life expectancy at birth, years | Field name and observed scale are consistent with WHO usage; exact upstream series/version is not supplied by Kaggle. |

## Variables used in the primary model

| Source column | Processed name | Meaning / unit | Verification status and modeling decision |
|---|---|---|---|
| Schooling | `schooling` | Recorded years of schooling | The values and dataset descriptions are consistent with a schooling-years measure, but the exact age group, construction, UN series, and version cannot be traced from the merged-file metadata. Retained with this ambiguity stated. |
| GDP | `gdp`; `log1p_gdp` | Recorded GDP measure; `log(1 + GDP)` in the main model | Kaggle identifies UN economic data but does not establish whether this field is total GDP or GDP per capita, its currency basis, price year, or conversion method. It is therefore not called “GDP per capita.” |
| Total expenditure | `total_expenditure` | Recorded health-expenditure measure; percentage-like scale | WHO publishes multiple expenditure indicators, including total health expenditure as a percentage of GDP. Kaggle does not identify the exact series used in this merged column, so the precise denominator remains unresolved and the coefficient is interpreted per recorded unit only. |
| Polio | `polio` | Polio three-dose vaccination coverage, percentage of one-year-olds | WHO defines Pol3 as the percentage of one-year-olds who received three doses of polio-containing vaccine in a given year (operationally, children aged 12–23 months surveyed). The merged column name/range match this indicator, although Kaggle does not provide row-level WHO series IDs. |

## HIV/AIDS correction

| Source column | Processed name | Meaning / unit | Verification status and modeling decision |
|---|---|---|---|
| HIV/AIDS | `hiv_aids`; `log1p_hiv_aids` | HIV/AIDS cause-specific mortality burden in the WHO “deaths per 1,000 live births” indicator family | The Kaggle record explicitly groups mortality factors and traces health data to WHO GHO; the corresponding WHO GHO table reports HIV/AIDS under deaths per 1,000 live births. Kaggle does not expose the original indicator code for each merged column, so finer construction details cannot be reconstructed. The field is a contemporaneous mortality measure and conceptually overlaps life expectancy. It is removed from the primary explanatory specification and retained only in a clearly labeled supplementary overlap check. |

## Other candidate fields

Adult mortality, infant deaths, and under-five deaths are not used as explanatory variables because they are mortality outcomes or mechanically close to the life-expectancy outcome. Income composition of resources and diphtheria vaccination are used only as alternative-measure sensitivity checks. Population, alcohol, BMI, hepatitis B, measles, percentage expenditure, and thinness fields remain available for audit/descriptive work; their exact upstream series should not be inferred from their short column names alone.

No undocumented definition is promoted to “verified.” A future data-integration project could rebuild the panel from versioned WHO/UN series, but that is outside this repository's current scope.
