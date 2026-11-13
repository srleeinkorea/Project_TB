"""문서함 관리자 메뉴 묶음을 만든다.

비공개_관리자메뉴.txt 에 적힌 문서를 하나로 묶어 관리자 비밀번호로 암호화한다.
문서함(index.html)에서 「편집 (관리자)」 → 비밀번호를 입력하면 브라우저 안에서만 복호화되어
관리자 메뉴가 나타난다. 평문·메뉴 제목은 GitHub에 올라가지 않는다.

사용:
    python 09_도구/build_admin.py          # 비밀번호를 물어본다
    VAULT_PASSWORD=... python 09_도구/build_admin.py

출력: 05_잠금문서/관리자/bundle.bin (암호문), params.json (salt·iter)
"""
import base64, getpass, hashlib, html, json, os, re, secrets, sys
from datetime import date
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = Path(__file__).resolve().parent.parent
MENU = ROOT / "비공개_관리자메뉴.txt"
OUT = ROOT / "05_잠금문서" / "관리자"
ITER = 600_000

MD_PAGE = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css');
body{{margin:0;background:#f5f7fb;color:#1c2940;font:14px/1.85 'Pretendard Variable',Pretendard,'Malgun Gothic',sans-serif;word-break:keep-all}}
.page{{max-width:980px;margin:24px auto;background:#fff;border:1px solid #dfe5ef;border-radius:16px;padding:32px 40px}}
h1{{font-size:24px;letter-spacing:-.03em;line-height:1.4}}h2{{font-size:18px;margin-top:32px;padding-top:16px;border-top:1px solid #dfe5ef}}h3{{font-size:15px}}
table{{border-collapse:collapse;width:100%;font-size:13px;margin:12px 0}}th{{background:#f0f3f9;color:#53627a;text-align:left}}
th,td{{border:1px solid #dfe5ef;padding:7px 10px;vertical-align:top}}blockquote{{margin:12px 0;padding:8px 14px;border-left:3px solid #c7861c;background:#fff7e8;color:#53627a}}
code{{background:#f0f3f9;padding:1px 5px;border-radius:4px}}a{{color:#365ee8}}
@media(max-width:720px){{.page{{margin:0;border-radius:0;padding:20px 16px}}table{{display:block;overflow-x:auto}}}}
</style></head><body><main class="page">{body}</main></body></html>"""


def read_menu():
    items = []
    for raw in MENU.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 3:
            sys.exit(f"형식 오류: {raw}")
        path = ROOT / parts[2]
        if not path.is_file():
            sys.exit(f"파일 없음: {parts[2]}")
        items.append((parts[0], parts[1], path))
    return items


def inline_css(text, folder):
    def rep(m):
        css = folder / m.group(1).split("?")[0]
        return "<style>\n" + css.read_text(encoding="utf-8") + "\n</style>" if css.is_file() else m.group(0)
    return re.sub(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+\.css[^"]*)"[^>]*>', rep, text)


def convert(path, title):
    ext = path.suffix.lower()
    if ext in (".html", ".htm"):
        return "html", inline_css(path.read_text(encoding="utf-8"), path.parent)
    if ext == ".md":
        try:
            import markdown
            body = markdown.markdown(path.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])
        except ImportError:
            body = "<pre>" + html.escape(path.read_text(encoding="utf-8")) + "</pre>"
        return "html", MD_PAGE.format(title=html.escape(title), body=body)
    return "file", base64.b64encode(path.read_bytes()).decode()


def main():
    items = read_menu()
    groups, files = [], {}
    for group, title, path in items:
        fid = hashlib.sha256(path.relative_to(ROOT).as_posix().encode("utf-8")).hexdigest()[:10]
        kind, data = convert(path, title)
        files[fid] = {"type": kind, "data": data, "name": path.name}
        g = next((g for g in groups if g["name"] == group), None)
        if not g:
            g = {"name": group, "items": []}
            groups.append(g)
        g["items"].append({"id": fid, "title": title, "name": path.name, "type": kind})
        print(f"  [{group}] {title}")
    payload = json.dumps({"built": date.today().isoformat(), "groups": groups, "files": files},
                         ensure_ascii=False).encode("utf-8")

    pw = os.environ.get("VAULT_PASSWORD") or getpass.getpass("관리자 비밀번호: ")
    if len(pw) < 6:
        sys.exit("비밀번호는 6자 이상이어야 한다.")
    if not os.environ.get("VAULT_PASSWORD") and getpass.getpass("비밀번호 확인: ") != pw:
        sys.exit("비밀번호 확인이 일치하지 않는다.")

    salt, iv = secrets.token_bytes(16), secrets.token_bytes(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw.encode("utf-8"))
    ct = AESGCM(key).encrypt(iv, payload, b"admin")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "bundle.bin").write_bytes(iv + ct)
    (OUT / "params.json").write_text(json.dumps({"salt": base64.b64encode(salt).decode(), "iter": ITER,
                                                 "built": date.today().isoformat()}), encoding="utf-8")
    print(f"완료: {len(items)}개 문서, {len(ct)/1e6:.2f} MB → {OUT}")
    print("다음: git add 05_잠금문서/관리자 && git commit -m \"관리자 메뉴 갱신\" && git push")


if __name__ == "__main__":
    main()
