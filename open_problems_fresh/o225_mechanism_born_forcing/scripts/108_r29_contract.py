#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/108 -- R29 合約閘（`r29-mech1-residual-v1`）。

C1 合約 doc 含關鍵定義（非單項族、V(a)、σ(u)、充要、MECH-2）
C2 預註冊 tag 齊備（P1–P5／Q1–Q4）
C3 判決規則在場（精確／禁用／唯讀／兩條獨立實作／否證原樣保留）
C4 負對照：合約明載「MECH-1 於本輪僅當 I* 為**純 u-符號/型別量**時判 ✅」⟹ 禁以含 dind／事件量之「不變量」冒充導出
C5 凍結指紋寫入 data/108_r29_freeze.json → GATE OPEN
用法: /usr/bin/python3 scripts/108_r29_contract.py
"""
import hashlib
import io
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
DOC = os.path.join(BASE, 'docs', '62_r29_contract.md')
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def main():
    print('=' * 112)
    print('O225 scripts/108 -- R29 合約閘')
    print('=' * 112)
    t = io.open(DOC, encoding='utf-8').read()
    keys = ['非單項族', 'V(a)', 'σ(u)', '充要', 'MECH-2', '{39, 40, 41, 42}']
    claim('C1', '合約含關鍵定義', all(k in t for k in keys), '缺 = %s' % [k for k in keys if k not in t])
    tags = ['P1', 'P2', 'P3', 'P4', 'P5', 'Q1', 'Q2', 'Q3', 'Q4']
    miss = [g for g in tags if ('**%s' % g) not in t]
    claim('C2', '預註冊 tag 齊備（P1–P5／Q1–Q4 = 9 條）', not miss, '缺 = %s' % (miss or '無'))
    rules = ['精確算術', '禁用', '唯讀 O222', '兩條獨立實作', '原樣保留 FAIL']
    claim('C3', '判決規則在場', all(k in t for k in rules), '缺 = %s' % [k for k in rules if k not in t])
    claim('C4', '負對照：禁以含 dind／事件量之「不變量」冒充導出（純 u-符號/型別量之閘在場）',
          '純 `u`-符號/型別量' in t and '不含 `dind`／事件量' in t,
          '閘條款 = %s' % ('在場' if '純 `u`-符號/型別量' in t else '缺失'))
    sha = hashlib.sha256(io.open(DOC, 'rb').read()).hexdigest()
    fp = os.path.join(BASE, 'data', '108_r29_freeze.json')
    io.open(fp, 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r29-mech1-residual-v1', 'contract': 'docs/62_r29_contract.md', 'sha256': sha,
         'frozen_at': time.strftime('%Y-%m-%d %H:%M:%S'), 'claims_declared': tags,
         'note': '見數前凍結：本指紋於 scripts/109（機器）與 scripts/110（審計）執行前寫定'}, indent=1, ensure_ascii=False))
    claim('C5', '凍結指紋已寫入', os.path.exists(fp), 'sha256 = %s…' % sha[:16])
    npass = sum(1 for c in CLAIMS if c['ok'])
    gate = 'OPEN' if npass == len(CLAIMS) else 'CLOSED'
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  GATE %s  |  r29-mech1-residual-v1' % (npass, len(CLAIMS), gate))
    io.open(os.path.join(BASE, 'data', '108_r29_contract.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r29-mech1-residual-v1', 'claims': CLAIMS, 'gate': gate, 'n_pass': npass, 'n_total': len(CLAIMS),
         'contract_sha256': sha}, indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
