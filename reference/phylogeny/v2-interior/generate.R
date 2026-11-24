suppressPackageStartupMessages(library(metafor))
stopifnot(as.character(packageVersion("metafor")) == "5.2.1")
obs <- read.csv("observations.csv", stringsAsFactors=FALSE)
raw <- read.csv("species-correlation.csv", row.names=1, check.names=FALSE)
A <- as.matrix(raw)
stopifnot(identical(rownames(A),colnames(A)))
fit <- rma.mv(yi, V=vi, random=~1|species, data=obs,
              R=list(species=A), Rscale="none", method="REML")
pred <- predict(fit)
out <- data.frame(beta=coef(fit)[1], se=fit$se[1], tau2=fit$sigma2[1],
                  ci_lb=fit$ci.lb[1], ci_ub=fit$ci.ub[1],
                  pi_lb=pred$pi.lb[1], pi_ub=pred$pi.ub[1],
                  logLik=as.numeric(logLik(fit)))
write.csv(out,"reference.csv",row.names=FALSE)
