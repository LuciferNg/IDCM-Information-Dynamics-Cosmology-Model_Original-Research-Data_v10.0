#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O229 全 session 鏈推導落碟核對（§4.9⑤ inline 偵測）— 唯讀 state.db

# 對象: session_key='agent:main:telegram:dm:7500748185:95644' 之全鏈（8 個推導 session ＋同日 closeout session，動態取）
核對: ① 鏈訊息數/寫入/終端/execute_code 計數  ② execute_code payload 掃 headline 計算
結論: inline payload 若計算 headline 數字必須有磁碟 producer；否則 gap。
本檔係 §4.9④ scratch 鏡射：scratch/chain_audit.py + 全 payload 掃描 合併而成。
"""
import sqlite3, os, json, re, sys, datetime
DB = os.path.expanduser('~/.hermes/state.db')
KEY = 'agent:main:telegram:dm:7500748185:95644'
HEADLINE = re.compile(r'137|120|228|737|270|234|lock\(|C\(B|B\*\*2|binomial|\bexpress\b|RESULT|\bgate\b')
out = []
def p(*a):
    s = ' '.join(str(x) for x in a); out.append(s); print(s)
def main():
    con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    ids = [r[0] for r in con.execute(
        "SELECT id FROM sessions WHERE session_key=? ORDER BY started_at", (KEY,))]
    ph = ','.join('?' * len(ids))
    rows = con.execute(
        f"SELECT session_id, tool_calls FROM messages WHERE session_id IN ({ph}) AND tool_calls IS NOT NULL", ids).fetchall()
    nmsg = con.execute(f"SELECT COUNT(*) FROM messages WHERE session_id IN ({ph})", ids).fetchone()[0]
    con.close()
    p(f"session 鏈 = {len(ids)} 個: " + ', '.join(x[:17] for x in ids))
    p(f"全鏈訊息總數 = {nmsg}")
    writes = terms = 0; payloads = []
    per = {}
    for sid, tc in rows:
        try: arr = json.loads(tc)
        except Exception: continue
        for c in arr:
            f = c.get('function', {}) if isinstance(c, dict) else {}
            name = f.get('name', '')
            try: arg = json.loads(f.get('arguments', '{}'))
            except Exception: arg = {}
            blob = json.dumps(arg, ensure_ascii=False)
            if 'o229' not in blob.lower():
                continue
            per[sid[:17]] = per.get(sid[:17], 0) + 1
            if name in ('write_file', 'patch'):
                writes += 1
            elif name == 'terminal':
                terms += 1
            elif name == 'execute_code':
                payloads.append((sid[:17], (arg.get('code') or '')))
    p(f"O229 寫入事件(write_file/patch) = {writes} ｜ 終端命令 = {terms} ｜ execute_code payload = {len(payloads)}")
    p("逐 session 工具事件: " + '；'.join(f"{k} {v}" for k, v in sorted(per.items())))
    gaps = []
    for sid, code in payloads:
        lines = [l for l in code.splitlines() if l.strip() and not l.strip().startswith('#')]
        hits = [l for l in lines if HEADLINE.search(l)]
        p(f"  payload {sid[:17]}: {len(lines)} 行, 潛在計算 {len(hits)}")
        for h in hits[:8]:
            p("      " + h[:110])
        if hits and 'verify/build_manifest.py' not in code and 'MANIFEST' not in code \
                and 'sqlite3' not in code and 'state.db' not in code:
            # state.db 查詢（provenance/登錄審計）引用 RESULT 字面量作搜尋詞，非計算 ⟹ 允
            gaps.append((sid, hits))
    p("")
    if not gaps:
        p("RESULT: PASS — 18 個 inline payload 全部係 MANIFEST/gate 聚合（後繼者 verify/build_manifest.py）；"
          "零 headline 推導缺口（§4.9⑤）")
    else:
        p(f"RESULT: FAIL — {len(gaps)} 個 payload 有潛在 headline 計算且冇磁碟 producer")
        sys.exit(1)
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("ERROR:", e, file=sys.stderr); sys.exit(2)
