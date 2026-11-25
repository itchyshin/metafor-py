#!/usr/bin/env Rscript

# Regenerate the shared, synthetic dependent-effects reference using the exact
# metafor release pinned in PROVENANCE.md. No tutorial prose, figures, or
# third-party datasets are copied into these fixtures.

archive <- Sys.getenv("METAFOR_SOURCE_ARCHIVE")
stopifnot(file.exists(archive),
          digest::digest(archive, algo="sha256", file=TRUE) ==
              "25c421cf52279294b11ab3166adfeb327dd22034a03a46487f081a19a163339b")
suppressPackageStartupMessages(library(metafor))
if (as.character(packageDescription("metafor")$Version) != "5.2-1") {
  stop("metafor 5.2-1 is required; see PROVENANCE.md")
}
script_arg <- grep("^--file=", commandArgs(), value = TRUE)[1]
here <- dirname(normalizePath(sub("^--file=", "", script_arg)))

write_matrix <- function(x, path) {
  rownames(x) <- as.character(seq_len(nrow(x)))
  colnames(x) <- as.character(seq_len(ncol(x)))
  write.csv(x, file.path(here, path), row.names = TRUE)
}

estimate_rows <- list()
covariance_rows <- list()
warning_rows <- list()
add <- function(model, fit, components = list()) {
  b <- as.numeric(fit$beta)
  labels <- rownames(fit$beta)
  if (is.null(labels)) labels <- names(fit$beta)
  if (is.null(labels)) labels <- paste0("beta", seq_along(b))
  for (i in seq_along(b)) {
    estimate_rows[[length(estimate_rows) + 1L]] <<- data.frame(
      model = model, quantity = "beta", name = labels[i], estimate = b[i])
    for (stat in c("se", "ci.lb", "ci.ub")) {
      values <- as.numeric(fit[[stat]])
      estimate_rows[[length(estimate_rows) + 1L]] <<- data.frame(
        model = model, quantity = stat, name = labels[i], estimate = values[i])
    }
  }
  B <- as.matrix(vcov(fit))
  for (i in seq_len(nrow(B))) for (j in seq_len(ncol(B))) {
    covariance_rows[[length(covariance_rows) + 1L]] <<- data.frame(
      model = model, row = rownames(B)[i], column = colnames(B)[j], estimate = B[i, j])
  }
  for (name in c("QE", "QEp", "k", "p", "ll")) {
    value <- fit[[name]]
    if (!is.null(value) && length(value) == 1L && is.finite(value)) {
      estimate_rows[[length(estimate_rows) + 1L]] <<- data.frame(
        model = model, quantity = name, name = name, estimate = as.numeric(value))
    }
  }
  for (entry in components) {
    estimate_rows[[length(estimate_rows) + 1L]] <<- data.frame(
      model = model, quantity = entry$quantity, name = entry$name,
      estimate = entry$estimate)
  }
  invisible(fit)
}

capture_fit <- function(model, expression) {
  withCallingHandlers(expression, warning = function(w) {
    warning_rows[[length(warning_rows) + 1L]] <<- data.frame(
      model = model, category = "R-warning", message = conditionMessage(w))
    invokeRestart("muffleWarning")
  })
}

# 1. Correlated sampling errors with fixed-effect GLS. The random intercept is
#    fixed to zero so metafor evaluates the supplied full V without estimating G.
set.seed(1101)
n <- 8L
x <- seq(-1, 1, length.out = n)
vi <- seq(0.05, 0.12, length.out = n)
R <- 0.42 ^ abs(outer(seq_len(n), seq_len(n), `-`))
V <- outer(sqrt(vi), sqrt(vi)) * R
X <- model.matrix(~ x)
yi <- drop(X %*% c(0.20, 0.12) + t(chol(V)) %*% rnorm(n))
gls <- data.frame(row_id = seq_len(n), yi = yi, vi = vi, x = x,
                  study = factor(rep(seq_len(n / 2), each = 2)))
write.csv(gls, file.path(here, "gls-rows.csv"), row.names = FALSE)
write_matrix(V, "gls-V.csv")
fit_gls <- capture_fit("correlated-gls", rma.mv(
  yi, V = V, mods = ~ x, random = ~ 1 | study, sigma2 = 0,
  data = gls, method = "REML"))
add("correlated-gls", fit_gls)

# 2. Two nested scalar random intercepts. Local effect labels 1:3 repeat under
#    every study; effect_key makes the intended nested identity explicit.
set.seed(42)
ns <- 12L
ne <- 3L
n <- ns * ne
nested <- expand.grid(study = seq_len(ns), effect_local = seq_len(ne))
nested$row_id <- seq_len(n)
nested$x <- rep(c(-1, 0, 1), ns)
nested$vi <- rep(c(0.08, 0.10, 0.12), ns)
study_shock <- rnorm(ns, 0, 0.35)
effect_shock <- rnorm(n, 0, 0.20)
nested$yi <- 0.35 + 0.18 * nested$x + study_shock[nested$study] +
  effect_shock + rnorm(n, 0, sqrt(nested$vi))
