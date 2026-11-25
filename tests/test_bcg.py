import json
from pathlib import Path

import numpy as np
import pytest

from metafor import escalc_rr, fit_meta

ROOT = Path(__file__).parents[1]
DATA = np.genfromtxt(ROOT / "reference/v1/bcg.csv", delimiter=",", names=True,
                     dtype=None, encoding="utf8")
REFERENCE = json.loads((ROOT / "reference/v1/bcg-reference.json").read_text())


@pytest.mark.bcg_models
def test_bcg_effect_sizes_match_reference():
    yi, vi = escalc_rr(DATA["tpos"], DATA["tneg"], DATA["cpos"], DATA["cneg"])
    np.testing.assert_allclose(yi, REFERENCE["yi"], rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(vi, REFERENCE["vi"], rtol=1e-12, atol=1e-12)


@pytest.mark.bcg_models
@pytest.mark.parametrize("key,design,method", [
    ("fe", None, "FE"),
    ("reml", None, "REML"),
    ("moderator", np.column_stack([np.ones(13), DATA["ablat"]]), "REML"),
])
def test_bcg_models_match_reference(key, design, method):
    yi, vi = escalc_rr(DATA["tpos"], DATA["tneg"], DATA["cpos"], DATA["cneg"])
    result = fit_meta(yi, vi, design, method)
    reference = REFERENCE[key]
    np.testing.assert_allclose(result.beta, np.atleast_1d(reference["beta"]), rtol=1e-5, atol=2e-6)
    np.testing.assert_allclose(result.se, np.atleast_1d(reference["se"]), rtol=1e-5, atol=2e-6)
    assert result.tau2 == pytest.approx(reference["tau2"], rel=1e-5, abs=2e-6)
    assert result.q == pytest.approx(reference["QE"], rel=1e-10, abs=1e-10)
    assert result.i2 == pytest.approx(reference["I2"], rel=1e-5, abs=2e-3)
    assert result.h2 == pytest.approx(reference["H2"], rel=1e-5, abs=2e-4)
    low, high = result.interval()
    np.testing.assert_allclose(low, reference["ci_lb"], rtol=1e-5, atol=2e-6)
    np.testing.assert_allclose(high, reference["ci_ub"], rtol=1e-5, atol=2e-6)


@pytest.mark.bcg_edges
def test_missing_rows_are_removed_consistently():
    yi = np.array([0.1, np.nan, 0.3, 0.5])
    vi = np.array([0.2, 0.2, 0.2, 0.2])
    with pytest.warns(RuntimeWarning, match="rows omitted"):
        result = fit_meta(yi, vi, method="FE")
    assert result.beta[0] == pytest.approx(np.mean([0.1, 0.3, 0.5]))
    assert result.row_indices == (0, 2, 3)


@pytest.mark.bcg_edges
def test_missing_moderator_rows_are_removed_with_the_same_design_mask():
    yi = np.array([0.1, 0.2, 0.3])
    vi = np.array([0.2, 0.2, 0.2])
    X = np.array([[1.0, 0.0], [1.0, np.nan], [1.0, 2.0]])
    with pytest.warns(RuntimeWarning, match="rows omitted"):
        result = fit_meta(yi, vi, X, method="FE")
    assert result.row_indices == (0, 2)
    np.testing.assert_allclose(result.beta, [0.1, 0.1], atol=1e-12)


@pytest.mark.bcg_edges
def test_zero_cell_correction_and_double_zero_row():
    yi, vi = escalc_rr([0, 0], [20, 10], [3, 0], [17, 10])
    assert np.isfinite(yi[0]) and np.isfinite(vi[0])
    assert np.isfinite(yi[1]) and np.isfinite(vi[1])


@pytest.mark.bcg_edges
@pytest.mark.parametrize("policy, expected_y, expected_v", [
    ("only0", [-1.6094379124341001, -0.4054651081081642], [2.2181818181818183, 0.6333333333333334]),
    ("all", [-1.6094379124341001, -0.336472236621213], [2.2181818181818183, 0.5038961038961038]),
    ("if0all", [-1.6094379124341001, -0.336472236621213], [2.2181818181818183, 0.5038961038961038]),
])
def test_r_zero_correction_policies(policy, expected_y, expected_v):
    yi, vi = escalc_rr([0, 2], [10, 8], [2, 3], [8, 7], to=policy)
    np.testing.assert_allclose(yi, expected_y, atol=1e-12)
    np.testing.assert_allclose(vi, expected_v, atol=1e-12)


@pytest.mark.bcg_edges
def test_r_zero_correction_none_policy_recodes_zero_event_row():
    yi, vi = escalc_rr([0, 2], [10, 8], [2, 3], [8, 7], to="none")
    assert np.isnan(yi[0]) and np.isnan(vi[0])
    assert yi[1] == pytest.approx(-0.4054651081081642)
    assert vi[1] == pytest.approx(0.6333333333333334)


@pytest.mark.bcg_edges
def test_exact_boundary_reml_is_zero():
    yi = np.array([-1.0, 0.0, 1.0])
    vi = np.ones(3)
    result = fit_meta(yi, vi, method="REML")
    assert result.tau2 == pytest.approx(0.0, abs=1e-10)


@pytest.mark.bcg_edges
def test_reml_compares_fisher_stationary_point_with_zero_boundary():
    with pytest.warns(RuntimeWarning, match="inferior local maximum"):
        result = fit_meta([0.0, 0.0, 25.0], [0.01, 0.01, 100.0])
    assert result.tau2 == pytest.approx(0.0, abs=1e-12)
    assert result.beta[0] == pytest.approx(0.001249938, abs=1e-8)


@pytest.mark.bcg_edges
def test_single_study_reml_has_defined_boundary_result():
    result = fit_meta([2.0], [0.4])
    assert result.tau2 == 0.0
    assert result.beta[0] == pytest.approx(2.0)
    assert result.h2 == 1.0 and result.i2 == 0.0


@pytest.mark.bcg_edges
def test_zero_sampling_variance_is_explicitly_unsupported():
    with pytest.raises(NotImplementedError, match="zero sampling variances"):
        fit_meta([-2.0, 0.0, 2.0], [0.2, 0.0, 0.2])
    with pytest.raises(ValueError, match="zero sampling variances"):
        fit_meta([-1.0, 1.0], [0.0, 0.2], method="FE")


@pytest.mark.bcg_edges
def test_native_missing_count_and_outcome_values_are_treated_as_missing():
    yi, vi = escalc_rr([None, 0], [10, 10], [2, 2], [8, 8])
    assert np.isnan(yi[0]) and np.isnan(vi[0])
    with pytest.warns(RuntimeWarning, match="rows omitted"):
        result = fit_meta([0.1, None, 0.3], [0.2, 0.2, 0.2], method="FE")
    assert result.row_indices == (0, 2)


@pytest.mark.bcg_edges
def test_hand_calculated_fixed_effect():
    yi = np.array([1.0, 3.0])
    vi = np.array([1.0, 3.0])
    result = fit_meta(yi, vi, method="FE")
    assert result.beta[0] == pytest.approx(1.5)
    assert result.se[0] == pytest.approx(np.sqrt(0.75))


@pytest.mark.phylogeny_model
@pytest.mark.parametrize("fixture", ["v1", "v2-interior"])
def test_synthetic_phylogenetic_fixtures_match_r_reference(fixture):
    import csv
    from metafor import fit_phylo
    root = ROOT / "reference/phylogeny" / fixture
    observations = list(csv.DictReader((root / "observations.csv").open()))
    with (root / "species-correlation.csv").open(newline="") as handle:
        matrix_rows = list(csv.reader(handle))
    correlation_labels = matrix_rows[0][1:]
    assert [row[0] for row in matrix_rows[1:]] == correlation_labels
    matrix = np.asarray([[float(x) for x in row[1:]] for row in matrix_rows[1:]])
    reference = next(csv.DictReader((root / "reference.csv").open()))
    result = fit_phylo(
        [float(row["yi"]) for row in observations],
        [float(row["vi"]) for row in observations],
        [row["species"] for row in observations], matrix, correlation_labels,
    )
    assert result.beta[0] == pytest.approx(float(reference["beta"]), abs=1e-6)
    assert result.se[0] == pytest.approx(float(reference["se"]), abs=1e-6)
    assert result.tau2 == pytest.approx(float(reference["tau2"]), abs=1e-6)
    low, high = result.interval()
    if "ci_lb" in reference:
        assert low[0] == pytest.approx(float(reference["ci_lb"]), abs=1e-6)
        assert high[0] == pytest.approx(float(reference["ci_ub"]), abs=1e-6)


@pytest.mark.phylogeny_model
def test_phylogenetic_optimizer_expands_past_its_initial_variance_bound():
    from metafor import fit_phylo
    result = fit_phylo([-1.,-1.,1.,1.],[.1]*4,["a","a","b","b"],
                       [[1.,.999],[.999,1.]],["a","b"])
    assert result.tau2 == pytest.approx(1950.00332547, rel=1e-4, abs=0.1)


@pytest.mark.phylogeny_model
def test_phylogenetic_variance_confounded_with_intercept_is_fixed_at_zero():
    from metafor import fit_phylo
    with pytest.warns(RuntimeWarning, match="not identifiable"):
        result = fit_phylo([1., 2., 3.], [.1, .1, .1], ["only"] * 3,
                           [[1.]], ["only"])
    assert result.tau2 == 0.
    assert result.beta[0] == pytest.approx(2.)
    assert result.se[0] == pytest.approx(np.sqrt(.1 / 3.))


@pytest.mark.bcg_models
def test_bcg_moderator_predictions_match_reference():
    yi, vi = escalc_rr(DATA["tpos"], DATA["tneg"], DATA["cpos"], DATA["cneg"])
    model = fit_meta(yi, vi, np.column_stack([np.ones(13), DATA["ablat"]]))
    prediction = model.predict(np.column_stack([np.ones(3), [0, 30, 60]]))
    reference = REFERENCE["prediction"]
    for field in ("pred", "se", "ci_lb", "ci_ub", "pi_lb", "pi_ub"):
        actual = prediction.estimate if field == "pred" else getattr(prediction, field)
        np.testing.assert_allclose(actual, reference[field], rtol=1e-5, atol=2e-6)


@pytest.mark.bcg_adapters
def test_forest_plot_data_preserves_raw_row_order_and_matches_effects():
    from metafor import forest_plot_data
    yi, vi = escalc_rr(DATA["tpos"], DATA["tneg"], DATA["cpos"], DATA["cneg"])
    model = fit_meta(yi, vi)
    data = forest_plot_data(yi, vi, DATA["author"], model)
    assert [row["row"] for row in data["rows"]] == list(range(1, 14))
    assert [row["label"] for row in data["rows"]] == list(DATA["author"])
    np.testing.assert_allclose([row["estimate"] for row in data["rows"]], REFERENCE["yi"])
    np.testing.assert_allclose([row["ci_lb"] for row in data["rows"]],
                               np.array(REFERENCE["yi"]) - 1.959963984540054*np.sqrt(REFERENCE["vi"]), atol=1e-8)
    summary = data["summary"]
    pred = model.predict()
    assert summary["estimate"] == pytest.approx(pred.estimate[0])
    assert summary["ci_lb"] == pytest.approx(pred.ci_lb[0])
    assert summary["ci_ub"] == pytest.approx(pred.ci_ub[0])
    assert summary["pi_lb"] == pytest.approx(pred.pi_lb[0])
    assert summary["pi_ub"] == pytest.approx(pred.pi_ub[0])
    assert data["scale"] == "log risk ratio"


@pytest.mark.bcg_edges
def test_forest_data_excludes_missing_rows_without_renumbering():
    from metafor import forest_plot_data
    data = forest_plot_data([0.1, np.nan, 0.3], [0.2, 0.1, 0.4], ["a", "missing", "c"])
    assert [row["row"] for row in data["rows"]] == [1, 3]


@pytest.mark.bcg_adapters
def test_formula_adapter_matches_matrix_design_and_preserves_rows():
    import pandas as pd
    from metafor import fit_meta_formula
    yi, vi = escalc_rr(DATA["tpos"], DATA["tneg"], DATA["cpos"], DATA["cneg"])
    table = pd.DataFrame({"yi": yi, "vi": vi, "ablat": DATA["ablat"]},
                         index=DATA["trial"])
    table.loc[4, "ablat"] = np.nan
    fitted = fit_meta_formula(table, "yi ~ ablat")
    keep = np.isfinite(table["ablat"].to_numpy())
    design = np.column_stack([np.ones(keep.sum()), table.loc[keep, "ablat"].to_numpy()])
    direct = fit_meta(yi[keep], vi[keep], design)
    np.testing.assert_allclose(fitted.result.beta, direct.beta, atol=1e-12)
    assert fitted.design_columns == ("Intercept", "ablat")
    assert fitted.row_index == tuple(table.index[keep].tolist())
    reversed_fit = fit_meta_formula(table.iloc[::-1], "yi ~ ablat")
    assert reversed_fit.row_index == tuple(table.index[keep].tolist()[::-1])
    np.testing.assert_allclose(reversed_fit.result.beta, direct.beta, atol=1e-12)


@pytest.mark.bcg_adapters
def test_formula_adapter_rejects_multiple_response_terms():
    import pandas as pd
    from metafor import fit_meta_formula
    with pytest.raises(ValueError, match="exactly one response"):
        fit_meta_formula(pd.DataFrame({"yi": [1., 2.], "ablat": [3., 4.], "vi": [.2, .3]}),
                         "yi + ablat ~ 1")


@pytest.mark.bcg_adapters
def test_formula_adapter_does_not_silently_drop_zero_sampling_variance():
    import pandas as pd
    from metafor import fit_meta_formula
    data = pd.DataFrame({"yi":[0.1,0.2,0.3],"vi":[0.2,0.0,0.3],"x":[1.,2.,3.]})
    with pytest.raises(NotImplementedError, match="zero sampling variances"):
        fit_meta_formula(data,"yi ~ x")
    with pytest.raises(ValueError, match="zero sampling variances"):
        fit_meta_formula(data,"yi ~ x",method="FE")


@pytest.mark.bcg_adapters
def test_formula_adapter_maps_nonfinite_response_back_to_original_rows():
    import pandas as pd
    from metafor import fit_meta_formula
    table = pd.DataFrame({"yi": [0.1, np.inf, 0.3, 0.5], "vi": [.2] * 4,
                          "x": [0., 1., 2., 3.]}, index=[11, 12, 13, 14])
    fitted = fit_meta_formula(table, "yi ~ x", method="FE")
    assert fitted.row_index == (11, 13, 14)
    assert fitted.result.row_indices == (0, 2, 3)


@pytest.mark.bcg_adapters
def test_table_adapter_example_emits_rows_and_matrix_parity():
    import subprocess
    import sys

    completed = subprocess.run(
        [sys.executable, str(ROOT / "examples/bcg.py"), "--case=table-adapter"],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )
    assert "TABLE_ADAPTER|design_columns|Intercept,ablat" in completed.stdout
    assert "TABLE_ADAPTER|row_ids|1,2,3,5,6,7,8,9,10,11,12,13" in completed.stdout
    assert "TABLE_ADAPTER|design_shape|12,2" in completed.stdout
    design_line = next(x for x in completed.stdout.splitlines()
                       if x.startswith("TABLE_ADAPTER|design_values|"))
    design_values = np.array([float(x) for x in design_line.rsplit("|", 1)[1].split(",")])
    keep = np.arange(len(DATA)) != 3
    expected_design = np.column_stack([np.ones(keep.sum()), DATA["ablat"][keep]]).ravel()
    np.testing.assert_allclose(design_values, expected_design, rtol=0, atol=1e-12)
    line = next(x for x in completed.stdout.splitlines()
                if x.startswith("TABLE_ADAPTER|matrix_max_abs_diff|"))
    assert float(line.rsplit("|", 1)[1]) <= 1e-12
