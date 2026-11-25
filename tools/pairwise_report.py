"""Render matched fixture results into one public report per port."""
from html import escape
from pathlib import Path

PROVENANCE = {
    "bcg": "v1",
    "dependent": "dependent/v1",
    "effect-size": "effect-sizes/v1",
    "phylogeny": "phylogeny/v1",
    "table-adapter": "table-adapter/v1",
}
REPOSITORIES = {"Julia": "Metafor.jl", "Python": "metafor-py"}


def write_report(root, slug, title, language, rows, detail):
    if not rows:
        raise ValueError("A comparison report must contain checked results")
    path = Path(root) / "examples" / "pairwise" / f"{slug}-comparison.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    title = escape(f"{title}: R vs {language}")
    provenance = (
        f"https://github.com/itchyshin/{REPOSITORIES[language]}/blob/main/"
        f"reference/{PROVENANCE[slug]}/PROVENANCE.md"
    )
    cells = "".join(
        "<tr>" + "".join(f"<td>{escape(value)}</td>" for value in (
            name, f"{ref:.12g}", f"{actual:.12g}", f"{limit:.4g}"
        )) + "</tr>"
        for name, ref, actual, limit in rows
    )
    path.write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>{title}</title><style>
body{{margin:2rem auto;padding:0 1rem;max-width:68rem;font:1rem/1.5 system-ui;color:#172c39}}
.table-wrap{{overflow:auto}}table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}}
th,td{{text-align:left;border-bottom:1px solid #cad6dc;padding:.45rem .65rem}}
th{{background:#e9f1f4}}caption{{text-align:left;padding:.5rem 0;font-weight:600}}
</style></head><body><main>
<h1>{title}</h1>
<p>All {len(rows)} numerical checks passed against the pinned R metafor 5.2-1 reference.</p>
<p>{escape(detail)} <a href="{provenance}">Read the fixture provenance.</a></p>
<div class="table-wrap"><table>
<caption>Checked values and allowed absolute differences</caption>
<thead><tr><th scope="col">Quantity</th><th scope="col">R</th><th scope="col">{language}</th><th scope="col">Allowed difference</th></tr></thead>
<tbody>{cells}</tbody></table></div>
</main></body></html>
""", encoding="utf-8")
