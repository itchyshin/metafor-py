# Compatibility with R metafor 5.2-1

| Function or option | Status | Scope |
|---|---|---|
| `escalc(measure="RR")`, `to` correction options | partial | Log risk ratio and variance for 2×2 counts. `only0`, `all`, `if0all`, and `none` are checked against the pinned release on hand cases. Other measures and correction options are unsupported. |
| `rma(..., method="FE")` | partial | Matrix design, inverse-variance fit, normal inference, checked against BCG. Small-sample tests and alternative intervals are unsupported. |
| `rma(..., method="REML")` | partial | Matrix design, one heterogeneity component, complete-data BCG parity, a zero-heterogeneity boundary, a local-maximum safeguard, and single-study boundary. REML with zero sampling variances is unsupported. |
| Missing and invalid rows | partial | Non-finite rows are omitted with a Python runtime warning and original row indices are retained. Warning text/categories do not reproduce R exactly; zero sampling variances are rejected explicitly. |
| Latitude moderator | verified | BCG design columns, coefficients, intervals, and predictions checked against the pinned reference. |
| Formula and table input | partial | Optional pandas/Patsy adapter for numeric formulas; categorical contrast parity and full R formula semantics are unsupported. |
| Mean and new-study prediction intervals | partial | Normal intervals for supplied design rows and scalar REML variance; FE new-study intervals return missing values. |
| Forest plot data and SVG | partial | Original log-risk-ratio-scale study intervals and REML summary are provided; R `forest.rma` layout defaults are not reproduced. |
| Supplied phylogenetic correlation | partial | One species random-intercept variance component with supplied correlation. Zero-boundary and interior synthetic fits are checked against R. When the random-effect design is contained in the fixed-effect design, REML warns and fixes the unidentifiable variance at zero. Tree estimation and unseen-species prediction are unsupported. |
| Dependent effects and other multivariate structures | unsupported | Planned after the BCG gate. |
