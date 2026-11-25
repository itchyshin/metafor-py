# Effect-size calculation alignment

The treatment group is `1` (BCG vaccination) and the comparison group is `2` (control). For each study, `a`, `b`, `c`, and `d` are respectively treatment events, treatment non-events, control events, and control non-events. Let `n1 = a + b`, `n2 = c + d`, `p1 = a/n1`, and `p2 = c/n2`.

| Symbol | R keyword | Data-input mapping | Recovery extractor | Truth value / check |
|---|---|---|---|---|
| `y_OR = log((p1/(1-p1))/(p2/(1-p2)))` | `measure="OR"` | BCG `tpos,tneg,cpos,cneg` are `a,b,c,d` | `escalc(... )$yi`; native `escalc_or(...)[0]` | `log(a*d/(b*c))`; checked against all 13 R fixture rows and a hand-calculated 2×2 table |
| `v_OR` | `measure="OR"` | same raw 2×2 counts | `escalc(... )$vi`; native `escalc_or(...)[1]` | `1/a + 1/b + 1/c + 1/d`; checked against all 13 R fixture rows and a hand calculation |
| `y_RD = p1 - p2` | `measure="RD"` | same raw 2×2 counts | `escalc(... )$yi`; native `escalc_rd(...)[0]` | Difference in event proportions; checked against all 13 R fixture rows and a hand calculation |
| `v_RD` | `measure="RD"` | same raw 2×2 counts | `escalc(... )$vi`; native `escalc_rd(...)[1]` | `p1(1-p1)/n1 + p2(1-p2)/n2`; checked against all 13 R fixture rows and a hand calculation |
| `C_add` | `add=0.5, to="only0"` | Add 0.5 to each cell in a study table with any zero cell | Native `to="only0"` implementation | Applied before `yi` and `vi`; checked with explicit zero-cell input and R calculations |
| `C_all`, `C_if0all`, `C_none` | `to="all"`, `"if0all"`, or `"none"` | All tables; all only when any zero occurs; or raw counts | Native matching `to` option | Tests check all policies. Raw-cell OR is missing when undefined; RD remains defined for zero-event cells with positive group totals. |

The pooled models use the existing inverse-variance `fit_meta` functions on the calculated `yi` and `vi`. OR results are on the log-odds-ratio scale; exponentiating a pooled log OR gives an odds ratio. RD results stay on the risk-difference scale. Their numerical magnitudes are not directly comparable because they use different scales.
