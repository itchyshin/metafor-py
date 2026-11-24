"""Matrix-first effect-size and univariate meta-analysis routines."""
from dataclasses import dataclass
import math
from statistics import NormalDist
import warnings
import numpy as np


def _float_array(values):
    raw = np.asarray(values)
    if raw.dtype != object:
        return np.asarray(values, dtype=float)
    result = np.empty(raw.shape, dtype=float)
    for index, value in np.ndenumerate(raw):
        try:
            result[index] = float(value)
        except (TypeError, ValueError):
            result[index] = np.nan
    return result

@dataclass(frozen=True)
class MetaResult:
    beta: np.ndarray
    covariance: np.ndarray
    tau2: float
    q: float
    i2: float
    h2: float
    converged: bool
    method: str
    row_indices: tuple = ()

    @property
    def se(self):
        return np.sqrt(np.diag(self.covariance))

    def interval(self, level=0.95):
        if not 0 < level < 1:
            raise ValueError("level must be between zero and one")
        # Normal quantile via a stable inverse-erf approximation.
        z = _normal_quantile((1 + level) / 2)
        return self.beta - z * self.se, self.beta + z * self.se

    def predict(self, Xnew=None, level=0.95):
        """Predict fitted means and new-study intervals for an explicit design matrix."""
        if not 0 < level < 1:
            raise ValueError("level must be between zero and one")
        if Xnew is None:
            if len(self.beta) != 1:
                raise ValueError("Xnew is required for a model with moderators")
            Xnew = np.ones((1, 1))
        x = np.asarray(Xnew, dtype=float)
        if x.ndim == 1:
            x = x.reshape(1, -1)
        if x.ndim != 2 or x.shape[1] != len(self.beta) or not np.all(np.isfinite(x)):
            raise ValueError("Xnew must be a finite matrix with one column per coefficient")
        estimate = x @ self.beta
        variance = np.einsum("ij,jk,ik->i", x, self.covariance, x)
        se = np.sqrt(np.maximum(variance, 0.0))
        z = _normal_quantile((1 + level) / 2)
        ci_lb, ci_ub = estimate - z * se, estimate + z * se
        if self.method == "REML":
            pi_se = np.sqrt(variance + self.tau2)
            pi_lb, pi_ub = estimate - z * pi_se, estimate + z * pi_se
        else:
            pi_lb = pi_ub = np.full_like(estimate, np.nan)
        return PredictionResult(estimate, se, ci_lb, ci_ub, pi_lb, pi_ub)


@dataclass(frozen=True)
class PredictionResult:
    estimate: np.ndarray
    se: np.ndarray
    ci_lb: np.ndarray
    ci_ub: np.ndarray
    pi_lb: np.ndarray
    pi_ub: np.ndarray


@dataclass(frozen=True)
class TableMetaResult:
    result: MetaResult
    row_index: tuple
    design_columns: tuple
    formula: str


@dataclass(frozen=True)
class DependentMetaResult:
    """Result for normal-normal GLS and dependent-effects REML models."""
    beta: np.ndarray
    covariance: np.ndarray
    variance_components: dict
    component_kernels: dict
    marginal_covariance: np.ndarray
    qe: float
    qep: float
    converged: bool
    method: str
    row_indices: tuple
    design_columns: tuple = ()
    outcome_covariance: np.ndarray | None = None

    @property
    def se(self):
        return np.sqrt(np.diag(self.covariance))

    def interval(self, level=0.95):
        if not 0 < level < 1:
            raise ValueError("level must be between zero and one")
        z = _normal_quantile((1 + level) / 2)
        return self.beta - z * self.se, self.beta + z * self.se


@dataclass(frozen=True)
class DependentTableMetaResult:
    result: DependentMetaResult
    row_indices: tuple
    row_ids: tuple
    design_columns: tuple
    formula: str


