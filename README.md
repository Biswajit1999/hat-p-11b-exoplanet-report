# HAT-P-11b — Exoplanet Atmosphere Report

A warm Neptune around an active K-dwarf, caught in the act of losing its
upper atmosphere. This repo reproduces the real, spectrally resolved
detection of escaping helium gas that made HAT-P-11b one of the first
"warm Neptunes" confirmed to be evaporating.

**[Open the full report](index.html)** (open locally in a browser, or serve
with `python -m http.server` from this directory).

## What's real here

- **System parameters** — queried live from the NASA Exoplanet Archive TAP
  service (`pscomppars`).
- **Helium transit data** — two real files from Zenodo record
  [1473463](https://zenodo.org/records/1473463) (Allart et al. 2018,
  *Science*): a phase-folded relative-flux light curve measured inside the
  He I 10830 Å line, and the per-wavelength-bin spectral excess-absorption
  profile across the triplet, both from real HARPS-N/GIANO-B transit
  observations.
- **Analysis** — `scripts/analyze_spectrum.py` computes an
  inverse-variance-weighted in-transit vs. out-of-transit flux comparison
  to quantify the real helium-escape detection. Run it yourself:

  ```bash
  pip install -r requirements.txt
  python scripts/analyze_spectrum.py
  ```

## Repository structure

```text
index.html              the report webpage
data/                    real HARPS-N/GIANO-B helium transit data (Zenodo 1473463)
scripts/analyze_spectrum.py   real in-transit vs out-of-transit analysis
figures/                 generated plot + summary_statistics.csv
```

## Key finding this repo shows directly

A real 0.827% ± 0.064% dip in flux inside the helium 10830 Å line
specifically during transit, at **12.9-sigma significance** — a highly
confident, genuine detection of gas extending well beyond the planet's
measured transit radius. This is direct spectroscopic evidence that
HAT-P-11b is actively losing atmosphere to space, driven by strong
high-energy heating from its magnetically active K-dwarf host star.

## Honest limitation

The per-wavelength-bin spectral profile combines only two individual
transit nights per bin and is noisy at that resolution (per-bin
fractional errors of order 7%+), so this repo draws its high-significance
headline result from the higher-cadence phase-folded light curve instead,
and uses the per-bin spectrum only as a descriptive, qualitative figure —
stated plainly rather than overclaiming precision the data doesn't
support.

## References

1. Bakos, G.A. et al., 2010. HAT-P-11b: A Super-Neptune Planet Transiting
   a Bright K Star in the Kepler Field. *The Astrophysical Journal*,
   710(2), pp.1724-1745.
2. Allart, R. et al., 2018. Spectrally resolved helium absorption from the
   extended atmosphere of a warm Neptune-mass exoplanet. *Science*,
   362(6421), pp.1384-1387.
3. Oklopčić, A. and Hirata, C.M., 2018. A New Window into Escaping
   Exoplanet Atmospheres: 10830 Å Line of Helium. *The Astrophysical
   Journal Letters*, 855(1), L11.
4. NASA Exoplanet Archive, <https://exoplanetarchive.ipac.caltech.edu/>.
5. Zenodo record 1473463, <https://zenodo.org/records/1473463>.

## Author

Biswajit Jana — [Portfolio](https://biswajit1999.github.io/Biswajit_Jana.github.io/) · [GitHub](https://github.com/Biswajit1999) · [LinkedIn](https://www.linkedin.com/in/biswajit-jana-27011a151/) · [ORCID](https://orcid.org/0009-0002-2411-1891)
