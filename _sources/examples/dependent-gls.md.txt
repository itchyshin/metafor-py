# Correlated sampling errors

Question: How should estimates be combined when their sampling errors have a supplied covariance matrix?

The GLS fixture supplies the full sampling covariance matrix `V` and a two-column design matrix. The model uses `V` directly; it does not estimate the sampling correlations.

Run the native example from the repository root:

```sh
python examples/dependent.py --case=gls
```

The output includes coefficients, standard errors, intervals, heterogeneity statistics, and coefficient covariance. The [R and Python comparison guide](../compare) compares these quantities with pinned R results and Python output.

## Data and provenance

The generated rows and supplied covariance matrix are documented with their row order, creation details, package versions, and terms in {download}`reference/dependent/v1/PROVENANCE.md <../../reference/dependent/v1/PROVENANCE.md>`.

## Differences from R metafor

The supplied positive-definite `V` case is verified on this fixture. Other multivariate covariance structures are unsupported; see {download}`COMPATIBILITY.md <../../COMPATIBILITY.md>`.
