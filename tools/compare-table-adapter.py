"""Check BCG table/formula adapters against the same native design matrix."""
from argparse import ArgumentParser
from html import escape
import math
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).parents[1]
parser = ArgumentParser(description=__doc__)
parser.add_argument("--julia-root", type=Path, default=ROOT.parent / "Metafor.jl")
JULIA_ROOT = parser.parse_args().julia_root.resolve()
ENV = dict(os.environ, OPENBLAS_NUM_THREADS="1", JULIA_NUM_THREADS="1")


def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, env=ENV, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {command}\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout


def parse(output):
    values = {}
    for line in output.splitlines():
        if line == "TABLE_ADAPTER_OK":
            values["ok"] = True
        elif line.startswith("TABLE_ADAPTER|"):
            _, key, value = line.split("|", 2)
            values[key] = value
    required = {"ok", "design_columns", "row_ids", "design_shape", "design_values", "beta", "matrix_max_abs_diff"}
    if not required <= values.keys():
        raise RuntimeError(f"Incomplete adapter output; missing {sorted(required-values.keys())}:\n{output}")
    return values


commands = {
    "Python": ([str(ROOT / ".venv/bin/python"), str(ROOT / "examples/bcg.py"), "--case=table-adapter"], ROOT),
    "Julia": (["julia", f"--project={JULIA_ROOT}", str(JULIA_ROOT / "examples/bcg.jl"), "--case=table-adapter"], JULIA_ROOT),
}
outputs = {language: parse(run(command, cwd)) for language, (command, cwd) in commands.items()}
py, jl = outputs["Python"], outputs["Julia"]

for language, result in outputs.items():
    if result["row_ids"] != "1,2,3,5,6,7,8,9,10,11,12,13":
        raise RuntimeError(f"{language}: retained trial IDs changed: {result['row_ids']}")
    if result["design_shape"] != "12,2":
        raise RuntimeError(f"{language}: expected a 12 by 2 design, got {result['design_shape']}")
    if float(result["matrix_max_abs_diff"]) > 1e-12:
        raise RuntimeError(f"{language}: formula and matrix fits differ by {result['matrix_max_abs_diff']}")

if py["design_values"] != jl["design_values"]:
    py_values = [float(x) for x in py["design_values"].split(",")]
    jl_values = [float(x) for x in jl["design_values"].split(",")]
    if len(py_values) != len(jl_values) or any(
        not math.isclose(a, b, rel_tol=0, abs_tol=1e-12)
        for a, b in zip(py_values, jl_values)
    ):
        raise RuntimeError("Python and Julia numeric design matrices differ")

py_beta = [float(x) for x in py["beta"].split(",")]
jl_beta = [float(x) for x in jl["beta"].split(",")]
if len(py_beta) != len(jl_beta) or any(
    not math.isclose(a, b, rel_tol=1e-8, abs_tol=1e-8)
    for a, b in zip(py_beta, jl_beta)
):
    raise RuntimeError(f"Python and Julia estimates differ: {py_beta} vs {jl_beta}")

max_beta_diff = max(abs(a - b) for a, b in zip(py_beta, jl_beta))
html = f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>BCG formula adapter parity</title>
<style>body{{font:16px/1.55 system-ui,sans-serif;max-width:900px;margin:3rem auto;padding:0 1rem;color:#18304a}}table{{border-collapse:collapse}}th,td{{padding:.55rem 1rem;border:1px solid #ccd5df;text-align:left}}.ok{{color:#14723a;font-weight:700}}</style>
<h1>Formula adapters preserve the BCG design</h1>
<p>The Python/Patsy and Julia/StatsModels adapters fit the same BCG log risk ratios with latitude as a moderator. Trial 4 has a missing latitude in this example.</p>
<p class="ok">PASS: both adapters retain the same 12 trials, produce the same 12 × 2 numeric design, and match their matrix fits within 1e-12.</p>
<table><thead><tr><th>Check</th><th>Python</th><th>Julia</th></tr></thead><tbody>
<tr><th>Retained trial IDs</th><td>{escape(py['row_ids'])}</td><td>{escape(jl['row_ids'])}</td></tr>
<tr><th>Design shape</th><td>{escape(py['design_shape'])}</td><td>{escape(jl['design_shape'])}</td></tr>
<tr><th>Design columns</th><td>{escape(py['design_columns'])}</td><td>{escape(jl['design_columns'])}</td></tr>
<tr><th>Formula estimates</th><td>{escape(py['beta'])}</td><td>{escape(jl['beta'])}</td></tr>
<tr><th>Largest cross-language coefficient difference</th><td colspan="2">{max_beta_diff:.3g} (allowed: 1e-8 absolute or relative)</td></tr>
</tbody></table>
<p>The intercept column label follows each language's formula package. The numeric design and estimate ordering are compared directly. This fixture does not establish complete R formula compatibility.</p>
<p><a href="https://itchyshin.github.io/metafor-py/">Python tutorials</a> · <a href="https://itchyshin.github.io/Metafor.jl/">Julia tutorials</a></p>
</html>
"""
OUT = ROOT / "examples/table-adapter-comparison.html"
OUT.write_text(html)
shutil.copy2(OUT, JULIA_ROOT / "examples/table-adapter-comparison.html")
print(f"TABLE_ADAPTER_PARITY_OK design_values=24 beta={len(py_beta)} max_abs_beta={max_beta_diff:.3g} artifact={OUT}")
