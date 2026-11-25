# Phylogenetic model at the zero boundary

Can the supplied species correlation improve this example?

## Data and model

The synthetic fixture has repeated observations for three labelled species and a supplied correlation matrix. In this boundary case, the estimated phylogenetic variance is zero.

## Run the example

From the repository root, run:

```sh
python examples/phylogeny.py --case=boundary
```

For checked outputs, see the [R and Python comparison guide](../compare).

## Interpretation

At the boundary, the fitted phylogenetic component contributes zero variance. The synthetic observations exercise the software’s handling of that boundary.

## Scope

These checks establish behavior only for the named synthetic or BCG fixture and options. They do not establish full compatibility with R metafor. See [Differences from R metafor](differences.md) and the function-by-option [compatibility table](differences.md).
