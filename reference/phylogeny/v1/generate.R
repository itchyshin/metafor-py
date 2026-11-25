archive <- Sys.getenv("METAFOR_SOURCE_ARCHIVE")
stopifnot(file.exists(archive),
          digest::digest(archive, algo="sha256", file=TRUE) ==
              "25c421cf52279294b11ab3166adfeb327dd22034a03a46487f081a19a163339b")
suppressPackageStartupMessages(library(metafor))
stopifnot(as.character(packageVersion("metafor")) == "5.2.1")
# Three species with a labelled correlation matrix and repeated observations.
A <- matrix(c(1,.6,.2,.6,1,.3,.2,.3,1),3,3,
            dimnames=list(c('sp_a','sp_b','sp_c'),c('sp_a','sp_b','sp_c')))
species <- c('sp_a','sp_a','sp_b','sp_c','sp_c')
Z <- model.matrix(~0+factor(species,levels=rownames(A)))
V <- diag(c(.10,.12,.08,.11,.09))
yi <- c(.35,.28,-.10,.42,.31)
fit <- rma.mv(yi,V,mods=~1,random=~1|species,R=list(species=A),Rscale='none',method='REML')
write.csv(data.frame(id=paste0('obs',1:5),species,yi,vi=diag(V)), 'observations.csv',row.names=FALSE)
write.csv(A,'species-correlation.csv',quote=FALSE)
write.csv(data.frame(beta=as.numeric(coef(fit)),se=fit$se,tau2=fit$sigma2[1],QE=fit$QE), 'reference.csv',row.names=FALSE)
