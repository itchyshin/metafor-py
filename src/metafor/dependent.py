"""Matrix-first estimators for correlated and dependent meta-analytic data."""
from dataclasses import replace
from itertools import product
import math
import warnings

import numpy as np
from scipy.optimize import OptimizeWarning, minimize
from scipy.stats import chi2

from .core import DependentMetaResult, DependentTableMetaResult, _float_array


def _group_values(values, n, name):
    if len(values) != n:
        raise ValueError(f"{name} must have one value per input observation")
    result = []
    for value in values:
        if isinstance(value, np.ndarray) and value.ndim > 0:
            value = tuple(value.tolist())
        elif isinstance(value, list):
            value = tuple(value)
        result.append(value)
    return result


def _missing_label(value):
    if value is None:
        return True
    value_type = type(value)
    if value_type.__module__.startswith("pandas") and value_type.__name__ in {"NAType", "NaTType"}:
        return True
    if isinstance(value, tuple):
        return any(_missing_label(part) for part in value)
    try:
        return bool(np.isnan(value))
    except (TypeError, ValueError):
        return False


def _indicator_kernel(values):
    values = list(values)
    return np.asarray([[left == right for right in values] for left in values], dtype=float)


def _reml_state(y, V, X, G):
    C = V + G
    try:
        chol = np.linalg.cholesky(C)
        logdet_c = 2 * float(np.log(np.diag(chol)).sum())
        inv_c = np.linalg.solve(chol.T, np.linalg.solve(chol, np.eye(len(y))))
        ci_x = inv_c @ X
        information = X.T @ ci_x
        chol_information = np.linalg.cholesky(information)
    except np.linalg.LinAlgError:
        return None
    logdet_information = 2 * float(np.log(np.diag(chol_information)).sum())
    covariance = np.linalg.solve(
        chol_information.T,
        np.linalg.solve(chol_information, np.eye(X.shape[1])),
    )
    beta = covariance @ (X.T @ (inv_c @ y))
    py = inv_c @ y - ci_x @ beta
    P = inv_c - ci_x @ covariance @ ci_x.T
    objective = 0.5 * (
        logdet_c + logdet_information + float(y @ py)
        + (len(y) - X.shape[1]) * math.log(2 * math.pi)
    )
    return objective, beta, covariance, P, py, C


def _reml_gradient(state, derivatives):
    _, _, _, P, py, _ = state
    return np.asarray([
        0.5 * (float(np.trace(P @ derivative)) - float(py @ derivative @ py))
        for derivative in derivatives
    ])


def _bounded_reml(y, V, X, build_covariance, covariance_derivatives, starts, bounds):
    def evaluate(parameters):
        G = build_covariance(parameters)
        state = _reml_state(y, V, X, G)
        if state is None or not np.isfinite(state[0]):
            return np.inf, np.zeros(len(parameters))
        gradient = _reml_gradient(state, covariance_derivatives(parameters))
        return state[0], gradient

    candidates = []
    for initial in starts:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", OptimizeWarning)
            fit = minimize(
                lambda pars: evaluate(pars)[0],
                np.asarray(initial, dtype=float),
                jac=lambda pars: evaluate(pars)[1],
                method="L-BFGS-B",
                bounds=bounds,
                options={"ftol": 1e-13, "gtol": 1e-8, "maxiter": 2000, "maxls": 60},
            )
        if fit.success and np.isfinite(fit.fun):
            candidates.append((float(fit.fun), np.asarray(fit.x, dtype=float)))
    if not candidates:
        raise RuntimeError("REML variance-component optimizer did not converge")
    return min(candidates, key=lambda item: item[0])[1]


