#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/102 -- R27 合約閘（`r27-crit1-orbit-v1`）：凍結合約＋預註冊核＋負對照。

C1 合約 doc 存在且含關鍵定義（orbit／⟨M,S⟩／雙奇／三層／見數前凍結）
C2 預註冊 tag 齊備（O1–O4／P1–P4／Q1–Q2 共 10 條）
C3 判決規則聲明在場（精確算術、禁用 import 清單、兩條獨立實作、唯讀 O222）
C4 負對照（併列）：合約**不以** R1／R4 之原式（`R ≡ 0 ⟺ tie 規則 u-奇`）作為 Part O／P 判據，且必須以「否證」形式出現
C5 寫入凍結指紋 data/102_r27_freeze.json（sha256 = 合約 doc 內容 sha256）→ GATE OPEN
用法: /usr/bin/python3 scripts/102_r27_contract.py
"""
import hashlib
import io
import json
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
DOC = os.path.join(BASE, 'docs', '58_r27_contract.md')
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def main():
    print('=' * 112)
    print('O225 scripts/102 -- R27 合約閘')
    print('=' * 112)
    t = io.open(DOC, encoding='utf-8').read()
    keys = ['orbit', '⟨M,S⟩', 'double_odd', '三層', '見數前凍結']
    claim('C1', '合約 doc 存在且含關鍵定義', all(k in t for k in keys),
          '缺 = %s' % [k for k in keys if k not in t])
    tags = ['O1', 'O2', 'O3', 'O4', 'P1', 'P2', 'P3', 'P4', 'Q1', 'Q2']
    miss = [g for g in tags if ('**%s**' % g) not in t]
    claim('C2', '預註冊 tag 齊備（O1–O4／P1–P4／Q1–Q2 = 10 條）', not miss, '缺 = %s' % (miss or '無'))
    rules = ['精確', '禁用', '唯讀', '兩條獨立實作']
    claim('C3', '判決規則聲明在場', all(k in t for k in rules), '缺 = %s' % [k for k in rules if k not in t])
    neg_ok = ('否證' in t) and ('144/256' in t)
    naive_as_criterion = bool(re.search(r'^-\s*\*\*P\d\*\*.*u-奇', t, re.M))
    claim('C4', '負對照：原式僅以「否證」形式出現，未作為 Part O／P 判據', neg_ok and not naive_as_criterion,
          '原式出現於否證語境 = %s；被誤用作判據 = %s' % (neg_ok, naive_as_criterion))
    sha = hashlib.sha256(io.open(DOC, 'rb').read()).hexdigest()
    fp = os.path.join(BASE, 'data', '102_r27_freeze.json')
    io.open(fp, 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r27-crit1-orbit-v1', 'contract': 'docs/58_r27_contract.md', 'sha256': sha,
         'frozen_at': time.strftime('%Y-%m-%d %H:%M:%S'), 'claims_declared': tags,
         'note': '見數前凍結：本指紋於 scripts/103（機器）與 scripts/104（審計）執行前寫定'},
        indent=1, ensure_ascii=False))
    claim('C5', '凍結指紋已寫入（sha256 = 合約內容）', os.path.exists(fp), 'sha256 = %s…' % sha[:16])
    npass = sum(1 for c in CLAIMS if c['ok'])
    gate = 'OPEN' if npass == len(CLAIMS) else 'CLOSED'
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  GATE %s  |  r27-crit1-orbit-v1' % (npass, len(CLAIMS), gate))
    io.open(os.path.join(BASE, 'data', '102_r27_contract.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r27-crit1-orbit-v1', 'claims': CLAIMS, 'gate': gate, 'n_pass': npass, 'n_total': len(CLAIMS),
         'contract_sha256': sha}, indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
