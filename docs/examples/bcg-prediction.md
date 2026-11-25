# Mean confidence intervals and prediction intervals

Question: What effect does the fitted BCG model predict at 0°, 30°, and 60° latitude?

The confidence interval describes uncertainty in the fitted mean. The prediction interval also includes estimated between-study variation. Both are reported on the log risk-ratio scale.

Run the native example from the repository root:

```sh
python examples/bcg.py --case=prediction
```

The generated JSON contains predictions, standard errors, confidence limits, and prediction limits. The <a href="../_static/comparisons/bcg-comparison.html">three-language comparison</a> compares every prediction field against the pinned reference.

## Interpretation

Exponentiating a log risk ratio gives a risk ratio. Interpret the interval on its reported scale unless you transform both endpoints consistently.

## Differences from R metafor

The package currently provides normal mean and new-study intervals for supplied design rows. Alternative small-sample interval methods are unsupported; see {download}`COMPATIBILITY.md <../../COMPATIBILITY.md>`.
