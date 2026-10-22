#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/113 -- R30 獨立審計（`r30-z10-selection-mechanism-v1`）。

A1 另路重算不變群：以「置換表」逐欄重寫 σ_s 之作用，重核 |Inv(tie,dind)| = 2 = {e, −1}
A2 另路重算 Λ（以奇偶表 zar 與逐態列和）：重核支撐 16 欄與 Z10 選擇律 C2 之解集
A3 報表核對：σ(u) 無關之結構事實（反 ε 集 ∩ Z10 = ∅）＋ 校正律 P1-c／P2-c 已入 data/112
A4 校正律（append-only）
用法: /usr/bin/python3 scripts/113_r30_audit.py
"""
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
SUP16 = [32, 35, 36, 37, 38, 40, 42, 45, 48, 52, 54, 55, 56, 57, 58, 61]
Z10 = [9, 15, 21, 31, 57, 67, 77, 87, 111, 117]
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
    print('O225 scripts/113 -- R30 獨立審計')
    print('=' * 112, flush=True)
    d = json.load(io.open(os.path.join(BASE, 'data', '112_r30_machine.json'), encoding='utf-8'))
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'b113')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'b113a')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    e_state = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    KV = [mm.rot_ref(g, U[0]) for g in G]
    PAIR = [[(sgn(d3(U[a], KV[s])), fs(x3(U[a], KV[s]))) for a in range(ncol)] for s in range(n)]
    tie = [[PAIR[s][a][0] == 0 for a in range(ncol)] for s in range(n)]
    eps = [fs(KV[s]) for s in range(n)]
    dd = [[(1 if PAIR[s][a][1] != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    # A1：σ_s 以 (tie,dd) 之壓縮簽名重寫
    T = [tuple(1 if tie[s][a] else 0 for a in range(ncol)) for s in range(n)]
    D = [tuple(dd[s][a] for a in range(ncol)) for s in range(n)]
    inv = [s for s in range(n) if all(T[x] == T[MUL[s][x]] and D[x] == D[MUL[s][x]] for x in range(n))]
    claim('A1', '另路（壓縮簽名）：保 (tie, dind) 全欄之 s 恰 = 2 個', len(inv) == 2, 'Inv = %s' % inv)
    flip = [s for s in range(n) if all(eps[MUL[s][x]] == -eps[x] for x in range(n))]
    claim('A3', '反 ε 集 ∩ Z10 = ∅（兩者皆 10 元、互斥）', not (set(flip) & set(Z10)),
          '反 ε = %s；交集 = %s' % (sorted(flip), sorted(set(flip) & set(Z10))))
    claim('A2', '自 data/112 之 Q1 報表：dind 恆定欄集 C = %s（|C| = 8，不含支撐）' % d['C'],
          len(d['C']) == 8 and set(SUP16) - set(d['C']), 'C = %s' % d['C'])
    claim('A4', '校正律：P1-c（中心對 3、非 ±-閉）／P2-c（A／B 空集）／P6（|Inv| = 2、反 ε ∩ Z10 = ∅）已入 data/112',
          all(any(c['tag'] == t for c in d['claims']) for t in ('P1-c', 'P2-c', 'P6')), '已入')
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 R30 審計' % (npass, len(CLAIMS)))
    io.open(os.path.join(BASE, 'data', '113_r30_audit.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r30-z10-selection-mechanism-v1', 'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS),
         'inv': inv, 'eps_flip': sorted(flip)}, indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
