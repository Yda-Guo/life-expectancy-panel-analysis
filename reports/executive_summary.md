# Executive summary

## Purpose and correction

This project asks how schooling, recorded GDP, health expenditure, and polio vaccination coverage are associated with national life expectancy, and how those associations change after controlling for persistent country differences and common year shocks. It is a transparent associational panel analysis, not a causal study.

The source contains 2,938 country-year observations for 193 countries in 2000–2015. A provenance review confirmed that the supplied `HIV/AIDS` field belongs to a WHO cause-specific mortality indicator family measured in deaths per 1,000 live births. Its contemporaneous use as an explanatory variable overlapped conceptually with the mortality-based life-expectancy outcome. It was therefore removed from the primary model; the older specification is retained only as a clearly labeled supplementary overlap check. GDP remains neutrally labeled because the merged metadata do not verify that it is per capita, and the exact total-expenditure denominator remains unresolved.

## Main comparison

All four models use the same 2,319 complete cases from 157 countries. Pooled and year-FE models use HC1 standard errors; country-FE and two-way-FE models use country-clustered standard errors.

| Variable | Pooled OLS | TWFE | TWFE 95% CI | p-value |
|---|---:|---:|---:|---:|
| Schooling | 1.6878 | 0.1340 | [-0.1068, 0.3748] | 0.275 |
| log(1 + GDP) | 1.0492 | -0.0157 | [-0.0886, 0.0571] | 0.672 |
| Total expenditure | -0.1003 | -0.0337 | [-0.1216, 0.0542] | 0.452 |
| Polio coverage | 0.0617 | 0.0049 | [-0.0017, 0.0115] | 0.145 |

The strong pooled schooling, GDP, and polio associations attenuate substantially when identification comes from within-country changes after common year effects are removed. The TWFE intervals are compatible with modest positive or negative associations, so the results emphasize effect size and uncertainty rather than a binary significance label.

## Focused diagnostics and sensitivity

- **Temporal ordering:** a one-year-lagged TWFE model uses 2,317 observations from 157 countries. Schooling is 0.1019 (95% CI -0.1199 to 0.3236), log GDP -0.0032 (-0.0779 to 0.0714), expenditure -0.0035 (-0.0910 to 0.0841), and polio 0.0049 (-0.0020 to 0.0119). The small, uncertain pattern persists; lagging does not solve endogeneity.
- **Complete-case selection:** included and excluded rows have almost identical observed mean life expectancy (69.26 versus 69.11; standardized difference 0.02). Excluded rows are later on average (2009.40 versus 2007.02; standardized difference -0.50), and observed-value differences for main covariates are smaller (absolute standardized differences at most 0.19). This highlights time-composition and generalizability limits; it does not prove missingness is ignorable.
- **Inference:** two-way clustering by country and year leaves point estimates unchanged. Standard errors are broadly similar, but only 16 year clusters make this a limited sensitivity check; country clustering remains primary.
- **Robustness cleanup:** the prior specification that exactly duplicated the baseline was removed. Twelve active coefficient/sample checks now address flag rules, definitions, alternative measures, influence, and subgroups; temporal and inference checks are reported separately.

## Bottom line

The strongest defensible result is not a single “determinant.” It is the contrast between large pooled cross-country associations and much smaller, uncertain within-country TWFE associations. The earlier headline HIV/AIDS result has been demoted because it primarily reflected a contemporaneous mortality-outcome overlap. Reverse causality, time-varying confounding, measurement error, unresolved metadata, complete-case selection, slow-moving variables, and a short 16-year panel remain important limitations.
