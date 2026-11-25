import csv
from pathlib import Path

import numpy as np
import pytest

from metafor import escalc_or, escalc_rd, fit_meta


ROOT = Path(__file__).parents[1]


def test_or_and_rd_match_pinned_metafor_reference():
    reference = list(csv.DictReader((ROOT / "reference/effect-sizes/v1/bcg-effect-sizes.csv").open()))
    counts = np.genfromtxt(ROOT / "reference/v1/bcg.csv", delimiter=",", names=True,
                           dtype=None, encoding="utf8")
    for measure, function in (("OR", escalc_or), ("RD", escalc_rd)):
        expected = [row for row in reference if row["measure"] == measure]
        yi, vi = function(counts["tpos"], counts["tneg"], counts["cpos"], counts["cneg"])
        np.testing.assert_allclose(yi, [float(row["yi"]) for row in expected], rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(vi, [float(row["vi"]) for row in expected], rtol=1e-12, atol=1e-12)


def test_or_and_rd_fixed_and_reml_models_match_pinned_reference():
    reference = list(csv.DictReader((ROOT / "reference/effect-sizes/v1/model-reference.csv").open()))
    counts = np.genfromtxt(ROOT / "reference/v1/bcg.csv", delimiter=",", names=True,
                           dtype=None, encoding="utf8")
    for measure, function in (("OR", escalc_or), ("RD", escalc_rd)):
        yi, vi = function(counts["tpos"], counts["tneg"], counts["cpos"], counts["cneg"])
        for method in ("FE", "REML"):
            expected = next(row for row in reference
                            if row["measure"] == measure and row["method"] == method)
            result = fit_meta(yi, vi, method=method)
            assert result.beta[0] == pytest.approx(float(expected["beta"]), rel=1e-5, abs=1e-9)
            assert result.se[0] == pytest.approx(float(expected["se"]), rel=1e-5, abs=1e-9)
            assert result.tau2 == pytest.approx(float(expected["tau2"]), rel=1e-5, abs=1e-9)
            assert result.q == pytest.approx(float(expected["QE"]), rel=1e-8, abs=1e-9)
            assert result.i2 == pytest.approx(float(expected["I2"]), rel=1e-5, abs=1e-7)
            assert result.h2 == pytest.approx(float(expected["H2"]), rel=1e-5, abs=1e-7)
            low, high = result.interval()
            assert low[0] == pytest.approx(float(expected["ci_lb"]), rel=1e-5, abs=1e-9)
            assert high[0] == pytest.approx(float(expected["ci_ub"]), rel=1e-5, abs=1e-9)


def test_all_zero_cell_policies_match_pinned_metafor_reference():
    reference = list(csv.DictReader((ROOT / "reference/effect-sizes/v1/zero-cell-reference.csv").open()))
    counts = ([0, 2], [10, 8], [2, 3], [8, 7])
    number = lambda value: np.nan if value == "NA" else float(value)
    for measure, function in (("OR", escalc_or), ("RD", escalc_rd)):
        for policy in ("only0", "all", "if0all", "none"):
            expected = [row for row in reference
                        if row["measure"] == measure and row["policy"] == policy]
            yi, vi = function(*counts, to=policy)
            np.testing.assert_allclose(yi, [number(row["yi"]) for row in expected], rtol=1e-12, atol=1e-12)
            np.testing.assert_allclose(vi, [number(row["vi"]) for row in expected], rtol=1e-12, atol=1e-12)


def test_or_hand_calculation_and_zero_cell_correction():
    yi, vi = escalc_or([2, 0], [8, 10], [5, 2], [5, 8])
    expected_y = [np.log((2 * 5) / (8 * 5)), np.log((0.5 * 8.5) / (10.5 * 2.5))]
    expected_v = [1 / 2 + 1 / 8 + 1 / 5 + 1 / 5,
                  1 / 0.5 + 1 / 10.5 + 1 / 2.5 + 1 / 8.5]
    np.testing.assert_allclose(yi, expected_y, atol=1e-12)
    np.testing.assert_allclose(vi, expected_v, atol=1e-12)


def test_rd_hand_calculation_uses_binomial_sampling_variance():
    yi, vi = escalc_rd([2], [8], [5], [5])
    p1, p2 = 0.2, 0.5
    assert yi[0] == pytest.approx(p1 - p2)
    assert vi[0] == pytest.approx(p1 * (1 - p1) / 10 + p2 * (1 - p2) / 10)


@pytest.mark.parametrize("function", [escalc_or, escalc_rd])
@pytest.mark.parametrize("policy", ["only0", "all", "if0all", "none"])
def test_zero_cell_policies_follow_metafor_table_rules(function, policy):
    yi, vi = function([0, 2], [10, 8], [2, 3], [8, 7], to=policy)
    raw = [(0.0, 10.0, 2.0, 8.0), (2.0, 8.0, 3.0, 7.0)]
    if policy == "only0":
        adjusted = [(0.5, 10.5, 2.5, 8.5), (2.0, 8.0, 3.0, 7.0)]
    elif policy == "none":
        adjusted = raw
    else:
        adjusted = [(0.5, 10.5, 2.5, 8.5), (2.5, 8.5, 3.5, 7.5)]
    if function is escalc_or:
        if policy == "none":
            assert np.isnan(yi[0]) and np.isnan(vi[0])
        for i, (a, b, c, d) in enumerate(adjusted):
            if policy == "none" and i == 0:
                continue
            assert yi[i] == pytest.approx(np.log(a * d / (b * c)))
            assert vi[i] == pytest.approx(1 / a + 1 / b + 1 / c + 1 / d)
    else:
        for i, (a, b, c, d) in enumerate(adjusted):
            p1, p2 = a / (a + b), c / (c + d)
            assert yi[i] == pytest.approx(p1 - p2)
            assert vi[i] == pytest.approx(p1 * (1 - p1) / (a + b) + p2 * (1 - p2) / (c + d))


def test_missing_counts_and_invalid_cells_are_handled_explicitly():
    yi, vi = escalc_or([None, 1], [5, 4], [2, 2], [3, 3])
    assert np.isnan(yi[0]) and np.isnan(vi[0])
    assert np.isfinite(yi[1]) and np.isfinite(vi[1])
    with pytest.raises(ValueError, match="nonnegative"):
        escalc_rd([-1], [3], [1], [2])
    with pytest.raises(ValueError, match="integers"):
        escalc_or([1.2], [3], [1], [2])
    with pytest.raises(ValueError, match="zero-cell"):
        escalc_or([1], [3], [1], [2], to="wrong")
