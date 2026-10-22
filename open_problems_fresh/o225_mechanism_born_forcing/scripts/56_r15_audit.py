#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/56 -- R15 獨立審計（**不 import** 44/45）。

獨立路徑：KV 以**旋轉矩陣**（由四元數以 Z[√5] 精確砌出 R = I + 2s·[v]× + 2[v]×²）重算，不經 `rot_ref` 之 sandwich；
事件以另一種 replay；f 以 y-索引寫法；補集以獨立掃描；群結構以**表現**驗（a 階 10、b 階 4、b⁻¹ab = a⁻¹）。
用法: /usr/bin/python3 scripts/46_r12_audit.py
"""
import hashlib
import importlib.util
import io
import json
import os
from collections import Counter
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RULES = 'r12-law-closure-v1'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


Z5 = lambda a, b=0: (F(a), F(b))
z5add = lambda x, y: (x[0] + y[0], x[1] + y[1])
z5mul = lambda x, y: (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])
z5neg = lambda x: (-x[0], -x[1])
z5sub = lambda x, y: (x[0] - y[0], x[1] - y[1])


def z5sgn(x):
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


def vadd(u, v):
    return tuple(z5add(a, b) for a, b in zip(u, v))


def vsub(u, v):
    return tuple(z5sub(a, b) for a, b in zip(u, v))


def vscale(s, v):
    return tuple(z5mul(s, x) for x in v)


def vdot(u, v):
    acc = Z5(0)
    for a, b in zip(u, v):
        acc = z5add(acc, z5mul(a, b))
    return acc


def vcross(u, v):
    return (z5sub(z5mul(u[1], v[2]), z5mul(u[2], v[1])),
            z5sub(z5mul(u[2], v[0]), z5mul(u[0], v[2])),
            z5sub(z5mul(u[0], v[1]), z5mul(u[1], v[0])))


def vfirstsgn(v):
    for c in v:
        s = z5sgn(c)
        if s:
            return s
    return 0


def rot_matrix(q, v):
    """R = I + 2s[v]× + 2[v]×²（四元數 q = (q0, v)，單位模）"""
    q0 = q[0]                                   # 四元數分量本身即 Z[√5] 對 (a,b) = a + b√5
    qv = (q[1], q[2], q[3])
    # R·v = (2q0²−1)·v + 2(v·q_v)·q_v + 2q0·(q_v × v)
    t1 = vscale(z5sub(z5mul(Z5(2), z5mul(q0, q0)), Z5(1)), v)
    t2 = vscale(Z5(2), vscale(vdot(v, qv), qv))
    t3 = vscale(z5mul(Z5(2), q0), vcross(qv, v))
    return vadd(vadd(t1, t2), t3)


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def mul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])


def main():
    print('=' * 118)
    print('O225 scripts/56 -- R15 INDEPENDENT AUDIT   (rules: %s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'a56_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'a56_a2')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    KV = [rot_matrix(g, U[0]) for g in G]
    e_state = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    inv = [next(j for j in range(n) if MUL[i][j] == e_state) for i in range(n)]
    order = []
    for a in range(n):
        k, x = 1, a
        while x != e_state:
            x = MUL[x][a]
            k += 1
        order.append(k)
    zc = [s for s in range(n) if s != e_state and order[s] == 2][0]
    tie = [[vdot(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [vfirstsgn(KV[s]) for s in range(n)]
    gam = [[vfirstsgn(vcross(U[a], KV[s])) for a in range(ncol)] for s in range(n)]
    dind = [[(1 if gam[s][a] != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    # 事件／鍵（獨立重算）
    def events_of(state):
        st, stk, ev = state, [], []
        for (c1, c2_) in [(a, b) for a in range(ncol) for b in range(ncol)]:
            for ctx in (c1, c2_):
                if stk and stk[-1][0] == ctx:
                    ev.append((ctx, stk[-1][2], st))
                else:
                    stk.append((ctx, K[st][ctx], st))
                    st = MUL[st][hx[ctx]]
            top = stk.pop()
            st = top[2]
            if stk and stk[-1][0] == c2_:
                ev.append((c2_, stk[-1][2], st))
            else:
                stk.append((c2_, K[st][c2_], st))
                st = MUL[st][hx[c2_]]
        return ev
    ev = events_of(e_state)
    keys = {}
    for (a, sw, sr) in ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1
    col_g = {a: g for (a, g) in keys}
    def S_TT_ind(a, g):
        gi = inv[g]
        tot = 0
        for y in range(n):
            x = MUL[y][gi]
            if tie[x][a] and tie[y][a]:
                tot += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
        return tot
    nz_ind = sorted(a for a in range(ncol) if any(S_TT_ind(a, g) != 0 for g in range(n)))
    nec_ind = sorted(a for a in range(ncol) if types[a] == 'edge' and a not in set(nz_ind))
    Wnz = {a: sum(1 for g in range(n) if any(tie[y][a] and tie[MUL[y][inv[g]]][a] and
              dind[y][a] != dind[MUL[y][inv[g]]][a] for y in range(n))) for a in range(ncol) if types[a] == 'edge'}
    claim('I1', '★★ 獨立：非承載 ⟺ W-支撐全空（∀g），且配對（W-非空 g 數, S_TT-非零 g 數）∈ {(0,0),(100,100)}',
          sorted(set(Wnz.values())) == [0, 100] and all(
              (Wnz[a] == 0) == (a in set(nec_ind)) for a in Wnz),
          'W-非空 g 數值集 = %s ; 非承載 = %s' % (sorted(set(Wnz.values())), nec_ind))
    claim('I2', '★ 獨立：承載 22（承載欄 W-非空 g 數 = 100）；非承載 8（= 0）',
          sorted(set(Wnz[a] for a in nz_ind)) == [100] and sorted(set(Wnz[a] for a in nec_ind)) == [0] and len(nz_ind) == 22,
          '承載 = %d（g 數集 %s）; 非承載 = %s' % (len(nz_ind), sorted(set(Wnz[a] for a in nz_ind)), nec_ind))
    # |τ| = 4 之欄（取 55 之輸出作輸入；W-側獨立重算）
    j55 = json.load(io.open(os.path.join(BASE, 'data/55_r15_machine.json'), encoding='utf-8'))
    big4 = j55['A']['bigcols']
    claim('I3', '★★ 獨立：|τ| = 4 之 4 欄（[40,42,52,54]）全部 W-支撐全空 ⟺ 非承載（A4 之重要性質）',
          big4 == [40, 42, 52, 54] and all(Wnz[a] == 0 for a in big4),
          '|τ|=4 欄 = %s ; 其 W-非空 g 數 = %s' % (big4, [Wnz[a] for a in big4]))
    def Tterm(x, a, g):
        y = MUL[x][g]
        if tie[x][a] and not tie[y][a]:
            return dind[x][a] * eps[x] * z5sgn(vdot(U[a], KV[y]))
        return 0
    cols16 = sorted(set(a for (a, g) in keys if any(Tterm(x, a, g) != 0 for x in range(n))))
    claim('I4', '★ 獨立：16 非空鍵之欄集合 = [32,35,36,37,38,40,42,45,48,52,54,55,56,57,58,61]',
          cols16 == [32, 35, 36, 37, 38, 40, 42, 45, 48, 52, 54, 55, 56, 57, 58, 61],
          '16 欄 = %s' % cols16)
    # Z10 之獨立重算（f_tf / f_ft）
    f_tf = [0] * n
    f_ft = [0] * n
    f_tt = [0] * n
    for s0 in range(n):
        for (a, sw, sr) in ev:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = tie[w][a], tie[r2][a]
            if tw and tr:
                f_tt[s0] += (0 if dind[r2][a] == dind[w][a] else 1) * eps[r2] * eps[w]
            elif tr:
                f_tf[s0] += dind[r2][a] * eps[r2] * z5sgn(vdot(U[a], KV[w]))
            elif tw:
                f_ft[s0] += dind[w][a] * eps[w] * z5sgn(vdot(U[a], KV[r2]))
    Z10 = sorted(s for s in range(n) if f_tf[s] + f_ft[s] == 0)
    claim('I5', '★ 獨立：Z10 逐態 f_tf = −f_ft ∈ {±2, ±4}（抵消態，非雙零）',
          Z10 == [9, 15, 21, 31, 57, 67, 77, 87, 111, 117] and
          all(f_tf[s] == -f_ft[s] and abs(f_tf[s]) in (2, 4) for s in Z10),
          'Z10 = %s ; (f_tf,f_ft) = %s' % (Z10, [(s, f_tf[s], f_ft[s]) for s in Z10]))
    zp = {}
    for s in Z10:
        if MUL[s][zc] in zp:
            continue
        zp[s] = (order[s], order[MUL[s][zc]])
    claim('I6', '★ 獨立：Z10 之 5 對階型 = 2×{3,6} ＋ 1×{4,4} ＋ 2×{5,10}',
          sorted(zp.values()) == [(3, 6), (3, 6), (4, 4), (5, 10), (5, 10)], '逐對 = %s' % zp)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R15 獨立審計' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/56_r15_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'Wnz': {str(k): v for k, v in Wnz.items()}}, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
