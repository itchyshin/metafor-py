# Fixed-effect and random-effects estimates

Question: What pooled estimate follows when all studies share one effect, and what changes when study effects vary?

The fixed-effect fit uses inverse sampling-variance weights. The REML fit estimates a between-study variance and uses it in the weights. Both fits use the same BCG log risk ratios and are checked against the pinned R fixture.

Run the native example from the repository root:

```sh
python examples/bcg.py --case=models
```

The output labels the `fixed` and `random` fits and reports coefficients, standard errors, heterogeneity, and intervals. The [R and Python comparison guide](../compare) shows each result from R and Python with quantity-specific tolerances.

## Interpretation

The REML estimate accounts for estimated variation among study effects. Its prediction interval is about a future study effect; it is wider than a confidence interval for the mean.

## Differences from R metafor

The supported FE and REML options and the unimplemented inference choices are listed by function in {download}`COMPATIBILITY.md <../../COMPATIBILITY.md>`.
