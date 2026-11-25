# Turning a formula into a checked design matrix

**Question.** If one study has no moderator value, do the formula and matrix interfaces fit the same studies?

## Data and model

We use the 13-study BCG fixture and compute each log risk ratio from its raw counts. Trial 4 is assigned a missing latitude so the example can check how the table adapter preserves study identity. The model is `yi ~ 1 + ablat`.

## Run the example

From the repository root, run:

```sh
python examples/bcg.py --case=table-adapter
```

The command needs the `tables` extra (`pandas` and `patsy`). See the [R and Python comparison guide](../compare) for the direct reference checks.

The example prints the retained trial IDs and formula coefficients. It also fits the same rows with an explicit matrix and reports the largest coefficient difference.

## Interpretation

The formula fit omits trial 4 and retains the other 12 trial IDs in their input order. Its estimates match the matrix fit to within `1e-12`. The report checks the retained IDs, all 24 numeric design values, and both coefficients against pinned R results. Patsy and StatsModels label the intercept differently, while the numeric design and coefficient order agree.

## Scope

This comparison checks one numeric BCG moderator and one missing row. It does not establish full R formula compatibility or categorical contrast parity. See [Differences from R metafor](differences.md) and the function-by-option [compatibility table](differences.md).
