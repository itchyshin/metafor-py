# Phylogenetic model at the zero boundary

**Question.** Can the supplied species correlation improve this example?

## Data and model

The synthetic fixture has repeated observations for three labelled species and a supplied correlation matrix. In this boundary case, the estimated phylogenetic variance is zero.

## Run the example

From the repository root, run:

```sh
python examples/phylogeny.py --case=boundary
```

The equivalent Julia command is `julia --project=. examples/phylogeny.jl --case=boundary` in [Metafor.jl](https://github.com/itchyshin/Metafor.jl). The shared three-language comparison is [effect-size parity](../_static/comparisons/effect-size-comparison.html); phylogenetic results are in the [phylogeny comparison](../_static/comparisons/phylogeny-comparison.html).

## Interpretation

At the boundary, the estimated shared phylogenetic component contributes no extra variance. This is a software check on a synthetic fixture, not evidence that phylogenetic structure is absent in any biological system.

## Scope

These checks establish behavior only for the named synthetic or BCG fixture and options. They do not establish full compatibility with R metafor. See [Differences from R metafor](differences.md) and the function-by-option [compatibility table](differences.md).
