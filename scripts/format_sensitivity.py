"""Remove only one enclosing Markdown fence for a post-hoc comparison.
Public edition: same transformation, output outside immutable evidence.
Copyright 2026 박성모. SPDX-License-Identifier: Apache-2.0
"""
import json
import re
from pathlib import Path


def analyze(evidence, output_dir):
    raw = [json.loads(line) for line in (evidence / "experiment-raw.jsonl").read_text(
        encoding="utf-8").splitlines()]
    out = {}
    for arm in ["A", "B", "C"]:
        total = exact = parsed = stripcount = 0
        for row in raw:
            if row["arm"] != arm:
                continue
            text = row["response"]["message"]["content"].strip()
            match = re.fullmatch(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
            if match:
                text = match[1]
                stripcount += 1
            try:
                data = json.loads(text)
                parsed += 1
            except json.JSONDecodeError:
                data = {}
            total += sum(data.get(key) == value for key, value in row["reference"].items())
            exact += data == row["reference"]
        out[arm] = {"n": 44, "only_outer_fence_removed": stripcount,
                    "parse_pass": parsed, "exact": exact,
                    "fields_correct": total, "fields_total": 176}
    result = {"status": "post-hoc descriptive sensitivity, primary protocol unchanged",
              "transformation": "remove one entire enclosing Markdown JSON code fence only; no value repair",
              "arms": out}
    (Path(output_dir) / "format-sensitivity.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return result
