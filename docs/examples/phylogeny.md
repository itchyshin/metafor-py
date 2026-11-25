# Supplied phylogenetic correlation

Question: How does a supplied species-correlation matrix enter a random-effects meta-analysis?

The fixture gives five observations on three species and a labelled correlation matrix. The model uses that matrix as supplied. It checks an exact zero-boundary case and an interior variance-component case.

Run the native example from the repository root:

```sh
python examples/phylogeny.py --case=boundary
python examples/phylogeny.py --case=interior
```

The <a href="../_static/comparisons/phylogeny-comparison.html">comparison page</a> shows the R, Python, and Julia estimates and intervals. The fixtures are synthetic software checks and make no empirical biological claim.

## Provenance

The generating R script, model inputs, reference outputs, and terms are recorded in {download}`reference/phylogeny/v1/PROVENANCE.md <../../reference/phylogeny/v1/PROVENANCE.md>`. The upstream [Berkey analysis](https://www.metafor-project.org/doku.php/analyses:berkey1998) is a separate multivariate example; this page does not reuse its data.

## Differences from R metafor

The port accepts a supplied correlation matrix and repeated species. Tree estimation and prediction for unseen species are unsupported; see {download}`COMPATIBILITY.md <../../COMPATIBILITY.md>`.
