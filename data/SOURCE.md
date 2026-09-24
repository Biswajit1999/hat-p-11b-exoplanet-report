# Data source

Both files are real reduced data products from Zenodo record
**1473463**, "Spectrally resolved helium absorption from the extended
atmosphere of a warm Neptune exoplanet" (Allart et al. 2018, *Science*,
362, 1384-1387), downloaded 2026-08-11 from
<https://zenodo.org/records/1473463>, archive
`Science_Allart_HAT-P-11b.zip`, folder `Files/Fig2/`.

The outer archive is 23,031,073 bytes and has Zenodo-reported and
independently reproduced MD5 `73e950dc65e278088fc8bc24fd644a50`.
The exact archive-member paths, member sizes, MD5 values, local renamed paths,
and canonical-LF SHA-256 values are in `data/zenodo_manifest.csv`. The local
files are content-identical after newline normalization; their working-tree
bytes may use CRLF on Windows. Run `python scripts/verify_zenodo_provenance.py`
for the offline check, or supply the downloaded ZIP with `--archive` to verify
the outer archive and member bytes too. Audit performed 2026-09-25.

- `helium_10830_line_profile.txt` (source: `Fig_2a.txt`) — the real
  helium 10830 A triplet absorption-line profile from CARMENES
  spectra (3.5 m telescope, Calar Alto Observatory): wavelength in air
  Angstroms, two individual-night excess
  in-transit absorption measurements (`data_1`, `data_2`), their mean
  and error (`data_mean`, `data_err_mean`), and the best-fit model
  excess absorption (`model`). 104 real wavelength bins.
- `helium_absorption_lightcurve.txt` (source: `Fig_2b_mean.txt`) — the
  real orbital-phase-folded relative flux measured inside the He 10830 A
  line during transit, combining both real transit nights: columns
  `Phase`, `Phase_err`, `flux`, `flux_err`. 18 real data points.

No numeric values were altered; files were renamed only for clarity.
The original archive also contains a best-fit model transit curve
(`Fig_2b_model.txt`) and full-resolution simulation cubes, not included
here to keep this repository small — see the Zenodo record directly for
those.

**Honest note on the line-profile file:** with only two individual
transit nights averaged per wavelength bin, `helium_10830_line_profile.txt`
is noisy at the single-bin level (per-bin fractional errors of order
7-20%). This repo's analysis therefore draws its main quantitative
result from the phase-folded light curve file, which combines many more
in-transit exposures, and uses the line-profile file only for a
qualitative, descriptive figure of the absorption region.

**Honest note on our headline statistic vs. the published one:** this
repo's own in-transit-vs-out-of-transit weighted-mean statistic
(0.827% +/- 0.064%, treating each phase-folded point as independent) is
a different estimator from the paper's own combined result, obtained
via a proper transit-model fit in a fixed 0.75 A passband: **1.08% +/-
0.05%**, with the two individual transits at 0.82% +/- 0.09% and 1.21%
+/- 0.06% (Allart et al. 2018). Both numbers are reported side by side
in this repo rather than treating our own simpler statistic as a
reproduction of the paper's measurement.
