#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/105 -- R28 合約閘（`r28-crit2-misc1-v1`）：凍結合約＋預註冊核＋負對照。

C1 合約 doc 存在且含關鍵定義（C1–C4、V0–V8、rank_GF(2)、Q₈、Aut 120／GeoAut 60）
C2 預註冊 tag 齊備（F1–F5、G1–G5 共 10 條）
C3 判決規則聲明在場（精確／禁用／唯讀／完整重算／兩條獨立實作）
C4 負對照：本輪**不得**以「部分 variant 抽樣」代替全族（合約須載「每個 variant 必須完整重算」）
C5 凍結指紋寫入 data/105_r28_freeze.json（sha256 = 合約內容 sha256）→ GATE OPEN
用法: /usr/bin/python3 scripts/105_r28_contract.py
"""
import hashlib
import io
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
DOC = os.path.join(BASE, 'docs', '60_r28_contract.md')
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def main():
    print('=' * 112)
    print('O225 scripts/105 -- R28 合約閘')
    print('=' * 112)
    t = io.open(DOC, encoding='utf-8').read()
    keys = ['C1', 'C4', 'V0', 'V8', 'rank_GF(2)', 'Q₈', '|Aut| = 120', '|GeoAut| = 60']
    claim('C1', '合約含關鍵定義（四判準、9 variant、秩、Q₈、Aut/GeoAut）', all(k in t for k in keys),
          '缺 = %s' % [k for k in keys if k not in t])
    tags = ['F1', 'F2', 'F3', 'F4', 'F5', 'G1', 'G2', 'G3', 'G4', 'G5']
    miss = [g for g in tags if ('**%s' % g) not in t]
    claim('C2', '預註冊 tag 齊備（F1–F5／G1–G5 = 10 條）', not miss, '缺 = %s' % (miss or '無'))
    rules = ['精確算術', '禁用', '唯讀 O222', '完整重算', '兩條獨立實作']
    claim('C3', '判決規則聲明在場', all(k in t for k in rules), '缺 = %s' % [k for k in rules if k not in t])
    claim('C4', '負對照：禁止以抽樣代替全族（「每個 variant 必須完整重算」在場）', '每個 variant 必須**完整重算**' in t,
          '抽樣替代之禁止條款 = %s' % ('在場' if '每個 variant 必須**完整重算**' in t else '缺失'))
    sha = hashlib.sha256(io.open(DOC, 'rb').read()).hexdigest()
    fp = os.path.join(BASE, 'data', '105_r28_freeze.json')
    io.open(fp, 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r28-crit2-misc1-v1', 'contract': 'docs/60_r28_contract.md', 'sha256': sha,
         'frozen_at': time.strftime('%Y-%m-%d %H:%M:%S'), 'claims_declared': tags,
         'note': '見數前凍結：本指紋於 scripts/106（機器）與 scripts/107（審計）執行前寫定'}, indent=1, ensure_ascii=False))
    claim('C5', '凍結指紋已寫入（sha256 = 合約內容）', os.path.exists(fp), 'sha256 = %s…' % sha[:16])
    npass = sum(1 for c in CLAIMS if c['ok'])
    gate = 'OPEN' if npass == len(CLAIMS) else 'CLOSED'
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  GATE %s  |  r28-crit2-misc1-v1' % (npass, len(CLAIMS), gate))
    io.open(os.path.join(BASE, 'data', '105_r28_contract.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r28-crit2-misc1-v1', 'claims': CLAIMS, 'gate': gate, 'n_pass': npass, 'n_total': len(CLAIMS),
         'contract_sha256': sha}, indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
