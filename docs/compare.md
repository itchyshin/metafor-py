# Compare R and Python

These reports compare selected outputs from the upstream R package with the
native Python implementation using named, versioned fixtures. Each report
records the checked fields and tolerances. A passing result is evidence for
those fixture cases and quantities; it does not establish general API
equivalence or support for an untested option.

## Pairwise comparison reports

* [BCG model and forest results](_static/comparisons/bcg-comparison.html)
* [Dependent-effects models](_static/comparisons/dependent-comparison.html)
* [Supplied phylogenetic correlation](_static/comparisons/phylogeny-comparison.html)
* [Effect-size calculations and models](_static/comparisons/effect-size-comparison.html)
* [Table and formula adapter](_static/comparisons/table-adapter-comparison.html)

The table-adapter report checks retained trial IDs, 24 design values, and two
coefficients against the pinned R reference. It also checks formula-to-matrix
agreement within Python. The other reports compare the Python quantities listed
in each report with corresponding pinned R results.

## How to read the results

The R values come from pinned reference inputs and scripts; Python results are
produced by this native implementation. Numeric comparisons use report-specific
tolerances rather than a claim of bit-for-bit equality. The fixture provenance
files identify the inputs, versions, generation steps, and checksums.

The comparisons do not cover all functions or options in R `metafor`. In
particular, no report establishes general formula compatibility, all
multivariate covariance structures, tree estimation, unseen-species
prediction, small-sample inference, or calibrated coverage. See the
[compatibility table](https://github.com/itchyshin/metafor-py/blob/main/COMPATIBILITY.md)
for current function-by-option scope and the
[tutorials](examples/index) for runnable cases.
