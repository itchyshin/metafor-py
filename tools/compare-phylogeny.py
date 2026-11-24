"""Compare boundary and interior supplied-correlation fits across R and both ports."""
from html import escape
import argparse
import os
from pathlib import Path
import subprocess
import csv
import math

ROOT = Path(__file__).parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--julia-root", type=Path, default=ROOT.parent / "Metafor.jl")
JULIA = parser.parse_args().julia_root.resolve()
ENV = dict(os.environ, OPENBLAS_NUM_THREADS="1", JULIA_NUM_THREADS="4")
commands = {
    "Python": ([str(ROOT / ".venv/bin/python"), str(ROOT / "examples/phylogeny.py")], ROOT),
    "Julia": (["julia", f"--project={JULIA}", str(JULIA / "examples/phylogeny.jl")], JULIA),
}

def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, env=ENV, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {command}\n{result.stdout}\n{result.stderr}")
    if result.stderr.strip():
        raise RuntimeError(f"Unexpected stderr from {command}:\n{result.stderr}")
    return result.stdout

def parse(output):
    fits = {}
    for line in output.splitlines():
        if not line.startswith("PHYLO|"):
            continue
        _, case, *fields = line.split("|")
        fits[case] = {key: float(value) for key, value in (field.split("=", 1) for field in fields)}
    if set(fits) != {"v1", "v2-interior"}:
        raise RuntimeError(f"Expected boundary and interior fits; output was:\n{output}")
    return fits

native = {name: parse(run(command, cwd)) for name, (command, cwd) in commands.items()}
fits = {"Python":native["Python"],"Julia":native["Julia"],"R":{}}
for case in ("v1","v2-interior"):
    with (ROOT / "reference/phylogeny" / case / "reference.csv").open(newline="") as handle:
        ref = next(csv.DictReader(handle))
    beta,se,tau2 = float(ref["beta"]),float(ref["se"]),float(ref["tau2"])
    fits["R"][case] = {
        "beta":beta,"se":se,"tau2":tau2,
        "ci_lb":float(ref.get("ci_lb") or beta-1.959963984540054*se),
        "ci_ub":float(ref.get("ci_ub") or beta+1.959963984540054*se),
    }
limits = {"beta": (1e-5,1e-4), "se": (1e-5,1e-4), "tau2": (1e-5,1e-4),
          "ci_lb": (1e-5,1e-4), "ci_ub": (1e-5,1e-4)}
errors = {}
for case in ("v1","v2-interior"):
    for field, (atol,rtol) in limits.items():
        ref = fits["R"][case][field]
        values = {name: fits[name][case][field] for name in ("Python","Julia")}
        errors[f"{case}.{field}"] = {name: abs(value-ref) for name,value in values.items()}
        for name,value in values.items():
            if not abs(value-ref) <= atol + rtol*abs(ref):
                raise RuntimeError(f"{case} {field} {name}: R={ref:.16g}, port={value:.16g}")

rows = []
for case in ("v1","v2-interior"):
    for field in limits:
        values = [fits[name][case][field] for name in ("R","Python","Julia")]
        rows.append(f"<tr><th>{escape(case)}</th><td>{field}</td>" +
                    "".join(f"<td>{value:.10g}</td>" for value in values) + "</tr>")
html = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Phylogenetic parity</title><style>body{font:15px/1.5 system-ui;max-width:900px;margin:2rem auto;padding:0 1rem;color:#172b3a}table{border-collapse:collapse;width:100%;margin:1rem 0}th,td{padding:.5rem;border-bottom:1px solid #ccd6dc;text-align:right}th:first-child,td:nth-child(2){text-align:left}thead{background:#eef4f5}</style><h1>Supplied-correlation phylogenetic fits</h1><p>Both ports and the pinned R reference fit a species random intercept with a supplied labelled correlation matrix and diagonal sampling variances. The first row is a zero-boundary case; the second has an interior species variance component. Inputs and R reference are synthetic and versioned beside each fixture.</p><p>Tolerance for every displayed quantity: 1e-5 + 1e-4 × |R|.</p><table><thead><tr><th>Fixture</th><th>Quantity</th><th>R metafor 5.2-1</th><th>Python</th><th>Julia</th></tr></thead><tbody>""" + "".join(rows) + """</tbody></table><p>Fixture provenance and generation scripts are in <code>reference/phylogeny/v1</code> and <code>reference/phylogeny/v2-interior</code>.</p></html>"""
out = ROOT / "examples/phylogeny-comparison.html"
out.write_text(html, encoding="utf-8")
print(f"PHYLOGENY_THREE_LANGUAGE_HTML_VERIFIED {out}")
print(f"MAX_ABS_ERRORS {errors}")
