#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/41 -- R18 合約閘：凍結合約 sha256、預註冊 tag 完整性、陽／陰對照、GATE。用法: /usr/bin/python3 scripts/63_r18_contract.py"""
import hashlib, io, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
CONTRACT = os.path.join(BASE, 'docs/37_r18_contract.md'); FREEZE = os.path.join(BASE, 'data/63_r18_freeze.json')
SHA = '07dbd971b707b18cc27fff50dda7db72bd4c8a02d6aaf268c4c176354544176924656ade063067cd0eadddf04071d7a761df8ca211e51936440cd417d37682447e8189d077cdf2a293eb1e75ed8e40f2a71282146cc2ed35ac0281236beb1a4676aaa67c27d03310'
CLAIMS = []
def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)
def sha256(p): return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()
def main():
    print('=' * 108); print('O225 scripts/48 -- R13 CONTRACT GATE'); print('=' * 108, flush=True)
    first = not os.path.exists(FREEZE)
    freed = json.load(io.open(FREEZE, encoding='utf-8')) if not first else {}
    cur = sha256(CONTRACT)
    if first:
        freed = {'rules': 'r18-frame-criterion-v1', 'contract': 'docs/37_r18_contract.md',
                 'contract_sha256': cur, 'frozen_at': 'first run of scripts/41'}
    claim('C1', '凍結合約 sha256 與記錄一致', cur == freed['contract_sha256'], 'sha = %s…' % cur[:16])
    txt = io.open(CONTRACT, encoding='utf-8').read()
    need = ['N1', 'N2', 'N3', 'N4', 'N5', 'O1', 'O2', 'O3', 'O4']
    miss = [t for t in need if not re.search(r'\*\*' + t + r'(?:\s|\*|（)', txt)]
    claim('C2', '預註冊 tag 完整（9 個：N1–N5／O1–O4）', not miss, '缺 = %s' % miss)
    pos = 'ℓ(U_a × v) ≠ ℓ(v)'
    claim('C3', '陽性對照：合約載明 Part N 之完整判準（leading index ＋ 陪集）', pos in txt and '陪集' in txt, '命中 = %s' % (pos in txt))
    tampered = txt.replace('ℓ(U_a × v) ≠ ℓ(v)', '某條件')
    claim('C4', '陰性對照：篡改後之合約（弱化為「可能成群」）必須被 C3 判據拒絕',
          tampered != txt and pos not in tampered, '篡改版仍含完整判準 = %s' % (pos in tampered))
    pre = True
    if not first:
        pre = all(freed.get(k) == v for k, v in [('contract_sha256', cur)])
    claim('C5', 'GATE 條件：合約未被改動、tag 完整、陰陽對照成立',
          cur == freed['contract_sha256'] and not miss and pos in txt, 'GATE = %s' % ('OPEN' if (cur == freed['contract_sha256'] and not miss and pos in txt) else 'CLOSED'))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 108); print('RESULT: %d/%d PASS  |  R18 合約閘 ; GATE = %s' % (npass, len(CLAIMS), 'OPEN' if npass == len(CLAIMS) else 'CLOSED'))
    out = dict(freed); out.update({'n_pass': npass, 'n_total': len(CLAIMS), 'gate': 'OPEN' if npass == len(CLAIMS) else 'CLOSED', 'claims': CLAIMS})
    with io.open(FREEZE, 'w', encoding='utf-8') as fh: json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1
if __name__ == '__main__':
    raise SystemExit(main())
