# Coverage inventory: metafor-py against R metafor 5.2-1

## Baseline and method

The comparison target is the official [CRAN source archive for metafor 5.2-1](https://cran.r-project.org/src/contrib/metafor_5.2-1.tar.gz), SHA-256 `25c421cf52279294b11ab3166adfeb327dd22034a03a46487f081a19a163339b`. The checksum is recorded in the BCG reference provenance and was independently checked against the downloaded archive for this inventory. The [CRAN package page](https://cran.r-project.org/web/packages/metafor/) and [reference manual](https://cran.r-project.org/web/packages/metafor/metafor.pdf) describe that release; the official [function overview](https://cran.r-project.org/web/packages/metafor/vignettes/diagram.pdf) groups its workflow.

The inventory reads the exports from that archive's R namespace with `getNamespaceExports()`. It contains **280 exported names**, including S3 methods and operators as well as user-facing functions. Each name appears once below, grouped by its main function family. `metafor` uses `exportPattern("^[^\.]")`; this count describes every name exported by the pinned namespace, including methods and operators; high-level model functions are a smaller subset.

These are coverage targets, not names re-exported by metafor-py. Both projects are native implementations with their own APIs. “Narrow analogue” means a related capability exists for the stated cases; it does not mean the R call, defaults, options, warnings, result classes, or method dispatch are compatible. The seven partial entries below describe only the exercised native scope. The other 273 exported names have no ported analogue in this phase.

## Native API and runtime boundary

metafor-py provides `escalc_rr`, `escalc_or`, `escalc_rd`, `fit_meta`, `fit_meta_formula`, `fit_phylo`, `MetaResult.predict` method, `forest_plot_data`, `fit_meta_cov`, `fit_meta_cov_formula`, `fit_meta_nested`, and `fit_meta_un`; result types and the dependency-free `write_forest_svg` helper are also exported.

Neither native package requires R or the R `metafor` package at runtime. R and the pinned archive are used to regenerate reference fixtures. Julia's table/formula support uses its declared StatsModels and Tables dependencies. Python's base package uses NumPy and SciPy; its formula/table adapter needs the optional pandas and Patsy extra. `write_forest_svg` uses Python's standard library; it does not establish the broader `forest()` plotting API.

## Coverage by family

| R export family | Names | Narrow native analogue(s) | Not covered in this family |
|---|---:|---|---:|
| Effect sizes and sampling covariance | 76 | `escalc` (only 2×2 RR, OR, and RD cases) | 75 |
| Model fitting and selection | 10 | `rma`, `rma.uni`, `rma.mv` (limited FE/REML and supplied-covariance cases) | 7 |
| Inference and fitted-model results | 99 | `predict.rma` (normal intervals for supported fitted results) | 98 |
| Plots and visual summaries | 38 | `forest`, `forest.rma` (forest coordinates; Python also writes one SVG form) | 36 |
| Diagnostics, sensitivity, and bias checks | 31 | none | 31 |
| Utilities and data helpers | 26 | none | 26 |
| **Total** | **280** | **7 partial names** | **273 not yet ported** |

The inventory covers exported function names; the full set of options has not yet been listed or tested. The long-term target is parity across the public functions **and their documented options and behaviors**, plus native documentation for each ported function and option. The compatibility matrix records the option boundaries of the current slice; later phases must expand that inventory family by family.

<details>
<summary>Diagnostics, sensitivity, and bias checks (31 exported names)</summary>

`cooks.distance.rma.mv`, `cooks.distance.rma.uni`, `cumul`, `cumul.rma.mh`, `cumul.rma.peto`, `cumul.rma.uni`, `dfbetas.rma.mv`, `dfbetas.rma.uni`, `fsn`, `hatvalues.rma.mv`, `hatvalues.rma.uni`, `hc`, `hc.rma.uni`, `hettest`, `influence.rma.uni`, `leave1out`, `leave1out.rma.mh`, `leave1out.rma.peto`, `leave1out.rma.uni`, `permutest`, `permutest.rma.ls`, `permutest.rma.uni`, `ranktest`, `regtest`, `robust`, `robust.rma.mv`, `robust.rma.uni`, `trimfill`, `trimfill.rma.uni`, `vif`, `vif.rma`

</details>

<details>
<summary>Effect sizes and sampling covariance (76 exported names)</summary>

`[.escalc`, `$<-.escalc`, `aggregate.escalc`, `bldiag`, `blsplit`, `cbind.escalc`, `cmicalc`, `contrmat`, `conv.2x2`, `conv.delta`, `conv.fivenum`, `conv.wald`, `escalc`, `pairmat`, `rbind.escalc`, `rcalc`, `transf.abt`, `transf.ahw`, `transf.arcsin`, `transf.clestod`, `transf.dtobesd`, `transf.dtocles`, `transf.dtocles.int`, `transf.dtocliffd`, `transf.dtolnor.logis`, `transf.dtolnor.norm`, `transf.dtomd`, `transf.dtoovl`, `transf.dtorbis`, `transf.dtorpb`, `transf.dtou1`, `transf.dtou2`, `transf.dtou3`, `transf.exp.int`, `transf.exp.mode`, `transf.iabt`, `transf.iabt.int`, `transf.iabt.mode`, `transf.iahw`, `transf.iahw.int`, `transf.iahw.mode`, `transf.iarcsin`, `transf.iarcsin.int`, `transf.iarcsin.mode`, `transf.iirft`, `transf.ilogit`, `transf.ilogit.int`, `transf.ilogit.mode`, `transf.ipft`, `transf.ipft.hm`, `transf.iprobit`, `transf.iprobit.int`, `transf.iprobit.mode`, `transf.irft`, `transf.isqrt`, `transf.lnortod.logis`, `transf.lnortod.norm`, `transf.lnortord`, `transf.lnortorr`, `transf.lnortortet.digby`, `transf.lnortortet.pearson`, `transf.logit`, `transf.pft`, `transf.probit`, `transf.r2toz`, `transf.rpbtod`, `transf.rpbtorbis`, `transf.rtod`, `transf.rtorpb`, `transf.rtoz`, `transf.ztor`, `transf.ztor.int`, `transf.ztor.mode`, `transf.ztor2`, `vcalc`, `vec2mat`

</details>

<details>
<summary>Inference and fitted-model results (99 exported names)</summary>

`[.list.rma`, `$<-.list.rma`, `AIC.matreg`, `AIC.rma`, `anova.rma`, `as.data.frame.anova.rma`, `as.data.frame.confint.rma`, `as.data.frame.list.anova.rma`, `as.data.frame.list.confint.rma`, `as.data.frame.list.rma`, `as.data.frame.vif.rma`, `as.matrix.list.rma`, `BIC.matreg`, `BIC.rma`, `blup`, `blup.rma.uni`, `coef.deltamethod`, `coef.matreg`, `coef.permutest.rma.uni`, `coef.rma`, `coef.summary.rma`, `confint.matreg`, `confint.rma.glmm`, `confint.rma.ls`, `confint.rma.mh`, `confint.rma.mv`, `confint.rma.peto`, `confint.rma.uni`, `confint.rma.uni.selmodel`, `deviance.rma`, `df.residual.rma`, `fitstats`, `fitstats.rma`, `fitted.rma`, `formula.rma`, `logLik.matreg`, `logLik.rma`, `model.matrix.rma`, `nobs.rma`, `predict.matreg`, `predict.rma`, `predict.rma.ls`, `print.anova.rma`, `print.confint.matreg`, `print.confint.rma`, `print.deltamethod`, `print.escalc`, `print.fsn`, `print.gosh.rma`, `print.hc.rma.uni`, `print.hettest`, `print.infl.rma.uni`, `print.list.anova.rma`, `print.list.confint.rma`, `print.list.rma`, `print.matreg`, `print.permutest.rma.uni`, `print.profile.rma`, `print.ranktest`, `print.regtest`, `print.rma.glmm`, `print.rma.mh`, `print.rma.mv`, `print.rma.peto`, `print.rma.uni`, `print.summary.matreg`, `print.summary.rma`, `print.tes`, `print.vcovmat`, `print.vif.rma`, `profile.rma.ls`, `profile.rma.mv`, `profile.rma.uni`, `profile.rma.uni.selmodel`, `ranef.rma.mv`, `ranef.rma.uni`, `residuals.rma`, `rstandard.rma.mh`, `rstandard.rma.mv`, `rstandard.rma.peto`, `rstandard.rma.uni`, `rstudent.rma.mh`, `rstudent.rma.mv`, `rstudent.rma.peto`, `rstudent.rma.uni`, `se.default`, `se.rma`, `sigma.matreg`, `summary.escalc`, `summary.matreg`, `summary.rma`, `vcov.deltamethod`, `vcov.matreg`, `vcov.rma`, `weights.rma.glmm`, `weights.rma.mh`, `weights.rma.mv`, `weights.rma.peto`, `weights.rma.uni`

</details>

<details>
<summary>Model fitting and selection (10 exported names)</summary>

`matreg`, `rma`, `rma.glmm`, `rma.mh`, `rma.mv`, `rma.peto`, `rma.uni`, `selmodel`, `selmodel.rma.uni`, `ma.uni`

</details>

<details>
<summary>Plots and visual summaries (38 exported names)</summary>

`addpoly`, `addpoly.default`, `addpoly.predict.rma`, `addpoly.rma`, `baujat`, `baujat.rma`, `forest`, `forest.cumul.rma`, `forest.default`, `forest.rma`, `funnel`, `funnel.default`, `funnel.rma`, `gosh`, `gosh.rma`, `labbe`, `labbe.rma`, `llplot`, `plot.cumul.rma`, `plot.gosh.rma`, `plot.infl.rma.uni`, `plot.permutest.rma.uni`, `plot.profile.rma`, `plot.rma.glmm`, `plot.rma.mh`, `plot.rma.mv`, `plot.rma.peto`, `plot.rma.uni`, `plot.rma.uni.selmodel`, `plot.vif.rma`, `points.regplot`, `qqnorm.rma.glmm`, `qqnorm.rma.mh`, `qqnorm.rma.mv`, `qqnorm.rma.peto`, `qqnorm.rma.uni`, `radial`, `regplot`

</details>

<details>
<summary>Utilities and data helpers (26 exported names)</summary>

`[.vcovmat`, `deltamethod`, `dfround`, `emmprep`, `fmtp`, `fmtp2`, `fmtt`, `fmtx`, `getmfopt`, `head.list.rma`, `metafor.news`, `radial.rma`, `ranef`, `regplot.rma`, `replmiss`, `reporter`, `reporter.rma.uni`, `se`, `setmfopt`, `simulate.rma`, `tail.list.rma`, `tes`, `to.long`, `to.table`, `to.wide`, `update.rma`

</details>

## Roadmap

1. **Phase 0: inventory and boundary.** Record the pinned public-export baseline, current native scope, exclusions, and dependencies. This document and the compatibility matrix are that baseline.
2. **Phase 1: KNHA.** Add and validate Knapp–Hartung small-sample inference for the supported univariate model, including its public options and interval behavior. Keep normal-inference results distinct from KNHA results.
3. **Phase 2: actual Berkey example.** Reproduce the published `dat.berkey1998` analysis using the real dataset and its documented provenance. The existing synthetic two-outcome fixture serves only as a software check and remains clearly distinct from the real dataset.
4. **Broader parity.** Extend multivariate model families and options, then the remaining effect-size, diagnostic, inference, visualization, and utility families. Add native API documentation alongside each implemented capability, with fixture-backed claims kept separate from untested options.

Full parity is reached only when every public function and documented option in the pinned R release is implemented, validated, and documented in the native API. Each unimplemented item remains a visible gap; a documented gap does not count as parity.