nested$study <- factor(nested$study)
nested$effect_key <- interaction(nested$study, nested$effect_local, drop = TRUE)
nested <- nested[, c("row_id", "yi", "vi", "x", "study", "effect_local", "effect_key")]
write.csv(nested, file.path(here, "nested-rows.csv"), row.names = FALSE)
write_matrix(diag(nested$vi), "nested-V.csv")
fit_nested <- capture_fit("nested-reml", rma.mv(
  yi, V = diag(nested$vi), mods = ~ x,
  random = list(~ 1 | study, ~ 1 | effect_key), data = nested, method = "REML"))
add("nested-reml", fit_nested, list(
  list(quantity = "variance", name = "study", estimate = fit_nested$sigma2[1]),
  list(quantity = "variance", name = "nested-effect", estimate = fit_nested$sigma2[2])))

# 3. Synthetic Berkey-style two-outcome model. Both sampling errors and the
#    study random effects are correlated within study; Sigma is unstructured.
set.seed(42)
ns <- 20L
outcomes <- c("benefit", "harm")
Sigma <- matrix(c(0.20, 0.07, 0.07, 0.12), nrow = 2)
V_block <- diag(sqrt(c(0.06, 0.09))) %*%
  matrix(c(1, 0.30, 0.30, 1), nrow = 2) %*%
  diag(sqrt(c(0.06, 0.09)))
u <- matrix(rnorm(ns * 2), nrow = ns, ncol = 2) %*% chol(Sigma)
e <- matrix(rnorm(ns * 2), nrow = ns, ncol = 2) %*% chol(V_block)
berkey <- data.frame(
  row_id = seq_len(ns * 2), study = factor(rep(seq_len(ns), each = 2)),
  outcome = factor(rep(outcomes, times = ns), levels = outcomes),
  vi = rep(c(0.06, 0.09), times = ns),
  yi = rep(c(0.40, 0.25), times = ns) + as.vector(t(u)) + as.vector(t(e)))
Vb <- matrix(0, nrow = ns * 2, ncol = ns * 2)
for (s in seq_len(ns)) {
  ix <- (2L * s - 1L):(2L * s)
  Vb[ix, ix] <- V_block
}
write.csv(berkey, file.path(here, "berkey-rows.csv"), row.names = FALSE)
write_matrix(Vb, "berkey-V.csv")
fit_berkey <- capture_fit("berkey-un", rma.mv(
  yi, V = Vb, mods = ~ 0 + outcome, random = ~ outcome | study,
  struct = "UN", data = berkey, method = "REML"))
Sigma_hat <- matrix(c(fit_berkey$tau2[1],
                      fit_berkey$rho[1] * sqrt(prod(fit_berkey$tau2)),
                      fit_berkey$rho[1] * sqrt(prod(fit_berkey$tau2)),
                      fit_berkey$tau2[2]), nrow = 2)
add("berkey-un", fit_berkey, list(
  list(quantity = "variance", name = outcomes[1], estimate = Sigma_hat[1, 1]),
  list(quantity = "variance", name = outcomes[2], estimate = Sigma_hat[2, 2]),
  list(quantity = "covariance", name = "benefit-harm", estimate = Sigma_hat[1, 2]),
  list(quantity = "correlation", name = "benefit-harm", estimate = fit_berkey$rho[1])))

write.csv(do.call(rbind, estimate_rows), file.path(here, "results.csv"), row.names = FALSE)
write.csv(do.call(rbind, covariance_rows), file.path(here, "coefficient-covariance.csv"), row.names = FALSE)
warnings <- if (length(warning_rows)) do.call(rbind, warning_rows) else
  data.frame(model = character(), category = character(), message = character())
write.csv(warnings, file.path(here, "warnings.csv"), row.names = FALSE)
writeLines(c(
  paste("R", as.character(getRversion())),
  paste("metafor", as.character(packageDescription("metafor")$Version)),
  paste("metadat", as.character(packageVersion("metadat"))),
  paste("Matrix", as.character(packageVersion("Matrix"))),
  paste("numDeriv", as.character(packageVersion("numDeriv"))),
  paste("nlme", as.character(packageVersion("nlme"))),
  paste("mathjaxr", as.character(packageVersion("mathjaxr"))),
  paste("pbapply", as.character(packageVersion("pbapply"))),
  paste("digest", as.character(packageVersion("digest"))),
  "optimizer: metafor 5.2-1 rma.mv defaults (nlminb)",
  "random data seeds: correlated GLS 1101; nested 42; Berkey-style 42",
  "GLS generating beta: intercept=0.20; x=0.12",
  "nested generating beta: intercept=0.35; x=0.18; study variance=0.1225; nested-effect variance=0.04",
  "Berkey-style generating beta: benefit=0.40; harm=0.25; Sigma=[[0.20,0.07],[0.07,0.12]]",
  "Berkey-style sampling correlation within study: 0.30"
), file.path(here, "REFERENCE-VERSIONS.txt"))

message("Wrote dependent-effects fixtures and references to ", here)
