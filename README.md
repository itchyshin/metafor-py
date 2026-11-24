# metafor-py

A native Python implementation of selected methods from Wolfgang Viechtbauer's R package metafor. The first runnable example is the BCG vaccine meta-analysis.

## Run the BCG example

Install the project and run `python examples/bcg.py`. The example reads the shared raw-count fixture, computes log risk ratios, fits fixed-effect and REML models, fits a latitude moderator, calculates mean and new-study intervals, and writes numeric results plus forest data and an SVG plot under `examples/`.

The reference values were regenerated with R metafor 5.2-1. The original data and tutorial are credited at https://wviechtb.github.io/metadat/reference/dat.bcg.html. This repository is experimental and covers only the functions and options listed in `COMPATIBILITY.md`.

## Three-language comparison pages

Open [`examples/bcg-comparison.html`](examples/bcg-comparison.html) for the R, Python and Julia BCG results and forest plots. Open [`examples/phylogeny-comparison.html`](examples/phylogeny-comparison.html) for the supplied-correlation phylogeny fits. Regenerate both pages with `python tools/compare-bcg.py --julia-root /path/to/Metafor.jl` and `python tools/compare-phylogeny.py --julia-root /path/to/Metafor.jl`.

The intended maintainers are Shinichi Nakagawa, Yefeng Yang, and Wolfgang Viechtbauer. This records the project’s intended team; it does not imply that any person has accepted a role.

## Differences from R metafor

This is an early native port. It includes matrix-first univariate models, an optional pandas/Patsy formula adapter, forest plot data, and an initial supplied-correlation phylogenetic example. It does not implement the full metafor formula semantics, all effect-size measures, small-sample inference choices, or the broader multivariate model families. See `COMPATIBILITY.md` for the current scope.