def _fit_covariance_inputs(yi, V, X, component_pairs, extra_valid=None):
    y = _float_array(yi)
    v = _float_array(V)
    if y.ndim != 1 or v.shape != (len(y), len(y)):
        raise ValueError("yi must be a vector and V must be square with one row per observation")
    design = np.ones((len(y), 1)) if X is None else _float_array(X)
    if design.ndim != 2 or design.shape[0] != len(y):
        raise ValueError("X must have one row per input observation")
    valid = np.isfinite(y) & np.all(np.isfinite(design), axis=1)
    if extra_valid is not None:
        valid &= np.asarray(extra_valid, dtype=bool)
    if not np.all(valid):
        warnings.warn("Missing or invalid rows omitted from analysis", RuntimeWarning, stacklevel=3)
    rows = np.flatnonzero(valid)
    if not len(rows):
        raise ValueError("no usable observations")
    y = y[rows]
    design = design[rows, :]
    v = v[np.ix_(rows, rows)]
    if not np.all(np.isfinite(v)):
        raise ValueError("retained sampling covariance must be finite")
    vscale = max(float(np.max(np.abs(v))), 1.0)
    if not np.allclose(v, v.T, rtol=0, atol=1e-10 * vscale):
        raise ValueError("sampling covariance must be symmetric")
    v = (v + v.T) / 2
    try:
        np.linalg.cholesky(v)
    except np.linalg.LinAlgError as error:
        raise ValueError("sampling covariance must be positive definite") from error
    p = design.shape[1]
    if np.linalg.matrix_rank(design) < p:
        raise ValueError("X is rank deficient")
    kernels = {}
    for name, raw_kernel in component_pairs:
        kernel = _float_array(raw_kernel)
        if kernel.shape != (len(valid), len(valid)):
            raise ValueError(f"component {name!r} must be square with one row per observation")
        kernel = kernel[np.ix_(rows, rows)]
        if not np.all(np.isfinite(kernel)):
            raise ValueError(f"component {name!r} must be finite on retained rows")
        scale = max(float(np.max(np.abs(kernel))), 1.0)
        if not np.allclose(kernel, kernel.T, rtol=0, atol=1e-10 * scale):
            raise ValueError(f"component {name!r} must be symmetric")
        kernel = (kernel + kernel.T) / 2
        if np.linalg.eigvalsh(kernel).min() < -1e-9 * scale:
            raise ValueError(f"component {name!r} must be positive semidefinite")
        kernels[str(name)] = kernel
    return y, v, design, kernels, tuple(rows.tolist())


def _component_pairs(components):
    if components is None:
        return []
    pairs = list(components.items()) if hasattr(components, "items") else list(components)
    names = [str(name) for name, _ in pairs]
    if len(set(names)) != len(names):
        raise ValueError("component names must be unique")
    return [(str(name), matrix) for name, matrix in pairs]


def _fit_components(y, V, X, kernels, method):
    method = str(method).upper()
    if method in ("FIXED", "FIXED-EFFECT"):
        method = "FE"
    if method not in ("FE", "REML"):
        raise ValueError("method must be FE or REML")
    names = list(kernels)
    matrices = [kernels[name] for name in names]
    if len(matrices) > 8:
        raise NotImplementedError("at most eight independent covariance components are supported")
    zero = np.zeros(len(matrices))
    if method == "FE" or not matrices:
        theta = zero
    else:
        q = len(matrices)
        scale = max(float(np.var(y)), float(np.mean(np.diag(V))), 1e-6)
        upper = max(scale * 1e6, 1.0)
        candidates = [(_reml_state(y, V, X, np.zeros_like(V))[0], zero.copy())]
        for active_bits in product((False, True), repeat=q):
            active = np.flatnonzero(active_bits)
            if not len(active):
                continue
            for start_scale in (0.01, 0.1, 1.0, 10.0):
                initial = np.full(len(active), min(scale * start_scale, upper * 0.1))

                def build(partial):
                    full = zero.copy()
                    full[active] = partial
                    return sum(
                        (full[j] * matrices[j] for j in range(q)), np.zeros_like(V)
                    )

                def derivatives(_partial):
                    return [matrices[j] for j in active]

                fitted = _bounded_reml(
                    y, V, X, build, derivatives, [initial],
                    [(0.0, upper)] * len(active),
                )
                full = zero.copy()
                full[active] = fitted
                candidates.append((_reml_state(y, V, X, build(fitted))[0], full))
        theta = min(candidates, key=lambda item: item[0])[1]
    G = sum(
        (theta[j] * matrices[j] for j in range(len(matrices))), np.zeros_like(V)
    )
    state = _reml_state(y, V, X, G)
    if state is None:
        raise ValueError("marginal covariance is not positive definite")
    _, beta, covariance, _, _, marginal = state
    sampling_state = _reml_state(y, V, X, np.zeros_like(V))
    qe = float(y @ sampling_state[3] @ y)
    df = len(y) - X.shape[1]
    qep = float(chi2.sf(qe, df)) if df > 0 else math.nan
    return beta, covariance, theta, marginal, qe, qep, method


