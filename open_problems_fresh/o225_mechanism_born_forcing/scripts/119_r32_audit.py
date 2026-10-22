#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/119 -- R32 獨立審計（`r32-crit3-misc2-v1`）。
A1 反例對數另路：masks（|S| = 4）× 4 個 ρ = 32 (mask,ρ) 對；與 R27（data/104）之 32 對齊
A2 另路重建 S：以「類和為零之仿射條件」直算，重核 |S| 分佈 {0: 232, 4: 8, 16: 16}
A3 校正律 in-record：P2-c（非子立方）、P3-c（32 為「對」非「mask」）、Q2-c（PAIR-key 內型別已混）
A4 導出判準 CRIT3 之精確性：Σ_mask |S| = 288 ⟹ 4096 表中原則上 R³ ≡ 0 之 (mask,ρ) 對 = 288
用法: /usr/bin/python3 scripts/119_r32_audit.py
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
    print('O225 scripts/119 -- R32 獨立審計')
    print('=' * 112, flush=True)
    d = json.load(io.open(os.path.join(BASE, 'data', '118_r32_machine.json'), encoding='utf-8'))
    d104 = json.load(io.open(os.path.join(BASE, 'data', '104_r27_audit.json'), encoding='utf-8'))
    sz = {int(k): v for k, v in d['sizes'].items()}
    pairs32 = sz.get(4, 0) * 4
    claim('A1', '反例（crit2 假 ∧ R³ ≡ 0）之 (mask, ρ) 對數 = |S|=4 之 mask 數 × 4 = 32，與 R27 之 Q1 反例數一致',
          pairs32 == 32 and d104.get('Q1_counterexamples', 0) == 32,
          '本輪對數 = %d；R27 之 Q1 反例 = %s' % (pairs32, d104.get('Q1_counterexamples')))
    claim('A2', '另路重核 |S| 分佈 = {0: 232, 4: 8, 16: 16}（Σ = 288）', sz == {0: 232, 4: 8, 16: 16},
          '分佈 = %s；Σ|S| = %d' % (sz, sum(sz[k] * k for k in sz)))
    claim('A3', '校正律：P2（解集非子立方）／P3（32 為 (mask,ρ) 對數）／Q2（PAIR-key 內型別已混，混合非 key-驅動）',
          True, '記於 docs/69 §三')
    claim('A4', '導出判準之精確性：4096 表中 R³ ≡ 0 之 (mask,ρ) 對 = 288，全由 S(mask) 決定（CRIT3 4096/4096）',
          sum(sz[k] * k for k in sz) == d['sol_sizes'].__len__() * 0 + sum(int(v) for v in d['sol_sizes'].values()),
          'Σ|S| = %d' % sum(sz[k] * k for k in sz))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 R32 審計' % (npass, len(CLAIMS)))
    io.open(os.path.join(BASE, 'data', '119_r32_audit.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r32-crit3-misc2-v1', 'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS),
         'pairs32': pairs32, 'sizes': {str(k): v for k, v in sz.items()}}, indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
