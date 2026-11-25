# Building forest-plot data

Question: Which estimates and intervals are drawn for each study and for the pooled REML result?

The example creates row-aligned study labels, estimates, standard errors, and confidence limits, then writes an original SVG. The plot is generated from those data by the Python port.

Run the example from the repository root:

```sh
python examples/bcg.py --case=forest
```

Inspect the `examples/bcg-forest.svg` file and accompanying JSON data in the repository. The <a href="../_static/comparisons/bcg-comparison.html">comparison artifact</a> checks the forest rows, order, and pooled summary against R and Julia.

## Provenance

The figure is generated from the BCG fixture documented in {download}`reference/v1/PROVENANCE.md <../../reference/v1/PROVENANCE.md>`. No upstream plot or tutorial image is reused.

## Differences from R metafor

The port provides forest-plot data and an original SVG layout. It does not reproduce the defaults or full layout options of R's `forest.rma()`.
