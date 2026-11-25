# Odds ratios from 2 × 2 counts

**Question.** How do event counts become a log odds ratio?

## Data and model

The BCG example treats vaccinated participants as group 1 and controls as group 2. For each study, the effect is log(ad/bc), and its sampling variance is the sum of the four reciprocal cell counts after the selected zero-cell correction.

## Run the example

From the repository root, run:

```sh
python examples/effect-sizes.py --case=odds-ratio
```

The equivalent Julia command is `julia --project=. examples/effect-sizes.jl --case=odds-ratio` in [Metafor.jl](https://github.com/itchyshin/Metafor.jl). The shared three-language comparison is [effect-size parity](../_static/comparisons/effect-size-comparison.html); phylogenetic results are in the [phylogeny comparison](../_static/comparisons/phylogeny-comparison.html).

## Interpretation

The estimate is on the log scale. Exponentiating it gives the odds ratio; a value below zero means lower odds in the vaccinated group. The fixture comparison checks each study estimate and variance against R metafor 5.2-1.

## Scope

These checks establish behavior only for the named synthetic or BCG fixture and options. They do not establish full compatibility with R metafor. See [Differences from R metafor](differences.md) and the function-by-option [compatibility table](differences.md).
