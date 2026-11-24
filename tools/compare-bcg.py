"""Run the three BCG examples, check parity, and write a local HTML report."""
from html import escape
import argparse
import csv
import math
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--julia-root", type=Path, default=ROOT.parent / "Metafor.jl")
JULIA = parser.parse_args().julia_root.resolve()
ENV = dict(os.environ, OPENBLAS_NUM_THREADS="1", JULIA_NUM_THREADS="4")
commands = {
    "Python": ([str(ROOT / ".venv/bin/python"), str(ROOT / "examples/bcg.py")], ROOT),
    "Julia": (["julia", f"--project={JULIA}", str(JULIA / "examples/bcg.jl")], JULIA),
}

def run(command, cwd):
    completed = subprocess.run(command, cwd=cwd, env=ENV, text=True,
                               capture_output=True)
    if completed.returncode:
        raise RuntimeError(f"Command failed ({completed.returncode}): {command}\n{completed.stdout}\n{completed.stderr}")
    return completed.stdout, completed.stderr

def parse(output):
    result = {"effects": [], "models": {}, "covariances": {}, "covariance_labels": {}, "rows": {}, "designs": {},
              "predictions": [], "forest_summary": {}, "versions": {}}
    for line in output.splitlines():
        parts = line.split("|")
        if parts[0] == "VERSION":
            result["versions"][parts[1]] = parts[2]
        elif parts[0] == "EFFECT":
            result["effects"].append((int(parts[1]), float(parts[2]), float(parts[3])))
        elif parts[0] == "RESULT":
            fields = {}
            for pair in parts[2:]:
                key, raw = pair.split("=", 1)
                vals = [float(x) for x in raw.split(",")]
                fields[key] = vals if len(vals) > 1 else vals[0]
            result["models"][parts[1]] = fields
        elif parts[0] == "COV":
            result["covariances"][parts[1]] = [float(x) for x in parts[2].split(",")]
        elif parts[0] == "COVLABELS":
            result["covariance_labels"][parts[1]] = parts[2].split(",")
        elif parts[0] == "ROWS":
            result["rows"][parts[1]] = [int(x) for x in parts[2].split(",") if x]
        elif parts[0] == "DESIGN":
            result["designs"][parts[1]] = {
                "nrows": int(parts[2]), "ncols": int(parts[3]),
                "values": [float(x) for x in parts[4].split(",") if x],
            }
        elif parts[0] == "PRED":
            row = {"model": parts[1]}
            for pair in parts[2:]:
                key, raw = pair.split("=", 1)
                row[key] = float(raw)
            result["predictions"].append(row)
        elif parts[0] == "FOREST_SUMMARY":
            for pair in parts[1:]:
                key, raw = pair.split("=", 1)
                result["forest_summary"][key] = float(raw)
    if len(result["effects"]) != 13 or len(result["predictions"]) != 3:
        raise RuntimeError(f"Incomplete result stream:\n{output}")
    return result

reference = json.loads((ROOT / "reference/v1/bcg-reference.json").read_text())
if reference["versions"].get("metafor") != "5.2.1" or reference["versions"].get("metadat") != "1.6.0":
    raise RuntimeError(f"Pinned R reference version mismatch: {reference['versions']}")
model_keys = {"fixed": "fe", "random": "reml", "latitude": "moderator"}
def label_sequence(value):
    return [value] if isinstance(value, str) else list(value)

r = {"effects": list(zip(range(1,14),reference["yi"],reference["vi"])),
     "models": {name: reference[key] for name,key in model_keys.items()},
     "covariances": {name:[value for row in reference[key]["vcov"] for value in row] for name,key in model_keys.items()},
     "covariance_labels": {name: label_sequence(reference["design_columns"][ref_key]) for name,ref_key in
                           (("fixed","FE"),("random","REML"),("latitude","moderator"))},
     "rows": {name:reference[key]["row_indices"] for name,key in model_keys.items()},
     "designs": {name:{"nrows":len(reference["design"][ref_key]),
                       "ncols":len(reference["design"][ref_key][0]),
                       "values":[value for row in reference["design"][ref_key] for value in row]}
                 for name,ref_key in (("fixed","FE"),("random","REML"),("latitude","moderator"))},
     "predictions": [{"model":"latitude","x":x,
                      **{out_key:reference["prediction"][ref_key][i] for out_key,ref_key in
                         (("estimate","pred"),("se","se"),("ci_lb","ci_lb"),("ci_ub","ci_ub"),("pi_lb","pi_lb"),("pi_ub","pi_ub"))}}
                     for i,x in enumerate(reference["prediction"]["latitude"])],
     "forest_summary": reference["forest"]["summary"]}
