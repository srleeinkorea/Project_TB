"""단일 HTML 문서를 비밀번호로 암호화해 공개 사이트용 잠금 페이지로 만든다.

사용:
    python tools/lock_doc.py <원본.html> <출력디렉터리> [제목]
    VAULT_PASSWORD=... 환경변수가 없으면 비밀번호를 물어본다.

출력: <출력디렉터리>/doc.bin (암호문), params.json (salt·iter), index.html (잠금 뷰어)
vault_build.py 와 같은 방식 (PBKDF2-SHA256 600,000회 + AES-256-GCM).
"""
import base64, getpass, json, os, secrets, sys
from datetime import date
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 600_000
VIEWER = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>__TITLE__</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600&family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#fbfbfd;--paper:#fff;--ink:#0f1222;--mute:#6b7083;--line:#e3e6ef;--blue:#5170FF;--red:#e0453f}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);font-family:'DM Sans','Noto Sans KR',sans-serif;font-size:14px}
#gate{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;padding:16px;background:var(--bg)}
#gate form{width:100%;max-width:400px;background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:30px 28px}
.kicker{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--blue);font-weight:600}
h1{font-family:'DM Serif Display','Noto Sans KR',serif;font-weight:400;font-size:24px;margin:6px 0 8px;line-height:1.25}
#gate p{color:var(--mute);font-size:13px;margin:0 0 18px}
input{font:inherit;width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:4px}
input:focus{outline:2px solid var(--blue);outline-offset:1px}
.row{display:flex;justify-content:flex-end;margin-top:12px}
button{font:inherit;cursor:pointer;background:var(--blue);color:#fff;border:1px solid var(--blue);border-radius:4px;padding:8px 18px;font-weight:600}
button:disabled{opacity:.5}.err{color:var(--red);font-size:12.5px;min-height:18px;margin-top:8px}
iframe{display:none;width:100%;height:100%;border:0;background:#fff}
</style></head><body>
<div id="gate"><form id="f">
<div class="kicker">Restricted · 대한결핵협회 × 마이허브</div>
<h1>__TITLE__</h1>
<p>이 문서는 암호화되어 있다. 비밀번호를 입력하면 브라우저 안에서만 복호화되어 표시된다.</p>
<input id="pw" type="password" autocomplete="current-password" placeholder="비밀번호" aria-label="비밀번호" autofocus>
<div class="err" id="err" role="alert"></div>
<div class="row"><button type="submit" id="go">열기</button></div>
</form></div>
<iframe id="view" title="문서" sandbox="allow-same-origin allow-scripts allow-popups"></iframe>
<script>
const $=i=>document.getElementById(i),enc=new TextEncoder();
const b64=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
$('f').onsubmit=async e=>{e.preventDefault();$('err').textContent='';$('go').disabled=true;
try{const p=await (await fetch('params.json',{cache:'no-store'})).json();
const base=await crypto.subtle.importKey('raw',enc.encode($('pw').value),'PBKDF2',false,['deriveKey']);
const key=await crypto.subtle.deriveKey({name:'PBKDF2',salt:b64(p.salt),iterations:p.iter,hash:'SHA-256'},base,{name:'AES-GCM',length:256},false,['decrypt']);
const buf=new Uint8Array(await (await fetch('doc.bin',{cache:'no-store'})).arrayBuffer());
let plain;try{plain=await crypto.subtle.decrypt({name:'AES-GCM',iv:buf.slice(0,12),additionalData:enc.encode('doc')},key,buf.slice(12));}
catch{throw new Error('비밀번호가 올바르지 않다.');}
const v=$('view');v.src=URL.createObjectURL(new Blob([plain],{type:'text/html'}));v.style.display='block';$('gate').style.display='none';$('pw').value='';
}catch(err){$('err').textContent=err.message;}finally{$('go').disabled=false;}};
</script></body></html>
"""

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    title = sys.argv[3] if len(sys.argv) > 3 else src.stem
    pw = os.environ.get("VAULT_PASSWORD") or getpass.getpass("비밀번호: ")
    if len(pw) < 4:
        sys.exit("비밀번호는 4자 이상이어야 한다.")
    salt = secrets.token_bytes(16)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw.encode())
    iv = secrets.token_bytes(12)
    ct = AESGCM(key).encrypt(iv, src.read_bytes(), b"doc")
    out.mkdir(parents=True, exist_ok=True)
    (out / "doc.bin").write_bytes(iv + ct)
    (out / "params.json").write_text(json.dumps({"salt": base64.b64encode(salt).decode(), "iter": ITER,
                                                 "built": date.today().isoformat(), "source": src.name}), encoding="utf-8")
    (out / "index.html").write_text(VIEWER.replace("__TITLE__", title), encoding="utf-8")
    print(f"완료: {src.name} → {out} ({len(ct):,} B)")

if __name__ == "__main__":
    main()
