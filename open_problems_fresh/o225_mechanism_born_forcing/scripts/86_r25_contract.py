#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/83 -- R25 合約閘：凍結合約 sha256、預註冊 tag 完整性、陽／陰對照、GATE。用法: /usr/bin/python3 scripts/83_r24_contract.py"""
import hashlib, io, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
CONTRACT = os.path.join(BASE, 'docs/52_r25_contract.md'); FREEZE = os.path.join(BASE, 'data/86_r25_freeze.json')
CLAIMS = []
def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)
def sha256(p): return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()
def main():
    print('=' * 108); print('O225 scripts/86 -- R25 CONTRACT GATE'); print('=' * 108, flush=True)
    first = not os.path.exists(FREEZE)
    freed = json.load(io.open(FREEZE, encoding='utf-8')) if not first else {}
    cur = sha256(CONTRACT)
    if first:
        freed = {'rules': 'r25-z10-selection-v1', 'contract': 'docs/52_r25_contract.md',
                 'contract_sha256': cur, 'frozen_at': 'first run of scripts/86'}
    claim('C1', '凍結合約 sha256 與記錄一致', cur == freed['contract_sha256'], 'sha = %s…' % cur[:16])
    txt = io.open(CONTRACT, encoding='utf-8').read()
    need = ['R1', 'R2', 'R3', 'R4', 'R5', 'S1', 'S2', 'S3', 'S4']
    miss = [t for t in need if not re.search(r'\*\*' + t + r'\*\*', txt)]
    claim('C2', '預註冊 tag 完整（9 個：R1–R5／S1–S4）', not miss, '缺 = %s' % miss)
    pos = 's ∈ Z10` ⟺ **該態 16 support 欄之 `N_a` 中正項數 = 負項數'
    pos2 = '`sgn(u_2) = −1`'
    claim('C3', '陽性對照：合約載明 Part R 之 R4 算子判據與 Part S 之 S4 新律（含極性）',
          pos in txt and pos2 in txt and '極性：**正向**' in txt, '命中 = %s／%s' % (pos in txt, pos2 in txt))
    tampered = txt.replace('正項數 = 負項數', '大致平衡')
    claim('C4', '陰性對照：篡改後之合約（弱化為「大致平衡」）必須被 C3 判據拒絕',
          tampered != txt and pos not in tampered, '篡改版仍含完整判準 = %s' % (pos in tampered))
    ok = (cur == freed['contract_sha256'] and not miss and pos in txt and pos2 in txt)
    claim('C5', 'GATE 條件：合約未被改動、tag 完整、陰陽對照成立', ok, 'GATE = %s' % ('OPEN' if ok else 'CLOSED'))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 108); print('RESULT: %d/%d PASS  |  R25 合約閘 ; GATE = %s' % (npass, len(CLAIMS), 'OPEN' if npass == len(CLAIMS) else 'CLOSED'))
    out = dict(freed); out.update({'n_pass': npass, 'n_total': len(CLAIMS), 'gate': 'OPEN' if npass == len(CLAIMS) else 'CLOSED', 'claims': CLAIMS})
    with io.open(FREEZE, 'w', encoding='utf-8') as fh: json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1
if __name__ == '__main__':
    raise SystemExit(main())
