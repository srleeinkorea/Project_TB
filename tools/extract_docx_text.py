"""Extract paragraphs and table cells from DOCX files in document order."""

from __future__ import annotations

import argparse
from pathlib import Path

from docx import Document
from docx.document import Document as DocumentType
from docx.table import Table
from docx.text.paragraph import Paragraph


def iter_block_items(parent: DocumentType):
    for child in parent.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, parent)
        elif child.tag.endswith("}tbl"):
            yield Table(child, parent)


def extract(path: Path) -> str:
    doc = Document(path)
    lines: list[str] = []
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if text:
                lines.append(text)
        else:
            for row in block.rows:
                cells = [" ".join(p.text.strip() for p in cell.paragraphs if p.text.strip()) for cell in row.cells]
                if any(cells):
                    lines.append(" | ".join(cells))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--text-out", type=Path)
    args = parser.parse_args()
    text = extract(args.input)
    if args.text_out:
        args.text_out.write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
