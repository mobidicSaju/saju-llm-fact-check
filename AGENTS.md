# Public research release (2026-11-03)

This folder is the standalone source for https://github.com/mobidicSaju/saju-llm-fact-check.

- Preserve all original evidence bytes and `experiment-frozen-hashes.json`. Never rerun a model to replace a failure, change a denominator, or overwrite observations.
- `scripts/reproduce.py --check` uses only Python's standard library and preserved records. Distinguish reanalysis from new model/engine execution.
- The reported metric is four-field faithfulness to the frozen implementation reference, not predictive validity, general calendar correctness, or free-text quality.
- Keep the original case study separate and unchanged. New observations belong to a new dated study.
- No GitHub Actions, paid CI/services, paid model calls, or automatic remote execution.
- Never add host-specific checkout/font activation paths, credentials, personal records, font programs, model weights, calendar DB, or complete external almanac PDFs.
- Apache-2.0 covers original authored material; preserve NOTICE and source citations. Third-party materials are not relicensed.
- Source changes require rebuilding manuscript.json/txt. PDF changes require full-page visual and text validation; IDML validation alone is not a native InDesign validation.
