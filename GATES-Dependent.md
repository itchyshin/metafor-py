# Dependent-effects milestone gates

Verified locally on 2026-11-24. These gates cover the correlated-sampling GLS, nested random-intercept, and two-outcome unstructured-covariance examples.

## Pinned reference

- R 4.6.0 and `metafor` 5.2-1; source archive SHA-256: `25c421cf52279294b11ab3166adfeb327dd22034a03a46487f081a19a163339b`.
- Runtime and dependency versions: `reference/dependent/v1/REFERENCE-VERSIONS.txt`.
- Fixture terms, seeds, and regeneration instructions: `reference/dependent/v1/PROVENANCE.md`.
- All fixture checksums pass with `cd reference/dependent/v1 && shasum -c SHA256SUMS`.

## Commands and evidence

Run from this repository root. Set `R_LIBS` to a library containing the pinned R dependencies before regenerating the reference.

```sh
METAFOR_SOURCE_ARCHIVE=/path/to/metafor_5.2-1.tar.gz R_LIBS=/path/to/metafor-5.2-1/library Rscript reference/dependent/v1/generate.R
(cd reference/dependent/v1 && shasum -c SHA256SUMS)
OPENBLAS_NUM_THREADS=1 .unlazy/clean-python/bin/python -m pytest -q
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m sphinx -W --keep-going -b html docs docs/_build/html
OPENBLAS_NUM_THREADS=1 .unlazy/clean-python/bin/python tools/compare-dependent.py
```

Evidence on 2026-11-24: reference regenerated and every checksum passed in both checkouts; Python suite **37 passed** (3 expected BCG missing-row warnings); strict Sphinx build succeeded; the comparator passed **54/54** quantities and coefficient-covariance entries across R, Python, and Julia. Current public comparison input: `examples/pairwise/dependent-comparison.html`.

The comparator uses quantity-specific tolerances: ordinary estimates `1e-6 + 1e-5 × |R|`; variance/covariance/correlation `1e-6 + 1e-4 × |R|`; coefficient-covariance entries `1e-7 + 1e-5 × |R|`; and `QEp` `1e-24 + 5e-4 × |R|`. The largest observed absolute difference across both ports and all 108 port-to-reference comparisons was `1.403e-7` (Berkey-style estimated correlation).

## Scope limits

The checked slice covers full positive-definite supplied sampling covariance, normal GLS/REML, independent scalar PSD kernels, nested random intercepts, and a two-outcome unstructured study covariance. See `COMPATIBILITY.md` for unsupported model structures, inference options, and formula semantics.
