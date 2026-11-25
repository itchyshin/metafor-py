# Two correlated outcomes per study

Question: How can two outcomes share a study-level covariance while their sampling errors are correlated?

The synthetic two-outcome case supplies the sampling covariance matrix and fits an unstructured 2 × 2 study-level outcome covariance. The benefit and harm labels define the model-matrix columns.

Run the native example from the repository root:

```sh
python examples/dependent.py --case=bivariate
```

The generated comparison reports both outcome means, the variance components, their covariance and correlation, and coefficient covariance. See the [R and Python comparison guide](../compare).

## Data and provenance

The fixture contains generated data that demonstrate a Berkey-style two-outcome structure. Its provenance, generation script, and checksums are in {download}`reference/dependent/v1/PROVENANCE.md <../../reference/dependent/v1/PROVENANCE.md>`.

## Differences from R metafor

The unstructured covariance is implemented for two outcomes on the checked fixture. Three or more outcomes and other structures are unsupported; see {download}`COMPATIBILITY.md <../../COMPATIBILITY.md>`.
