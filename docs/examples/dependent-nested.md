# Nested study and effect variation

Question: How can the model represent variation among studies and among effects within each study?

The synthetic fixture has repeated local effect labels across studies. The nested key therefore includes both the parent study and local effect identity. This preserves row and group alignment when constructing covariance kernels.

Run the native example from the repository root:

```sh
python examples/dependent.py --case=nested
```

The script fits a REML model with study and nested-effect variance components. Its estimates and coefficient covariance appear in the [R and Python comparison guide](../compare).

## Interpretation

Each nonnegative variance component describes a level of the supplied grouping structure. The fixture is synthetic and does not estimate a biological or clinical effect.

## Differences from R metafor

Nested random intercepts are verified on the supplied fixture. Crossed or correlated structures beyond the listed scalar kernels remain unsupported; see {download}`COMPATIBILITY.md <../../COMPATIBILITY.md>`.
