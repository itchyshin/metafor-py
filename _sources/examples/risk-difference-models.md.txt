# Pooling risk differences

**Question.** What does heterogeneity look like on an absolute scale?

## Data and model

Use the BCG study risk differences and their binomial sampling variances as the model inputs. Fit the same fixed-effect and REML specifications used for the log odds ratios.

## Run the example

From the repository root, run:

```sh
python examples/effect-sizes.py --case=risk-difference
```

The equivalent Julia command is `julia --project=. examples/effect-sizes.jl --case=risk-difference` in [Metafor.jl](https://github.com/itchyshin/Metafor.jl). The shared three-language comparison is [effect-size parity](../_static/comparisons/effect-size-comparison.html); phylogenetic results are in the [phylogeny comparison](../_static/comparisons/phylogeny-comparison.html).

## Interpretation

The pooled risk difference is an absolute probability contrast. Heterogeneity summaries depend on the scale and sampling variances, so they need not match the log odds ratio analysis.

## Scope

These checks establish behavior only for the named synthetic or BCG fixture and options. They do not establish full compatibility with R metafor. See [Differences from R metafor](differences.md) and the function-by-option [compatibility table](differences.md).
