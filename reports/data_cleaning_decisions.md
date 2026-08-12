# Data-cleaning decisions

## Observed facts

- Raw SHA-256 before and after cleaning: `872125dd1dd0f9140fbead61df20585a815f5cf47db68f08bf54efaf87963b11` (unchanged).
- Processed rows: 2,938; country-year duplicates: 0.
- Columns are standardized to snake_case only in the processed dataset.
- Strings are trimmed and observations are sorted by country and year.
- Ten single-year countries are retained: Cook Islands, Dominica, Marshall Islands, Monaco, Nauru, Niue, Palau, Saint Kitts and Nevis, San Marino, Tuvalu.
- Suspicious-value classifications: {'merely_unusual': 62, 'unresolved': 40, 'clearly_invalid': 18}.
- Zero counts: {'income_composition_of_resources': 130, 'percentage_expenditure': 611, 'schooling': 28}.

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
