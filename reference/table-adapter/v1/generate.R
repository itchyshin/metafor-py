# Run from the repository root with the pinned reference R library available.
stopifnot(as.character(packageVersion("metafor")) == "5.2.1")
archive <- Sys.getenv("METAFOR_SOURCE_ARCHIVE")
stopifnot(file.exists(archive),
          digest::digest(archive, algo="sha256", file=TRUE) ==
              "25c421cf52279294b11ab3166adfeb327dd22034a03a46487f081a19a163339b")
bcg <- read.csv("reference/v1/bcg.csv")
bcg$ablat[bcg$trial == 4] <- NA_real_
es <- metafor::escalc(measure="RR", ai=tpos, bi=tneg, ci=cpos, di=cneg, data=bcg)
fit <- metafor::rma.uni(yi, vi, mods=~ablat, data=es, method="REML")
keep <- !is.na(es$ablat)
design <- model.matrix(~ablat, es[keep, ])
stopifnot(identical(dim(design), dim(fit$X)),
          isTRUE(all.equal(as.numeric(design), as.numeric(fit$X))))
dir <- "reference/table-adapter/v1"
write.csv(data.frame(trial=es$trial[keep], intercept=design[,1], ablat=design[,2]),
          file.path(dir, "design.csv"), row.names=FALSE)
write.csv(data.frame(term=names(coef(fit)), estimate=unname(coef(fit))),
          file.path(dir, "coefficients.csv"), row.names=FALSE)
writeLines(c(R.version.string, paste("metafor", packageVersion("metafor")),
             paste("metadat", packageVersion("metadat"))),
           file.path(dir, "REFERENCE-VERSIONS.txt"))
