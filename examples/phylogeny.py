"""Fit boundary and interior synthetic phylogenetic examples."""
import csv
import json
from pathlib import Path
import numpy as np
from metafor import fit_phylo

ROOT = Path(__file__).parents[1]
results = {}
for case in ("v1", "v2-interior"):
    base = ROOT / "reference/phylogeny" / case
    observations = list(csv.DictReader((base / "observations.csv").open()))
    matrix_rows = list(csv.reader((base / "species-correlation.csv").open(newline="")))
    labels = matrix_rows[0][1:]
    if [row[0] for row in matrix_rows[1:]] != labels:
        raise ValueError("correlation matrix row and column labels must match")
    A = np.asarray([[float(x) for x in row[1:]] for row in matrix_rows[1:]])
    fit = fit_phylo([float(r["yi"]) for r in observations],
                    [float(r["vi"]) for r in observations],
                    [r["species"] for r in observations], A, labels)
    low, high = fit.interval()
    results[case] = {"beta": float(fit.beta[0]), "se": float(fit.se[0]),
                     "tau2": float(fit.tau2), "ci_lb": float(low[0]),
                     "ci_ub": float(high[0])}
    values = results[case]
    print("PHYLO|{}|beta={:.16g}|se={:.16g}|tau2={:.16g}|ci_lb={:.16g}|ci_ub={:.16g}".format(
        case, values["beta"], values["se"], values["tau2"], values["ci_lb"], values["ci_ub"]))
out = ROOT / "examples/phylogeny-results.json"
out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print(f"PHYLOGENY_EXAMPLE_OK {out}")
