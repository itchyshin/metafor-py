# Missing observations and row identity

**Question.** What happens when one study has incomplete counts?

## Data and model

The BCG fixture and row labels are retained while effect sizes are computed. Non-finite input values produce a missing effect and variance for that row; model fitting removes incomplete rows using one shared row mask.

## Run the example

From the repository root, run:

```sh
python -m pytest tests/test_effect_sizes.py -k missing
```

The equivalent Julia command is `julia --project test/runtests.jl effect-sizes` in [Metafor.jl](https://github.com/itchyshin/Metafor.jl). The shared three-language comparison is [effect-size parity](../_static/comparisons/effect-size-comparison.html); phylogenetic results are in the [phylogeny comparison](../_static/comparisons/phylogeny-comparison.html).

## Interpretation

The focused checks confirm that missing counts remain aligned and do not shift later studies. Model row indices are retained by the fit result. Warning wording differs from R; see the compatibility table.

## Scope

These checks establish behavior only for the named synthetic or BCG fixture and options. They do not establish full compatibility with R metafor. See [Differences from R metafor](differences.md) and the function-by-option [compatibility table](differences.md).
