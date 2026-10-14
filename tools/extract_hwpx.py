"""Extract paragraph text from HWPX documents without modifying them."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

from lxml import etree


def natural_key(name: str) -> list[object]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", name)]


def extract_hwpx(path: Path) -> dict[str, object]:
    sections: list[dict[str, object]] = []
    all_paragraphs: list[str] = []
    with zipfile.ZipFile(path) as archive:
        names = sorted(
            (
                name
                for name in archive.namelist()
                if name.lower().startswith("contents/section") and name.lower().endswith(".xml")
            ),
            key=natural_key,
        )
        for name in names:
            root = etree.fromstring(archive.read(name))
            paragraphs: list[str] = []
            for paragraph in root.xpath(".//*[local-name()='p']"):
                pieces = paragraph.xpath(".//*[local-name()='t']//text()")
                text = "".join(str(piece) for piece in pieces).replace("\u000b", "\n").strip()
                if text:
                    paragraphs.append(text)
            all_paragraphs.extend(paragraphs)
            sections.append({"path": name, "paragraphs": paragraphs})
    return {"source": str(path), "sections": sections, "text": "\n".join(all_paragraphs)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--text-out", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    result = extract_hwpx(args.input)
    if args.text_out:
        args.text_out.write_text(str(result["text"]), encoding="utf-8")
    if args.json_out:
        args.json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if not args.text_out and not args.json_out:
        print(result["text"])


if __name__ == "__main__":
    main()
