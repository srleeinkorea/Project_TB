"""Minimal HWP 5.x text extractor.

Reads the OLE/CFB container directly and extracts HWPTAG_PARA_TEXT records
from BodyText/Section* streams.  This is intentionally read-only and has no
third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path


FREESECT = 0xFFFFFFFF
ENDOFCHAIN = 0xFFFFFFFE
FATSECT = 0xFFFFFFFD
DIFSECT = 0xFFFFFFFC
NOSTREAM = 0xFFFFFFFF


@dataclass
class DirEntry:
    index: int
    name: str
    obj_type: int
    left: int
    right: int
    child: int
    start_sector: int
    size: int


class CompoundFile:
    def __init__(self, path: Path):
        self.path = path
        self.data = path.read_bytes()
        if self.data[:8] != bytes.fromhex("D0CF11E0A1B11AE1"):
            raise ValueError(f"Not an OLE/CFB file: {path}")

        self.major = struct.unpack_from("<H", self.data, 0x1A)[0]
        self.sector_size = 1 << struct.unpack_from("<H", self.data, 0x1E)[0]
        self.mini_sector_size = 1 << struct.unpack_from("<H", self.data, 0x20)[0]
        self.num_fat_sectors = struct.unpack_from("<I", self.data, 0x2C)[0]
        self.first_dir_sector = struct.unpack_from("<I", self.data, 0x30)[0]
        self.mini_cutoff = struct.unpack_from("<I", self.data, 0x38)[0]
        self.first_mini_fat_sector = struct.unpack_from("<I", self.data, 0x3C)[0]
        self.num_mini_fat_sectors = struct.unpack_from("<I", self.data, 0x40)[0]
        self.first_difat_sector = struct.unpack_from("<I", self.data, 0x44)[0]
        self.num_difat_sectors = struct.unpack_from("<I", self.data, 0x48)[0]

        difat = list(struct.unpack_from("<109I", self.data, 0x4C))
        difat = [sid for sid in difat if sid not in (FREESECT, ENDOFCHAIN)]
        sid = self.first_difat_sector
        for _ in range(self.num_difat_sectors):
            sec = self._sector(sid)
            count = self.sector_size // 4
            values = struct.unpack_from(f"<{count}I", sec, 0)
            difat.extend(x for x in values[:-1] if x not in (FREESECT, ENDOFCHAIN))
            sid = values[-1]
            if sid == ENDOFCHAIN:
                break

        fat_entries: list[int] = []
        for fat_sid in difat[: self.num_fat_sectors]:
            sec = self._sector(fat_sid)
            fat_entries.extend(struct.unpack_from(f"<{self.sector_size // 4}I", sec, 0))
        self.fat = fat_entries

        directory_bytes = self._read_fat_chain(self.first_dir_sector)
        self.entries = self._parse_directory(directory_bytes)
        roots = [entry for entry in self.entries if entry.obj_type == 5]
        if not roots:
            raise ValueError("CFB root directory entry not found")
        self.root = roots[0]
        self.root_stream = self._read_fat_chain(self.root.start_sector)[: self.root.size]

        if self.first_mini_fat_sector not in (FREESECT, ENDOFCHAIN):
            mini_fat_bytes = self._read_fat_chain(self.first_mini_fat_sector)
            expected = self.num_mini_fat_sectors * self.sector_size
            mini_fat_bytes = mini_fat_bytes[:expected]
            self.mini_fat = list(
                struct.unpack_from(f"<{len(mini_fat_bytes) // 4}I", mini_fat_bytes, 0)
            )
        else:
            self.mini_fat = []

        self.paths = self._build_paths()

    def _sector(self, sid: int) -> bytes:
        if sid >= 0xFFFFFFF0:
            raise ValueError(f"Invalid sector id: 0x{sid:08X}")
        start = (sid + 1) * self.sector_size
        end = start + self.sector_size
        if end > len(self.data):
            raise ValueError(f"Sector {sid} exceeds file size")
        return self.data[start:end]

    def _read_fat_chain(self, start_sid: int) -> bytes:
        if start_sid in (FREESECT, ENDOFCHAIN):
            return b""
        chunks: list[bytes] = []
        sid = start_sid
        seen: set[int] = set()
        while sid != ENDOFCHAIN:
            if sid in seen:
                raise ValueError(f"Cycle in FAT chain at sector {sid}")
            if sid >= len(self.fat):
                raise ValueError(f"FAT sector reference out of range: {sid}")
            seen.add(sid)
            chunks.append(self._sector(sid))
            sid = self.fat[sid]
            if sid in (FREESECT, FATSECT, DIFSECT):
                break
        return b"".join(chunks)

    def _parse_directory(self, raw: bytes) -> list[DirEntry]:
        entries: list[DirEntry] = []
        for index in range(0, len(raw) // 128):
            chunk = raw[index * 128 : (index + 1) * 128]
            name_len = struct.unpack_from("<H", chunk, 0x40)[0]
            if 2 <= name_len <= 64:
                name = chunk[: name_len - 2].decode("utf-16le", errors="replace")
            else:
                name = ""
            size = struct.unpack_from("<Q", chunk, 0x78)[0]
            if self.major == 3:
                size &= 0xFFFFFFFF
            entries.append(
                DirEntry(
                    index=index,
                    name=name,
                    obj_type=chunk[0x42],
                    left=struct.unpack_from("<I", chunk, 0x44)[0],
                    right=struct.unpack_from("<I", chunk, 0x48)[0],
                    child=struct.unpack_from("<I", chunk, 0x4C)[0],
                    start_sector=struct.unpack_from("<I", chunk, 0x74)[0],
                    size=size,
                )
            )
        return entries

    def _walk_siblings(self, index: int, parent: str, out: dict[str, DirEntry], seen: set[int]) -> None:
        if index in (NOSTREAM, FREESECT) or index >= len(self.entries) or index in seen:
            return
        seen.add(index)
        entry = self.entries[index]
        self._walk_siblings(entry.left, parent, out, seen)
        path = f"{parent}/{entry.name}" if parent else entry.name
        out[path] = entry
        if entry.obj_type in (1, 5) and entry.child not in (NOSTREAM, FREESECT):
            self._walk_siblings(entry.child, path, out, seen)
        self._walk_siblings(entry.right, parent, out, seen)

    def _build_paths(self) -> dict[str, DirEntry]:
        out: dict[str, DirEntry] = {}
        seen: set[int] = set()
        if self.root.child not in (NOSTREAM, FREESECT):
            self._walk_siblings(self.root.child, "", out, seen)
        return out

    def _read_mini_chain(self, start_sid: int, size: int) -> bytes:
        if start_sid in (FREESECT, ENDOFCHAIN):
            return b""
        chunks: list[bytes] = []
        sid = start_sid
        seen: set[int] = set()
        while sid != ENDOFCHAIN and len(b"".join(chunks)) < size:
            if sid in seen or sid >= len(self.mini_fat):
                break
            seen.add(sid)
            start = sid * self.mini_sector_size
            chunks.append(self.root_stream[start : start + self.mini_sector_size])
            sid = self.mini_fat[sid]
        return b"".join(chunks)[:size]

    def read_stream(self, path: str) -> bytes:
        entry = self.paths[path]
        if entry.obj_type != 2:
            raise ValueError(f"Not a stream: {path}")
        if entry.size < self.mini_cutoff:
            return self._read_mini_chain(entry.start_sector, entry.size)
        return self._read_fat_chain(entry.start_sector)[: entry.size]


def clean_para_text(payload: bytes) -> str:
    units = list(struct.unpack(f"<{len(payload) // 2}H", payload[: len(payload) // 2 * 2]))
    out: list[str] = []
    i = 0
    extended_controls = set(range(1, 9)) | {11, 12} | set(range(14, 24))
    while i < len(units):
        code = units[i]
        if code in extended_controls:
            i += 8
            continue
        if code == 9:
            out.append("\t")
        elif code in (10, 13):
            out.append("\n")
        elif code == 24:
            out.append("-")
        elif code in (25, 30, 31):
            out.append(" ")
        elif code >= 32:
            out.append(chr(code))
        i += 1
    return "".join(out).replace("\r\n", "\n").replace("\r", "\n").strip()


def parse_records(data: bytes) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    pos = 0
    while pos + 4 <= len(data):
        header = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        tag_id = header & 0x3FF
        level = (header >> 10) & 0x3FF
        size = (header >> 20) & 0xFFF
        if size == 0xFFF:
            if pos + 4 > len(data):
                break
            size = struct.unpack_from("<I", data, pos)[0]
            pos += 4
        if pos + size > len(data):
            break
        payload = data[pos : pos + size]
        pos += size
        record: dict[str, object] = {"tag_id": tag_id, "level": level, "size": size}
        if tag_id == 67:
            record["text"] = clean_para_text(payload)
        records.append(record)
    return records


def extract_hwp(path: Path) -> dict[str, object]:
    cfb = CompoundFile(path)
    file_header = cfb.read_stream("FileHeader")
    signature = file_header[:32].split(b"\x00", 1)[0].decode("ascii", errors="replace")
    flags = struct.unpack_from("<I", file_header, 36)[0]
    compressed = bool(flags & 0x1)
    encrypted = bool(flags & 0x2)
    if encrypted:
        raise ValueError("Encrypted HWP files are not supported")

    section_paths = sorted(
        (p for p in cfb.paths if p.startswith("BodyText/Section")),
        key=lambda p: int(p.rsplit("Section", 1)[1]),
    )
    sections: list[dict[str, object]] = []
    all_paragraphs: list[str] = []
    for section_path in section_paths:
        raw = cfb.read_stream(section_path)
        if compressed:
            raw = zlib.decompress(raw, -15)
        records = parse_records(raw)
        paragraphs = [str(r["text"]) for r in records if r.get("text")]
        all_paragraphs.extend(paragraphs)
        sections.append(
            {
                "path": section_path,
                "record_count": len(records),
                "paragraphs": paragraphs,
            }
        )
    return {
        "source": str(path),
        "signature": signature,
        "compressed": compressed,
        "stream_paths": sorted(cfb.paths),
        "sections": sections,
        "text": "\n".join(all_paragraphs),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--text-out", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    result = extract_hwp(args.input)
    if args.text_out:
        args.text_out.write_text(str(result["text"]), encoding="utf-8")
    if args.json_out:
        args.json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if not args.text_out and not args.json_out:
        print(result["text"])


if __name__ == "__main__":
    main()
