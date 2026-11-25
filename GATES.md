# Gates: metafor-py BCG, dependent-effects, and phylogeny milestone

OWNS: src/**, tests/**, docs/**, examples/**, reference/**, tools/**, COMPATIBILITY.md

Scope: verify the native Python port, its Julia/R parity examples, references, and tutorial build.

- [x] G1: Python package suite passes
  CHECK: OPENBLAS_NUM_THREADS=1 ./.unlazy/clean-python/bin/python -m pytest -q
  EXPECT: 37 passed
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/z3437171/Dropbox/Github Local/metafor-py; path=b12a711c1484/40 entries; output=-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html | 37 passed, 3 warnings in 3.26s

- [x] G2: Python tutorial builds with warnings treated as errors
  CHECK: OPENBLAS_NUM_THREADS=1 ./.venv/bin/python -m sphinx -W --keep-going -b html docs docs/_build/html
  EXPECT: build succeeded.
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/z3437171/Dropbox/Github Local/metafor-py; path=b12a711c1484/40 entries; output=build succeeded. | The HTML pages are in docs/_build/html.

- [x] G3: BCG comparison verifies R, Python, and Julia
  CHECK: OPENBLAS_NUM_THREADS=1 JULIA_NUM_THREADS=1 ./.unlazy/clean-python/bin/python tools/compare-bcg.py
  EXPECT: BCG_THREE_LANGUAGE_HTML_VERIFIED
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/z3437171/Dropbox/Github Local/metafor-py; path=b12a711c1484/40 entries; output=COMPARATOR_FAILURE_CONTROLS_OK coefficient forest covariance-label permutation | MAX_ABS_ERRORS {"H2": 1.7763568394002505e-14, "I2": 5.684341886080802e-14, "QE": 1.4210854715202004e-13, "beta": 1.3877787807814457e-15, "ci_lb": 1.94289029309

- [x] G4: supplied phylogeny comparison verifies R, Python, and Julia
  CHECK: OPENBLAS_NUM_THREADS=1 JULIA_NUM_THREADS=1 ./.unlazy/clean-python/bin/python tools/compare-phylogeny.py
  EXPECT: PHYLOGENY_THREE_LANGUAGE_HTML_VERIFIED
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/z3437171/Dropbox/Github Local/metafor-py; path=b12a711c1484/40 entries; output=PHYLOGENY_THREE_LANGUAGE_HTML_VERIFIED /Users/z3437171/Dropbox/Github Local/metafor-py/examples/phylogeny-comparison.html | MAX_ABS_ERRORS {'v1.beta': {'Python': 4.601874437071274e-14, 'Julia': 4.601874437071274e-14}, 'v1.se': {'Python': 1.

- [x] G5: dependent-effects comparison verifies R, Python, and Julia
  CHECK: OPENBLAS_NUM_THREADS=1 JULIA_NUM_THREADS=1 ./.unlazy/clean-python/bin/python tools/compare-dependent.py
  EXPECT: Wrote 54/54 passing comparisons
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/z3437171/Dropbox/Github Local/metafor-py; path=b12a711c1484/40 entries; output=Wrote 12 coefficient-covariance entries to /Users/z3437171/Dropbox/Github Local/metafor-py/examples/dependent-julia-covariance.csv | Wrote 54/54 passing comparisons to /Users/z3437171/Dropbox/Github Local/metafor-py/examples/dependent-compa

- [x] G6: all shared dependent reference files match their checksums
  CHECK: cd reference/dependent/v1 && shasum -c SHA256SUMS && echo FIXTURE_CHECKSUMS_OK
  EXPECT: FIXTURE_CHECKSUMS_OK
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/z3437171/Dropbox/Github Local/metafor-py; path=b12a711c1484/40 entries; output=warnings.csv: OK | FIXTURE_CHECKSUMS_OK

- [x] G7: twenty tutorial pages build and four comparison pages are linked into the generated Python site
  CHECK: python3 -c "from pathlib import Path; p=Path('docs/_build/html/examples'); names=[x for x in Path('docs/examples').glob('*.md') if x.stem!='index']; c=Path('docs/_build/html/_static/comparisons'); assert len(names)==20 and all((p/(x.stem+'.html')).is_file() for x in names); assert all((c/n).is_file() for n in ['bcg-comparison.html','dependent-comparison.html','phylogeny-comparison.html','effect-size-comparison.html']); print('PYTHON_20_TUTORIALS_AND_PARITY_ARTIFACT_OK')"
  EXPECT: PYTHON_20_TUTORIALS_AND_PARITY_ARTIFACT_OK
  EVIDENCE: exit=0; warning-as-error Sphinx build succeeded; twenty topic pages and four comparison HTML files verified.

- [x] G8: the Python GitHub Pages workflow parses as YAML
  CHECK: ruby -e 'require "yaml"; YAML.load_file(".github/workflows/pages.yml"); puts "PAGES_WORKFLOW_YAML_OK"'
  EXPECT: PAGES_WORKFLOW_YAML_OK
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/z3437171/Dropbox/Github Local/metafor-py; path=b12a711c1484/40 entries; output=PAGES_WORKFLOW_YAML_OK

- [x] G7: all twenty tutorial pages build and the comparison pages are linked into the generated Python site
  CHECK: python3 -c "from pathlib import Path; p=Path('docs/_build/html/examples'); names=[x for x in Path('docs/examples').glob('*.md') if x.stem!='index']; c=Path('docs/_build/html/_static/comparisons'); assert len(names)==20 and all((p/(x.stem+'.html')).is_file() for x in names); assert all((c/n).is_file() for n in ['bcg-comparison.html','dependent-comparison.html','phylogeny-comparison.html','effect-size-comparison.html']); print('PYTHON_20_TUTORIALS_AND_PARITY_ARTIFACT_OK')"
  EXPECT: PYTHON_20_TUTORIALS_AND_PARITY_ARTIFACT_OK
  EVIDENCE: exit=0; warning-as-error Sphinx build succeeded; twenty topic pages and four comparison HTML files verified.

- [x] G9: pinned R effect sizes and pooled models match both native implementations
  CHECK: OPENBLAS_NUM_THREADS=1 ./.unlazy/clean-python/bin/python tools/compare_effect_sizes.py
  EXPECT: EFFECT_SIZE_PARITY_OK checks=232
  EVIDENCE: exit=0; max absolute differences effect=3.9968028886505635e-15, model=5.4569682106375694e-12, correction=4.884981308350689e-15; tolerances 1e-12 for study effects/corrections and 1e-8 for models.