def fit_meta_cov(yi, V, X=None, components=None, method="REML", design_columns=None):
    """Fit GLS/REML using a supplied sampling covariance and PSD kernels.

    `components` is an ordered mapping from names to known positive-semidefinite
    covariance kernels. Missing outcome/design rows mask the same rows and
    columns of `V` and each kernel.
    """
    pairs = _component_pairs(components)
    y, v, design, kernels, rows = _fit_covariance_inputs(yi, V, X, pairs)
    beta, covariance, theta, marginal, qe, qep, method = _fit_components(
        y, v, design, kernels, method
    )
    labels = tuple(design_columns or (f"x{i + 1}" for i in range(design.shape[1])))
    if len(labels) != design.shape[1]:
        raise ValueError("design_columns must have one label per column of X")
    return DependentMetaResult(
        beta, covariance, dict(zip(kernels, map(float, theta))), kernels,
        marginal, qe, qep, True, method, rows, labels
    )


def fit_meta_cov_formula(data, formula, V, id=None, components=None, method="REML"):
    """Fit a full-covariance model from a pandas table and Patsy formula."""
    try:
        import pandas as pd
        from patsy import dmatrices
    except ImportError as error:
        raise ImportError(
            "fit_meta_cov_formula requires the 'tables' extra (pandas and patsy)"
        ) from error
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    if id is not None and id not in data.columns:
        raise ValueError(f"row ID column {id!r} is missing")
    frame = data.copy().reset_index(drop=True)
    n = len(frame)
    try:
        y_frame, x_frame = dmatrices(
            formula, frame, NA_action="drop", return_type="dataframe"
        )
    except Exception as error:
        raise ValueError(f"could not build design matrix from formula {formula!r}") from error
    if y_frame.shape[1] != 1:
        raise ValueError("formula must specify exactly one response")
    positions = x_frame.index.to_numpy(dtype=int)
    design = np.full((n, x_frame.shape[1]), np.nan)
    outcome = np.full(n, np.nan)
    design[positions, :] = x_frame.to_numpy(dtype=float)
    outcome[positions] = y_frame.iloc[:, 0].to_numpy(dtype=float)
    columns = tuple(str(value) for value in x_frame.columns)
    fit = fit_meta_cov(
        outcome, V, X=design, components=components, method=method,
        design_columns=columns
    )
    row_indices = fit.row_indices
    row_ids = (
        tuple(frame[id].iloc[i] for i in row_indices)
        if id is not None
        else tuple(data.index[i] for i in row_indices)
    )
    if len(set(row_ids)) != len(row_ids):
        raise ValueError("row IDs must be unique")
    return DependentTableMetaResult(
        fit, row_indices, row_ids, columns, str(formula)
    )


def fit_meta_nested(yi, V, groups, X=None, group_names=None, method="REML", design_columns=None):
    """Fit nested random intercepts from grouping vectors ordered outer to inner.

    Encode lower levels as tuples containing parent labels, such as
    ``(study, effect)``; repeated local effect labels under different studies
    then refer to distinct random intercepts.
    """
    y = _float_array(yi)
    if y.ndim != 1:
        raise ValueError("yi must be a vector")
    n = len(y)
    if hasattr(groups, "items"):
        items = list(groups.items())
    else:
        values = list(groups)
        names = list(group_names) if group_names is not None else [f"group{i + 1}" for i in range(len(values))]
        if len(names) != len(values):
            raise ValueError("group_names must have one name per grouping vector")
        items = list(zip(names, values))
    if not items:
        raise ValueError("at least one grouping vector is required")
    group_values = [(str(name), _group_values(values, n, str(name))) for name, values in items]
    if len({name for name, _ in group_values}) != len(group_values):
        raise ValueError("group names must be unique")
    design = np.ones((n, 1)) if X is None else _float_array(X)
    if design.ndim != 2 or design.shape[0] != n:
        raise ValueError("X must have one row per input observation")
    valid = np.isfinite(y) & np.all(np.isfinite(design), axis=1)
    for _, values in group_values:
        valid &= np.asarray([not _missing_label(value) for value in values])
    if not np.all(valid):
        warnings.warn("Missing or invalid rows omitted from analysis", RuntimeWarning, stacklevel=2)
    rows = np.flatnonzero(valid)
    if not len(rows):
        raise ValueError("no usable observations")
    kernels = {
        name: _indicator_kernel([values[i] for i in rows])
        for name, values in group_values
    }
    v = _float_array(V)
    if v.shape != (n, n):
        raise ValueError("V must be square with one row per input observation")
    result = fit_meta_cov(
        y[rows], v[np.ix_(rows, rows)], X=design[rows, :], components=kernels,
        method=method, design_columns=design_columns
    )
    return replace(result, row_indices=tuple(rows.tolist()))


