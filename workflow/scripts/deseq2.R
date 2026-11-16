# Snakemake script: DESeq2 differential expression and variance-stabilized matrix.
log <- file(snakemake@log[[1]], open = "wt"); sink(log); sink(log, type = "message")
suppressPackageStartupMessages({ library(DESeq2); library(data.table) })

counts <- fread(snakemake@input[["counts"]])          # samples x genes, first column sample_id
samples <- fread(snakemake@input[["samples"]])         # must contain sample_id + design variables
mat <- t(as.matrix(counts[, -1])); colnames(mat) <- counts$sample_id
coldata <- as.data.frame(samples)[match(colnames(mat), samples$sample_id), ]
rownames(coldata) <- coldata$sample_id
stopifnot(!any(is.na(coldata$sample_id)))

design <- as.formula(snakemake@params[["design"]])
for (v in all.vars(design)) coldata[[v]] <- factor(coldata[[v]])

dds <- DESeqDataSetFromMatrix(round(mat), coldata, design)
dds <- dds[rowSums(counts(dds) >= 10) >= 3, ]
dds <- DESeq(dds, parallel = FALSE)

contrast <- unlist(snakemake@params[["contrast"]])
res <- results(dds, contrast = contrast, alpha = 0.05)
out <- data.frame(gene = rownames(res), as.data.frame(res))
fwrite(out[order(out$pvalue), ], snakemake@output[["results"]], sep = "\t")

vst_mat <- assay(vst(dds, blind = FALSE))
fwrite(data.frame(sample_id = colnames(vst_mat), t(vst_mat), check.names = FALSE),
       snakemake@output[["vst"]], sep = "\t")