outputs = {"R": r, **{name: parse(run(command, cwd)[0]) for name, (command, cwd) in commands.items()}}
shutil.copyfile(JULIA / "examples/bcg-forest.svg", ROOT / "examples/bcg-forest-julia.svg")
py, jl = outputs["Python"], outputs["Julia"]
limits = {"yi": (1e-12, 1e-10), "vi": (1e-12, 1e-10),
          "beta": (2e-6, 1e-5), "se": (2e-6, 1e-5),
          "ci_lb": (2e-6, 1e-5), "ci_ub": (2e-6, 1e-5),
          "pi_lb": (2e-6, 1e-5), "pi_ub": (2e-6, 1e-5),
          "estimate": (2e-6, 1e-5), "tau2": (2e-6, 1e-5),
          "QE": (2e-5, 1e-5), "I2": (2e-5, 1e-5), "H2": (2e-5, 1e-5),
          "covariance": (1e-12,1e-10), "design": (1e-12,1e-10)}
errors = {key: [] for key in limits}

def seq(x):
    return x if isinstance(x, list) else [x]

def compare(field, ref, value, context, tolerance=None):
    a, b = seq(ref), seq(value)
    if len(a) != len(b):
        raise RuntimeError(f"{context}: different vector lengths")
    atol, rtol = tolerance or limits[field]
    for i, (x, y) in enumerate(zip(a, b)):
        error = abs(x-y)
        if not error <= atol + rtol*abs(x):
            raise RuntimeError(f"{context}[{i}]: R={x:.16g}, port={y:.16g}, abs error={error:.3g}")
        errors[field].append(error)

def reject_if_bad_coordinates(row, expected_row, expected_label):
    if int(row["row"]) != expected_row or row["label"] != expected_label:
        raise RuntimeError("forest row identity or label differs")

def reject_if_bad_covariance_labels(actual, expected):
    if actual != expected:
        raise RuntimeError(f"coefficient covariance labels/order differs: {actual} != {expected}")

try:
    compare("beta", 0.0, 1.0, "deliberate comparator self-test", (0.0,0.0))
except RuntimeError:
    pass
else:
    raise RuntimeError("comparator accepted a deliberately perturbed coefficient")
try:
    reject_if_bad_coordinates({"row":1,"label":"wrong"},1,"expected")
except RuntimeError:
    pass
else:
    raise RuntimeError("comparator accepted a deliberately perturbed forest label")
try:
    reject_if_bad_covariance_labels(["ablat", "intrcpt"], ["intrcpt", "ablat"])
except RuntimeError:
    pass
else:
    raise RuntimeError("comparator accepted deliberately permuted covariance labels")

for language, port in (("Python", py), ("Julia", jl)):
    for i, row in enumerate(r["effects"]):
        if port["effects"][i][0] != row[0]:
            raise RuntimeError(f"{language}: study row order differs")
        compare("yi", row[1], port["effects"][i][1], f"{language} row {i+1} yi")
        compare("vi", row[2], port["effects"][i][2], f"{language} row {i+1} vi")
    for model in ("fixed", "random", "latitude"):
        reject_if_bad_covariance_labels(port["covariance_labels"][model], r["covariance_labels"][model])
        if port["rows"][model] != r["rows"][model]:
            raise RuntimeError(f"{language} {model}: row indices differ")
        expected_design, actual_design = r["designs"][model], port["designs"][model]
        if (actual_design["nrows"],actual_design["ncols"]) != (expected_design["nrows"],expected_design["ncols"]):
            raise RuntimeError(f"{language} {model}: design matrix dimensions differ")
        compare("design", expected_design["values"], actual_design["values"], f"{language} {model} design")
        for field in ("beta", "se", "ci_lb", "ci_ub", "tau2", "QE", "I2", "H2"):
            tolerance = (1e-12, 1e-10) if model == "fixed" else None
            compare(field, r["models"][model][field], port["models"][model][field], f"{language} {model} {field}", tolerance)
        compare("covariance", r["covariances"][model], port["covariances"][model],
                f"{language} {model} coefficient covariance", (1e-12,1e-10))
    for i, (ref, got) in enumerate(zip(r["predictions"], port["predictions"])):
        if ref["model"] != got["model"] or ref["x"] != got["x"]:
            raise RuntimeError(f"{language}: prediction labels/order differ at row {i}")
        for field in ("estimate", "se", "ci_lb", "ci_ub", "pi_lb", "pi_ub"):
            compare(field, ref[field], got[field], f"{language} prediction {i} {field}")

frozen_forest = reference["forest"]
frozen_forest_rows = [
    {"row":frozen_forest["row"][i],"label":frozen_forest["label"][i],
     **{field:frozen_forest[field][i] for field in ("estimate","se","ci_lb","ci_ub")}}
    for i in range(len(frozen_forest["row"]))
]
py_forest = json.loads((ROOT / "examples/bcg-forest-data.json").read_text())
with (JULIA / "examples/bcg-forest-data.csv").open(newline="") as handle:
    jl_rows = list(csv.DictReader(handle))
for language, rows in (("Python", py_forest["rows"]), ("Julia", [row for row in jl_rows if row["row"] != "pooled"])):
    if len(rows) != 13:
        raise RuntimeError(f"{language}: forest data should contain 13 study rows")
    for index, (row, frozen) in enumerate(zip(rows, frozen_forest_rows), start=1):
        reject_if_bad_coordinates(row,index,frozen["label"])
        for field in ("estimate","se","ci_lb","ci_ub"):
            compare(field, frozen[field], float(row[field]), f"{language} forest row {index} {field}", (1e-9,1e-10))
