#!/usr/bin/env python3
"""Run both native demos and write their pinned-R comparison as local HTML."""
import argparse
import csv
import html
from pathlib import Path
import re
import shutil
import subprocess
import sys


REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "reference" / "dependent" / "v1"
EXAMPLES = REPO / "examples"


def read_values(path, key_fields):
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    values = {}
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        if key in values:
            raise ValueError(f"duplicate result key in {path}: {key}")
        values[key] = float(row["estimate"])
    return values


def tolerance(key, covariance=False):
    if covariance:
        return 1e-7, 1e-5
    quantity = key[1]
    if quantity == "QEp":
        return 1e-24, 5e-4
    if quantity in ("variance", "covariance", "correlation"):
        return 1e-6, 1e-4
    return 1e-6, 1e-5


def compare(reference, python, julia, covariance=False):
    if set(reference) != set(python) or set(reference) != set(julia):
        missing_python = sorted(set(reference) - set(python))
        extra_python = sorted(set(python) - set(reference))
        missing_julia = sorted(set(reference) - set(julia))
        extra_julia = sorted(set(julia) - set(reference))
        raise ValueError(
            "result keys differ; "
            f"Python missing={missing_python}, extra={extra_python}; "
            f"Julia missing={missing_julia}, extra={extra_julia}"
        )
    rows = []
    for key in sorted(reference):
        ref = reference[key]
        py = python[key]
        jl = julia[key]
        atol, rtol = tolerance(key, covariance)
        limit = atol + rtol * abs(ref)
        py_error = abs(py - ref)
        jl_error = abs(jl - ref)
        rows.append((key, ref, py, jl, max(py_error, jl_error), limit,
                     py_error <= limit and jl_error <= limit))
    return rows


def render_table(title, rows, key_names):
    head = "".join(f"<th>{html.escape(name)}</th>" for name in key_names)
    body = []
    for key, ref, py, jl, error, limit, passed in rows:
        cells = "".join(f"<td>{html.escape(value)}</td>" for value in key)
        status = "PASS" if passed else "FAIL"
        body.append(
            f"<tr><td>{cells}</td><td>{ref:.12g}</td><td>{py:.12g}</td>"
            f"<td>{jl:.12g}</td><td>{error:.3g}</td><td>{limit:.3g}</td>"
            f"<td class='{status.lower()}'>{status}</td></tr>"
        )
    return (
        f"<h2>{html.escape(title)}</h2><div class='table-wrap'><table>"
        f"<thead><tr><th colspan='{len(key_names)}'>Result</th>"
        f"<th>R 5.2-1</th><th>Python</th><th>Julia</th><th>Max abs error</th>"
        f"<th>Allowed</th><th>Status</th></tr><tr>{head}</tr></thead>"
        f"<tbody>{''.join(body)}</tbody></table></div>"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--julia-repo", type=Path,
        default=REPO.parent / "Metafor.jl",
        help="Metafor.jl checkout (default: sibling directory ../Metafor.jl)",
    )
    parser.add_argument(
        "--output", type=Path, default=EXAMPLES / "dependent-comparison.html"
    )
    args = parser.parse_args()
    julia = shutil.which("julia")
    if julia is None:
        raise SystemExit("julia executable was not found on PATH")
    julia_repo = args.julia_repo.resolve()
    if not (julia_repo / "Project.toml").is_file():
        raise SystemExit(f"Julia project not found: {julia_repo}")
    EXAMPLES.mkdir(parents=True, exist_ok=True)
    py_results = EXAMPLES / "dependent-python-results.csv"
    py_covariance = EXAMPLES / "dependent-python-covariance.csv"
    jl_results = EXAMPLES / "dependent-julia-results.csv"
    jl_covariance = EXAMPLES / "dependent-julia-covariance.csv"
    subprocess.run(
        [sys.executable, str(EXAMPLES / "dependent.py"),
         "--output", str(py_results), "--covariance-output", str(py_covariance)],
        cwd=REPO, check=True,
    )
    subprocess.run(
        [julia, f"--project={julia_repo}", str(julia_repo / "examples" / "dependent.jl"),
         "--output", str(jl_results), "--covariance-output", str(jl_covariance)],
        cwd=julia_repo, check=True,
    )
    estimates = compare(
        read_values(FIXTURE / "results.csv", ("model", "quantity", "name")),
        read_values(py_results, ("model", "quantity", "name")),
        read_values(jl_results, ("model", "quantity", "name")),
    )
    covariances = compare(
        read_values(FIXTURE / "coefficient-covariance.csv", ("model", "row", "column")),
        read_values(py_covariance, ("model", "row", "column")),
        read_values(jl_covariance, ("model", "row", "column")),
        covariance=True,
    )
    total = len(estimates) + len(covariances)
    passed = sum(row[-1] for row in estimates) + sum(row[-1] for row in covariances)
    versions = (FIXTURE / "REFERENCE-VERSIONS.txt").read_text()
    source = (FIXTURE / "PROVENANCE.md").read_text()
    source_sha = next(
        token.strip("`.,") for token in source.split()
        if re.fullmatch(r"[0-9a-f]{64}", token.strip("`.,"))
    )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Dependent-effects parity</title><style>
