# metafor-py

**Selected meta-analysis methods, implemented natively in Python.**

`metafor-py` is an experimental, independently developed Python port of selected
methods from the R package [`metafor`](https://www.metafor-project.org/). It is
not the R package and does not yet reproduce its full API. The
[compatibility table](COMPATIBILITY.md) records verified, partial, unsupported,
and intentionally different behavior by function and option.

## Start here

The [documentation site](https://itchyshin.github.io/metafor-py/) follows the
analysis path from study effects through model fitting, uncertainty, and
study-level results. Begin with the [Getting Started guide](https://itchyshin.github.io/metafor-py/getting-started.html)
for an install and runnable BCG example with numeric output and a forest plot.
The [tutorial index](https://itchyshin.github.io/metafor-py/examples/index.html)
has 21 topic pages. The [function reference](https://itchyshin.github.io/metafor-py/reference/index.html)
describes the current Python API, and the [R and Python comparison guide](https://itchyshin.github.io/metafor-py/compare.html)
links five fixture reports. See [news](https://itchyshin.github.io/metafor-py/news.html)
for project status and [citation guidance](https://itchyshin.github.io/metafor-py/citation.html)
for software and upstream references.

Install from a local checkout with Python 3.10 or newer:

```sh
python -m pip install -e .
python examples/bcg.py
```

Install optional pandas/Patsy table support with:

```sh
python -m pip install -e '.[tables]'
```

The BCG example reads pinned counts from `reference/v1/bcg.csv` and writes
results and forest-plot data under `examples/`. The Python code runs without R;
R is used only to generate and check reference fixtures.

## Current scope

The implemented examples cover log risk ratios, log odds ratios, risk
differences, fixed-effect and REML fits, a latitude moderator, mean and
new-study prediction intervals, forest data and SVG output, supplied sampling
covariance, nested random effects, a two-outcome model, a supplied
phylogenetic-correlation matrix, and numeric table/formula adapters.

The comparison reports check selected quantities on named fixtures against
pinned R results. Agreement on a fixture does not establish general API parity,
support for an untested option, or calibrated uncertainty. The comparison page
and [compatibility table](COMPATIBILITY.md) state the scope and open limits.

## Project team and upstream credit

The project-intended team for this Python port is Shinichi Nakagawa, Yefeng
Yang, and Wolfgang Viechtbauer. This records the intended team; it does not
imply that every named person has accepted a project role. Wolfgang Viechtbauer
is the author of the upstream R `metafor` package, a separate attribution.
See the upstream [project site](https://www.metafor-project.org/) and
[R documentation](https://wviechtb.github.io/metafor/).

## License and status

The package and documentation are licensed under GPL-2.0-or-later; see
[`LICENSE`](LICENSE). The package is experimental and unreleased. The
documentation source and Python code live on `main`; the generated site is
served from the repository's `gh-pages` branch.
