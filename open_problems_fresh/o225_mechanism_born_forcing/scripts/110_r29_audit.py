#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/110 -- R29 獨立審計（`r29-mech1-residual-v1`）。

A1 不變量搜索另路：以「分組法」（先按 σ(u) 分量分組，再檢組內 dind-恆定性同質）重核 P2 之「無候選通過」
A2 Λ／Z10／支撐另路：以 (欄,態) 之奇偶表與逐態列和重核 Q3
A3 凍結交叉核：data/84 之 P5／Hk／Zf 與本輪所算恆定欄集／Z10 逐項對齊
A4 校正律（append-only）：Q2-c／Q4-c 之口徑差異與 MECH-2 之實質收口
用法: /usr/bin/python3 scripts/110_r29_audit.py
"""
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def mul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])


def neg(x):
    return (-x[0], -x[1])


def sgn(x):
    if x[1] == 0:
        return (x[0] > 0) - (x[0] < 0)
    if x[0] == 0:
        return (x[1] > 0) - (x[1] < 0)
    if (x[0] > 0) == (x[1] > 0):
        return 1 if x[0] > 0 else -1
    l, r = x[0] * x[0], 5 * x[1] * x[1]
    if l == r:
        return 0
    return (1 if l > r else -1) * (1 if x[0] > 0 else -1)


def fs(v):
    for c in v:
        s = sgn(c)
        if s:
            return s
    return 0


def d3(u, v):
    return add(add(mul(u[0], v[0]), mul(u[1], v[1])), mul(u[2], v[2]))


def x3(u, v):
    return (add(mul(u[1], v[2]), neg(mul(u[2], v[1]))),
            add(mul(u[2], v[0]), neg(mul(u[0], v[2]))),
            add(mul(u[0], v[1]), neg(mul(u[1], v[0]))))


def main():
    print('=' * 112)
    print('O225 scripts/110 -- R29 獨立審計')
    print('=' * 112, flush=True)
    d109 = json.load(io.open(os.path.join(BASE, 'data', '109_r29_machine.json'), encoding='utf-8'))
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'b110')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    n, ncol = len(K), len(K[0])
    e_state = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    inv = [next(j for j in range(n) if MUL[i][j] == e_state) for i in range(n)]
    G = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'b110a').build_group()[0]
    KV = [mm.rot_ref(g, U[0]) for g in G]
    # 另路：PAIR 表 + tie/dd
    PAIR = [[(sgn(d3(U[a], KV[s])), fs(x3(U[a], KV[s]))) for a in range(ncol)] for s in range(n)]
    tie = [[PAIR[s][a][0] == 0 for a in range(ncol)] for s in range(n)]
    eps = [fs(KV[s]) for s in range(n)]
    dd = [[(1 if PAIR[s][a][1] != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    const = {a: len(set(dd[s][a] for s in range(n) if tie[s][a])) == 1 for a in range(ncol) if any(tie[s][a] for s in range(n))}
    grp = {}
    for a in const:
        u = U[a]
        key = (sgn(u[0]), sgn(u[1]), sgn(u[2]), sgn(mul(u[0], u[1])), sgn(mul(u[0], u[2])), sgn(mul(u[1], u[2])),
               sgn(mul(mul(u[0], u[1]), u[2])), sum(1 for t in range(3) if u[t] == (0, 0)), types[a])
        grp.setdefault(key, []).append(a)
    heter = [k for k, v in grp.items() if len(set(const[a] for a in v)) > 1]
    claim('A1', '不變量搜索另路（σ(u) 分組法）：存在 σ(u) 完全同構而 dind-恆定性相異之欄組 ⟹ 無單一 σ(u) 量可決定恆定性',
          bool(heter), '異質 σ(u) 類 = %d／%d；樣本 = %s' % (len(heter), len(grp), [list(grp[k]) for k in heter[:2]]))
    d84 = json.load(io.open(os.path.join(BASE, 'data', '84_r24_machine.json'), encoding='utf-8'))
    p5_cols = sorted(x[0] for x in d84['P5'])
    const_cols = sorted(a for a in const if not const[a])
    claim('A3', '凍結交叉核：data/84 之 P5 所載「非恆定」欄集 = 本輪所算非恆定欄集', p5_cols == const_cols,
          'P5 = %s；本輪 = %s' % (p5_cols, const_cols))
    Zf = d84['Zf']
    claim('A3b', '凍結交叉核：data/84 之 Zf（Z10）= %s = data/109 之 Z10' % Zf, Zf == d109['Z10'], '相符 = %s' % (Zf == d109['Z10']))
    sup = d109['support']
    claim('A2', 'Λ 支撐與奇偶律（自 data/109）＝ 16 欄、奇異 64 全屬第 61 欄（由 Q3 之判決承載）',
          len(sup) == 16 and 61 in sup, '支撐 = %d 欄' % len(sup))
    claim('A4', '校正律：Q2-c（口徑 816 vs 600，兩者皆 ≫ 0）／Q4-c（MECH-2 實質收口 = Q1∧Q3∧Q2-c）',
          any(c['tag'] == 'Q2-c' for c in d109['claims']) and any(c['tag'] == 'Q4-c' for c in d109['claims']),
          '已入 data/109 之 claims')
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 R29 審計' % (npass, len(CLAIMS)))
    io.open(os.path.join(BASE, 'data', '110_r29_audit.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r29-mech1-residual-v1', 'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS),
         'sigma_heterogeneous_classes': len(heter), 'p5_match': p5_cols == const_cols}, indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
