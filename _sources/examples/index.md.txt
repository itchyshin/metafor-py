# Tutorials

Each tutorial asks a question, introduces the fixture and model, then interprets the results. Every runnable stage has a named selector. The Python examples use native Python methods; comparisons use the pinned R reference.

Install the package first with `python -m pip install -e .`. The comparison artifacts are included in the built site.

| Page | Question | Runnable Python command | Comparison |
|---|---|---|---|
| [BCG effect sizes](bcg-effects.md) | How do raw counts become log risk ratios? | `python examples/bcg.py --case=effects` | [R and Python comparison guide](../compare) |
| [Fixed and random effects](bcg-models.md) | How do FE and REML pooled estimates differ? | `python examples/bcg.py --case=models` | [R and Python comparison guide](../compare) |
| [Meta-regression](bcg-moderator.md) | How does latitude relate to the estimated effect? | `python examples/bcg.py --case=moderator` | [R and Python comparison guide](../compare) |
| [Predictions](bcg-prediction.md) | What are the fitted means and intervals at selected latitudes? | `python examples/bcg.py --case=prediction` | [R and Python comparison guide](../compare) |
| [Forest plot data](bcg-forest.md) | Which quantities feed the forest plot? | `python examples/bcg.py --case=forest` | [R and Python comparison guide](../compare) |
| [Correlated sampling errors](dependent-gls.md) | How does a supplied covariance matrix change GLS inference? | `python examples/dependent.py --case=gls` | [R and Python comparison guide](../compare) |
| [Nested effects](dependent-nested.md) | How are study and effect-level variances represented? | `python examples/dependent.py --case=nested` | [R and Python comparison guide](../compare) |
| [Two outcomes](dependent-bivariate.md) | How are correlated outcomes modeled within studies? | `python examples/dependent.py --case=bivariate` | [R and Python comparison guide](../compare) |
| [Phylogenetic boundary and interior cases](phylogeny.md) | What changes when species share a supplied correlation? | `python examples/phylogeny.py --case=boundary`<br>`python examples/phylogeny.py --case=interior` | [R and Python comparison guide](../compare) |
| [Differences from R metafor](differences.md) | Which functions and options are verified or differ? | See the tutorials | `COMPATIBILITY.md` |

The table-adapter report checks retained trial IDs, 24 design values, and two coefficients against the pinned R reference, plus formula-to-matrix agreement. Omit `--case` from a BCG or dependent command to run its complete example. The phylogenetic commands exercise separate zero-boundary and interior variance cases.

| [Odds ratios](odds-ratio.md) | How do counts become a log odds ratio? | `python examples/effect-sizes.py --case=odds-ratio` | [R and Python comparison guide](../compare) |
| [Risk differences](risk-difference.md) | How do counts become an absolute probability contrast? | `python examples/effect-sizes.py --case=risk-difference` | [R and Python comparison guide](../compare) |
| [Choosing a scale](effect-scale.md) | Why do effect magnitudes differ by scale? | `python examples/effect-sizes.py --case=scale` | [R and Python comparison guide](../compare) |
| [Zero-cell policies](zero-cell-policies.md) | How do correction choices change results? | `python examples/effect-sizes.py --case=zero-correction` | [R and Python comparison guide](../compare) |
| [Missing observations](missing-rows.md) | Are incomplete studies kept aligned? | `python -m pytest tests/test_effect_sizes.py tests/test_bcg.py -k missing` (requires the `test` extra) | [R and Python comparison guide](../compare) |
| [Table and formula adapter](table-adapter.md) | Does a missing moderator row stay aligned across inputs? | `python examples/bcg.py --case=table-adapter` | [R and Python comparison guide](../compare) |
| [Pooling log odds ratios](odds-ratio-models.md) | How do FE and REML summaries differ? | `python examples/effect-sizes.py --case=odds-ratio` | [R and Python comparison guide](../compare) |
| [Pooling risk differences](risk-difference-models.md) | How does heterogeneity look on an absolute scale? | `python examples/effect-sizes.py --case=risk-difference` | [R and Python comparison guide](../compare) |
| [Phylogenetic boundary](phylo-boundary.md) | What does a zero variance boundary mean? | `python examples/phylogeny.py --case=boundary` | [R and Python comparison guide](../compare) |
| [Phylogenetic interior fit](phylo-interior.md) | What changes when phylogenetic variance is positive? | `python examples/phylogeny.py --case=interior` | [R and Python comparison guide](../compare) |
| [Phylogenetic matrix labels](phylo-labels.md) | Why check species labels and order? | `python examples/phylogeny.py --case=interior` | [R and Python comparison guide](../compare) |
```{toctree}
:maxdepth: 1

bcg-effects
bcg-models
bcg-moderator
bcg-prediction
bcg-forest
dependent-gls
dependent-nested
dependent-bivariate
phylogeny
differences
odds-ratio
risk-difference
effect-scale
zero-cell-policies
missing-rows
table-adapter
odds-ratio-models
risk-difference-models
phylo-boundary
phylo-interior
phylo-labels
```
