"""Compare boundary and interior supplied-correlation fits across R and both ports."""
from html import escape
import argparse
import os
from pathlib import Path
import subprocess
import csv
import math
import shutil

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
colors = {"R": "#315caa", "Python": "#d36b25", "Julia": "#16836b"}
xmin, xmax, left, width = -1.6, 1.5, 100, 650
def xpos(value):
    return left + (value - xmin) * width / (xmax - xmin)

svg_parts = [f'<svg role="img" aria-labelledby="plot-title plot-desc" viewBox="0 0 820 252"><title id="plot-title">Phylogenetic model estimates and intervals</title><desc id="plot-desc">R, Python, and Julia coefficient estimates with 95 percent normal intervals for boundary and interior synthetic fixtures.</desc>']
zero_x = xpos(0)
svg_parts.append(f'<line x1="{zero_x:.1f}" y1="22" x2="{zero_x:.1f}" y2="224" stroke="#8997a8" stroke-dasharray="4 4"/><text x="{zero_x+5:.1f}" y="18" fill="#46566b">zero</text>')
for k, tick in enumerate((-1.5, -1, -0.5, 0, 0.5, 1, 1.5)):
    x = xpos(tick)
    svg_parts.append(f'<line x1="{x:.1f}" y1="224" x2="{x:.1f}" y2="229" stroke="#45556a"/><text x="{x:.1f}" y="246" text-anchor="middle" fill="#45556a">{tick:g}</text>')
for case_i, case in enumerate(("v1", "v2-interior")):
    base_y = 50 + case_i * 100
    svg_parts.append(f'<text x="12" y="{base_y-15}" font-weight="700" fill="#1b3049">{"Boundary" if case == "v1" else "Interior"}</text>')
    for i, name in enumerate(("R", "Python", "Julia")):
        result = fits[name][case]
        y = base_y + i * 22
        x1, x2, point = xpos(result["ci_lb"]), xpos(result["ci_ub"]), xpos(result["beta"])
        color = colors[name]
        svg_parts.append(f'<text x="12" y="{y+4}" fill="{color}">{name}</text><line x1="{x1:.2f}" y1="{y}" x2="{x2:.2f}" y2="{y}" stroke="{color}" stroke-width="2.5"/><circle cx="{point:.2f}" cy="{y}" r="4" fill="{color}"/>')
svg_parts.append('<text x="425" y="251" text-anchor="middle" fill="#34445a">Mean effect and 95% normal interval</text></svg>')
plot = "".join(svg_parts)

matrix_rows = []
with (ROOT / "reference/phylogeny/v2-interior/species-correlation.csv").open(newline="") as handle:
    matrix = list(csv.reader(handle))
labels = matrix[0][1:]
for row in matrix[1:]:
    cells = "".join(f'<td style="background:rgba(40,112,145,{max(.12,float(value)):.2f})">{float(value):.1f}</td>' for value in row[1:])
    matrix_rows.append(f"<tr><th>{escape(row[0])}</th>{cells}</tr>")
matrix_table = "<table class=matrix><thead><tr><th>Species</th>" + "".join(f"<th>{escape(label)}</th>" for label in labels) + "</tr></thead><tbody>" + "".join(matrix_rows) + "</tbody></table>"

html = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Phylogenetic parity</title><style>body{font:16px/1.55 system-ui,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;color:#172b3a}table{border-collapse:collapse;width:100%;margin:1rem 0}th,td{padding:.5rem;border-bottom:1px solid #ccd6dc;text-align:right}th:first-child,td:nth-child(2){text-align:left}thead{background:#eef4f5}svg{width:100%;height:auto;background:#fbfcfd;border:1px solid #d6dfe7;border-radius:8px}.matrix{max-width:480px}.matrix td,.matrix th{text-align:center}.matrix td{font-variant-numeric:tabular-nums}</style><h1>Supplied-correlation phylogenetic fits</h1><p>Both ports and the pinned R reference fit a species random intercept with a supplied labelled correlation matrix and diagonal sampling variances. The first fixture estimates a boundary variance; the second estimates an interior species variance. The inputs and R references are synthetic and versioned beside each fixture.</p><p>Tolerance for every displayed quantity: 1e-5 + 1e-4 × |R|.</p><h2>Coefficient estimates and intervals</h2>""" + plot + """<h2>Supplied species correlation</h2><p>The same labelled matrix is used in both synthetic cases. Cell shading increases with correlation.</p>""" + matrix_table + """<h2>Numerical comparison</h2><table><thead><tr><th>Fixture</th><th>Quantity</th><th>R metafor 5.2-1</th><th>Python</th><th>Julia</th></tr></thead><tbody>""" + "".join(rows) + """</tbody></table><p>Fixture provenance and generation scripts are in <code>reference/phylogeny/v1</code> and <code>reference/phylogeny/v2-interior</code>. Open the <a href="https://itchyshin.github.io/metafor-py/">Python tutorials</a> or <a href="https://itchyshin.github.io/Metafor.jl/">Julia tutorials</a>. These results demonstrate fixture-level numerical agreement and do not estimate a tree or claim a biological effect.</p></html>"""
out = ROOT / "examples/phylogeny-comparison.html"
out.write_text(html, encoding="utf-8")
shutil.copy2(out, JULIA / "examples/phylogeny-comparison.html")
print(f"PHYLOGENY_THREE_LANGUAGE_HTML_VERIFIED {out}")
print(f"MAX_ABS_ERRORS {errors}")
