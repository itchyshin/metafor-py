# Aligning a phylogenetic matrix by species

**Question.** Why should correlation-matrix labels be checked before fitting?

## Data and model

A correlation matrix is meaningful only when each row and column refers to the intended species. The fixture includes labels on both axes; the example verifies that their order agrees before passing the matrix to the model.

## Run the example

From the repository root, run:

```sh
python examples/phylogeny.py --case=interior
```

The equivalent Julia command is `julia --project=. examples/phylogeny.jl --case=interior` in [Metafor.jl](https://github.com/itchyshin/Metafor.jl). The shared three-language comparison is [effect-size parity](../_static/comparisons/effect-size-comparison.html); phylogenetic results are in the [phylogeny comparison](../_static/comparisons/phylogeny-comparison.html).

## Interpretation

The model maps observation species to the labelled matrix. Reordering either axis without applying the same permutation changes the model. Unseen species and tree estimation are outside the current supported scope.

## Scope

These checks establish behavior only for the named synthetic or BCG fixture and options. They do not establish full compatibility with R metafor. See [Differences from R metafor](differences.md) and the function-by-option [compatibility table](differences.md).
