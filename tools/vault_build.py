"""기밀 문서 암호화 보관함 빌드.

confidential/manifest.txt 에 적힌 파일을 비밀번호로 암호화해 confidential/vault/ 에 쓴다.
평문은 저장소에 올리지 않고(.gitignore), 암호문과 뷰어(confidential/index.html)만 올린다.

사용:
    python tools/vault_build.py            # 비밀번호를 물어본다
    VAULT_PASSWORD=... python tools/vault_build.py

manifest.txt 형식 (한 줄에 하나, '|' 구분, '#'은 주석):
    경로 | 표시 제목 | 분류
"""
import base64
import getpass
import hashlib
import json
import mimetypes
import os
import secrets
import shutil
import sys
from datetime import date
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = Path(__file__).resolve().parent.parent
CONF = ROOT / "confidential"
VAULT = CONF / "vault"
MANIFEST = CONF / "manifest.txt"
ITER = 600_000

MIME = {
    ".hwp": "application/x-hwp",
    ".hwpx": "application/x-hwpx",
    ".md": "text/markdown",
}


def derive(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER)
    return kdf.derive(password.encode("utf-8"))


def read_manifest():
    entries = []
    for raw in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            sys.exit(f"manifest 형식 오류: {raw}")
        path = ROOT / parts[0]
        if not path.is_file():
            sys.exit(f"파일 없음: {parts[0]}")
        title = parts[1]
        category = parts[2] if len(parts) > 2 and parts[2] else "기타"
        entries.append((parts[0], path, title, category))
    return entries


def main():
    password = os.environ.get("VAULT_PASSWORD") or getpass.getpass("보관함 비밀번호: ")
    if len(password) < 4:
        sys.exit("비밀번호는 4자 이상이어야 한다.")
    if not os.environ.get("VAULT_PASSWORD"):
        if getpass.getpass("비밀번호 확인: ") != password:
            sys.exit("비밀번호 확인이 일치하지 않는다.")

    entries = read_manifest()
    salt = secrets.token_bytes(16)
    key = derive(password, salt)
    aes = AESGCM(key)

    if VAULT.exists():
        shutil.rmtree(VAULT)
    VAULT.mkdir(parents=True)

    items = []
    total = 0
    for rel, path, title, category in entries:
        data = path.read_bytes()
        fid = hashlib.sha256(rel.encode("utf-8")).hexdigest()[:16]
        iv = secrets.token_bytes(12)
        ct = aes.encrypt(iv, data, fid.encode("ascii"))
        (VAULT / f"{fid}.bin").write_bytes(iv + ct)
        ext = path.suffix.lower()
        mime = MIME.get(ext) or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        items.append({
            "id": fid,
            "title": title,
            "name": path.name,
            "category": category,
            "size": len(data),
            "mime": mime,
            "ext": ext,
        })
        total += len(data)
        print(f"  {rel}  ({len(data):,} B)")

    manifest = json.dumps({"built": date.today().isoformat(), "items": items}, ensure_ascii=False).encode("utf-8")
    iv = secrets.token_bytes(12)
    (VAULT / "manifest.bin").write_bytes(iv + aes.encrypt(iv, manifest, b"manifest"))
    (VAULT / "params.json").write_text(json.dumps({
        "salt": base64.b64encode(salt).decode(),
        "iter": ITER,
        "built": date.today().isoformat(),
        "count": len(items),
    }), encoding="utf-8")
    print(f"완료: {len(items)}개, {total/1e6:.1f} MB → {VAULT}")


if __name__ == "__main__":
    main()
