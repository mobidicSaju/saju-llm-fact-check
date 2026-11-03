#!/usr/bin/env python3
"""Compare the public proof and native PDF with PyMuPDF; no app control.
This is a text/font/geometry check, not a substitute for visual review.
Copyright 2026 박성모. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import fitz

ROOT = Path(__file__).resolve().parents[1]
APPROVED_FONTS = {"YoonMyungjoPro730", "YoonMyungjoPro760",
                  "YoonGothicPro740", "YoonGothicPro760"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def normal_text(text):
    return re.sub(r"\s", "", unicodedata.normalize("NFC", text))


def display_path(path):
    path = path.resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof", type=Path, default=ROOT / "paper/PAPER_PUBLIC_A4.pdf")
    parser.add_argument("--native", type=Path, default=ROOT / "paper/PAPER_PUBLIC_A4_INDESIGN.pdf")
    parser.add_argument("--report", type=Path, default=ROOT / "reproduced/pdf-verification.json")
    parser.add_argument("--render", type=Path, help="Optionally render native pages as PNG for visual review")
    args = parser.parse_args()
    mismatches, outside, fonts = [], [], {}
    if args.render:
        args.render.mkdir(parents=True, exist_ok=True)
    with fitz.open(args.proof) as proof, fitz.open(args.native) as native:
        require(len(proof) == len(native) == 16, "Expected two 16-page documents")
        for number, (reference, page) in enumerate(zip(proof, native), 1):
            require(abs(page.rect.width - 595.275591) < .01 and
                    abs(page.rect.height - 841.889764) < .01, f"Page {number} is not A4")
            if normal_text(reference.get_text()) != normal_text(page.get_text()):
                mismatches.append(number)
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        box = fitz.Rect(span["bbox"])
                        if box.x0 < -.5 or box.y0 < -.5 or box.x1 > page.rect.width + .5 or box.y1 > page.rect.height + .5:
                            outside.append({"page": number, "text": span["text"], "bbox": list(box)})
            for font in page.get_fonts():
                fonts[font[0]] = font
            if args.render:
                page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(
                    args.render / f"page-{number:04d}.png")
        embedded = []
        names = set()
        for xref in fonts:
            name, extension, kind, content = native.extract_font(xref)
            require(bool(content), f"Font is not embedded: {name}")
            plain = re.sub(r"^[A-Z]{6}\+", "", name)
            names.add(plain)
            embedded.append({"name": name, "bytes": len(content), "type": kind})
        require(names == APPROVED_FONTS, "The native PDF must use exactly the four approved Yoon faces")
        report = {"proof": display_path(args.proof), "native": display_path(args.native),
                  "pages": len(native), "a4": True,
                  "ordered_text_mismatches": mismatches, "outside_page": outside,
                  "embedded_fonts": embedded,
                  "native_sha256": hashlib.sha256(args.native.read_bytes()).hexdigest(),
                  "native_bytes": args.native.stat().st_size,
                  "visual_review_performed_by_this_script": False,
                  "native_indesign_open_performed_by_this_script": False}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    require(not mismatches and not outside, "PDF comparison failed; inspect the report")


if __name__ == "__main__":
    main()
