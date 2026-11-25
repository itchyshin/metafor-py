# BCG table adapter reference

The input is the versioned BCG fixture in [reference/v1](../../v1/PROVENANCE.md). This case omits trial 4 by marking its latitude missing. The R script builds the intercept and latitude columns and fits a REML meta-regression. It writes the retained trial IDs, the design matrix, and coefficients in model order. The same BCG data provenance and terms apply.

Run `METAFOR_SOURCE_ARCHIVE=/path/to/metafor_5.2-1.tar.gz Rscript reference/table-adapter/v1/generate.R` from the repository root with the package versions in `REFERENCE-VERSIONS.txt`. The generator checks the [metafor 5.2-1 source archive](https://cran.r-project.org/src/contrib/metafor_5.2-1.tar.gz) SHA-256 before regenerating results.

| File | SHA-256 |
|---|---|
| `design.csv` | `5d140fa72b38b0ebec63969fc8369c6483ac2193b0e1bd0983178c57f68524ad` |
| `coefficients.csv` | `0971628c12c45c84e894f444976bad249d0506190401b959d6867e62c03d4d6b` |
