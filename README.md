# Determinants of Life Expectancy: A Panel Data Analysis

## Project overview

This project studies the socioeconomic, healthcare, and public-health factors associated with national life expectancy.

The dataset contains country-year observations, allowing the use of panel-data methods.

## Research question

Which socioeconomic, healthcare, and public-health factors are associated with changes in national life expectancy?

The analysis examines whether these relationships remain after controlling for country fixed effects and year fixed effects.

## Data

Source: Kaggle, Life Expectancy (WHO)

Each observation represents one country in one year.

The original dataset is stored in:

```text
data/raw/life_expectancy.csv
```

## Planned analysis

1. Data audit and cleaning
2. Missing-value analysis
3. Exploratory data analysis
4. Pooled OLS
5. Country fixed effects
6. Country and year two-way fixed effects
7. Robustness checks
8. Final research report

## Main outcome

* Life expectancy

## Candidate explanatory variables

* Schooling
* Income composition of resources
* GDP
* Total health expenditure
* BMI
* Polio vaccination coverage
* Diphtheria vaccination coverage
* HIV/AIDS

## Research principles

* Preserve the original dataset
* Document all data transformations
* Avoid automatic global mean imputation
* Use appropriate panel-data methods
* Distinguish association from causation
* Make all results reproducible
