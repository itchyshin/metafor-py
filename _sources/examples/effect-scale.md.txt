# Choosing an effect scale

**Question.** Why can one dataset produce estimates with very different magnitudes?

## Data and model

The same BCG counts can be summarized as a log risk ratio, log odds ratio, or risk difference. Each scale answers a related question but weights the data differently and uses different units.

## Run the example

From the repository root, run:

```sh
python examples/effect-sizes.py --case=scale
```

For checked outputs, see the [R and Python comparison guide](../compare).

## Interpretation

Read each pooled result with its scale label. The pooled log odds ratio can be exponentiated to an odds ratio; the risk difference is already an absolute probability contrast. The three numeric values are not interchangeable.

## Scope

These checks establish behavior only for the named synthetic or BCG fixture and options. They do not establish full compatibility with R metafor. See [Differences from R metafor](differences.md) and the function-by-option [compatibility table](differences.md).
