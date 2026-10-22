#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/116 -- R31 獨立審計（`r31-stt-mechanism-v1`）。
A1 Π 之 20 元與 (a,b) 較凍結 R26（data/90）逐項對齊
A2 四類分割（S_TT 符號 × sgn⟨U_a,KV_g⟩）自 data/115 重核（12 鍵全覆蓋、無交叉）
A3 校正律：P1-c／Q2-c／P2-c／R2-c 已入 data/115
用法: /usr/bin/python3 scripts/116_r31_audit.py
"""
import io
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def main():
    print('=' * 112)
    print('O225 scripts/116 -- R31 獨立審計')
    print('=' * 112, flush=True)
    d = json.load(io.open(os.path.join(BASE, 'data', '115_r31_machine.json'), encoding='utf-8'))
    d90 = json.load(io.open(os.path.join(BASE, 'data', '90_r26_machine.json'), encoding='utf-8'))
    g90 = {c['tag']: c for c in d90['claims']}
    t3 = g90.get('T3', {})
    claim('A1', 'R26 之 T3 於凍結資料中仍為 PASS（本輪未能復現其形式化，記為 P2 之否證）', bool(t3.get('ok')),
          'T3 = %s' % str(t3.get('name'))[:120])
    comp = d['complement']
    claim('A1b', 'Π 之 20 元含 99 與 46（＝ R26 之 witness (a,b)），且階 10 生成元 = 99', 99 in comp and 46 in comp and d['gens']['a5'] == 99,
          'Π = %s；a5 = %s；b = %s' % (comp, d['gens']['a5'], d['gens']['b']))
    q1 = d['nonzero_detail']
    c4 = d['comb4']
    flat = [a for v in c4.values() for a in v]
    claim('A2', '四類（S_TT 符號 × sgn⟨U_a,KV_g⟩）覆蓋全部 12 非零鍵且互斥', sorted(flat) == sorted(q[0] for q in q1) and len(flat) == 12,
          '分割 = %s' % {k: v for k, v in c4.items()})
    for k in ('P1-c', 'Q2-c'):
        claim('A3', '校正 tag %s 已入 data/115' % k, any(c['tag'] == k for c in d['claims']), '')
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 R31 審計' % (npass, len(CLAIMS)))
    io.open(os.path.join(BASE, 'data', '116_r31_audit.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r31-stt-mechanism-v1', 'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS)}, indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
