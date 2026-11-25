# Synthetic phylogenetic fixture

This original synthetic fixture contains five observations on three named species, a supplied positive-definite correlation matrix, and sampling variances. It uses no copied tree, dataset, prose, or figure. R reference values are generated with the pinned metafor 5.2-1 source. The model adds one species-level variance component proportional to the supplied correlation matrix. The fixture and its script are original project material under GPL-2.0-or-later. The fixture is for software parity and makes no empirical biological claim. The tutorial page uses original prose; the upstream Berkey example is linked as further reading only.

## Regeneration

Set `METAFOR_SOURCE_ARCHIVE` to the [CRAN 5.2-1 source archive](https://cran.r-project.org/src/contrib/metafor_5.2-1.tar.gz).
The generator checks SHA-256 `25c421cf52279294b11ab3166adfeb327dd22034a03a46487f081a19a163339b`
and the installed metafor version. Run `Rscript generate.R` from this fixture
directory with the pinned R library active. The repository's `reference/v1/PROVENANCE.md` lists the reference runtime
and dependency versions.
