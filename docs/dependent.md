# How should we combine dependent effect estimates?

Several estimates from one study can share sampling error, and outcomes from the same study can also share a study-level effect. Treating every row as independent can understate uncertainty. This tutorial asks how to fit those data when the sampling covariance is supplied.

The example uses original synthetic fixtures, not the Berkey dataset. The rows and covariance matrices were generated with the pinned R reference script. Their versions, seeds, checksum, and terms are recorded in `reference/dependent/v1/PROVENANCE.md`; the upstream [`rma.mv()` reference](https://wviechtb.github.io/metafor/reference/rma.mv.html) describes the corresponding R model family.

## Data

The fixture set contains three cases:

1. Eight estimates with a correlated sampling covariance matrix and an intercept plus moderator.
2. Thirty-six estimates nested in 12 studies and 36 study-specific effects. Local effect labels repeat across studies, so the nested key is `(study, effect)`.
3. Two outcomes from each of 20 studies, with both correlated sampling errors and an unstructured study-level outcome covariance.

The first two fixtures store observations and matrices as CSV. The third is a synthetic, Berkey-style example. All three fixtures, reference outputs, R versions, seeds, and SHA-256 checksums are in the source directory `reference/dependent/v1/`.

## Model

For retained rows, let `V` be the supplied sampling covariance, `X` the fixed-effect design, and `K_j` a known positive-semidefinite random-effect kernel. The marginal covariance and fitted coefficients are

$$
C=V+\sum_j \theta_j K_j,\qquad
\hat\beta=(X^T C^{-1}X)^{-1}X^T C^{-1}y,
$$

with each variance component `theta_j` constrained to be nonnegative. The nested example uses `K_study = Z_study Z_study'` and `K_effect = Z_effect Z_effect'`. The bivariate example estimates a positive-semidefinite 2 × 2 covariance matrix for the two outcomes within each study.

The matrix-first API keeps sampling and random-effect covariance separate. Missing outcomes or design/group labels use one common row mask, and the matching rows and columns are removed from `V`.

```python
from metafor import fit_meta_cov, fit_meta_nested, fit_meta_un

# Full sampling covariance, fixed effects, and a supplied design matrix.
fit = fit_meta_cov(yi, V, X=X, method="FE")

# Independent random intercepts, ordered from outer to inner.
groups = {
    "study": study,
    "study/effect": list(zip(study, effect_local)),
}
fit = fit_meta_nested(yi, V, groups=groups, X=X, method="REML")

# Two outcomes with an unstructured covariance within study.
fit = fit_meta_un(yi, V, study, outcome,
                  outcome_levels=("benefit", "harm"), method="REML")
```

Install the project and optional table support with `pip install -e '.[tables]'` before running the example. For a pandas table, `fit_meta_cov_formula(data, "yi ~ x", V, id="row_id")` builds the design matrix with Patsy and preserves input row identity. This is a numeric-formula adapter; full R formula semantics are not claimed.

## Interpretation

The shared synthetic R reference estimates the nested intercept at 0.6034 and its moderator slope at 0.2770. It estimates study and nested-effect variances of 0.1133 and 0.0221. In the two-outcome case, the estimated benefit and harm means are 0.4856 and 0.2422; the estimated between-outcome covariance is 0.2316. These numbers describe only the generated fixtures.

The comparison report places R and Python estimates and coefficient-covariance entries side by side. Its current gate checks 42 estimates and 12 coefficient-covariance entries against R with quantity-specific tolerances. See the [R and Python comparison guide](compare) for the report and its scope.

## Differences from R metafor

The ports cover supplied positive-definite sampling covariance matrices, normal-normal GLS/REML, independent scalar PSD kernels, nested random intercepts, and a two-outcome unstructured study covariance. The tested fixtures match coefficients, standard errors, intervals, heterogeneity statistics, variance/covariance components, and coefficient covariance within the recorded tolerances.

This is partial `rma.mv()` coverage. The current implementation does not claim support for AR/CAR, spatial, GEN, phylogenetic tree estimation, estimated sampling correlations, three or more outcomes in the unstructured model, small-sample inference, profile intervals, or the full diagnostic suite. Error text and warning categories can differ from R. The repository root file `COMPATIBILITY.md` records status by function and option.
