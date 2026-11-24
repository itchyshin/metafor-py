"""Run the correlated GLS, nested, and bivariate dependent-effects examples."""
import argparse
import csv
from pathlib import Path

import numpy as np

from metafor import fit_meta_cov, fit_meta_nested, fit_meta_un


ROOT = Path(__file__).parents[1] / "reference" / "dependent" / "v1"


def read_rows(name):
    with (ROOT / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def read_matrix(name):
    with (ROOT / name).open(newline="") as stream:
        rows = list(csv.reader(stream))
    return np.asarray([[float(value) for value in row[1:]] for row in rows[1:]])


def records(model, fit, labels, k):
    output = []
    lower, upper = fit.interval()
    for i, label in enumerate(labels):
        output.extend([
            (model, "beta", label, fit.beta[i]),
            (model, "se", label, fit.se[i]),
            (model, "ci.lb", label, lower[i]),
            (model, "ci.ub", label, upper[i]),
        ])
    output.extend([
        (model, "QE", "QE", fit.qe),
        (model, "QEp", "QEp", fit.qep),
        (model, "k", "k", k),
        (model, "p", "p", len(labels)),
    ])
    return output


def covariance_records(model, fit, labels):
    return [
        (model, labels[i], labels[j], fit.covariance[i, j])
        for i in range(len(labels)) for j in range(len(labels))
    ]


def run():
    estimates = []
    covariances = []

    gls_rows = read_rows("gls-rows.csv")
    gls_y = np.asarray([float(row["yi"]) for row in gls_rows])
    gls_x = np.asarray([float(row["x"]) for row in gls_rows])
    gls_X = np.column_stack([np.ones(len(gls_y)), gls_x])
    gls = fit_meta_cov(
        gls_y, read_matrix("gls-V.csv"), X=gls_X,
        design_columns=("intrcpt", "x"), method="FE",
    )
    estimates.extend(records("correlated-gls", gls, ("intrcpt", "x"), len(gls_y)))
    covariances.extend(covariance_records("correlated-gls", gls, ("intrcpt", "x")))

    nested_rows = read_rows("nested-rows.csv")
    nested_y = np.asarray([float(row["yi"]) for row in nested_rows])
    nested_x = np.asarray([float(row["x"]) for row in nested_rows])
    nested_X = np.column_stack([np.ones(len(nested_y)), nested_x])
    study = [row["study"] for row in nested_rows]
    effect_local = [row["effect_local"] for row in nested_rows]
    nested = fit_meta_nested(
        nested_y, read_matrix("nested-V.csv"),
        groups={"study": study,
                "study/effect": list(zip(study, effect_local))},
        X=nested_X, design_columns=("intrcpt", "x"), method="REML",
    )
    estimates.extend(records("nested-reml", nested, ("intrcpt", "x"), len(nested_y)))
    estimates.extend([
        ("nested-reml", "variance", "study", nested.variance_components["study"]),
        ("nested-reml", "variance", "nested-effect", nested.variance_components["study/effect"]),
    ])
    covariances.extend(covariance_records("nested-reml", nested, ("intrcpt", "x")))

    berkey_rows = read_rows("berkey-rows.csv")
    berkey_y = np.asarray([float(row["yi"]) for row in berkey_rows])
    berkey = fit_meta_un(
        berkey_y, read_matrix("berkey-V.csv"),
        study=[row["study"] for row in berkey_rows],
        outcome=[row["outcome"] for row in berkey_rows],
        outcome_levels=("benefit", "harm"), method="REML",
    )
    berkey_labels = ("outcomebenefit", "outcomeharm")
    estimates.extend(records("berkey-un", berkey, berkey_labels, len(berkey_y)))
    sigma = berkey.outcome_covariance
    covariance = sigma[0, 1]
    estimates.extend([
        ("berkey-un", "variance", "benefit", sigma[0, 0]),
        ("berkey-un", "variance", "harm", sigma[1, 1]),
        ("berkey-un", "covariance", "benefit-harm", covariance),
        ("berkey-un", "correlation", "benefit-harm", covariance / np.sqrt(sigma[0, 0] * sigma[1, 1])),
    ])
    covariances.extend(covariance_records("berkey-un", berkey, berkey_labels))
    return estimates, covariances


def write_csv(path, header, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(Path(__file__).with_name("dependent-python-results.csv")))
    parser.add_argument("--covariance-output", default=str(Path(__file__).with_name("dependent-python-covariance.csv")))
    args = parser.parse_args()
    estimates, covariances = run()
    write_csv(args.output, ("model", "quantity", "name", "estimate"), estimates)
    write_csv(args.covariance_output, ("model", "row", "column", "estimate"), covariances)
    print(f"Wrote {len(estimates)} R-comparable estimates to {args.output}")
    print(f"Wrote {len(covariances)} coefficient-covariance entries to {args.covariance_output}")


if __name__ == "__main__":
    main()
