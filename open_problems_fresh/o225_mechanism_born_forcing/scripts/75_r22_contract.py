#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/41 -- R22 合約閘：凍結合約 sha256、預註冊 tag 完整性、陽／陰對照、GATE。用法: /usr/bin/python3 scripts/75_r22_contract.py"""
import hashlib, io, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
CONTRACT = os.path.join(BASE, 'docs/45_r22_contract.md'); FREEZE = os.path.join(BASE, 'data/75_r22_freeze.json')
SHA = 'a3ab551d5783ed70f6e439c86512deff2b4a96c38f994f8a9db8161cccb87528eb971efe0982282d6fa5f73d301665512b92c2222e105067403d8d5020179ac7f3af1409ab65f9ec92f311509a347ebe035ea809dfc68fe92728646475fdb93a481bb3793bd848d7c27fff50dda7db72bd4c8a02d6aaf268c4c176354544176924656ade063067cd0eadddf04071d7a761df8ca211e51936440cd417d37682447e8189d077cdf2a293eb1e75ed8e40f2a71282146cc2ed35ac0281236beb1a4676aaa67c27d03310'
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
        freed = {'rules': 'r22-two-coordinate-v1', 'contract': 'docs/45_r22_contract.md',
                 'contract_sha256': cur, 'frozen_at': 'first run of scripts/41'}
    claim('C1', '凍結合約 sha256 與記錄一致', cur == freed['contract_sha256'], 'sha = %s…' % cur[:16])
    txt = io.open(CONTRACT, encoding='utf-8').read()
    need = ['W1', 'W2', 'W3', 'W4', 'W5', 'X1', 'X2', 'X3']
    miss = [t for t in need if not re.search(r'\*\*' + t + r'(?:\s|\*|（)', txt)]
    claim('C2', '預註冊 tag 完整（8 個：W1–W5／X1–X3）', not miss, '缺 = %s' % miss)
    pos = 'dind(x,a) = [sgn((A_x)_{lidx(A_x)})·sgn(x_{lidx(x)}) = −1]'
    claim('C3', '陽性對照：合約載明 Part W 之兩座標分解與 Part X 之異號相消', pos in txt and '異號' in txt, '命中 = %s' % (pos in txt))
    tampered = txt.replace('= [sgn((A_x)_{lidx(A_x)})·sgn(x_{lidx(x)}) = −1]', '某條件')
    claim('C4', '陰性對照：篡改後之合約（弱化為「可能成群」）必須被 C3 判據拒絕',
          tampered != txt and pos not in tampered, '篡改版仍含完整判準 = %s' % (pos in tampered))
    pre = True
    if not first:
        pre = all(freed.get(k) == v for k, v in [('contract_sha256', cur)])
    claim('C5', 'GATE 條件：合約未被改動、tag 完整、陰陽對照成立',
          cur == freed['contract_sha256'] and not miss and pos in txt, 'GATE = %s' % ('OPEN' if (cur == freed['contract_sha256'] and not miss and pos in txt) else 'CLOSED'))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 108); print('RESULT: %d/%d PASS  |  R22 合約閘 ; GATE = %s' % (npass, len(CLAIMS), 'OPEN' if npass == len(CLAIMS) else 'CLOSED'))
    out = dict(freed); out.update({'n_pass': npass, 'n_total': len(CLAIMS), 'gate': 'OPEN' if npass == len(CLAIMS) else 'CLOSED', 'claims': CLAIMS})
    with io.open(FREEZE, 'w', encoding='utf-8') as fh: json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1
if __name__ == '__main__':
    raise SystemExit(main())
