# Mendelian randomization

**Rules:** `workflow/rules/mr.smk` · **Status:** planned; rules and parameters are in place, scripts not yet written.

- **Exposures:** circulating omega-3, DHA, omega-6, omega-6:omega-3 ratio, linoleic acid (public GWAS).
- **Outcome:** rheumatoid arthritis (public GWAS).
- **Instruments:** p < 5 × 10⁻⁸, clumped at r² < 0.001 within 10 Mb.
- **Methods:** inverse-variance weighted, MR-Egger, weighted median; colocalization at key loci such as FADS1/2.
- **Reverse MR:** RA genetic liability on fatty-acid levels.
