# Regenerate the 2x2 effect-size reference with R metafor 5.2-1.
options(digits=17)
stopifnot(as.character(packageVersion("metafor")) == "5.2.1")
archive <- Sys.getenv("METAFOR_SOURCE_ARCHIVE")
stopifnot(nzchar(archive), file.exists(archive))
stopifnot(digest::digest(file=archive, algo="sha256") ==
  "25c421cf52279294b11ab3166adfeb327dd22034a03a46487f081a19a163339b")
dat <- read.csv(file.path("..", "..", "v1", "bcg.csv"), check.names=FALSE)
out <- do.call(rbind, lapply(c("OR", "RD"), function(measure) {
  result <- metafor::escalc(measure=measure, ai=tpos, bi=tneg, ci=cpos, di=cneg,
                            data=dat, add=0.5, to="only0")
  data.frame(measure=measure, author=dat$author, yi=result$yi, vi=result$vi)
}))
write.csv(out, "bcg-effect-sizes.csv", row.names=FALSE, na="NA")
models <- do.call(rbind, lapply(c("OR", "RD"), function(measure) {
  effects <- out[out$measure == measure,]
  do.call(rbind, lapply(c("FE", "REML"), function(method) {
    fit <- metafor::rma(yi=effects$yi, vi=effects$vi, method=method)
    data.frame(measure=measure, method=method, beta=as.numeric(coef(fit)), se=fit$se,
               tau2=fit$tau2, QE=fit$QE, I2=fit$I2, H2=fit$H2,
               ci_lb=fit$ci.lb, ci_ub=fit$ci.ub)
  }))
}))
write.csv(models, "model-reference.csv", row.names=FALSE)
zero_data <- data.frame(study=c("zero-cell","complete"), ai=c(0,2), bi=c(10,8), ci=c(2,3), di=c(8,7))
zero_cells <- do.call(rbind, lapply(c("OR","RD"), function(measure) {
  do.call(rbind, lapply(c("only0","all","if0all","none"), function(policy) {
    result <- metafor::escalc(measure=measure, ai=ai, bi=bi, ci=ci, di=di,
                              data=zero_data, add=0.5, to=policy)
    data.frame(measure=measure, policy=policy, study=zero_data$study,
               yi=result$yi, vi=result$vi)
  }))
}))
write.csv(zero_cells, "zero-cell-reference.csv", row.names=FALSE, na="NA")
packages <- c("metafor", "digest", "Matrix", "numDeriv", "nlme", "mathjaxr", "pbapply")
versions <- data.frame(
  package=c("R", packages),
  version=c(R.version.string, vapply(packages, function(package) {
    if (requireNamespace(package, quietly=TRUE)) as.character(packageVersion(package)) else NA_character_
  }, character(1)))
)
write.csv(versions, "versions.csv", row.names=FALSE)
cat("EFFECT_SIZE_REFERENCE_OK", nrow(out), "rows\n")
