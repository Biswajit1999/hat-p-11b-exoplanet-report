from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_zenodo_provenance as provenance


def test_renamed_inputs_match_audited_zenodo_members():
    rows = provenance.verify()
    assert len(rows) == 2
    assert {row["archive_entry"].rsplit("/", 1)[-1] for row in rows} == {
        "Fig_2a.txt",
        "Fig_2b_mean.txt",
    }