def fit_meta_formula(data, formula, vi="vi", method="REML"):
    """Fit from a pandas table and Patsy formula, retaining input row identity."""
    try:
        import pandas as pd
        from patsy import dmatrices
    except ImportError as error:
        raise ImportError("fit_meta_formula requires the 'tables' extra (pandas and patsy)") from error
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    if vi not in data.columns:
        raise ValueError(f"sampling-variance column {vi!r} is missing")
    frame = data.copy().reset_index(drop=True)
    variance = pd.to_numeric(frame[vi], errors="coerce").to_numpy(dtype=float)
    if np.any(np.isfinite(variance) & (variance < 0)):
        raise ValueError("sampling variances must be nonnegative")
    if np.any(np.isfinite(variance) & (variance == 0)):
        _, eligible_design = dmatrices(formula, frame, NA_action="drop", return_type="dataframe")
        eligible = eligible_design.index.to_numpy(dtype=int)
        if np.any(variance[eligible] == 0):
            if method.upper() in ("FE", "FIXED", "FIXED-EFFECT"):
                raise ValueError("fixed-effect fitting does not accept zero sampling variances")
            if method.upper() == "REML":
                raise NotImplementedError("REML with zero sampling variances is not supported")
    valid = np.isfinite(variance) & (variance > 0)
    if not np.all(valid):
        warnings.warn("Missing or invalid rows omitted from analysis", RuntimeWarning, stacklevel=2)
    frame = frame.loc[valid]
    y_frame, x_frame = dmatrices(formula, frame, NA_action="drop", return_type="dataframe")
    if len(x_frame) < len(frame):
        warnings.warn("Missing or invalid rows omitted from analysis", RuntimeWarning, stacklevel=2)
    if y_frame.shape[1] != 1:
        raise ValueError("formula must specify exactly one response")
    positions = x_frame.index.to_numpy(dtype=int)
    y = y_frame.iloc[:, 0].to_numpy(dtype=float)
    X = x_frame.to_numpy(dtype=float)
    model = fit_meta(y, variance[positions], X, method)
    positions = positions[np.asarray(model.row_indices, dtype=int)]
    original_index = tuple(data.index[positions].tolist())
    return TableMetaResult(model, original_index, tuple(x_frame.columns.tolist()), formula)


def forest_plot_data(yi, vi, labels, pooled=None, level=0.95):
    """Build original forest-plot coordinates on the log-risk-ratio scale."""
    y, v, names = np.asarray(yi, float), np.asarray(vi, float), list(labels)
    if y.ndim != 1 or v.shape != y.shape or len(names) != len(y):
        raise ValueError("yi, vi and labels must have equal lengths")
    z = _normal_quantile((1 + level) / 2)
    rows = []
    for i, (estimate, variance, label) in enumerate(zip(y, v, names)):
        if not np.isfinite(estimate) or not np.isfinite(variance) or variance <= 0:
            continue
        se = math.sqrt(variance)
        rows.append({"row": i + 1, "label": str(label), "estimate": float(estimate),
                     "se": se, "ci_lb": float(estimate - z * se),
                     "ci_ub": float(estimate + z * se)})
    summary = None
    if pooled is not None:
        pred = pooled.predict(level=level)
        summary = {"estimate": float(pred.estimate[0]), "se": float(pred.se[0]),
                   "ci_lb": float(pred.ci_lb[0]), "ci_ub": float(pred.ci_ub[0]),
                   "pi_lb": float(pred.pi_lb[0]), "pi_ub": float(pred.pi_ub[0]),
                   "tau2": float(pooled.tau2)}
    return {"scale": "log risk ratio", "level": float(level),
            "rows": rows, "summary": summary}


def _normal_quantile(p):
    # Use the standard library inverse CDF so analytic FE intervals retain
    # enough precision for the pinned reference's strict tolerance.
    if not 0 < p < 1: raise ValueError("probability must be in (0, 1)")
    return NormalDist().inv_cdf(p)


def escalc_rr(ai, bi, ci, di, add=0.5, to="only0"):
    """Return log risk ratios and variances; rows are [a,b,c,d]."""
    x=np.column_stack([_float_array(c) for c in (ai,bi,ci,di)])
    if x.ndim != 2 or x.shape[1] != 4: raise ValueError("four equally sized count vectors are required")
    if np.any(np.isfinite(x) & (x < 0)): raise ValueError("counts must be nonnegative")
    if np.any(np.isfinite(x) & (x != np.floor(x))): raise ValueError("counts must be integers")
    yi=np.full(len(x),np.nan); vi=np.full(len(x),np.nan)
    for i,(a,b,c,d) in enumerate(x):
        if not np.all(np.isfinite([a,b,c,d])): continue
        aa,bb,cc,dd=a,b,c,d
        zero=(a==0 or c==0 or b==0 or d==0)
        if to == "only0" and zero: aa+=add; bb+=add; cc+=add; dd+=add
        elif to == "all": aa+=add; bb+=add; cc+=add; dd+=add
        elif to == "if0all" and np.any(np.isfinite(x) & (x == 0)): aa+=add; bb+=add; cc+=add; dd+=add
        elif to == "none" and (a==0 or c==0): continue
        elif to not in ("only0","all","if0all","none"): raise ValueError("unsupported zero-cell policy")
        nt=aa+bb; nc=cc+dd
        if aa == 0 or cc == 0 or nt == 0 or nc == 0: continue
        yi[i]=math.log((aa/nt)/(cc/nc))
        vi[i]=1/aa-1/nt+1/cc-1/nc
    return yi,vi


