# Dependent effects and supplied covariance

When several estimates share studies or outcomes, their sampling errors may be
correlated. The dependent-effects functions accept a supplied sampling
covariance matrix `V`, keeping that known sampling covariance separate from
estimated study-level variation.

* `fit_meta_cov(yi, V, X=None, components=None, method="REML",
  design_columns=None)` fits GLS or REML with `V` and optional supplied
  positive-semidefinite scalar kernels.
* `fit_meta_nested(yi, V, groups, X=None, group_names=None, method="REML",
  design_columns=None)` builds independent nested random-intercept kernels
  from grouping vectors. Inner labels should include their parent labels, such
  as `(study, effect)`.
* `fit_meta_un(yi, V, study, outcome, outcome_levels, method="REML")` fits a
  two-outcome model with an unstructured positive-semidefinite study covariance.
* `fit_meta_cov_formula(data, formula, V, id=None, components=None,
  method="REML")` uses the optional pandas/Patsy table adapter and preserves
  retained row IDs while masking both axes of `V`.

For example, the matrix-first form is:

```python
from metafor import fit_meta_cov

fit = fit_meta_cov(yi, V, X=X, method="REML")
```

Current checks cover correlated GLS, a nested two-component fixture, and a
synthetic two-outcome fixture. This is partial coverage of `rma.mv()`: at most
eight independent scalar components are accepted; three or more outcomes,
AR/CAR and spatial structures, estimated sampling correlations, small-sample
inference, profile intervals, and the full diagnostic suite are outside the
current scope. Warning wording and error behavior may differ from R.

Start with the [dependent-effects article](../dependent), then inspect the
[comparison guide](../compare) for fixture quantities and tolerances.
