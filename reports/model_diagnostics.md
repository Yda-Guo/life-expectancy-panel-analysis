# Model diagnostics

## Observed sample facts

- The shared main comparison sample has 2,319 observations from 157 countries, covering 2000–2015.
- Ten single-year countries are excluded from fixed-effects comparisons because they provide no within-country identifying variation.
- The 18 clearly invalid observations are represented by preserved original variables, row/variable flags, and `_analysis` copies in which only the affected analysis value is missing. The main model does not use adult mortality, infant deaths, or under-five deaths.

## Variation and overlap

- Within/between variation is saved in `tables/model_within_between_variation.csv`. Variables with a within-to-overall SD ratio below 0.25 should be treated as having relatively little within-country variation.
- Schooling–income composition correlation: 0.794.
- Schooling–log(1 + GDP) correlation: 0.622.
- Income composition–log(1 + GDP) correlation: 0.588.
- Polio–diphtheria correlation: 0.681.
- Maximum VIF among the main non-fixed-effect regressors (with an intercept in the auxiliary regressions): 2.06. VIF is calculated on raw regressors and does not directly diagnose collinearity after fixed-effect demeaning.

## Modeling decisions

- The preferred parsimonious covariates are schooling, `log1p_gdp`, total expenditure, polio, and `log1p_hiv_aids`.
- GDP is not described as per capita because the supplied documentation does not verify that definition.
- Schooling, income composition, and GDP are not placed together in the primary model because they are conceptually overlapping development measures.
- Polio and diphtheria are compared in robustness checks; both are included together only as an explicit collinearity sensitivity check.
- Adult mortality, infant deaths, and under-five deaths are excluded from the primary specification because they are mortality outcomes or mechanically close to life expectancy.
- `status` is excluded from country fixed-effects models because it is time-invariant within countries in these data.
- Variable selection is based on definitions, missingness, within-country variation, and conceptual parsimony—not p-values.
