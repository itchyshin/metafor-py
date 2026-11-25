# Phylogenetic model with an interior variance

**Question.** What changes when the estimated phylogenetic variance is positive?

## Data and model

Keep the same model structure but use the separate synthetic fixture designed to give an interior variance estimate. Species labels and correlation-matrix order are checked before fitting.

## Run the example

From the repository root, run:

```sh
python examples/phylogeny.py --case=interior
```

The equivalent Julia command is `julia --project=. examples/phylogeny.jl --case=interior` in [Metafor.jl](https://github.com/itchyshin/Metafor.jl). The shared three-language comparison is [effect-size parity](../_static/comparisons/effect-size-comparison.html); phylogenetic results are in the [phylogeny comparison](../_static/comparisons/phylogeny-comparison.html).

## Interpretation

The positive estimate means the supplied correlation contributes to the fitted covariance for this fixture. The comparison checks coefficients, standard errors, intervals, and variance against the pinned R reference.

## Scope

These checks establish behavior only for the named synthetic or BCG fixture and options. They do not establish full compatibility with R metafor. See [Differences from R metafor](differences.md) and the function-by-option [compatibility table](differences.md).
