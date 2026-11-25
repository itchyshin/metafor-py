# Predictions and forest summaries

The result returned by `fit_meta()` can predict fitted means at new design
rows. For a model with a moderator, each prediction row must use the same
columns and order as the fitted design matrix.

```python
prediction = model.predict(X_new)
prediction.estimate
prediction.ci_lb, prediction.ci_ub
prediction.pi_lb, prediction.pi_ub
```

The confidence interval describes uncertainty in the fitted mean. For a
random-effects fit, the prediction interval also includes estimated
between-study variation and is therefore usually wider. These intervals use
normal-theory calculations. A fixed-effect fit does not estimate
between-study variance, so new-study prediction limits are unavailable.

`forest_plot_data(yi, vi, labels, pooled=None, level=0.95)` returns study estimates,
intervals, labels, and row positions as structured data. Pass a fitted model as
`pooled` to include its summary. `write_forest_svg(data, path,
title="BCG study effects")` writes an
original SVG from this data; it does not reproduce the defaults or layout of
R's `forest.rma()`.

The BCG example writes prediction results, row-aligned forest JSON, and a
forest SVG under `examples/`. The [Getting Started page](../getting-started)
shows the plot and interprets one prediction. The checked outputs are listed in
the [comparison guide](../compare).
