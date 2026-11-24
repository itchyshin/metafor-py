# Does BCG vaccination reduce tuberculosis risk?

The BCG example asks whether vaccination lowers tuberculosis incidence across 13 studies, and whether the effect changes with absolute latitude. The published example provides the study counts and describes the motivating question. This page uses the shared data fixture and original prose. [Dataset and upstream example](https://wviechtb.github.io/metadat/reference/dat.bcg.html)

## Data

Each study reports tuberculosis cases and non-cases in vaccinated and control groups. We calculate the log risk ratio from those counts. Negative values indicate a lower risk among vaccinated participants.

```{literalinclude} ../examples/bcg.py
:language: python
```

## Models

The script fits an inverse-variance fixed-effect model, a REML random-effects model, and a REML model with absolute latitude as a moderator. REML allows underlying study effects to vary around a mean. The moderator coefficient is the estimated change in log risk ratio per degree of latitude.

## Interpretation

The pooled log risk ratio is negative, consistent with lower tuberculosis risk among vaccinated participants in these studies. The negative latitude coefficient indicates a more negative estimated log risk ratio at higher absolute latitudes. These are associations in this set of studies, and the moderator result alone does not establish why effects vary geographically.

The example also predicts mean log risk ratios at 0°, 30°, and 60° latitude. The confidence interval describes uncertainty in the fitted mean. The prediction interval is wider because it includes both uncertainty in that mean and the estimated variation among study effects. It writes the numeric results, the row-aligned forest data, and an original SVG plot under `examples/`.

## Supplied phylogenetic correlation

The next runnable example uses five synthetic observations on three species and a supplied labelled species-correlation matrix. It includes an exact zero-boundary case and an interior variance-component case, each checked against the pinned R reference. The fixtures are for software parity, not empirical biological claims.

```{literalinclude} ../examples/phylogeny.py
:language: python
```

Run `OPENBLAS_NUM_THREADS=1 .venv/bin/python tools/compare-phylogeny.py` to fit R, Python and Julia from the shared fixtures and write `examples/phylogeny-comparison.html`. Tree estimation and prediction for unseen species are not part of this first example. The correlation matrix and observation order are supplied explicitly.

## Differences from R metafor

This experimental Python port supports log risk ratios, matrix and optional pandas/Patsy formula inputs, fixed-effect and REML models, normal mean and new-study prediction intervals, forest data, and the supplied-correlation phylogenetic model shown here. It omits non-finite rows with a runtime warning and preserves row indices. Warning wording and categories differ from R. REML with zero sampling variances is unsupported; the fit raises an explicit error instead of silently discarding those rows. Full R formula semantics, other effect-size measures, multivariate structures, and many diagnostic and inference options remain unsupported. See the [compatibility table](https://github.com/itchyshin/metafor-py/blob/main/COMPATIBILITY.md).
