"""Verify renamed HAT-P-11 b inputs against audited Zenodo members."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "zenodo_manifest.csv"


def canonical_lf(payload: bytes) -> bytes:
    return payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def verify(archive: Path | None = None) -> list[dict[str, str]]:
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    archive_file = None
    if archive is not None:
        archive_payload = archive.read_bytes()
        if hashlib.md5(archive_payload).hexdigest() != rows[0]["archive_md5"]:
            raise ValueError("archive MD5 does not match the Zenodo receipt")
        archive_file = zipfile.ZipFile(archive)
    try:
        for row in rows:
            local = canonical_lf((ROOT / row["local_path"]).read_bytes())
            if hashlib.sha256(local).hexdigest() != row["canonical_lf_sha256"]:
                raise ValueError(f"canonical SHA-256 mismatch: {row['local_path']}")
            if archive_file is not None:
                member = archive_file.read(row["archive_entry"])
                if len(member) != int(row["archive_size_bytes"]):
                    raise ValueError(f"archive size mismatch: {row['archive_entry']}")
                if hashlib.md5(member).hexdigest() != row["archive_md5_member"]:
                    raise ValueError(f"archive member MD5 mismatch: {row['archive_entry']}")
                if canonical_lf(member) != local:
                    raise ValueError(f"canonical bytes differ: {row['archive_entry']}")
    finally:
        if archive_file is not None:
            archive_file.close()
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    checked = verify(args.archive)
    print(f"Verified {len(checked)} renamed Zenodo inputs with canonical-LF hashes.")


if __name__ == "__main__":
    main()