body{{font:16px/1.5 system-ui,sans-serif;max-width:1280px;margin:2rem auto;padding:0 1rem;color:#17212b}}
h1,h2{{line-height:1.2}}.summary{{padding:1rem;background:#eef6f5;border-left:4px solid #17806d}}
.meta{{color:#425466;font-size:.94rem}}.table-wrap{{overflow-x:auto;margin:1rem 0 2rem}}
table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums;white-space:nowrap}}
th,td{{border-bottom:1px solid #d9e0e5;padding:.45rem .6rem;text-align:right}}
th{{background:#f4f7f8}}td:first-child,th:first-child{{text-align:left}}td.pass{{color:#126b35;font-weight:700}}td.fail{{color:#b42318;font-weight:700}}
code{{overflow-wrap:anywhere}}a{{color:#075caa}}
</style></head><body>
<h1>Dependent-effects results: R, Python, and Julia</h1>
<p class="summary"><strong>{passed} / {total} comparisons pass.</strong> The shared synthetic cases cover correlated-sampling GLS, nested random intercepts, and a two-outcome unstructured study covariance.</p>
<p class="meta">Reference: <a href="https://cran.r-project.org/web/packages/metafor/index.html">metafor 5.2-1</a>; source SHA-256 <code>{html.escape(source_sha)}</code>. Full runtime and seed record: <a href="../reference/dependent/v1/REFERENCE-VERSIONS.txt">REFERENCE-VERSIONS.txt</a>. Synthetic fixture provenance: <a href="../reference/dependent/v1/PROVENANCE.md">PROVENANCE.md</a>.</p>
<details><summary>Runtime and fixture truth</summary><pre>{html.escape(versions)}</pre></details>
{render_table("Coefficients, intervals, heterogeneity and covariance components", estimates, ("Model", "Quantity", "Name"))}
{render_table("Fixed-effect coefficient covariance", covariances, ("Model", "Row", "Column"))}
<h2>How to read this page</h2><p>Each row compares the same fixture and statistical target across the pinned R reference and both native implementations. Variance components allow 1e-6 absolute plus 1e-4 relative error; other estimates allow 1e-6 absolute plus 1e-5 relative error; small heterogeneity p-values use 1e-24 absolute plus 5e-4 relative error. Tests also cover a hand-calculated GLS case, missing-row masking on both covariance axes, reused nested labels, and a zero-variance boundary.</p>
<p>Example model definitions follow the upstream <a href="https://wviechtb.github.io/metafor/reference/rma.mv.html">rma.mv reference</a>. These fixtures use original synthetic data, not the Berkey dataset.</p>
</body></html>"""
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document)
    print(f"Wrote {passed}/{total} passing comparisons to {args.output}")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
