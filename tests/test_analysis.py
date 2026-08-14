"""Executable checks on the weighted-mean statistic and a regression
guard that the pipeline still reproduces the documented headline
numbers -- including keeping the paper's own combined value attached
for comparison, per the instrument-attribution fix this repo went
through -- when run on the real downloaded light curve."""

import csv

import numpy as np
import analyze_spectrum as spec


def test_weighted_mean_matches_hand_computed_case():
    values = np.array([1.0, 2.0])
    errors = np.array([1.0, 0.5])  # weights 1 and 4
    mean, err = spec.weighted_mean(values, errors)
    assert np.isclose(mean, 1.8, rtol=1e-10)
    assert np.isclose(err, np.sqrt(1.0 / 5.0), rtol=1e-10)


def test_pipeline_reproduces_documented_headline_numbers():
    spec.FIG_DIR.mkdir(exist_ok=True)
    spec.main()
    rows = {}
    with (spec.FIG_DIR / "summary_statistics.csv").open() as f:
        for row in csv.DictReader(f):
            rows[row["quantity"]] = row["value"]
    assert int(rows["n_in_transit_points"]) == 8
    own_depth = float(rows["this_repo_own_statistic"].split(" +/- ")[0])
    own_snr = float(rows["this_repo_own_statistic_snr"])
    paper_depth = float(rows["paper_combined_value"].split(" +/- ")[0])
    assert abs(own_depth - 0.827) < 0.01
    assert abs(own_snr - 12.9) < 0.1
    # Regression guard: the paper's real combined value (1.08%, Allart et
    # al. 2018) must stay recorded for comparison -- this repo was
    # specifically fixed to stop presenting its own statistic as a
    # reproduction of this number.
    assert abs(paper_depth - 1.08) < 1e-6
