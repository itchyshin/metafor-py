# Does latitude explain effect variation?

Question: Is absolute latitude associated with the study log risk ratio in this example?

The model uses an intercept and absolute latitude as its design matrix. Its slope is the expected change in log risk ratio per degree. Interpret it as a study-level association.

Run the native Python example from the repository root:

```sh
python examples/bcg.py --case=moderator
```

The script reports the latitude coefficient, its interval, and predictions at 0°, 30°, and 60°. The [R and Python comparison guide](../compare) checks the design matrix and coefficient labels as well as the estimates.

## Data and provenance

The raw data source is the [`dat.bcg` documentation](https://wviechtb.github.io/metadat/reference/dat.bcg.html). The checked-in fixture and R version details are recorded in {download}`reference/v1/PROVENANCE.md <../../reference/v1/PROVENANCE.md>`.

## Differences from R metafor

The numeric formula/table adapter is partial. Categorical contrasts and full R formula semantics are unsupported; see {download}`COMPATIBILITY.md <../../COMPATIBILITY.md>`.
