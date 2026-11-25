from pathlib import Path
import os
import shutil

project = "metafor-py"
extensions = ["myst_parser", "sphinx.ext.mathjax"]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
master_doc = "index"
exclude_patterns = ["_build"]
html_static_path = ["_static"]
html_css_files = ["metafor.css"]
html_theme = "sphinx_rtd_theme"
html_show_copyright = False
html_show_sphinx = False
html_theme_options = {
    "navigation_depth": 3,
    "collapse_navigation": False,
    "sticky_navigation": True,
}
myst_enable_extensions = ["amsmath", "dollarmath"]
myst_heading_anchors = 3
mathjax3_config = {"tex": {"inlineMath": [["$", "$"], ["\\(", "\\)"]]}}

comparison_dir = Path(__file__).resolve().parent / "_static" / "comparisons"
comparison_dir.mkdir(parents=True, exist_ok=True)
comparison_names = (
    "bcg-comparison.html",
    "dependent-comparison.html",
    "phylogeny-comparison.html",
    "effect-size-comparison.html",
    "table-adapter-comparison.html",
)
pairwise_dir = Path(__file__).resolve().parent.parent / "examples" / "pairwise"
repo_root = Path(__file__).resolve().parent.parent
missing = [name for name in comparison_names if not (pairwise_dir / name).is_file()]
if missing and os.environ.get("METAFOR_PREVIEW") != "1":
    raise RuntimeError("Missing final comparison inputs: " + ", ".join(missing))
for name in comparison_names:
    source = pairwise_dir / name
    if source.is_file():
        shutil.copy2(source, comparison_dir / name)

def copy_forest_plot(app):
    source = repo_root / "examples" / "bcg-forest.svg"
    if not source.is_file():
        raise FileNotFoundError(f"The BCG forest plot required by Getting Started is missing: {source}")
    target = Path(app.outdir) / "_static" / "bcg-forest.svg"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup(app):
    app.connect("builder-inited", copy_forest_plot)
