"""Recompute statistics from recorded observations, without an engine or DB.
Copyright 2026 박성모. SPDX-License-Identifier: Apache-2.0
"""
from datetime import datetime
import statistics
from integrity import read_json, require


def check(evidence):
    solar = read_json(evidence / "official-solar-term-comparison.json")
    differences = []
    date_mismatches = 0
    for row in solar["results"]:
        published = datetime.fromisoformat(row["official"]["date"] + "T" + row["official"]["time"])
        observed = datetime.fromisoformat(row["database_time_kst"])
        minutes = int((observed - published).total_seconds() / 60)
        require(minutes == row["signed_database_minus_official_minutes"], "Solar-term difference mismatch")
        require(abs(minutes) == row["absolute_minutes"], "Solar-term absolute difference mismatch")
        differences.append(minutes)
        date_mismatches += observed.date() != published.date()
    absolute = [abs(value) for value in differences]
    calculated = {"official_records": 48, "paired_records": len(differences),
                  "exact_minute_matches": sum(value == 0 for value in differences),
                  "minute_mismatches": sum(value != 0 for value in differences),
                  "mean_signed_minutes": statistics.mean(differences),
                  "median_signed_minutes": statistics.median(differences),
                  "min_signed_minutes": min(differences), "max_signed_minutes": max(differences),
                  "mean_absolute_minutes": statistics.mean(absolute),
                  "median_absolute_minutes": statistics.median(absolute),
                  "max_absolute_minutes": max(absolute), "calendar_date_mismatches": date_mismatches}
    require(calculated == solar["summary"], "Solar-term summary mismatch")
    lunar = read_json(evidence / "official-lunar-month-start-checks.json")
    lunar_counts = {"cases": len(lunar["results"]), "lunar_to_solar_matches": 0,
                    "solar_to_lunar_matches": 0, "noon_day_ganji_matches": 0}
    for row in lunar["results"]:
        published = row["official"]
        observed = row["actual_solar"]
        solar_date = f'{observed["year"]:04}-{observed["month"]:02}-{observed["day"]:02}'
        forward = solar_date == published["solar_date"]
        backward = row["actual_lunar"] == {"year": published["lunar_year"],
            "month": published["lunar_month"], "day": published["lunar_day"],
            "leap": published["is_leap_month"]}
        noon = row["noon_day_ganji_ko"] == published["calendar_day_ganji_ko"]
        require((forward, backward, noon) == (row["lunar_to_solar_match"],
            row["solar_to_lunar_match"], row["published_calendar_day_ganji_match"]), "Month-start score mismatch")
        lunar_counts["lunar_to_solar_matches"] += forward
        lunar_counts["solar_to_lunar_matches"] += backward
        lunar_counts["noon_day_ganji_matches"] += noon
    require(lunar_counts == lunar["summary"], "Month-start summary mismatch")
    ipchun = read_json(evidence / "official-ipchun-engine-checks.json")
    scored = []
    for row in ipchun["results"]:
        expected = row["declared_policy_expected_year_month"]
        correct = all(row["actual_natal"][key] == value for key, value in expected.items())
        require(correct == row["year_month_match"], "Ipchun recorded score mismatch")
        scored.append((row["offset_minutes"], correct))
    robust = [correct for offset, correct in scored if offset != 0]
    ipchun_counts = {"cases": len(scored), "year_month_matches": sum(correct for _, correct in scored),
                     "robust_before_after_cases": len(robust), "robust_before_after_matches": sum(robust)}
    require(ipchun_counts == ipchun["summary"], "Ipchun summary mismatch")
    unknown = read_json(evidence / "unknown-time-enumeration.json")
    total_minutes = 0
    candidates = []
    for row in unknown["results"]:
        total_minutes += row["minutes_evaluated"]
        counts = row["candidate_minute_counts"]
        for field, values in counts.items():
            require(sum(values.values()) == row["minutes_evaluated"], f"Unknown-time minute sum mismatch: {field}")
        candidates.append({"date": row["date"], "candidate_counts": {key: len(values) for key, values in counts.items()}})
    require(total_minutes == 5760 and len(candidates) == 4, "Expected four complete days")
    return {"scope": "Reanalysis of recorded observations only; no engine execution or independent source transcription.",
            "solar_terms": calculated, "lunar_month_starts": lunar_counts,
            "ipchun": ipchun_counts, "unknown_time_minutes": total_minutes,
            "unknown_time_candidates": candidates}
