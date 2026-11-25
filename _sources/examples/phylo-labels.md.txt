# Aligning a phylogenetic matrix by species

**Question.** Why should correlation-matrix labels be checked before fitting?

## Data and model

A correlation matrix is meaningful only when each row and column refers to the intended species. The fixture includes labels on both axes; the example verifies that their order agrees before passing the matrix to the model.

## Run the example

From the repository root, run:

```sh
python examples/phylogeny.py --case=interior
```

For checked outputs, see the [R and Python comparison guide](../compare).

## Interpretation

The model maps observation species to the labelled matrix. Reordering either axis without applying the same permutation changes the model. Unseen species and tree estimation are outside the current supported scope.

## Scope

These checks establish behavior only for the named synthetic or BCG fixture and options. They do not establish full compatibility with R metafor. See [Differences from R metafor](differences.md) and the function-by-option [compatibility table](differences.md).
