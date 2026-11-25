# Effect-size reference provenance

This fixture contains odds-ratio and risk-difference calculations and pooled fixed-effect/REML fits for the 13 raw 2×2 BCG study tables in [`../../v1/bcg.csv`](../../v1/bcg.csv). The data originate from `metadat::dat.bcg`; redistribution terms and the upstream dataset page are recorded in [`../../v1/PROVENANCE.md`](../../v1/PROVENANCE.md). No upstream tutorial prose or figure is copied.

`generate.R` computes log odds ratios, risk differences, their sampling variances, and FE/REML pooled fits with R `metafor` 5.2-1. It also records the four zero-cell policies on a hand-checkable two-row fixture. The source archive is <https://cran.r-project.org/src/contrib/metafor_5.2-1.tar.gz>, SHA-256 `25c421cf52279294b11ab3166adfeb327dd22034a03a46487f081a19a163339b`. The script verifies the archive hash and package version before writing results. It uses the default continuity correction explicitly (`add=0.5`, `to="only0"`).

Regenerate from this directory with the pinned source available:

```sh
METAFOR_SOURCE_ARCHIVE=/path/to/metafor_5.2-1.tar.gz Rscript generate.R
```

The equation and code alignment is documented in `EFFECT_SIZE_ALIGNMENT.md`. R is required only to regenerate the reference; neither port requires R to run.
