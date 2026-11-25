"""Run BCG odds-ratio, risk-difference, and zero-cell examples."""
import argparse
import csv
from pathlib import Path

import numpy as np

from metafor import escalc_or, escalc_rd, escalc_rr, fit_meta

ROOT = Path(__file__).parents[1]
FIELDS = ("measure", "kind", "method", "row", "author", "yi", "vi", "beta", "se",
          "tau2", "QE", "I2", "H2", "ci_lb", "ci_ub")


def record(measure, kind, *, method="", row="", author="", yi="", vi="", **values):
    return {"measure": measure, "kind": kind, "method": method, "row": row,
            "author": author, "yi": yi, "vi": vi,
            **{name: values.get(name, "") for name in FIELDS[7:]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("all", "odds-ratio", "risk-difference", "scale", "zero-correction"), default="all")
    args = parser.parse_args()
    with (ROOT / "reference/v1/bcg.csv").open(newline="") as stream:
        data = list(csv.DictReader(stream))
    counts = {name: np.asarray([float(row[name]) for row in data])
              for name in ("tpos", "tneg", "cpos", "cneg")}
    functions = {"OR": escalc_or, "RD": escalc_rd, "RR": escalc_rr}
    selected = {"odds-ratio": ("OR",), "risk-difference": ("RD",),
                "scale": ("RR", "OR", "RD"), "all": ("OR", "RD")}
    rows = []

    if args.case == "zero-correction":
        values = {"a": [0, 2], "b": [10, 8], "c": [2, 3], "d": [8, 7]}
        for measure in ("OR", "RD"):
            for policy in ("only0", "all", "if0all", "none"):
                yi, vi = functions[measure](values["a"], values["b"], values["c"], values["d"], to=policy)
                rows.extend(record(measure, "correction", method=policy, row=i + 1,
                                   yi=float(effect), vi=float(variance))
                            for i, (effect, variance) in enumerate(zip(yi, vi)))
    else:
        for measure in selected[args.case]:
            yi, vi = functions[measure](counts["tpos"], counts["tneg"], counts["cpos"], counts["cneg"])
            for index, (effect, variance) in enumerate(zip(yi, vi), start=1):
                rows.append(record(measure, "effect", row=index, author=data[index - 1]["author"],
                                   yi=float(effect), vi=float(variance)))
            for method in ("FE", "REML"):
                fit = fit_meta(yi, vi, method=method)
                lower, upper = fit.interval()
                rows.append(record(measure, "model", method=method,
                                   beta=float(fit.beta[0]), se=float(fit.se[0]),
                                   tau2=float(fit.tau2), QE=float(fit.q), I2=float(fit.i2),
                                   H2=float(fit.h2), ci_lb=float(lower[0]), ci_ub=float(upper[0])))

    result = ROOT / "examples/generated/effect-sizes" / f"python-{args.case}.csv"
    result.parent.mkdir(parents=True, exist_ok=True)
    with result.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    if not rows or not result.stat().st_size:
        raise RuntimeError("effect-size example produced no results")
    print(f"EFFECT_SIZE_EXAMPLE_OK case={args.case} rows={len(rows)} {result}")


if __name__ == "__main__":
    main()
