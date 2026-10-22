#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/41 -- R11 合約閘：凍結合約 sha256、預註冊 tag 完整性、陽／陰對照、GATE。用法: /usr/bin/python3 scripts/41_r11_contract.py"""
import hashlib, io, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
CONTRACT = os.path.join(BASE, 'docs/22_r11_contract.md'); FREEZE = os.path.join(BASE, 'data/41_r11_freeze.json')
SHA = 'f17d35f3ae3bba28316df54a214a791f95230af5878d341a1f3813bf8202004b'
CLAIMS = []
def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)
def sha256(p): return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()
def main():
    print('=' * 108); print('O225 scripts/41 -- R11 CONTRACT GATE'); print('=' * 108, flush=True)
    first = not os.path.exists(FREEZE)
    freed = json.load(io.open(FREEZE, encoding='utf-8')) if not first else {}
    cur = sha256(CONTRACT)
    if first:
        freed = {'rules': 'r11-mechanism-proof-and-laws-v1', 'contract': 'docs/22_r11_contract.md',
                 'contract_sha256': cur, 'frozen_at': 'first run of scripts/41'}
    claim('C1', '凍結合約 sha256 與記錄一致', cur == freed['contract_sha256'], 'sha = %s…' % cur[:16])
    txt = io.open(CONTRACT, encoding='utf-8').read()
    need = ['T1', 'T2', 'T3', 'U0', 'U1', 'U2', 'U3', 'U4', 'V1', 'V2', 'V3', 'V4', 'V5', 'W1', 'W2', 'W3', 'W4', 'W5']
    miss = [t for t in need if not re.search(r'\*\*' + t + r'(?:\s|\*|（)', txt)]
    claim('C2', '預註冊 tag 完整（18 個：T1–T3／U0–U4／V1–V5／W1–W5）', not miss, '缺 = %s' % miss)
    pos = 'R(s) ≡ 0 ∀s ⟺ ∀s∀軸對 {a,ā}: K(s,ā) = −K(s,a)'
    claim('C3', '陽性對照：合約載明 T1 之完整雙向判準（不可只寫方向）', pos in txt, '命中 = %s' % (pos in txt))
    tampered = txt.replace('R(s) ≡ 0 ∀s ⟺ ∀s∀軸對 {a,ā}: K(s,ā) = −K(s,a)', 'R(s) ≡ 0 ⟺ tie 層奇')
    claim('C4', '陰性對照：篡改後之合約（弱化為單層判準）必須被 C3 判據拒絕',
          tampered != txt and pos not in tampered, '篡改版仍含完整判準 = %s' % (pos in tampered))
    pre = True
    if not first:
        pre = all(freed.get(k) == v for k, v in [('contract_sha256', cur)])
    claim('C5', 'GATE 條件：合約未被改動、tag 完整、陰陽對照成立',
          cur == freed['contract_sha256'] and not miss and pos in txt, 'GATE = %s' % ('OPEN' if (cur == freed['contract_sha256'] and not miss and pos in txt) else 'CLOSED'))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 108); print('RESULT: %d/%d PASS  |  R11 合約閘 ; GATE = %s' % (npass, len(CLAIMS), 'OPEN' if npass == len(CLAIMS) else 'CLOSED'))
    out = dict(freed); out.update({'n_pass': npass, 'n_total': len(CLAIMS), 'gate': 'OPEN' if npass == len(CLAIMS) else 'CLOSED', 'claims': CLAIMS})
    with io.open(FREEZE, 'w', encoding='utf-8') as fh: json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1
if __name__ == '__main__':
    raise SystemExit(main())
