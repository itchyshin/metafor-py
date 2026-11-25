# Effect sizes from binary outcomes

The package calculates three effect measures for two-group event counts:
log risk ratio, log odds ratio, and risk difference. Each function returns an
effect estimate and its sampling variance for every row.

```python
from metafor import escalc_or, escalc_rd, escalc_rr

yi_rr, vi_rr = escalc_rr(ai, bi, ci, di)
yi_or, vi_or = escalc_or(ai, bi, ci, di)
yi_rd, vi_rd = escalc_rd(ai, bi, ci, di)
```

The full function signatures are `escalc_rr(ai, bi, ci, di, add=0.5,
to="only0")`, `escalc_or(ai, bi, ci, di, add=0.5, to="only0")`, and
`escalc_rd(ai, bi, ci, di, add=0.5, to="only0")`.

Here `ai` and `bi` are event and non-event counts in the treatment group;
`ci` and `di` are the corresponding control counts. Inputs are array-like and
must have equal length. The default continuity correction adds 0.5 according
to `to="only0"`. The supported policies are `only0`, `if0all`, `all`, and
`none`; `none` leaves zero-cell estimates undefined where required. These are
the implemented policies, not the complete set of R `escalc()` options.

`escalc_rr()` returns log risk ratios, so zero represents equal risks and a
negative value represents lower risk in the treatment group. `escalc_or()`
returns log odds ratios on the same zero-centered scale. `escalc_rd()` returns
an absolute risk difference on the probability scale. Exponentiate a log risk
ratio or log odds ratio to express it as a ratio.

The formulas, variances, BCG fixture, correction policies, and selected edge
cases are checked against pinned R references or hand calculations. Undefined
inputs can produce a Python warning; warning wording and categories do not
reproduce R exactly. Other effect measures and correction options are not
implemented.

See the [effect-size tutorials](../examples/index) for odds-ratio,
risk-difference, scale-choice, and zero-cell examples, and the
[cross-language comparisons](../compare) for the checked outputs.
