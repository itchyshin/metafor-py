# Dependent-effects model contract (v1)

This file defines the statistical target shared by the Python and Julia ports. The
reference generator is `generate.R` in this directory and runs with the pinned
metafor 5.2-1 source archive recorded in `../PROVENANCE.md`.

## Core model

After applying one common row mask to `y`, `X`, and both axes of the supplied
sampling covariance matrix `V`, let `y` have length `k`, let `X` be `k × p`, and
let `V` be positive definite. For known positive-semidefinite random-effect
kernels `K_j` and nonnegative variance components `theta_j`,

\[
C = V + \sum_{j=1}^{q} \theta_j K_j,\qquad
\hat\beta = (X^T C^{-1} X)^{-1} X^T C^{-1} y,
\]

\[
P = C^{-1} - C^{-1}X(X^T C^{-1}X)^{-1}X^TC^{-1},
\]

and the minimized restricted negative log likelihood is

\[
\ell_R = \tfrac12\{\log|C| + \log|X^TC^{-1}X| + y^TPy
                  + (k-p)\log(2\pi)\}.
\]

The estimator targets the minimum over the admissible variance-component
space, explicitly comparing zero-variance faces. The coefficient covariance is
`(X' C^-1 X)^-1`; tests compare estimates and inferential quantities, not optimizer
iteration counts. `V` is treated as known and is never rescaled or estimated.

## Model terms

- **Correlated sampling errors:** pass the full `V`; fixed-effect GLS is the
  `q = 0` case. For a supplied covariance, filtering observations uses the same
  retained indices on rows and columns (`V[keep, keep]`).
- **Nested random intercepts:** for each grouping level `j`, form indicator matrix
  `Z_j` after resolving nested labels as tuples of their parent labels and the
  local level. Then `K_j = Z_j Z_j'`. Reused local labels in different parents
  remain distinct lower-level groups.
- **Supplied phylogenetic correlation:** map observed species to the labeled
  supplied matrix `A`, construct `Z`, and use `K_phylo = Z A Z'`.
- **Berkey-style unstructured study effect:** for outcome `a` in study `s`, let
  `u_s ~ N(0, Sigma)` with `Sigma = L L'` positive semidefinite. The random
  covariance is `G[(s,a),(t,b)] = 1(s=t) Sigma[a,b]`; the sampling covariance is
  supplied separately in `V`. The fixed design has one coefficient per outcome.

For residual heterogeneity, use the sampling covariance alone:
`P_V = V^-1 - V^-1 X (X' V^-1 X)^-1 X' V^-1` and `QE = y' P_V y`.
This differs from `P`, which uses `C` inside the REML objective.

Rows with missing outcomes or design/group labels are removed once and retained
in `row_indices`; when input `V` is full-sized it is subset on both axes. A
non-finite or non-positive-definite retained `V`, a rank-deficient `X`, invalid
kernel, or no retained rows is an error. A boundary optimum is valid and reports
zero for the affected variance component.

## Symbol-to-implementation alignment

| Symbol | API / covariance term | DGP draw | Recovery extractor | Truth / check |
|---|---|---|---|---|
| `y` | `yi` vector in original row order | Fixed synthetic outcome vector | `result.yi` aligned by `row_indices` | Exact fixture values and retained order |
| `V` | Full sampling covariance matrix | Fixed positive-definite matrix with nonzero off-diagonals | `result.V` after two-axis masking | Input entries recovered exactly before masking |
| `X` | Fixed-effect design matrix | Intercept and numeric moderator columns | `result.beta`, `result.covariance` | Column labels and row order match the fixture |
| `Z_j` | Group indicator for nested level `j` | Study/effect labels with reused local labels | `result.components[j].kernel` | Tuple nesting distinguishes reused labels |
| `theta_j` | Nonnegative multiplier of `K_j` | Fixed known-covariance kernel | `result.components[j].estimate` | Compared with metafor 5.2-1 and boundary truth |
| `A` | Label-aligned phylogenetic correlation | Supplied labeled PSD matrix | `result.components[phylo].kernel` | Matrix permutation with labels preserves fit |
| `Sigma` | Unstructured within-study outcome covariance | Positive-semidefinite 2 × 2 truth for generated case | `result.outcome_covariance` | Diagonals, covariance, and boundary behavior compared |
| `C` | `V + G` marginal covariance | `V` plus generated random-effect covariance | `result.marginal_covariance` | Symmetric positive definite; agrees with component sum |
| `P` | REML residual projection matrix | Derived from `C` and `X` | Restricted likelihood term `y' P y` | Compared through the objective and estimates |
| `P_V` | Sampling-only residual projection matrix | Derived from `V` and `X` | `result.qe = y' P_V y` | Compared against R `QE` |
| `row_indices` | One common retained-row map | Explicit missing outcome and missing group cases | `result.row_indices` | Same original indices in Julia and Python |

## Compatibility boundary for this milestone

Supported target: normal-normal REML/FE with a supplied full sampling covariance,
one or more independent scalar covariance kernels, nested random-intercept
kernels, a supplied phylogenetic kernel, and a two-outcome unstructured study
covariance. The first implementation does not claim parity for general `rma.mv`
structures such as AR, CAR, spatial, GEN, multiple correlated random terms,
small-sample inference, profile intervals, or estimated sampling correlations.
