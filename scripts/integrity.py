"""Integrity checks for the immutable public observations.
Copyright 2026 박성모. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def verify_evidence(evidence):
    evidence = Path(evidence).resolve()
    manifest = read_json(evidence / "published-evidence-sha256.json")
    records = {**manifest["original_evidence"], **manifest["derived_provenance"]}
    for name, record in records.items():
        path = (evidence / name).resolve()
        require(path.is_relative_to(evidence), "Manifest path escapes evidence directory")
        data = path.read_bytes()
        require(len(data) == record["bytes"], f"Evidence size mismatch: {name}")
        require(hashlib.sha256(data).hexdigest() == record["sha256"],
                f"Evidence SHA-256 mismatch: {name}")
    frozen = read_json(evidence / "experiment-frozen-hashes.json")
    for name, expected in frozen.items():
        require(name in records, f"Frozen input is absent from public manifest: {name}")
        require(records[name]["sha256"] == expected, f"Frozen input hash mismatch: {name}")
    return {"original_files": len(manifest["original_evidence"]),
            "derived_provenance_files": len(manifest["derived_provenance"]),
            "frozen_inputs": len(frozen)}
