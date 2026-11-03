#!/usr/bin/env python3
"""Verify and reanalyze the public evidence using Python's standard library.
Copyright 2026 박성모. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import analyze_experiment
import check_calendar_observations
import format_sensitivity
from integrity import read_json, require, verify_evidence

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUTPUTS = ["experiment-scored.json", "experiment-summary.json",
           "validator-fault-injection.json", "format-sensitivity.json"]


def reproduce(output):
    verified = verify_evidence(EVIDENCE)
    output = Path(output).resolve()
    require(output != ROOT and not output.is_relative_to(EVIDENCE),
            "Choose an output directory outside the evidence directory and distinct from the repository root.")
    output.mkdir(parents=True, exist_ok=True)
    summary = analyze_experiment.analyze(output)
    format_sensitivity.analyze(EVIDENCE, output)
    comparisons = {}
    for name in OUTPUTS:
        actual = output / name
        expected = EVIDENCE / name
        require(read_json(actual) == read_json(expected), f"Reanalysis differs from preserved result: {name}")
        require(actual.read_bytes() == expected.read_bytes(), f"Reanalysis bytes differ: {name}")
        # Explicit UTF-8 and LF preserve the original serialization across operating systems.
        comparisons[name] = {"json_equal": True,
            "bytes_equal": actual.read_bytes() == expected.read_bytes(),
            "preserved_sha256": hashlib.sha256(expected.read_bytes()).hexdigest()}
    calendar = check_calendar_observations.check(EVIDENCE)
    report = {"evidence_integrity": verified, "calls": summary["n_calls"],
        "exact_responses": {arm: summary["arms"][arm]["exact"] for arm in ("A", "B", "C")},
        "generated_results": comparisons, "calendar_observation_checks": calendar,
        "network_calls": 0, "new_model_calls": 0, "engine_reexecuted": False}
    (output / "reproduction-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "reproduced")
    parser.add_argument("--check", action="store_true", help="Use a temporary output directory; preserve the checkout.")
    args = parser.parse_args()
    if args.check:
        with TemporaryDirectory(prefix="saju-fact-reanalysis-") as folder:
            report = reproduce(Path(folder))
    else:
        report = reproduce(args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