def fit_meta(yi, vi, X=None, method="REML"):
    """Fit normal-normal FE or intercept-only/matrix REML by scalar search."""
    y=_float_array(yi); v=_float_array(vi)
    if y.ndim != 1 or v.shape != y.shape: raise ValueError("yi and vi must be equal length vectors")
    if X is None:
        X=np.ones((len(y),1))
    else:
        X=_float_array(X)
        if X.ndim != 2 or X.shape[0] != len(y): raise ValueError("X must have one row per input observation")
    method=method.upper()
    zero_variance=np.isfinite(y)&(v==0)&np.all(np.isfinite(X),axis=1)
    if np.any(np.isfinite(v)&(v<0)): raise ValueError("sampling variances must be nonnegative")
    if np.any(zero_variance):
        if method in ("FE", "FIXED", "FIXED-EFFECT"):
            raise ValueError("fixed-effect fitting does not accept zero sampling variances")
        if method == "REML":
            raise NotImplementedError("REML with zero sampling variances is not supported")
    mask=np.isfinite(y)&np.isfinite(v)&(v>0)&np.all(np.isfinite(X),axis=1)
    if not np.all(mask):
        warnings.warn("Missing or invalid rows omitted from analysis", RuntimeWarning, stacklevel=2)
    row_indices=tuple(np.flatnonzero(mask).tolist())
    y=y[mask]; v=v[mask]; X=X[mask,:]
    if not len(y): raise ValueError("no usable observations")
    p=X.shape[1]
    if np.linalg.matrix_rank(X)<p: raise ValueError("X is rank deficient")
    q0=float(len(y)-p)
    def at(t):
        w=1/(v+t); xtwx=X.T@(w[:,None]*X); cov=np.linalg.inv(xtwx); beta=cov@(X.T@(w*y)); resid=y-X@beta; q=float(np.sum(w*resid**2)); return beta,cov,q
    if method in ("FE","FIXED","FIXED-EFFECT"):
        beta,cov,q=at(0.0); tau=0.; conv=True
    elif method=="REML":
        if len(y) == 1 and p == 1:
            beta,cov,q=at(0.0)
            return MetaResult(beta,cov,0.0,0.0,0.0,1.0,True,"REML",row_indices)
        def objective(t):
            beta,cov,q=at(t)
            return .5*(np.sum(np.log(v+t))+np.linalg.slogdet(X.T@((1/(v+t))[:,None]*X))[1]+q+(len(y)-p)*math.log(2*math.pi))
        upper=max(float(np.var(y))*100, float(np.max(v))*100, 1.)
        # metafor initializes ML/REML from the unweighted residual projection.
        P0=np.eye(len(y))-X@np.linalg.solve(X.T@X, X.T)
        rss0=float(y@P0@y)
        trace_pv=float(np.trace(P0@np.diag(v)))
        tau=max(0.0,(rss0-trace_pv)/(len(y)-p))
        for _ in range(1000):
            w=1/(v+tau); W=np.diag(w)
            P=W-W@X@np.linalg.solve(X.T@W@X, X.T@W)
            PP=P@P
            adj=float((y@PP@y-np.trace(P))/np.trace(PP))
            while tau+adj < 0:
                adj *= 0.5
            updated=tau+adj
            if abs(updated-tau) <= 1e-5:
                tau=updated
                break
            tau=updated
        else:
            raise RuntimeError("REML Fisher scoring did not converge")
        # metafor checks the boundary likelihood after Fisher scoring; a
        # converged interior stationary point can still be an inferior mode.
        interior_objective, boundary_objective = objective(tau), objective(0.0)
        if tau > 1e-5 and interior_objective - boundary_objective > np.finfo(float).eps ** 0.25:
            warnings.warn("REML Fisher scoring found an inferior local maximum; the zero-heterogeneity boundary was selected",
                          RuntimeWarning, stacklevel=2)
            tau = 0.0
        beta,cov,q=at(tau); conv=True
    else: raise ValueError("method must be FE or REML")
    df=q0; cval=float(np.sum(1/v)-np.sum((1/v)**2)/np.sum(1/v)) if p==1 else max(df,0.)
    # metafor reports QE from the fixed sampling variances, independent of
    # the fitted random-effects variance.
    w0=1/v
    beta0=np.linalg.solve(X.T@(w0[:,None]*X),X.T@(w0*y))
    q=float(np.sum(w0*(y-X@beta0)**2))
    if method in ("FE", "FIXED", "FIXED-EFFECT"):
        i2=max(0.,(q-df)/q)*100 if q>0 else 0.
        h2=q/df if df>0 else math.nan
    else:
        # metafor's default i2def=1 uses the generalized typical sampling
        # variance (k-p) / trace(P), with P formed at sampling variances.
        W=np.diag(w0)
        # R's crossprod(Y, P) calculation symmetrizes P numerically, so use
        # its symmetric equivalent before taking the trace.
        P=W-W@X@np.linalg.solve(X.T@W@X, X.T@W)
        vt=df/np.trace(P)
        i2=100*tau/(vt+tau) if vt+tau>0 else 0.
        h2=tau/vt+1 if vt>0 else math.nan
    return MetaResult(beta,cov,float(tau),q,float(i2),float(h2),conv,method,row_indices)


