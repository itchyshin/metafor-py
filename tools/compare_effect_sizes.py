"""Compare pinned R effect sizes with the native Julia and Python outputs."""
from __future__ import annotations

import csv
import html
import math
import os
import shutil
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JULIA_ROOT = Path(os.environ.get("METAFOR_JL_ROOT", ROOT.parent / "Metafor.jl"))
REF = ROOT / "reference/effect-sizes/v1"
OUT = ROOT / "examples/effect-size-comparison.html"
TOLS = {"effect": 1e-12, "model": 1e-8, "correction": 1e-12}


def rows(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def number(value):
    if value in ("", "NA", "NaN"):
        return math.nan
    return float(value)


def close(a, b, atol):
    return (math.isnan(a) and math.isnan(b)) or math.isclose(a, b, rel_tol=atol, abs_tol=atol)


def main():
    native = {
        "Python": rows(ROOT / "examples/generated/effect-sizes/python-all.csv"),
        "Julia": rows(JULIA_ROOT / "examples/generated/effect-sizes/julia-all.csv"),
        "Python scale": rows(ROOT / "examples/generated/effect-sizes/python-scale.csv"),
        "Julia scale": rows(JULIA_ROOT / "examples/generated/effect-sizes/julia-scale.csv"),
    }
    for language, path in (("Python", ROOT), ("Julia", JULIA_ROOT)):
        native[language + " zero"] = rows(path / "examples/generated/effect-sizes" / ("python-zero-correction.csv" if language == "Python" else "julia-zero-correction.csv"))
    r_effects = rows(REF / "bcg-effect-sizes.csv")
    r_models = rows(REF / "model-reference.csv")
    r_zero = rows(REF / "zero-cell-reference.csv")
    rr_ref = json.loads((ROOT / "reference/v1/bcg-reference.json").read_text())

    checks = []
    for lang in ("Python", "Julia"):
        for ref in r_effects:
            # The reference has adjacent OR/RD blocks, so identify by within-measure order.
            same = [x for x in r_effects if x["measure"] == ref["measure"]]
            index = same.index(ref) + 1
            got = next(x for x in native[lang] if x["measure"] == ref["measure"] and x["kind"] == "effect" and int(x["row"]) == index)
            for field in ("yi", "vi"):
                checks.append((f"{lang} {ref['measure']} study {index} {field}", number(ref[field]), number(got[field]), TOLS["effect"]))
        for ref in r_models:
            got = next(x for x in native[lang] if x["measure"] == ref["measure"] and x["kind"] == "model" and x["method"] == ref["method"])
            for field in ("beta", "se", "tau2", "QE", "I2", "H2", "ci_lb", "ci_ub"):
                checks.append((f"{lang} {ref['measure']} {ref['method']} {field}", number(ref[field]), number(got[field]), TOLS["model"]))
        for ref in r_zero:
            got = next(x for x in native[lang + " zero"] if x["measure"] == ref["measure"] and x["method"] == ref["policy"] and int(x["row"]) == (1 if ref["study"] == "zero-cell" else 2))
            for field in ("yi", "vi"):
                checks.append((f"{lang} {ref['measure']} to={ref['policy']} {ref['study']} {field}", number(ref[field]), number(got[field]), TOLS["correction"]))
        scale = native[lang + " scale"]
        for index, (expected_y, expected_v) in enumerate(zip(rr_ref["yi"], rr_ref["vi"]), start=1):
            got = next(x for x in scale if x["measure"] == "RR" and x["kind"] == "effect" and int(x["row"]) == index)
            checks.extend(((f"{lang} RR study {index} yi", expected_y, number(got["yi"]), TOLS["effect"]),
                           (f"{lang} RR study {index} vi", expected_v, number(got["vi"]), TOLS["effect"])))
        for method, rkey in (("FE", "fe"), ("REML", "reml")):
            got = next(x for x in scale if x["measure"] == "RR" and x["kind"] == "model" and x["method"] == method)
            for field, rfield in (("beta", "beta"), ("se", "se"), ("tau2", "tau2"), ("QE", "QE"),
                                  ("I2", "I2"), ("H2", "H2"), ("ci_lb", "ci_lb"), ("ci_ub", "ci_ub")):
                checks.append((f"{lang} RR {method} {field}", rr_ref[rkey][rfield], number(got[field]), TOLS["model"]))
    failed = [(name, r, x, tol) for name, r, x, tol in checks if not close(r, x, tol)]
    if failed:
        raise SystemExit(f"{len(failed)} parity checks failed: {failed[:5]}")
    maximum = {"effect": 0.0, "model": 0.0, "correction": 0.0}
    for name, ref, got, tol in checks:
        cat = "model" if any(k in name for k in (" FE ", " REML ")) else "correction" if "to=" in name else "effect"
        if math.isfinite(ref) and math.isfinite(got):
            maximum[cat] = max(maximum[cat], abs(ref - got))
    body = "\n".join(f"<tr><th>{html.escape(k)}</th><td>{v:.3g}</td><td>≤ {TOLS[k]:.0e}</td></tr>" for k, v in maximum.items())
    OUT.write_text(f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Effect-size parity: R, Julia, Python</title><style>body{{font:16px/1.55 system-ui,sans-serif;max-width:900px;margin:3rem auto;padding:0 1rem;color:#18304a}}table{{border-collapse:collapse}}th,td{{padding:.55rem 1rem;border:1px solid #ccd5df;text-align:left}}.ok{{color:#14723a;font-weight:700}}</style><h1>Effect sizes: R, Julia, and Python</h1><p>Native results are compared with pinned R metafor 5.2-1 references. The BCG study counts are summarized as log risk ratios, log odds ratios, and risk differences. Hand-checkable tables exercise all four zero-cell policies.</p><p class="ok">PASS: {len(checks)} numeric comparisons passed their stated absolute and relative tolerances.</p><table><thead><tr><th>Result group</th><th>Maximum absolute difference</th><th>Tolerance</th></tr></thead><tbody>{body}</tbody></table><p>Open the <a href="https://itchyshin.github.io/metafor-py/">Python tutorials</a> or <a href="https://itchyshin.github.io/Metafor.jl/">Julia tutorials</a>. Model comparisons include FE and REML estimates, standard errors, heterogeneity summaries, and 95% normal intervals. The artifact reports numeric parity for these fixtures; it does not claim full metafor compatibility. Reference provenance and exact versions are recorded in each repository under <code>reference/effect-sizes/v1/</code>.</p><p>Rebuild with <code>python tools/compare_effect_sizes.py</code> after running `--case=all`, `--case=scale`, and `--case=zero-correction` in each native example script.</p></html>""")
    shutil.copy2(OUT, JULIA_ROOT / "examples/effect-size-comparison.html")
    print(f"EFFECT_SIZE_PARITY_OK checks={len(checks)} max={maximum} artifact={OUT}")


if __name__ == "__main__":
    main()
