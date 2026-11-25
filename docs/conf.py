from pathlib import Path
import shutil

project = "metafor-py"
extensions = ["myst_parser"]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
master_doc = "index"
exclude_patterns = ["_build"]
html_static_path = ["_static"]
html_css_files = ["metafor.css"]
html_theme = "sphinx_rtd_theme"

repo = Path(__file__).resolve().parent.parent
comparison_dir = Path(__file__).resolve().parent / "_static" / "comparisons"
comparison_dir.mkdir(parents=True, exist_ok=True)
for name in ("bcg-comparison.html", "dependent-comparison.html", "phylogeny-comparison.html", "effect-size-comparison.html", "table-adapter-comparison.html"):
    shutil.copy2(repo / "examples" / name, comparison_dir / name)
