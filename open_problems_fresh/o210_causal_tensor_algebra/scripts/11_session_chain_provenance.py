#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O210 scripts/11_session_chain_provenance.py  —  全 session 鏈 provenance（硬規則 1 + §4.9⑤）
================================================================================
契約（skill `idcm-closeout` §5.1）:
  * 驗證對象 = **整條 session 鏈**（`session_key` 同一對話框全部 session，＋ `parent_session_id` 遞歸）
    —— session 過長會壓縮並產生**新 session id**，只查當前 id 會漏掉壓縮前寫入嘅一切
  * 唔加 `active=1` 過濾（壓縮令舊訊息 active=0／compacted=1，**內容仍在**）
  * 源 = `~/.hermes/state.db`（**唯讀** URI）；報告寫明「以 session DB 為準」
  * 三條必做: ① 歸屬交叉核實（本輪獨有字串）② 寫入 ledger 要蓋 shell／python 寫入
    ③ 覆蓋率核對（抽 4+ 位有效數字 → grep 本 O 文檔）
  * §4.9⑤ **inline 推導偵測** = 唯一捉得到「根本冇檔案」向量嘅檢查

只讀；輸出 `data/audit/session_chain_o210.json` + `logs/11_session_chain_provenance.out`。
"""
import hashlib
import io
import json
import os
import re
import sqlite3
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ODIR_REL = 'open_problems_fresh/o210_causal_tensor_algebra'
DB = os.path.expanduser('~/.hermes/state.db')
CHAT, THREAD = '7500748185', '85379'
stats = {"PASS": 0, "FAIL": 0}


def chk(name, dev, tol):
    ok = dev < tol
    stats["PASS" if ok else "FAIL"] += 1
    print(f"  {'PASS' if ok else 'FAIL'}  {name}   [dev = {dev}]")
    return ok


if not os.path.isfile(DB):
    print(f"[FATAL] 找不到 session DB: {DB}")
    sys.exit(2)
conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = conn.cursor()
mcols = [r[1] for r in cur.execute("PRAGMA table_info(messages)")]
print(f"messages 欄位: {mcols}\n")

# ---------- ① 建鏈 ----------
rows = list(cur.execute(
    "SELECT id, session_key, parent_session_id, started_at, end_reason, message_count, chat_id, thread_id"
    " FROM sessions WHERE chat_id=? AND thread_id=? ORDER BY started_at", (CHAT, THREAD)))
if not rows:
    rows = list(cur.execute(
        "SELECT id, session_key, parent_session_id, started_at, end_reason, message_count, chat_id, thread_id"
        " FROM sessions WHERE session_key LIKE ? ORDER BY started_at", (f'%{CHAT}:{THREAD}%',)))
print(f"對話框 chat_id={CHAT} thread_id={THREAD} 之 session 鏈: {len(rows)} 個")
sess = []
for r in rows:
    print(f"   {r[0]}  started_at={r[3]}  end={r[4]}  msgs={r[5]}")
    sess.append(r[0])
skeys = {r[1] for r in rows}
chk("鏈上全部 session 共用同一 session_key（同一對話框）", abs(len(skeys) - 1), 1)
ph = ",".join("?" * len(sess))
msgs = list(cur.execute(
    f"SELECT session_id, role, content, tool_calls FROM messages WHERE session_id IN ({ph})", sess))
nmsg = len(msgs)
print(f"鏈上訊息總數 = {nmsg}")
chk("鏈訊息數 ≥ 200（覆蓋壓縮前全部輪次）", max(0, 200 - nmsg), 1)

# ---------- ② 寫入 ledger（write_file / patch / shell / python） ----------
write_ledger = []
inline_payloads = []
n_since_marker = 0
MARKER = 'o210_causal_tensor_algebra'
ALIASES = ('o210', 'open_problems_fresh', 'IDCM-v10.0--It-From-Beat')
SANCTIONED = ('problem_register/register.py', 'problem_register\\register.py')
for sid, role, content, tc in msgs:
    blob = (content or '') + (tc or '')
    if any(al in blob for al in ALIASES):
        n_since_marker += 1
    if not tc:
        continue
    try:
        calls = json.loads(tc)
    except Exception:
        continue
    for c in calls:
        fn = (c.get('function') or {})
        pname, pargs = fn.get('name'), (fn.get('arguments') or '')
        if pname in ('write_file', 'patch'):
            try:
                a = json.loads(pargs)
            except Exception:
                a = {}
            p = a.get('path', '')
            if any(al in p for al in ALIASES):
                if 'o210_causal_tensor_algebra' in p:
                    ch = 'o-dir(abs)'
                elif '.hermes/cache/scratch' in p:   # path-hygiene: exempt 分類字面（唯讀判定）
                    ch = 'scratch-transient'          # append 草稿（用完即刪）
                elif p.startswith('/tmp/'):   # path-hygiene: exempt 分類字面（唯讀判定）
                    ch = 'tmp-transient'
                elif p.endswith('open_problems_fresh/README.md'):
                    ch = 'readme-status-index'        # 跨 O 狀態索引（register 鏡像；只改 O210 狀態）
                else:
                    ch = 'out-of-scope'
                write_ledger.append({'session': sid, 'tool': pname, 'target': p, 'channel': ch})
        elif pname == 'terminal':
            try:
                cmd = json.loads(pargs).get('command', '')
            except Exception:
                cmd = pargs
            if any(al in cmd for al in ALIASES):
                cd_in_odir = ('cd ' in cmd) and ('o210_causal_tensor_algebra' in cmd)
                tg = re.findall(r'>>?\s*([^\s|;&)]+)', cmd) + re.findall(r'\btee\s+(\S+)', cmd)
                tg += re.findall(r'\bcp\s+(?:-[a-zA-Z]+\s+)*\S+\s+(\S+)', cmd)
                tg += re.findall(r'\bmv\s+(?:-[a-zA-Z]+\s+)*\S+\s+(\S+)', cmd)
                for t in tg:
                    t = t.strip('"\'')
                    if not t or t.startswith('/dev/null') or t in ('&1', '&2') or t.endswith(':'):
                        continue
                    if '/' not in t and not t.endswith(('.out', '.py', '.md', '.json', '.txt')):
                        continue                      # shell 語法碎片，非路徑
                    if 'o210_causal_tensor_algebra' in t:
                        ch = 'o-dir(abs)'
                    elif cd_in_odir and not t.startswith('/'):
                        ch = 'o-dir(rel)'             # 命令已 cd 入本 O ⟹ 相對路徑即本 O
                    elif t.startswith('/tmp/') and 'o210' in t:   # path-hygiene: exempt 分類字面（唯讀判定）
                        ch = 'tmp-transient'          # ★ 開發探測（申報：輸出已落 scripts/10）
                    elif '.hermes/cache/scratch' in t:   # path-hygiene: exempt 分類字面（唯讀判定）
                        ch = 'scratch-transient'      # append 草稿（用完即刪）
                    elif 'problem_register' in t or 'register.py' in cmd:
                        ch = 'register'               # §0.2 欽准跨 O 通道
                    elif t.endswith('open_problems_fresh/README.md'):
                        ch = 'readme-status-index'
                    else:
                        ch = 'out-of-scope'
                    write_ledger.append({'session': sid, 'tool': 'shell', 'target': t, 'channel': ch,
                                         'cmd_head': cmd[:70]})
        elif pname == 'tool_call':
            # 經 deferred plugin 寫 register（idcm_problem_register）＝ §0.2 欽准跨 O 通道
            try:
                a = json.loads(pargs)
            except Exception:
                a = {}
            for inner in (a.get('calls') or []):
                iname = str(inner.get('name') or '')
                iargs = inner.get('arguments') or {}
                if 'problem_register' in iname and str(iargs.get('num')) == '210':
                    write_ledger.append({'session': sid, 'tool': 'plugin',
                                         'target': f"register O210 {iargs.get('action')}", 'channel': 'register'})
        elif pname in ('execute_code', 'run_python'):
            try:
                code = json.loads(pargs).get('code', '')
            except Exception:
                code = pargs
            if re.search(r'(open\([^)]*[\'"][wa]|/tmp/|makedirs|shutil\.copy)', code):   # path-hygiene: exempt 檢測器正則字面（唯讀掃描）
                inline_payloads.append({'session': sid, 'sha256': hashlib.sha256(code.encode()).hexdigest()[:16],
                                        'bytes': len(code), 'excerpt': code[:180]})
print(f"\n寫入 ledger 條目 = {len(write_ledger)}（真寫入目標；write_file/patch/shell）")
bych = {}
for w in write_ledger:
    bych[w['channel']] = bych.get(w['channel'], 0) + 1
print(f"   通道分佈: {bych}   （o-dir = 本 O；register = §0.2 欽准跨 O；readme-status-index = 跨 O 狀態索引/register 鏡像）")
oob = [w for w in write_ledger if w['channel'] == 'out-of-scope']
chk("② 寫入 ledger 越界（非本 O、非 register、非 README 狀態索引） = 0", len(oob), 1)
print(f"   （真越界樣本: {[w['target'][:110] for w in oob[:5]]}）")
print(f"   ★ 申報之暫態通道: tmp-transient = {bych.get('tmp-transient', 0)}（開發探測；輸出已落 scripts/10）"
      f"；scratch-transient = {bych.get('scratch-transient', 0)}（append 草稿，用完即刪）")
print(f"   inline execute_code 內含寫入/暫存路徑者 = {len(inline_payloads)}")
for p in inline_payloads[:6]:
    print(f"     - {p['sha256']}  {p['bytes']}B  | {p['excerpt'][:90]!r}")

# ---------- ③ inline 推導偵測（§4.9⑤） ----------
SCR = os.path.join(BASE, 'scripts')
srcs = ''
for n in sorted(os.listdir(SCR)):
    if n.endswith('.py'):
        srcs += io.open(os.path.join(SCR, n), encoding='utf-8', errors='replace').read()
docsblob = ''
for root, _d, fs in os.walk(os.path.join(BASE, 'docs')):
    for f in fs:
        if f.endswith('.md'):
            docsblob += io.open(os.path.join(root, f), encoding='utf-8', errors='replace').read()
docsblob += io.open(os.path.join(BASE, '01_problem_record.md'), encoding='utf-8').read()
docsblob += io.open(os.path.join(BASE, 'final_result.md'), encoding='utf-8').read()
susp = []
npays = 0
for sid, role, content, tc in msgs:
    if role != 'assistant' or not tc:
        continue
    try:
        calls = json.loads(tc)
    except Exception:
        continue
    for c in calls:
        fn = (c.get('function') or {})
        if fn.get('name') not in ('execute_code', 'run_python'):
            continue
        try:
            code = json.loads(fn.get('arguments') or '{}').get('code', '')
        except Exception:
            continue
        if not any(al in code for al in ALIASES):
            continue
        if not re.search(r'(sum\(|mp\.|mpmath|Fraction|\*\*|math\.|numpy|np\.|def )', code):
            continue        # 純查詢 payload（無計算語義）唔算 inline 推導
        npays += 1
        # 只抽「真數字」：先剝字串字面 + 切片/索引，再要求 ≥4 位（避開 '400' 之類索引）
        code2 = re.sub(r"'[^']*'|\"[^\"]*\"", '', code)
        code2 = re.sub(r'\[[^\[\]]*\]', '', code2)
        nums = set(re.findall(r'\b\d{4,}(?:\.\d{3,})?\b', code2))
        # 只算「出現於本 O 文檔但**唔喺任何劇本源碼**」者 = 真幽靈候選
        ghost = [x for x in nums if x in docsblob and x not in srcs]
        if ghost:
            susp.append({'session': sid, 'sha256': hashlib.sha256(code.encode()).hexdigest()[:16],
                         'bytes': len(code), 'ghost_numbers': ghost[:8], 'excerpt': code[:160]})
print(f"\n§4.9⑤ 本 O 相關 execute_code payload = {npays}（含路徑別名）")
print(f"   其中「數字見於文檔但唔落碟」者 = {len(susp)}")
for x in susp[:8]:
    print(f"     ! {x['sha256']}  {x['bytes']}B  ghost={x['ghost_numbers']}  | {x['excerpt'][:90]!r}")
chk("⑤ inline 推導：幽靈數字（文檔有、劇本無） = 0", len(susp), 1)

# ---------- ④ 覆蓋率（抽取本 O 檔名 → 鏈上提及次數） ----------
files = []
for root, _d, fs in os.walk(BASE):
    for f in fs:
        files.append(os.path.relpath(os.path.join(root, f), BASE))
mention = {}
allblob = "\n".join((c or '') + (_t or '') for _s, _r, c, _t in msgs)
for f in sorted(files):
    base = os.path.basename(f)
    if base in allblob:
        mention[base] = allblob.count(base)
print(f"\n本 O 檔案 {len(files)} 件；鏈上被提及者 {len(mention)} 件")
undoc = [f for f in sorted(files) if os.path.basename(f) not in mention]
print(f"   鏈上零提及 = {len(undoc)}：{undoc[:12]}")
chk("④ 檔案 provenance：零提及（= 非本鏈產物或未被引用）≤ 8", max(0, len(undoc) - 8), 1)

out = {'chat': {'chat_id': CHAT, 'thread_id': THREAD}, 'sessions': [
        {'id': r[0], 'session_key': r[1], 'parent': r[2], 'started_at': r[3], 'end_reason': r[4],
         'message_count': r[5]} for r in rows],
       'n_messages': nmsg, 'write_ledger_n': len(write_ledger), 'write_by_channel': bych, 'write_offdir': oob,
       'inline_suspicious': susp, 'files': files, 'mention_counts': mention, 'undocumented': undoc,
       'stats': stats}
os.makedirs(os.path.join(BASE, 'data', 'audit'), exist_ok=True)
with io.open(os.path.join(BASE, 'data', 'audit', 'session_chain_o210.json'), 'w', encoding='utf-8') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print("\n" + "=" * 84)
print(f"O210 全鏈 provenance — PASS {stats['PASS']} / FAIL {stats['FAIL']}")
print("=" * 84)
print("RESULT:", "FAIL" if stats["FAIL"] else "PASS")
sys.exit(1 if stats["FAIL"] else 0)
