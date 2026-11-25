# Supplied phylogenetic correlation

`fit_phylo(yi, vi, species, correlation, correlation_labels, X=None,
method="REML")` fits one species-level random-intercept variance component
using a supplied species-correlation matrix. Matrix labels are matched to the
species vector; supply labels that identify the matrix row and column order.

The function estimates a nonnegative variance component. Tested examples
include a zero-boundary case and an interior case with positive variance. If
the random-effect design is contained in the fixed-effect design, the
variance is unidentifiable; the implementation warns and fixes it at zero.

The correlation matrix is an input. The package does not estimate a tree or
correlation matrix, and it does not predict effects for unseen species. The
checked fixtures are synthetic software tests, not empirical biological
analyses. Their parity checks cover only the recorded matrix, options, outputs,
and tolerances.

Run the [phylogenetic tutorials](../examples/index) for boundary, interior, and
label-alignment examples. The [comparison guide](../compare) links the
R and Python result page.
