# From counts to log risk ratios

Question: How do the reported tuberculosis case counts translate into study effects?

Each row has cases and non-cases for vaccinated and control groups. `escalc_rr` computes the log risk ratio and its sampling variance. Negative log risk ratios correspond to lower observed risk in the vaccinated group.

The fixture is derived from [`dat.bcg`](https://wviechtb.github.io/metadat/reference/dat.bcg.html). Its source, terms, and pinned R reference are recorded in {download}`reference/v1/PROVENANCE.md <../../reference/v1/PROVENANCE.md>`. The page uses original prose and an original plot.

Run the native Python example from the repository root:

```sh
python examples/bcg.py --case=effects
```

The script reads the raw counts from the versioned fixture, computes every study effect, and writes the results for comparison with R and Julia. The <a href="../_static/comparisons/bcg-comparison.html">Open the local comparison page</a> reports differences by output and tolerance.

## Interpretation

The pooled estimates summarize the study effects. They do not adjust for the latitude moderator; that question is handled in [meta-regression](bcg-moderator.md).

## Differences from R metafor

The Python implementation supports the log risk ratio and the checked zero-cell correction options listed in {download}`COMPATIBILITY.md <../../COMPATIBILITY.md>`. Other `escalc()` measures are unsupported.
