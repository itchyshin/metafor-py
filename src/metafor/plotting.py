"""Small dependency-free SVG rendering helpers for native examples."""
from html import escape
from pathlib import Path


def write_forest_svg(data, path, title="BCG study effects"):
    """Render forest coordinates on their declared log-risk-ratio scale."""
    rows = data["rows"]
    summary = data.get("summary")
    if not rows:
        raise ValueError("forest plot needs at least one finite study")
    if summary is None:
        raise ValueError("forest plot needs a pooled summary")
    width, left, right = 1120, 330, 1080
    top, row_h = 92, 28
    summary_y = top + row_h * len(rows) + 24
    height = summary_y + 72
    low = min([r["ci_lb"] for r in rows] + [summary["pi_lb"]])
    high = max([r["ci_ub"] for r in rows] + [summary["pi_ub"]])
    pad = 0.06 * (high - low)
    low, high = low - pad, high + pad

    def x(value):
        return left + (value - low) / (high - low) * (right - left)

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<style>text{font:14px system-ui,sans-serif;fill:#1b2d3a}.small{font-size:12px}.ci{stroke:#345f74;stroke-width:2}.summary{stroke:#a13c31;fill:#a13c31}.axis{stroke:#8a9aa3;stroke-width:1}</style>',
             f'<text x="20" y="32" font-size="20" font-weight="700">{escape(title)}</text>',
             f'<text x="20" y="54" class="small">Study log risk ratios with 95% normal intervals</text>',
             f'<line x1="{x(0):.1f}" y1="68" x2="{x(0):.1f}" y2="{summary_y + 18}" class="axis" stroke-dasharray="4 4"/>']
    for i, row in enumerate(rows):
        y = top + row_h * i
        parts.extend([
            f'<text x="20" y="{y + 5}">{escape(row["label"])}</text>',
            f'<line x1="{x(row["ci_lb"]):.1f}" y1="{y}" x2="{x(row["ci_ub"]):.1f}" y2="{y}" class="ci"/>',
            f'<line x1="{x(row["ci_lb"]):.1f}" y1="{y - 4}" x2="{x(row["ci_lb"]):.1f}" y2="{y + 4}" class="ci"/>',
            f'<line x1="{x(row["ci_ub"]):.1f}" y1="{y - 4}" x2="{x(row["ci_ub"]):.1f}" y2="{y + 4}" class="ci"/>',
            f'<rect x="{x(row["estimate"]) - 5:.1f}" y="{y - 5}" width="10" height="10" fill="#345f74"/>',
        ])
    y = summary_y
    parts.extend([
        '<line x1="20" y1="{}" x2="{}" y2="{}" class="axis"/>'.format(y - 15, right, y - 15),
        f'<text x="20" y="{y + 5}" font-weight="700">REML mean</text>',
        f'<line x1="{x(summary["pi_lb"]):.1f}" y1="{y}" x2="{x(summary["pi_ub"]):.1f}" y2="{y}" class="summary" stroke-dasharray="5 4" opacity=".65"/>',
        f'<line x1="{x(summary["ci_lb"]):.1f}" y1="{y}" x2="{x(summary["ci_ub"]):.1f}" y2="{y}" class="summary" stroke-width="4"/>',
        f'<polygon points="{x(summary["estimate"]):.1f},{y - 8} {x(summary["ci_ub"]):.1f},{y} {x(summary["estimate"]):.1f},{y + 8} {x(summary["ci_lb"]):.1f},{y}" class="summary"/>',
        f'<text x="{left}" y="{height - 16}" class="small">log risk ratio (negative values favor vaccination)</text>',
        '</svg>',
    ])
    target = Path(path)
    target.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return target