def fit_meta_un(yi, V, study, outcome, outcome_levels, method="REML"):
    """Fit a study-clustered unstructured covariance for exactly two outcomes."""
    y = _float_array(yi)
    if y.ndim != 1:
        raise ValueError("yi must be a vector")
    n = len(y)
    studies = _group_values(study, n, "study")
    outcomes = _group_values(outcome, n, "outcome")
    levels = list(outcome_levels)
    if len(levels) != 2 or len(set(levels)) != 2:
        raise NotImplementedError("unstructured outcome covariance currently supports exactly two outcomes")
    X = np.asarray([[float(value == level) for level in levels] for value in outcomes])
    valid = np.isfinite(y) & np.asarray([not _missing_label(value) for value in studies])
    valid &= np.asarray([not _missing_label(value) for value in outcomes])
    if not np.all(valid):
        warnings.warn("Missing or invalid rows omitted from analysis", RuntimeWarning, stacklevel=2)
    rows = np.flatnonzero(valid)
    if not len(rows):
        raise ValueError("no usable observations")
    unknown = sorted(set(outcomes[i] for i in rows) - set(levels), key=str)
    if unknown:
        raise ValueError(f"observed outcomes absent from outcome_levels: {unknown}")
    y = y[rows]
    X = X[rows, :]
    studies = [studies[i] for i in rows]
    outcomes = [outcomes[i] for i in rows]
    v_full = _float_array(V)
    if v_full.shape != (n, n):
        raise ValueError("V must be square with one row per input observation")
    # Reuse covariance validation and common two-axis masking.
    y, v, X, _, local_rows = _fit_covariance_inputs(
        y, v_full[np.ix_(rows, rows)], X, []
    )
    if len(local_rows) != len(rows):
        raise ValueError("outcome design contains an unusable row")
    if np.linalg.matrix_rank(X) < X.shape[1]:
        raise ValueError("outcome design is rank deficient")
    levels_index = {level: i for i, level in enumerate(levels)}
    outcome_index = np.asarray([levels_index[value] for value in outcomes], dtype=int)
    same_study = np.asarray([[left == right for right in studies] for left in studies], dtype=bool)
    scale = max(float(np.var(y)), float(np.mean(np.diag(v))), 1e-6)
    upper = max(math.sqrt(scale * 1e6), 1.0)

    def sigma_and_derivatives(parameters):
        a, b, c = parameters
        L = np.array([[a, 0.0], [b, c]])
        sigma = L @ L.T
        d_sigma = (
            np.array([[2 * a, b], [b, 0.0]]),
            np.array([[0.0, a], [a, 2 * b]]),
            np.array([[0.0, 0.0], [0.0, 2 * c]]),
        )
        return sigma, d_sigma

    def build(parameters):
        sigma, _ = sigma_and_derivatives(parameters)
        return same_study * sigma[outcome_index[:, None], outcome_index[None, :]]

    def derivatives(parameters):
        _, d_sigma = sigma_and_derivatives(parameters)
        return [same_study * d[outcome_index[:, None], outcome_index[None, :]] for d in d_sigma]

    starts = [
        [upper * 0.001, 0.0, upper * 0.001],
        [upper * 0.01, upper * 0.002, upper * 0.008],
        [upper * 0.01, -upper * 0.002, 0.0],
        [0.0, 0.0, upper * 0.01],
        [upper * 0.02, upper * 0.01, upper * 0.02],
    ]
    method_name = str(method).upper()
    if method_name in ("FIXED", "FIXED-EFFECT", "FE"):
        parameters = np.zeros(3)
        method_name = "FE"
    elif method_name == "REML":
        parameters = _bounded_reml(
            y, v, X, build, derivatives, starts,
            [(0.0, upper), (-upper, upper), (0.0, upper)],
        )
    else:
        raise ValueError("method must be FE or REML")
    sigma, _ = sigma_and_derivatives(parameters)
    state = _reml_state(y, v, X, build(parameters))
    if state is None:
        raise ValueError("marginal covariance is not positive definite")
    _, beta, covariance, _, _, marginal = state
    sampling_state = _reml_state(y, v, X, np.zeros_like(v))
    qe = float(y @ sampling_state[3] @ y)
    df = len(y) - X.shape[1]
    qep = float(chi2.sf(qe, df)) if df > 0 else math.nan
    labels = tuple(f"outcome{level}" for level in levels)
    vc = {f"outcome_variance:{levels[i]}": float(sigma[i, i]) for i in range(2)}
    vc[f"outcome_covariance:{levels[0]}/{levels[1]}"] = float(sigma[0, 1])
    return DependentMetaResult(
        beta, covariance, vc, {}, marginal, qe, qep, True, method_name,
        tuple(rows.tolist()), labels, sigma
    )
