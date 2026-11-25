# Pooling log odds ratios

**Question.** How do fixed-effect and REML summaries differ on the same effects?

## Data and model

First calculate the BCG study log odds ratios and sampling variances. Then fit inverse-variance fixed-effect and one-component REML models to those same rows.

## Run the example

From the repository root, run:

```sh
python examples/effect-sizes.py --case=odds-ratio
```

For checked outputs, see the [R and Python comparison guide](../compare).

## Interpretation

The fixed-effect estimate assumes one common underlying effect. REML estimates between-study variation and usually widens uncertainty when heterogeneity is present. Both intervals here use normal quantiles.

## Scope

These checks establish behavior only for the named synthetic or BCG fixture and options. They do not establish full compatibility with R metafor. See [Differences from R metafor](differences.md) and the function-by-option [compatibility table](differences.md).
