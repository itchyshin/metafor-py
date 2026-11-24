from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from metafor import fit_meta_cov, fit_meta_cov_formula, fit_meta_nested, fit_meta_un


ROOT = Path(__file__).parents[1] / "reference" / "dependent" / "v1"
REF = pd.read_csv(ROOT / "results.csv")
COV_REF = pd.read_csv(ROOT / "coefficient-covariance.csv")


def read_matrix(name):
    return pd.read_csv(ROOT / name, index_col=0).to_numpy(dtype=float)


def expected(model, quantity, name):
    rows = REF.query("model == @model and quantity == @quantity and name == @name")
    assert len(rows) == 1
    return float(rows.iloc[0].estimate)


def compare_coefficients(model, fit, labels):
    beta = np.array([expected(model, "beta", name) for name in labels])
    se = np.array([expected(model, "se", name) for name in labels])
    lower = np.array([expected(model, "ci.lb", name) for name in labels])
    upper = np.array([expected(model, "ci.ub", name) for name in labels])
    fit_lower, fit_upper = fit.interval()
    np.testing.assert_allclose(fit.beta, beta, rtol=1e-5, atol=1e-6)
    np.testing.assert_allclose(fit.se, se, rtol=1e-5, atol=1e-6)
    np.testing.assert_allclose(fit_lower, lower, rtol=1e-5, atol=1e-6)
    np.testing.assert_allclose(fit_upper, upper, rtol=1e-5, atol=1e-6)
    np.testing.assert_allclose(
        fit.covariance,
        np.array([
            [
                float(COV_REF.query(
                    "model == @model and row == @row and column == @column"
                ).iloc[0].estimate)
                for column in labels
            ]
            for row in labels
        ]),
        rtol=1e-5,
        atol=1e-7,
    )
    assert fit.qe == pytest.approx(expected(model, "QE", "QE"), rel=1e-5, abs=1e-6)
    assert fit.qep == pytest.approx(expected(model, "QEp", "QEp"), rel=5e-4, abs=1e-24)


@pytest.mark.dependent_gls
def test_correlated_sampling_covariance_matches_pinned_r_reference():
    rows = pd.read_csv(ROOT / "gls-rows.csv")
    X = np.column_stack([np.ones(len(rows)), rows.x.to_numpy()])
    fit = fit_meta_cov(rows.yi, read_matrix("gls-V.csv"), X=X, method="FE")
    compare_coefficients("correlated-gls", fit, ["intrcpt", "x"])


@pytest.mark.dependent_nested
def test_nested_random_intercepts_match_pinned_r_reference_with_reused_levels():
    rows = pd.read_csv(ROOT / "nested-rows.csv")
    groups = {
        "study": rows.study.astype(str).to_numpy(),
        "study/effect": list(zip(rows.study.astype(str), rows.effect_local)),
    }
    X = np.column_stack([np.ones(len(rows)), rows.x.to_numpy()])
    fit = fit_meta_nested(
        rows.yi,
        read_matrix("nested-V.csv"),
        groups=groups,
        X=X,
        method="REML",
    )
    compare_coefficients("nested-reml", fit, ["intrcpt", "x"])
    assert fit.variance_components["study"] == pytest.approx(
        expected("nested-reml", "variance", "study"), rel=1e-4, abs=1e-6
    )
    assert fit.variance_components["study/effect"] == pytest.approx(
        expected("nested-reml", "variance", "nested-effect"), rel=1e-4, abs=1e-6
    )
    lower_kernel = fit.component_kernels["study/effect"]
    assert lower_kernel[0, 1] == 0
    assert lower_kernel[0, 3] == 0  # same local effect label, different study


@pytest.mark.dependent_un
def test_berkey_style_unstructured_study_covariance_matches_pinned_r_reference():
    rows = pd.read_csv(ROOT / "berkey-rows.csv")
    fit = fit_meta_un(
        rows.yi,
        read_matrix("berkey-V.csv"),
        study=rows.study.astype(str),
        outcome=rows.outcome,
        outcome_levels=["benefit", "harm"],
        method="REML",
    )
    compare_coefficients("berkey-un", fit, ["outcomebenefit", "outcomeharm"])
    np.testing.assert_allclose(
        fit.outcome_covariance,
        np.array([
            [expected("berkey-un", "variance", "benefit"),
             expected("berkey-un", "covariance", "benefit-harm")],
            [expected("berkey-un", "covariance", "benefit-harm"),
             expected("berkey-un", "variance", "harm")],
        ]),
        rtol=1e-4,
        atol=1e-6,
    )
    assert np.linalg.eigvalsh(fit.outcome_covariance).min() >= -1e-10


