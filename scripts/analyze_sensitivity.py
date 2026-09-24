"""Specification sensitivity for the descriptive HAT-P-11 b helium dip."""

from __future__ import annotations

import csv
from itertools import product
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import analyze_spectrum as spectrum

FIGURES = ROOT / "figures"
MULTIVERSE_FILE = FIGURES / "phase_window_multiverse.csv"
JACKKNIFE_FILE = FIGURES / "phase_point_jackknife.csv"
SUMMARY_FILE = FIGURES / "sensitivity_summary.csv"
FIGURE_FILE = FIGURES / "hatp11b_sensitivity_audit.png"


def mean_and_error(values: np.ndarray, errors: np.ndarray, rule: str) -> tuple[float, float]:
    weights = 1.0 / errors**2 if rule == "inverse_variance" else np.ones(len(values))
    normalized = weights / weights.sum()
    return float(normalized @ values), float(np.sqrt(np.sum((normalized * errors) ** 2)))


def estimate(flux: np.ndarray, errors: np.ndarray, in_mask: np.ndarray, out_mask: np.ndarray, rule: str) -> dict[str, float]:
    inside, inside_error = mean_and_error(flux[in_mask], errors[in_mask], rule)
    outside, outside_error = mean_and_error(flux[out_mask], errors[out_mask], rule)
    depth = (outside - inside) * 100.0
    depth_error = np.hypot(inside_error, outside_error) * 100.0
    return {"depth_percent": depth, "formal_error_percent": depth_error, "formal_snr": depth / depth_error}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main() -> dict[str, object]:
    FIGURES.mkdir(exist_ok=True)
    phase, flux, errors = spectrum.load_lightcurve()
    rows: list[dict[str, object]] = []
    for half_width, out_minimum, weighting, baseline_side in product(
        (0.012, 0.016, 0.020, 0.024, 0.028),
        (0.024, 0.028, 0.032),
        ("inverse_variance", "uniform"),
        ("both", "pre", "post"),
    ):
        if out_minimum < half_width:
            continue
        in_mask = np.abs(phase) < half_width
        out_mask = np.abs(phase) >= out_minimum
        if baseline_side == "pre":
            out_mask &= phase < 0
        elif baseline_side == "post":
            out_mask &= phase > 0
        if in_mask.sum() < 3 or out_mask.sum() < 2:
            continue
        rows.append({
            "in_transit_half_width_phase": half_width,
            "out_of_transit_minimum_abs_phase": out_minimum,
            "weighting": weighting,
            "baseline_side": baseline_side,
            "n_in": int(in_mask.sum()),
            "n_out": int(out_mask.sum()),
            **estimate(flux, errors, in_mask, out_mask, weighting),
        })
    write_csv(MULTIVERSE_FILE, rows)

    default_in = np.abs(phase) < 0.020
    default_out = np.abs(phase) >= 0.024
    jackknife: list[dict[str, object]] = []
    for omitted in np.where(default_in | default_out)[0]:
        in_mask, out_mask = default_in.copy(), default_out.copy()
        group = "in" if in_mask[omitted] else "out"
        in_mask[omitted] = False; out_mask[omitted] = False
        jackknife.append({
            "omitted_index": int(omitted),
            "omitted_phase": float(phase[omitted]),
            "omitted_group": group,
            **estimate(flux, errors, in_mask, out_mask, "inverse_variance"),
        })
    write_csv(JACKKNIFE_FILE, jackknife)

    depths = np.asarray([row["depth_percent"] for row in rows])
    snr = np.asarray([row["formal_snr"] for row in rows])
    jack_depths = np.asarray([row["depth_percent"] for row in jackknife])
    summary = [
        {"quantity": "predeclared_designs", "value": len(rows), "interpretation": "all valid phase-window/weight/baseline combinations"},
        {"quantity": "depth_min_percent", "value": float(depths.min()), "interpretation": "estimator-choice envelope"},
        {"quantity": "depth_median_percent", "value": float(np.median(depths)), "interpretation": "not a retrieval"},
        {"quantity": "depth_max_percent", "value": float(depths.max()), "interpretation": "estimator-choice envelope"},
        {"quantity": "all_depths_positive", "value": bool(np.all(depths > 0)), "interpretation": "directional stability"},
        {"quantity": "formal_snr_min", "value": float(snr.min()), "interpretation": "independence-conditioned only"},
        {"quantity": "formal_snr_max", "value": float(snr.max()), "interpretation": "not detection significance"},
        {"quantity": "jackknife_depth_min_percent", "value": float(jack_depths.min()), "interpretation": "default masks, one point deleted"},
        {"quantity": "jackknife_depth_max_percent", "value": float(jack_depths.max()), "interpretation": "default masks, one point deleted"},
    ]
    write_csv(SUMMARY_FILE, summary)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7), constrained_layout=True)
    ax = axes[0]
    colors = {"both": "#155e75", "pre": "#b45309", "post": "#7c3aed"}
    for side in colors:
        values = [row["depth_percent"] for row in rows if row["baseline_side"] == side]
        ax.hist(values, bins=np.linspace(depths.min() - .03, depths.max() + .03, 17), alpha=.58, label=side, color=colors[side])
    ax.axvline(1.08, color="#111827", ls="--", label="published 1.08%")
    ax.set(xlabel="Descriptive in-minus-out absorption [%]", ylabel="Analysis designs", title="74-choice specification multiverse")
    ax.legend(frameon=False); ax.grid(axis="x", alpha=.2)
    ax = axes[1]
    ax.plot([row["omitted_phase"] for row in jackknife], jack_depths, "o", color="#155e75")
    ax.axhspan(depths.min(), depths.max(), color="#b45309", alpha=.13, label="multiverse envelope")
    ax.axhline(1.08, color="#111827", ls="--", label="published estimator")
    ax.set(xlabel="Omitted orbital phase", ylabel="Descriptive absorption [%]", title="Leave-one-phase-point-out audit")
    ax.legend(frameon=False); ax.grid(alpha=.2)
    fig.suptitle("HAT-P-11 b: the dip direction is stable; its magnitude is estimator-dependent", fontsize=14, weight="bold")
    fig.savefig(FIGURE_FILE, dpi=190)
    plt.close(fig)
    return {"multiverse": rows, "jackknife": jackknife, "summary": summary}


if __name__ == "__main__":
    result = main(); values = np.asarray([row["depth_percent"] for row in result["multiverse"]])
    print(f"{len(values)} designs: {values.min():.3f}-{values.max():.3f}% absorption; all positive={bool(np.all(values > 0))}")
