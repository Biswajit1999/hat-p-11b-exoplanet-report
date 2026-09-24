from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import analyze_sensitivity as sensitivity


def test_predeclared_designs_keep_positive_dip_but_expose_choice_sensitivity():
    result = sensitivity.main()
    depth = np.asarray([row["depth_percent"] for row in result["multiverse"]])
    assert len(depth) == 74
    assert np.all(depth > 0)
    assert depth.min() < 0.55
    assert depth.max() > 1.15
    for path in (sensitivity.MULTIVERSE_FILE, sensitivity.JACKKNIFE_FILE, sensitivity.SUMMARY_FILE, sensitivity.FIGURE_FILE):
        assert Path(path).is_file() and Path(path).stat().st_size > 200
