# Missing observations and row identity

**Question.** What happens when one study has incomplete counts?

## Data and model

The BCG fixture and row labels are retained while effect sizes are computed. Non-finite input values produce a missing effect and variance for that row; model fitting removes incomplete rows using one shared row mask.

## Run the example

Install the test dependencies and run the focused check from the repository root:

```sh
python -m pip install -e ".[test]"
python -m pytest tests/test_effect_sizes.py tests/test_bcg.py -k missing
```

For checked outputs, see the [R and Python comparison guide](../compare).

## Interpretation

The focused checks confirm that missing counts remain aligned and do not shift later studies. Model row indices are retained by the fit result. Warning wording differs from R; see the compatibility table.

## Scope

These checks establish behavior only for the named synthetic or BCG fixture and options. They do not establish full compatibility with R metafor. See [Differences from R metafor](differences.md) and the function-by-option [compatibility table](differences.md).