py_summary = py_forest["summary"]
jl_summary = next(row for row in jl_rows if row["row"] == "pooled")
for field in ("estimate","se","ci_lb","ci_ub","pi_lb","pi_ub","tau2"):
    compare(field, r["forest_summary"][field], float(py_summary[field]), f"Python forest summary {field}")
    compare(field, r["forest_summary"][field], float(jl_summary[field]), f"Julia forest summary {field}")

def fmt(v):
    if isinstance(v, list):
        return ", ".join(f"{x:.8g}" for x in v)
    return f"{v:.8g}"

model_html = []
for model in ("fixed", "random", "latitude"):
    for field in ("beta", "se", "ci_lb", "ci_ub", "tau2", "QE", "I2", "H2"):
        vals = [outputs[name]["models"][model][field] for name in ("R", "Python", "Julia")]
        model_html.append("<tr><th>{}</th><td>{}</td>{}</tr>".format(model, field,
            "".join(f"<td>{escape(fmt(v))}</td>" for v in vals)))
effects_html = []
for i, (row, yi, vi) in enumerate(r["effects"]):
    effects_html.append(f"<tr><th>{row}</th><td>{fmt(yi)}</td><td>{fmt(py['effects'][i][1])}</td><td>{fmt(jl['effects'][i][1])}</td><td>{fmt(vi)}</td><td>{fmt(py['effects'][i][2])}</td><td>{fmt(jl['effects'][i][2])}</td></tr>")
prediction_html = []
for i, latitude in enumerate((0, 30, 60)):
    for field in ("estimate", "se", "ci_lb", "ci_ub", "pi_lb", "pi_ub"):
        values = [outputs[name]["predictions"][i][field] for name in ("R", "Python", "Julia")]
        prediction_html.append(f"<tr><th>{latitude}</th><td>{field}</td>" + "".join(f"<td>{fmt(x)}</td>" for x in values) + "</tr>")
error_html = "".join(f"<tr><th>{k}</th><td>{max(v, default=0):.3g}</td></tr>" for k,v in sorted(errors.items()) if v)
plots = "".join((ROOT / f"examples/bcg-forest{'-julia' if i else ''}.svg").read_text() for i in range(2))
report = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>BCG parity across R, Python and Julia</title><style>body{{font:15px/1.45 system-ui;max-width:1120px;margin:2rem auto;padding:0 1rem;color:#172b3a}}table{{border-collapse:collapse;width:100%;margin:1rem 0 2rem}}th,td{{padding:.45rem;border-bottom:1px solid #ccd6dc;text-align:right}}th:first-child,td:nth-child(2){{text-align:left}}thead{{background:#eef4f5}}svg{{width:49%;height:auto;border:1px solid #d5dfe4}}code{{background:#eef4f5;padding:.1rem .3rem}}</style><h1>BCG parity across R, Python and Julia</h1><p>Each program reads the same 13-study raw-count fixture. This page is written after all effect sizes, model coefficients, standard errors, confidence intervals, heterogeneity statistics and moderator prediction intervals pass the field tolerances below.</p><p>Effect sizes: <code>1e-12 + 1e-10 × |R|</code>. Estimates, intervals and variance components: <code>2e-6 + 1e-5 × |R|</code>. Heterogeneity: <code>2e-5 + 1e-5 × |R|</code>.</p><h2>Effect sizes</h2><table><thead><tr><th>Row</th><th>R yi</th><th>Python yi</th><th>Julia yi</th><th>R vi</th><th>Python vi</th><th>Julia vi</th></tr></thead><tbody>{''.join(effects_html)}</tbody></table><h2>Models and heterogeneity</h2><table><thead><tr><th>Model</th><th>Quantity</th><th>R metafor 5.2-1</th><th>Python</th><th>Julia</th></tr></thead><tbody>{''.join(model_html)}</tbody></table><h2>Latitude predictions</h2><table><thead><tr><th>Latitude</th><th>Quantity</th><th>R</th><th>Python</th><th>Julia</th></tr></thead><tbody>{''.join(prediction_html)}</tbody></table><h2>Original forest plots</h2><p>Study points and confidence intervals are shown on the log-risk-ratio scale. The summary diamond shows the REML mean confidence interval; dashed limits show the new-study prediction interval.</p>{plots}<h2>Maximum absolute errors</h2><table><thead><tr><th>Field</th><th>Error</th></tr></thead><tbody>{error_html}</tbody></table><p>Data provenance and original teaching question: <a href="https://wviechtb.github.io/metadat/reference/dat.bcg.html">metadat BCG example</a>. This page uses original prose and plots and is a local artifact.</p></html>'''
out = ROOT / "examples/bcg-comparison.html"
out.write_text(report, encoding="utf-8")
print(f"BCG_THREE_LANGUAGE_HTML_VERIFIED {out}")
print("COMPARATOR_FAILURE_CONTROLS_OK coefficient forest covariance-label permutation")
print("MAX_ABS_ERRORS " + json.dumps({k: max(v,default=0) for k,v in errors.items()}, sort_keys=True))
