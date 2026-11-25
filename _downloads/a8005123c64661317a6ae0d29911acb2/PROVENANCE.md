# Reference provenance

`generate.R` creates the BCG reference data and results with R metafor 5.2-1 and metadat 1.6.0. The metafor source archive is https://cran.r-project.org/src/contrib/metafor_5.2-1.tar.gz; SHA-256 `25c421cf52279294b11ab3166adfeb327dd22034a03a46487f081a19a163339b` (computed locally from the downloaded archive). The CRAN metadata lists GPL (>= 2) for both metafor and metadat. `bcg.csv` derives from metadat's `dat.bcg`; source and dataset documentation: https://wviechtb.github.io/metadat/reference/dat.bcg.html. The underlying studies are described by Colditz et al. (1994), https://doi.org/10.1001/jama.1994.03510330076038. The tutorial wiki has separate CC BY-NC-SA terms; no wiki prose or figures are copied. The BCG SVG is original, generated from this data by the port examples.

Page-specific provenance: both port tutorials use original wording to teach the upstream question and link to its data documentation. No third-party figure is adapted.

Regenerate from this directory with the exact package versions active and the source archive available by setting METAFOR_SOURCE_ARCHIVE=/path/to/metafor_5.2-1.tar.gz and running Rscript generate.R. The script verifies SHA-256 25c421cf52279294b11ab3166adfeb327dd22034a03a46487f081a19a163339b before writing. The JSON records R and dependency versions, coefficient covariance matrices, design matrices, row indices, predictions and forest coordinates. R is needed for reference regeneration; both ports and their tests use only the saved fixtures.

Frozen BCG JSON SHA-256: `43f1777f44acc09d0e6174f0e18cefe298f5be49cea2bd068fbb5174f9af6270`. The reference also records the pinned R coefficient-axis labels (`intrcpt`, `ablat`) so cross-language covariance comparisons can detect label permutations.
