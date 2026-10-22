#!/usr/bin/env python3
"""O210 scripts/13 — MANIFEST 產生器（收尾凍結；skill idcm-closeout §4.9 / trail_integrity_check C4）。

契約：
  1. 掃描本 O 目錄全部檔案（排除 `data/MANIFEST.json` 自身與 .pyc），記 bytes + sha256。
  2. `untracked_by_design` = **自指產物**（MANIFEST 自身、本劇本之 log —— 產生時自身 log 尚未 flush）。
  3. **必須係鏈上最後一支**（跑喺全部寫入之後）；否則之後任何寫入都會令 sha 失效，C4 會 FAIL。
  4. 只讀本 O 目錄；唯一寫入 = `data/MANIFEST.json`。
  5. 零字面 True；輸出 `RESULT: PASS` / `RESULT: FAIL`。
"""
import datetime
import hashlib
import io
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_REL = 'data/MANIFEST.json'
UTD = [OUT_REL, 'logs/13_manifest.out']
stats = {'PASS': 0, 'FAIL': 0}


def chk(name, dev, tol):
    ok = dev < tol
    stats['PASS' if ok else 'FAIL'] += 1
    print(f"  {'PASS' if ok else 'FAIL'}  {name}   [dev = {dev}]")
    return ok


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 16), b''):
            h.update(b)
    return h.hexdigest()


files = []
for root, dirs, fs in os.walk(BASE):
    dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__')]
    for f in sorted(fs):
        rel = os.path.relpath(os.path.join(root, f), BASE)
        if rel == OUT_REL or rel.endswith('.pyc'):
            continue
        files.append({'path': rel, 'bytes': os.path.getsize(os.path.join(BASE, rel)),
                      'sha256': sha256(os.path.join(BASE, rel))})
files.sort(key=lambda x: x['path'])
scripts = [x for x in files if x['path'].startswith('scripts/') and x['path'].endswith('.py')]
docs = [x for x in files if x['path'].startswith('docs/') and x['path'].endswith('.md')]
logs = [x for x in files if x['path'].startswith('logs/')]
print(f"   檔案總數 = {len(files)}（scripts={len(scripts)}　docs={len(docs)}　logs={len(logs)}）")
chk("覆蓋 scripts/*.py ≥ 13", 0 if len(scripts) >= 13 else 1, 1)
chk("覆蓋 docs/*.md ≥ 13", 0 if len(docs) >= 13 else 1, 1)
chk("覆蓋 logs/*.out ≥ 13", 0 if len(logs) >= 13 else 1, 1)
mf = {'generated_at': datetime.datetime.now().isoformat(timespec='seconds'),
      'base': 'open_problems_fresh/o210_causal_tensor_algebra',
      'files': files,
      'untracked_by_design': UTD,
      'note': ('O210 收尾凍結（R8）。任何後續重跑都會令 logs/11_session_chain_provenance.out'
               '（動態 session 統計）及 data/audit/*.json 失效 ⟹ 必須重新產生 MANIFEST 並經 register 通報。'),
      'n_scripts': len(scripts), 'n_docs': len(docs), 'n_logs': len(logs)}
os.makedirs(os.path.join(BASE, 'data'), exist_ok=True)
with io.open(os.path.join(BASE, OUT_REL), 'w', encoding='utf-8') as f:
    json.dump(mf, f, ensure_ascii=False, indent=1)
    f.write('\n')
back = json.load(io.open(os.path.join(BASE, OUT_REL), encoding='utf-8'))
chk("寫入後讀回：path 集合一致", 0 if {x['path'] for x in back['files']} == {x['path'] for x in files} else 1, 1)
chk("寫入後讀回：sha 逐個一致", sum(1 for a, b in zip(files, back['files']) if a['sha256'] != b['sha256']), 1)
chk("self 唔在 files（避免自指）", 0 if OUT_REL not in {x['path'] for x in files} else 1, 1)
print(f"  MANIFEST → {OUT_REL}（{len(files)} 檔；untracked_by_design = {UTD}）")
print("=" * 84)
print(f"O210 MANIFEST — PASS {stats['PASS']} / FAIL {stats['FAIL']}")
print("=" * 84)
print("RESULT: PASS" if stats['FAIL'] == 0 else "RESULT: FAIL")
sys.exit(0 if stats['FAIL'] == 0 else 1)