def fit_phylo(yi, vi, species, correlation, correlation_labels, X=None, method="REML"):
    """Fit a species random intercept, aligning a supplied matrix by its labels."""
    y=np.asarray(yi,float); v=np.asarray(vi,float); species=np.asarray(species,dtype=object)
    A=np.asarray(correlation,float); axis_labels=list(correlation_labels)
    if y.ndim!=1 or v.shape!=y.shape or species.shape!=y.shape:
        raise ValueError("yi, vi and species must be equal-length vectors")
    if A.ndim!=2 or A.shape[0]!=A.shape[1] or not np.all(np.isfinite(A)):
        raise ValueError("correlation must be a finite square matrix")
    if A.shape[0] != len(axis_labels) or len(set(axis_labels)) != len(axis_labels):
        raise ValueError("correlation labels must be unique and match the matrix dimensions")
    if not np.allclose(A,A.T,rtol=0,atol=1e-12) or np.linalg.eigvalsh(A).min() < -1e-10:
        raise ValueError("correlation must be symmetric positive semidefinite")
    if X is None:
        X=np.ones((len(y),1))
    else:
        X=np.asarray(X,float)
        if X.ndim!=2 or X.shape[0]!=len(y):
            raise ValueError("X must have one row per observation")
    mask=np.isfinite(y)&np.isfinite(v)&(v>0)&np.all(np.isfinite(X),axis=1)
    if species.ndim != 1:
        raise ValueError("species must be a vector")
    mask &= np.array([not (s is None or (isinstance(s,float) and np.isnan(s))) for s in species])
    row_indices=tuple(np.flatnonzero(mask).tolist())
    y,v,species,X=y[mask],v[mask],species[mask],X[mask,:]
    if not len(y):
        raise ValueError("no usable observations")
    labels=list(dict.fromkeys(species.tolist()))
    absent=[label for label in labels if label not in axis_labels]
    if absent:
        raise ValueError(f"species absent from correlation labels: {absent}")
    idx=[axis_labels.index(label) for label in labels]
    A=A[np.ix_(idx,idx)]
    Z=np.column_stack([species==label for label in labels]).astype(float)
    projected_Z = X @ np.linalg.lstsq(X, Z, rcond=None)[0]
    confounded = np.linalg.norm(Z - projected_Z) <= 1e-10 * max(np.linalg.norm(Z), 1.0)
    if X is None: X=np.ones((len(y),1))
    p=X.shape[1]
    if np.linalg.matrix_rank(X)<p: raise ValueError("X is rank deficient")
    K=Z@A@Z.T
    def at(tau):
        C=np.diag(v)+tau*K
        sign,logdet=np.linalg.slogdet(C)
        if sign<=0: return None
        precision=np.linalg.solve(C,np.eye(len(y)))
        cov=np.linalg.solve(X.T@precision@X,np.eye(p))
        beta=cov@(X.T@precision@y)
        residual=y-X@beta
        q=float(residual@precision@residual)
        objective=.5*(logdet+np.linalg.slogdet(X.T@precision@X)[1]+q+(len(y)-p)*math.log(2*math.pi))
        return beta,cov,q,objective
    method=method.upper()
    if method=="FE": tau=0.
    elif method=="REML":
        if confounded:
            warnings.warn("phylogenetic variance is not identifiable from the fixed-effect design; setting tau2 to zero", RuntimeWarning)
            tau=0.
        else:
            from scipy.optimize import minimize_scalar
            upper=max(float(np.var(y))*100,1.)
            for _ in range(12):
                fit=minimize_scalar(lambda t:at(t)[3],bounds=(0,upper),method="bounded",options={"xatol":1e-12})
                tau=min([(0.,at(0.)[3]),(float(fit.x),fit.fun),(upper,at(upper)[3])],key=lambda z:z[1])[0]
                if tau < upper*(1-1e-6):
                    break
                upper *= 10
            else:
                raise RuntimeError("phylogenetic REML optimum remained at the expanding upper bound")
    else: raise ValueError("method must be FE or REML")
    beta,cov,q,_=at(tau)
    return MetaResult(beta,cov,float(tau),q,float("nan"),float("nan"),True,method,row_indices)
