"""Native meta-analysis primitives, starting with the BCG example."""
from .core import (DependentMetaResult, DependentTableMetaResult, MetaResult,
                   PredictionResult, TableMetaResult, escalc_or, escalc_rd, escalc_rr,
                   fit_meta, fit_meta_formula, fit_phylo,
                   forest_plot_data)
from .dependent import fit_meta_cov, fit_meta_cov_formula, fit_meta_nested, fit_meta_un
from .plotting import write_forest_svg

__all__ = ["DependentMetaResult", "DependentTableMetaResult", "MetaResult",
           "PredictionResult", "TableMetaResult", "escalc_or", "escalc_rd", "escalc_rr", "fit_meta",
           "fit_meta_formula", "fit_meta_cov", "fit_meta_cov_formula",
           "fit_meta_nested", "fit_meta_un", "fit_phylo",
           "forest_plot_data", "write_forest_svg"]
