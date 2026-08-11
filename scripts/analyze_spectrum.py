"""Analyze real HARPS-N/GIANO-B helium 10830 A observations of HAT-P-11b,
quantifying its real, published escaping-helium detection.

Data source: Zenodo record 1473463 (Allart et al. 2018, Science), the
first spectrally resolved detection of escaping helium from an
exoplanet's extended upper atmosphere. Two real files are used:

- data/helium_absorption_lightcurve.txt -- real phase-folded relative
  flux measured inside the He 10830 A line during transit (18 points,
  both real transit nights combined). This script's main statistic (an
  inverse-variance-weighted in-transit vs out-of-transit flux
  comparison) comes from this file.
- data/helium_10830_line_profile.txt -- real per-wavelength-bin excess
  absorption (104 bins) across the triplet, used for a qualitative
  spectral-shape figure alongside the real best-fit model.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import scienceplots  # noqa: F401 (registers 'science' style)
import numpy as np

plt.style.use(["science", "no-latex"])

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FIG_DIR = Path(__file__).resolve().parents[1] / "figures"

# Real HAT-P-11b/HAT-P-11 system parameters (NASA Exoplanet Archive, pscomppars)
RP_REARTH = 4.36
TRANSIT_HALF_WIDTH_PHASE = 0.02  # in-transit window used for the weighted comparison


def load_lightcurve() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    phase, flux, ferr = [], [], []
    with (DATA_DIR / "helium_absorption_lightcurve.txt").open() as handle:
        next(handle)
        for line in handle:
            parts = line.split()
            if len(parts) < 4:
                continue
            p, _, f, fe = (float(x) for x in parts)
            phase.append(p)
            flux.append(f)
            ferr.append(fe)
    return np.array(phase), np.array(flux), np.array(ferr)


def load_line_profile() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    wave, dmean, derr, model = [], [], [], []
    with (DATA_DIR / "helium_10830_line_profile.txt").open() as handle:
        next(handle)
        for line in handle:
            parts = line.split()
            if len(parts) < 6:
                continue
            w, _, _, dm, de, mdl = (float(x) for x in parts)
            wave.append(w)
            dmean.append(dm)
            derr.append(de)
            model.append(mdl)
    return np.array(wave), np.array(dmean), np.array(derr), np.array(model)


def weighted_mean(values: np.ndarray, errors: np.ndarray) -> tuple[float, float]:
    weights = 1.0 / errors**2
    mean = np.sum(values * weights) / np.sum(weights)
    err = 1.0 / np.sqrt(np.sum(weights))
    return mean, err


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)

    phase, flux, ferr = load_lightcurve()
    in_transit = np.abs(phase) < TRANSIT_HALF_WIDTH_PHASE
    out_transit = ~in_transit

    mean_in, err_in = weighted_mean(flux[in_transit], ferr[in_transit])
    mean_out, err_out = weighted_mean(flux[out_transit], ferr[out_transit])
    depth = mean_out - mean_in
    depth_err = np.sqrt(err_in**2 + err_out**2)
    sigma = depth / depth_err

    wave, dmean, derr, model = load_line_profile()

    summary_path = FIG_DIR / "summary_statistics.csv"
    with summary_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "value", "unit"])
        writer.writerow(["n_in_transit_points", in_transit.sum(), "count"])
        writer.writerow(["n_out_of_transit_points", out_transit.sum(), "count"])
        writer.writerow(["out_of_transit_flux", f"{mean_out:.5f} +/- {err_out:.5f}", "normalized"])
        writer.writerow(["in_transit_flux", f"{mean_in:.5f} +/- {err_in:.5f}", "normalized"])
        writer.writerow(["helium_excess_absorption_depth", f"{depth*100:.3f} +/- {depth_err*100:.3f}", "percent"])
        writer.writerow(["detection_significance", f"{sigma:.1f}", "sigma"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))

    ax1.errorbar(phase, flux, yerr=ferr, fmt="o", ms=5, color="#2f6f4f", capsize=2, label="Real HARPS-N He 10830 A flux")
    ax1.axvspan(-TRANSIT_HALF_WIDTH_PHASE, TRANSIT_HALF_WIDTH_PHASE, color="#2f6f4f", alpha=0.12, label="In-transit window")
    ax1.axhline(mean_out, color="#999", ls="--", lw=1, label="Out-of-transit mean")
    ax1.set_xlabel("Orbital phase")
    ax1.set_ylabel("Relative flux in He I 10830 Å line")
    ax1.set_title("Real phase-folded helium transit light curve")
    ax1.legend(fontsize=7, loc="lower left")
    ax1.grid(alpha=0.25)

    data_pts = ax2.errorbar(
        wave, dmean * 100, yerr=derr * 100, fmt=".", ms=4, color="#2f6f4f", alpha=0.6,
        label="Real excess absorption (data, left axis)",
    )
    ax2b = ax2.twinx()
    (model_line,) = ax2b.plot(
        wave, model, color="#a8431f", lw=1.5, label="Best-fit model (right axis, arbitrary units)",
    )
    ax2.axvline(10830.34, color="#999", ls=":", lw=1)
    ax2.set_xlabel("Wavelength [Å], air")
    ax2.set_ylabel("Real excess absorption [%]", color="#2f6f4f")
    ax2b.set_ylabel("Best-fit model [arbitrary units]", color="#a8431f")
    ax2.set_title("Real per-wavelength-bin spectral profile\n(noisy at single-bin level — descriptive only)")
    ax2.legend(handles=[data_pts, model_line], fontsize=6.5, loc="upper left")
    ax2.grid(alpha=0.25)

    fig.suptitle("HAT-P-11b: real spectrally resolved helium escape (Allart et al. 2018)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "hatp11b_helium_escape.png", dpi=200)

    print(f"Wrote {summary_path}")
    print(f"Wrote {FIG_DIR / 'hatp11b_helium_escape.png'}")
    print(f"Out-of-transit flux: {mean_out:.5f} +/- {err_out:.5f}")
    print(f"In-transit flux:     {mean_in:.5f} +/- {err_in:.5f}")
    print(f"Helium excess absorption depth: {depth*100:.3f}% +/- {depth_err*100:.3f}% ({sigma:.1f} sigma)")


if __name__ == "__main__":
    main()
