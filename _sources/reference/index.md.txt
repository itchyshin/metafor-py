# Reference

This reference covers methods currently exposed by the experimental `metafor`
Python module. The API is deliberately smaller than R `metafor`. The
[compatibility table](https://github.com/itchyshin/metafor-py/blob/main/COMPATIBILITY.md)
records scope by function and option.

## Choose a topic

| Topic | Start here |
|---|---|
| Study-level effects from 2 × 2 counts | [Effect sizes](effect-sizes) |
| Fixed-effect and REML models | [Univariate models](univariate) |
| Mean and new-study intervals | [Prediction and forest summaries](prediction) |
| Supplied sampling covariance and dependent effects | [Dependent effects](dependent) |
| A supplied species-correlation matrix | [Phylogenetic model](phylogeny) |

All five pages describe native Python functions and inputs at the level needed
to choose a workflow. Runnable examples and fixture comparisons show the
checked cases. Consult the full function signatures and release notes in the
source when an option is not described here.

## Common inputs

Model functions accept numeric vectors for effect estimates and sampling
variances. `X` is a numeric design matrix whose rows follow observation order.
Dependent-effects functions accept a full sampling covariance matrix `V`;
functions that accept a table or formula require the optional pandas and Patsy
dependencies. The tutorials show row alignment and missing-value handling for
the supported cases.

The core package depends on NumPy and SciPy. Install from a checkout with
`python -m pip install -e .`. Optional table support is installed with
`python -m pip install -e '.[tables]'`.

```{toctree}
:maxdepth: 1

effect-sizes
univariate
prediction
dependent
phylogeny
```
