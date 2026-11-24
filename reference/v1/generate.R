# Regenerate using metafor 5.2-1 and metadat 1.6.0; see PROVENANCE.md.
stopifnot(as.character(packageVersion('metafor')) == '5.2.1')
archive <- Sys.getenv('METAFOR_SOURCE_ARCHIVE')
stopifnot(nzchar(archive), file.exists(archive))
stopifnot(digest::digest(file=archive, algo='sha256') == '25c421cf52279294b11ab3166adfeb327dd22034a03a46487f081a19a163339b')
suppressPackageStartupMessages(library(metafor))
stopifnot(as.character(packageVersion('metadat')) == '1.6.0')
data(dat.bcg, package='metadat')
dat <- escalc(measure='RR', ai=tpos, bi=tneg, ci=cpos, di=cneg, data=dat.bcg)
fe <- rma(yi, vi, data=dat, method='FE')
re <- rma(yi, vi, data=dat, method='REML')
mod <- rma(yi, vi, mods=~ablat, data=dat, method='REML')
extract <- function(x) list(beta=unname(as.vector(coef(x))), se=unname(x$se), vcov=unname(as.matrix(vcov(x))), ci_lb=unname(x$ci.lb), ci_ub=unname(x$ci.ub), tau2=x$tau2, QE=x$QE, QEp=x$QEp, I2=x$I2, H2=x$H2, row_indices=seq_len(length(x$yi)))
pred <- predict(mod, newmods=c(0,30,60))
pooled <- predict(re)
forest <- list(row=seq_len(nrow(dat)), label=as.character(dat.bcg$author),
               estimate=unname(dat$yi), se=sqrt(unname(dat$vi)),
               ci_lb=unname(dat$yi-qnorm(.975)*sqrt(dat$vi)),
               ci_ub=unname(dat$yi+qnorm(.975)*sqrt(dat$vi)),
               summary=list(estimate=unname(pooled$pred), se=unname(pooled$se),
                            ci_lb=unname(pooled$ci.lb), ci_ub=unname(pooled$ci.ub),
                            pi_lb=unname(pooled$pi.lb), pi_ub=unname(pooled$pi.ub), tau2=re$tau2))
design <- list(FE=matrix(1,nrow(dat),1), REML=matrix(1,nrow(dat),1),
               moderator=model.matrix(~ablat,data=dat))
design_columns <- list(FE=names(coef(fe)), REML=names(coef(re)),
                       moderator=names(coef(mod)))
result <- list(versions=list(R=R.version.string, metafor=as.character(packageVersion('metafor')), metadat=as.character(packageVersion('metadat')), dependencies=setNames(lapply(c('Matrix','numDeriv','nlme','mathjaxr','pbapply','digest','jsonlite'), function(p) as.character(packageVersion(p))),c('Matrix','numDeriv','nlme','mathjaxr','pbapply','digest','jsonlite'))), yi=unname(dat$yi), vi=unname(dat$vi), design=design, design_columns=design_columns, fe=extract(fe), reml=extract(re), moderator=extract(mod), prediction=list(latitude=c(0,30,60), pred=unname(pred$pred), se=unname(pred$se), ci_lb=unname(pred$ci.lb), ci_ub=unname(pred$ci.ub), pi_lb=unname(pred$pi.lb), pi_ub=unname(pred$pi.ub)), forest=forest)
write.csv(as.data.frame(dat.bcg), 'bcg.csv', row.names=FALSE, na='')
jsonlite::write_json(result, 'bcg-reference.json', auto_unbox=TRUE, pretty=TRUE, digits=16, na='null')
