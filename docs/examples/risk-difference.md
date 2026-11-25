# Risk differences from 2 × 2 counts

**Question.** What changes when effects stay on the probability scale?

## Data and model

For each study, divide events by the total in each group. The risk difference is the vaccinated proportion minus the control proportion. Its variance adds the two independent binomial proportion variances.

## Run the example

From the repository root, run:

```sh
python examples/effect-sizes.py --case=risk-difference
```

For checked outputs, see the [R and Python comparison guide](../compare).

## Interpretation

A negative difference means a lower event probability in the vaccinated group. Risk differences remain in probability units, so their magnitudes cannot be compared directly with log risk ratios or log odds ratios.

## Scope

These checks establish behavior only for the named synthetic or BCG fixture and options. They do not establish full compatibility with R metafor. See [Differences from R metafor](differences.md) and the function-by-option [compatibility table](differences.md).
