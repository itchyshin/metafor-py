# Univariate models

`fit_meta(yi, vi, X=None, method="REML")` fits an inverse-variance model to
effect estimates `yi` and sampling variances `vi`. Use `method="FE"` for the
fixed-effect fit or `method="REML"` for the scalar random-effects fit. If `X`
is omitted, the model estimates an intercept; otherwise supply a numeric design
matrix with one row per observation.

The optional table adapter is `fit_meta_formula(data, formula, vi="vi",
method="REML")`. It uses pandas and Patsy to build a numeric design matrix.
Categorical contrast parity and full R formula semantics are not claimed.

```python
import numpy as np
from metafor import fit_meta

fixed = fit_meta(yi, vi, method="FE")
random = fit_meta(yi, vi, method="REML")
X = np.column_stack([np.ones(len(yi)), moderator])
moderated = fit_meta(yi, vi, X=X, method="REML")
```

For example, `fit_meta_formula(data, "yi ~ x", method="REML")` reads effect
estimates from the `yi` column and sampling variances from the default `vi`
column.

The result contains coefficient estimates and covariance, standard errors,
heterogeneity summaries, and normal-theory intervals. For REML, `tau2` is the
estimated between-study variance, constrained to be nonnegative.

Non-finite response or design rows are omitted with a Python runtime warning;
the result retains the original row indices. Zero sampling variances are
rejected explicitly. The implementation uses normal inference; small-sample
tests, alternative estimators, and the broad diagnostic suite in R `metafor`
are not available here.

The BCG examples compare fixed-effect, random-effects, and latitude-moderated
fits with a pinned R reference. These checks apply to the documented fixture
and quantities. See the [BCG article](../bcg) and the
[comparison guide](../compare).
