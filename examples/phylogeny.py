"""Fit boundary and interior synthetic phylogenetic examples."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
from metafor import fit_phylo

ROOT = Path(__file__).parents[1]
parser = argparse.ArgumentParser(description="Run a supplied-correlation phylogenetic fixture.")
parser.add_argument("--case", choices=("all", "boundary", "interior"), default="all")
case_arg = parser.parse_args().case
case_for_fixture = {"boundary": "v1", "interior": "v2-interior"}
results = {}
fixtures = ("v1", "v2-interior") if case_arg == "all" else (case_for_fixture[case_arg],)
for case in fixtures:
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
out = (
    ROOT / "examples/phylogeny-results.json"
    if case_arg == "all"
    else ROOT / "examples/generated/phylogeny" / f"{case_arg}-results.json"
)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print(f"PHYLOGENY_EXAMPLE_OK {out}")