def test_gls_uses_full_covariance_and_hand_calculable_generalized_least_squares():
    y = np.array([0.2, 1.1, 0.7])
    X = np.ones((3, 1))
    V = np.array([[0.5, 0.1, 0.0], [0.1, 0.8, 0.12], [0.0, 0.12, 0.6]])
    fit = fit_meta_cov(y, V, X=X, method="FE")
    ViX = np.linalg.solve(V, X)
    beta = np.linalg.solve(X.T @ ViX, X.T @ np.linalg.solve(V, y))
    covariance = np.linalg.inv(X.T @ ViX)
    np.testing.assert_allclose(fit.beta, beta, rtol=0, atol=1e-12)
    np.testing.assert_allclose(fit.covariance, covariance, rtol=0, atol=1e-12)


def test_missing_row_masks_both_axes_of_sampling_covariance_once():
    y = np.array([0.2, np.nan, 0.7, 1.0])
    X = np.ones((4, 1))
    V = np.array(
        [[0.5, np.nan, 0.08, 0.0], [np.nan, np.nan, np.nan, np.nan],
         [0.08, np.nan, 0.7, 0.1], [0.0, np.nan, 0.1, 0.9]]
    )
    with pytest.warns(RuntimeWarning, match="Missing or invalid rows omitted"):
        fit = fit_meta_cov(y, V, X=X, method="FE")
    keep = np.array([0, 2, 3])
    Vk = V[np.ix_(keep, keep)]
    Xk = X[keep]
    yk = y[keep]
    cov = np.linalg.inv(Xk.T @ np.linalg.solve(Vk, Xk))
    beta = cov @ Xk.T @ np.linalg.solve(Vk, yk)
    assert fit.row_indices == (0, 2, 3)
    np.testing.assert_allclose(fit.beta, beta, rtol=0, atol=1e-12)


def test_pandas_missing_nested_label_is_omitted_with_its_covariance_row():
    y = np.array([0.2, 9.0, 0.7])
    V = np.diag([0.2, np.nan, 0.3])
    groups = {"study": ["A", pd.NA, "B"]}
    with pytest.warns(RuntimeWarning, match="Missing or invalid rows omitted"):
        fit = fit_meta_nested(y, V, groups, X=np.ones((3, 1)), method="FE")
    assert fit.row_indices == (0, 2)
    np.testing.assert_allclose(fit.beta, [0.4], rtol=0, atol=1e-12)


def test_reml_selects_zero_boundary_when_residuals_are_exactly_explained():
    x = np.array([-1.0, 0.0, 1.0, 2.0])
    X = np.column_stack([np.ones(4), x])
    y = 0.4 + 0.2 * x
    K = np.diag([1.0, 2.0, 1.0, 3.0])
    fit = fit_meta_cov(
        y, np.eye(4) * 0.1, X=X, components={"heterogeneity": K}, method="REML"
    )
    assert fit.variance_components["heterogeneity"] == pytest.approx(0.0, abs=1e-8)
    np.testing.assert_allclose(fit.beta, [0.4, 0.2], rtol=0, atol=1e-10)


def test_invalid_retained_sampling_covariance_is_rejected():
    with pytest.raises(ValueError, match="positive definite"):
        fit_meta_cov([0.1, 0.2], [[1.0, 2.0], [2.0, 1.0]], method="FE")
    with pytest.raises(ValueError, match="positive semidefinite"):
        fit_meta_cov(
            [0.1, 0.2], np.eye(2), method="REML",
            components={"invalid": [[1.0, 2.0], [2.0, 1.0]]},
        )


@pytest.mark.dependent_gls
def test_formula_adapter_preserves_design_and_row_identity_with_full_covariance():
    rows = pd.read_csv(ROOT / "gls-rows.csv")
    V = read_matrix("gls-V.csv")
    adapted = fit_meta_cov_formula(
        rows, "yi ~ x", V, id="row_id", method="FE"
    )
    direct = fit_meta_cov(
        rows.yi, V,
        X=np.column_stack([np.ones(len(rows)), rows.x.to_numpy()]),
        method="FE",
    )
    assert adapted.row_indices == tuple(range(len(rows)))
    assert adapted.row_ids == tuple(rows.row_id)
    assert adapted.design_columns[-1] == "x"
    np.testing.assert_allclose(adapted.result.beta, direct.beta, rtol=0, atol=1e-12)

    missing = rows.copy()
    missing.loc[1, "x"] = np.nan
    V_missing = V.copy()
    V_missing[1, :] = np.nan
    V_missing[:, 1] = np.nan
    with pytest.warns(RuntimeWarning, match="Missing or invalid rows omitted"):
        reduced = fit_meta_cov_formula(
            missing, "yi ~ x", V_missing, id="row_id", method="FE"
        )
    keep = tuple(i for i in range(len(rows)) if i != 1)
    direct_reduced = fit_meta_cov(
        missing.yi.iloc[list(keep)], V_missing[np.ix_(keep, keep)],
        X=np.column_stack([np.ones(len(keep)), missing.x.iloc[list(keep)].to_numpy()]),
        method="FE",
    )
    assert reduced.row_indices == keep
    assert reduced.row_ids == tuple(rows.row_id.iloc[list(keep)])
    np.testing.assert_allclose(reduced.result.beta, direct_reduced.beta, rtol=0, atol=1e-12)
