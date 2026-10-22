#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/120 -- R33 合約閘（`r33-closure-batch-v1`）。用法: /usr/bin/python3 scripts/120_r33_contract.py"""
import hashlib
import io
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
DOC = os.path.join(BASE, 'docs', '70_r33_contract.md')
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def main():
    print('=' * 112)
    print('O225 scripts/120 -- R33 合約閘')
    print('=' * 112)
    t = io.open(DOC, encoding='utf-8').read()
    keys = ['C1', 'C2', 'C3', 'C4', 'C5', '512', 'no-go', 'Λ⁻¹(0)', '4 元組', '否定閉合']
    claim('C1', '合約含五項完備類與關鍵詞', all(k in t for k in keys), '缺 = %s' % [k for k in keys if k not in t])
    tags = ['**C1', '**C2', '**C3', '**C4', '**C5']
    miss = [g for g in tags if g not in t]
    claim('C2', '完備候選類 C1–C5 預註冊齊備', not miss, '缺 = %s' % (miss or '無'))
    rules = ['精確算術', '禁用', '唯讀 O222', '兩條獨立實作', '原樣保留 FAIL']
    claim('C3', '判決規則在場', all(k in t for k in rules), '缺 = %s' % [k for k in rules if k not in t])
    claim('C4', '負對照：C2 明載「R31 P2 ✗ 屬凍結 T3 之重證，非新殘餘」（禁以重證冒充新發現）',
          '非新殘餘' in t, '閘條款 = %s' % ('在場' if '非新殘餘' in t else '缺失'))
    sha = hashlib.sha256(io.open(DOC, 'rb').read()).hexdigest()
    fp = os.path.join(BASE, 'data', '120_r33_freeze.json')
    io.open(fp, 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r33-closure-batch-v1', 'contract': 'docs/70_r33_contract.md', 'sha256': sha,
         'frozen_at': time.strftime('%Y-%m-%d %H:%M:%S')}, indent=1, ensure_ascii=False))
    claim('C5', '凍結指紋已寫入', os.path.exists(fp), 'sha256 = %s…' % sha[:16])
    npass = sum(1 for c in CLAIMS if c['ok'])
    gate = 'OPEN' if npass == len(CLAIMS) else 'CLOSED'
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  GATE %s  |  r33-closure-batch-v1' % (npass, len(CLAIMS), gate))
    io.open(os.path.join(BASE, 'data', '120_r33_contract.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r33-closure-batch-v1', 'claims': CLAIMS, 'gate': gate, 'n_pass': npass, 'n_total': len(CLAIMS),
         'contract_sha256': sha}, indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())