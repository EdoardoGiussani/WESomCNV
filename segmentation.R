#!/usr/bin/env Rscript

library(DNAcopy)
library(dplyr)

args = commandArgs(trailingOnly = T)

setwd(args[2])
cn <- read.table(args[1], header=TRUE, stringsAsFactors = FALSE)
CNA.object <- CNA(genomdat = cn[,7], chrom = cn[,1], maploc = cn [,2], data.type = 'logratio')
CNA.smoothed <- smooth.CNA(CNA.object)
segs <- segment(CNA.smoothed, verbose=0, min.width=2)

if (median(segs$output$seg.mean) > -0.001 && median(segs$output$seg.mean) < 0.001 ){

  segsp <- segments.p(segs)
  segsp$ID <- NULL
  segsp$num.mark <- NULL
  segsp$bstat <- NULL
  segsp$lcl <- NULL
  segsp$ucl <- NULL
  
  pValueFilter <- dplyr::filter(segsp, pval <= 0.00001)

  pValueFilter <- rename(pValueFilter, start = loc.start, end = loc.end, log2 = seg.mean, pVal = pval)
  write.table(pValueFilter, file = "output.r.tsv", row.names = F, col.names = T, quote = F, sep = "\t")
  cat('Centered')
} else {
  cat(median(segs$output$seg.mean))
}
