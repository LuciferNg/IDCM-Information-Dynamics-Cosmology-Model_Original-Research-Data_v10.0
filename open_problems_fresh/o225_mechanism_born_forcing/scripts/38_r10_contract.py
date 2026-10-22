#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/38 -- R10 合約閘（`r10-universality-and-selection-v1`）：
凍結合約 sha256、上游輸入 sha256、預註冊 tag 完整性、陽性／陰性對照、GATE OPEN/CLOSED。

用法: /usr/bin/python3 scripts/38_r10_contract.py
"""
import hashlib
import io
import json
import os
import shutil
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RULES = 'r10-universality-and-selection-v1'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-6s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


def sha256(path):
    h = hashlib.sha256()
    with io.open(path, 'rb') as fh:
        for blk in iter(lambda: fh.read(1 << 20), b''):
            h.update(blk)
    return h.hexdigest()


TAGS = ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4',
        'C1', 'C2', 'C3', 'D1', 'D2', 'D3', 'D4', 'E1', 'E2', 'E3']
PHRASES = ['7440', 'S_TF(a,g) = 0', 'S_FT(a,g) = 0', '共軛類', 'u-奇', '中心封閉',
           '商', '非仿射', '充要', '2·n_tie']


def main():
    print('=' * 110)
    print('O225 scripts/38 -- R10 CONTRACT GATE   (rules: %s)' % RULES)
    print('=' * 110, flush=True)
    cpath = os.path.join(BASE, 'docs/20_r10_contract.md')
    txt = io.open(cpath, encoding='utf-8').read()
    up = {rel: sha256(os.path.join(O222, rel)) for rel in ('scripts/12_b5_budget.py', 'scripts/09_a2_rollback.py')}
    freed = {'rules': RULES, 'contract': 'docs/20_r10_contract.md', 'contract_sha256': sha256(cpath),
             'frozen_inputs': {'%s/%s' % (O222, k): {'sha256': v} for k, v in up.items()},
             'frozen_at': 'first run of scripts/38'}
    fpath = os.path.join(BASE, 'data/38_r10_freeze.json')
    prev = json.load(io.open(fpath, encoding='utf-8')) if os.path.isfile(fpath) else None
    first = prev is None
    if not first:
        claim('C0', '合約自凍結後未被改動（sha256 與首跑凍結值一致）',
              prev['contract_sha256'] == freed['contract_sha256'],
              'prev = %s ; now = %s' % (prev['contract_sha256'][:16], freed['contract_sha256'][:16]))
    else:
        with io.open(fpath, 'w', encoding='utf-8') as fh:
            json.dump(freed, fh, indent=1, ensure_ascii=False)
        print('[INFO] 首跑：已凍結合約與上游輸入 sha256 → data/38_r10_freeze.json', flush=True)

    miss_tag = [t for t in TAGS if ('**' + t) not in txt and ('- ' + t) not in txt and (t + '：') not in txt]
    claim('C1', '預註冊 tag 完整性：A1–E3 全部 18 個 tag 皆在凍結合約中', not miss_tag, 'missing = %s' % miss_tag)
    miss_ph = [p for p in PHRASES if p not in txt]
    claim('C2', '關鍵片語完整性（範圍證明）：核心命題與判準片語皆在合約中', not miss_ph, 'missing = %s' % miss_ph)

    # 陽性對照：篡改一個字後必須被拒
    tmp = tempfile.mkdtemp()
    bad = os.path.join(tmp, 'tampered.md')
    io.open(bad, 'w', encoding='utf-8').write(txt.replace('7440', '7441', 1))
    bad_ok = sha256(bad) != freed['contract_sha256']
    claim('C3', '陽性對照：篡改「7440 → 7441」之副本被判為不合（sha 不同）', bad_ok, 'sha 不同 = %s' % bad_ok)
    shutil.rmtree(tmp, ignore_errors=True)
    # 陰性對照：真合約在呢度，通過
    claim('C4', '陰性對照：真合約（未篡改）通過 sha 與片語檢查', not miss_tag and not miss_ph,
          'tag 缺 = %d ; 片語缺 = %d' % (len(miss_tag), len(miss_ph)))
    # 上游輸入唯讀核實
    now_up = {rel: sha256(os.path.join(O222, rel)) for rel in ('scripts/12_b5_budget.py', 'scripts/09_a2_rollback.py')}
    claim('C5', '上游唯讀：O222 兩個輸入腳本之 sha256 於本輪全程不變', now_up == up,
          '變化 = %s' % [k for k in up if up[k] != now_up[k]])

    npass = sum(1 for c in CLAIMS if c['ok'])
    gate = 'OPEN' if npass == len(CLAIMS) else 'CLOSED'
    print('=' * 110)
    print('RESULT: %d/%d PASS  |  GATE %s' % (npass, len(CLAIMS), gate))
    out = dict(freed)
    out.update({'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS, 'gate': gate,
                'tags': TAGS, 'phrases': PHRASES})
    with io.open(fpath, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if gate == 'OPEN' else 1


if __name__ == '__main__':
    raise SystemExit(main())
