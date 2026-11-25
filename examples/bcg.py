"""Run a focused stage or the complete 13-study BCG example."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

from metafor import escalc_rr, fit_meta, forest_plot_data, write_forest_svg

ROOT = Path(__file__).parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case",
        choices=("all", "effects", "models", "moderator", "prediction", "forest"),
        default="all",
    )
    case = parser.parse_args().case

    with (ROOT / "reference/v1/bcg.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    count = lambda name: np.array([float(row[name]) for row in rows])
    yi, vi = escalc_rr(count("tpos"), count("tneg"), count("cpos"), count("cneg"))
    latitude = count("ablat")
    designs = {
        "fixed": np.ones((len(yi), 1)),
        "random": np.ones((len(yi), 1)),
        "latitude": np.column_stack([np.ones(len(yi)), latitude]),
    }
    requested = {
        "all": ("fixed", "random", "latitude"),
        "effects": (),
        "models": ("fixed", "random"),
        "moderator": ("latitude",),
        "prediction": ("latitude",),
        "forest": ("random",),
    }[case]
    models = {
        name: fit_meta(yi, vi, designs[name] if name == "latitude" else None,
                       method="FE" if name == "fixed" else "REML" if name == "random" else "REML")
        for name in requested
    }
    predictions = None
    if case in ("all", "moderator", "prediction"):
        predictions = models["latitude"].predict(
            np.column_stack([np.ones(3), [0.0, 30.0, 60.0]])
        )
    forest = None
    if case in ("all", "forest"):
        forest = forest_plot_data(yi, vi, [row["author"] for row in rows], models["random"])

    output = {
        name: {
            "beta": model.beta.tolist(),
            "se": model.se.tolist(),
            "tau2": model.tau2,
            "QE": model.q,
            "I2": model.i2,
            "H2": model.h2,
            "ci_lb": model.interval()[0].tolist(),
            "ci_ub": model.interval()[1].tolist(),
        }
        for name, model in models.items()
    }
    if predictions is not None:
        output["prediction"] = {
            "latitude": [0.0, 30.0, 60.0],
            "estimate": predictions.estimate.tolist(),
            "se": predictions.se.tolist(),
            "ci_lb": predictions.ci_lb.tolist(),
            "ci_ub": predictions.ci_ub.tolist(),
            "pi_lb": predictions.pi_lb.tolist(),
            "pi_ub": predictions.pi_ub.tolist(),
        }
    output["yi"] = yi.tolist()
    output["vi"] = vi.tolist()
    result_path = (
        ROOT / "examples/bcg-results.json"
        if case == "all"
        else ROOT / "examples/generated/bcg" / f"{case}-results.json"
    )
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(output, indent=2) + "\n")

    def fmt(values):
        return ",".join(f"{float(value):.16g}" for value in np.atleast_1d(values))

    if case in ("all", "effects"):
        for i, (effect, variance) in enumerate(zip(yi, vi), start=1):
            print(f"EFFECT|{i}|{effect:.16g}|{variance:.16g}")
    coefficient_labels = {"fixed": ["intrcpt"], "random": ["intrcpt"],
                          "latitude": ["intrcpt", "ablat"]}
    for name, model in models.items():
        ci_lb, ci_ub = model.interval()
        print("RESULT|{}|beta={}|se={}|tau2={:.16g}|QE={:.16g}|I2={:.16g}|H2={:.16g}|ci_lb={}|ci_ub={}".format(
            name, fmt(model.beta), fmt(model.se), model.tau2, model.q,
            model.i2, model.h2, fmt(ci_lb), fmt(ci_ub)))
        print(f"COV|{name}|{fmt(model.covariance.ravel())}")
        print(f"COVLABELS|{name}|{','.join(coefficient_labels[name])}")
        print(f"ROWS|{name}|{','.join(str(i + 1) for i in model.row_indices)}")
        print(f"DESIGN|{name}|{len(designs[name])}|{designs[name].shape[1]}|{fmt(designs[name].ravel())}")
    if predictions is not None:
        for i, value in enumerate((0.0, 30.0, 60.0)):
            print("PRED|latitude|x={:.16g}|estimate={:.16g}|se={:.16g}|ci_lb={:.16g}|ci_ub={:.16g}|pi_lb={:.16g}|pi_ub={:.16g}".format(
                value, predictions.estimate[i], predictions.se[i], predictions.ci_lb[i],
                predictions.ci_ub[i], predictions.pi_lb[i], predictions.pi_ub[i]))
    if forest is not None:
        forest_json = ROOT / "examples/bcg-forest-data.json"
        forest_json.write_text(json.dumps(forest, indent=2) + "\n")
        svg_path = write_forest_svg(forest, ROOT / "examples/bcg-forest.svg")
        if len(forest["rows"]) != 13 or svg_path.stat().st_size == 0:
            raise RuntimeError("forest plot output is incomplete")
        summary = forest["summary"]
        print("FOREST_SUMMARY|estimate={estimate:.16g}|se={se:.16g}|ci_lb={ci_lb:.16g}|ci_ub={ci_ub:.16g}|pi_lb={pi_lb:.16g}|pi_ub={pi_ub:.16g}|tau2={tau2:.16g}".format(**summary))
        print(f"FOREST_PLOT_OK {svg_path}")
    print(f"BCG_EXAMPLE_OK case={case} {result_path}")


if __name__ == "__main__":
    main()
