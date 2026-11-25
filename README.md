# metafor-py

**Native Python methods inspired by the R package [`metafor`](https://www.metafor-project.org/).**

**Tutorials and examples:** [metafor-py documentation](https://itchyshin.github.io/metafor-py/) · [source repository](https://github.com/itchyshin/metafor-py)

`metafor-py` is an experimental, independently developed Python port of selected meta-analysis methods. It is not the R package and does not yet reproduce its full API. The [compatibility table](COMPATIBILITY.md) records what is verified, partial, unsupported, or intentionally different.

The project follows the teaching and analysis structure of the R package: calculate study effects, fit models, interpret uncertainty, and inspect plots. Each port uses native Python arrays and structured results in its core, with optional pandas/Patsy adapters.

## Start with the tutorials

The [documentation site](https://itchyshin.github.io/metafor-py/) contains 20 topic-focused tutorials and a differences guide. Start with the [BCG example](https://itchyshin.github.io/metafor-py/examples/bcg-effects.html), then explore fixed and random effects, meta-regression, predictions, forest data, correlated effects, nested effects, a two-outcome model, and phylogenetic boundary and interior fits.

```sh
python -m pip install -e '.[test,docs,tables]'
python examples/bcg.py
python examples/dependent.py
python examples/phylogeny.py
```

The tutorial overview lists the focused `--case` commands. Running these scripts without a selector rebuilds each complete comparison result.

The [three-language BCG comparison](https://itchyshin.github.io/metafor-py/_static/comparisons/bcg-comparison.html), [dependent-effects comparison](https://itchyshin.github.io/metafor-py/_static/comparisons/dependent-comparison.html), and [phylogenetic comparison](https://itchyshin.github.io/metafor-py/_static/comparisons/phylogeny-comparison.html), and [effect-size comparison](https://itchyshin.github.io/metafor-py/_static/comparisons/effect-size-comparison.html) place R metafor 5.2-1, Python, and Julia results side by side. The plots and comparison pages are original. Fixture provenance and checksums live under [`reference/`](reference/).

GitHub Actions checks documentation builds from `main`. GitHub Pages serves the static site from the `gh-pages` branch; the source tutorials and package code remain on `main`.

Build the documentation locally:

```sh
python -m sphinx -W --keep-going -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` after the build. The [GitHub Pages workflow](.github/workflows/pages.yml) builds this documentation from the repository and deploys it from `main`.

## What the project covers

- Log risk ratios from 2×2 study counts, fixed-effect and REML models, and a latitude moderator.
- Mean and prediction intervals, row-aligned forest data, and an original SVG plot.
- Supplied sampling covariance matrices, nested scalar random effects, two-outcome covariance, and a supplied phylogenetic correlation matrix.
- Versioned R reference fixtures used for parity checks. The ports run without R.

These methods cover a small part of the R package. See [`COMPATIBILITY.md`](COMPATIBILITY.md) before relying on a function or option. Do not infer support from the package name or from one passing example.

## Relationship to R `metafor`

The upstream R package was written by Wolfgang Viechtbauer and provides a much broader collection of meta-analysis methods. This repository credits and links to the [official project site](https://www.metafor-project.org/), [R documentation](https://wviechtb.github.io/metafor/), and the [BCG dataset documentation](https://wviechtb.github.io/metadat/reference/dat.bcg.html). The tutorial pages use original prose and distinguish synthetic fixtures from published data. GPL notices are retained where derivative code or data require them.

Project-intended maintainers: Shinichi Nakagawa, Yefeng Yang, and Wolfgang Viechtbauer. This records the project's intended team and does not imply that anyone has accepted a role.

## License and status

This repository is experimental and unreleased. The source is licensed under GPL-2.0-or-later; see [`LICENSE`](LICENSE) and each fixture's provenance record for data terms. The documentation site is published from `main`; no package release has been made.
