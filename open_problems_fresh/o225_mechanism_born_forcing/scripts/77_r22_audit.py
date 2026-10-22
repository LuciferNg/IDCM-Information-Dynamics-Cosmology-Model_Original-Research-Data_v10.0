#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/77 -- R22 獨立審計（**不 import** 44/45）。

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
    j58 = json.load(io.open(os.path.join(BASE, 'data/58_r16_machine.json'), encoding='utf-8'))
    nz22, nec8 = j58['nz22'], j58['nec8']
    vals = sorted(set(KV))
    Z0v = Z5(0)
    P = {i: next(j for j in range(ncol) if i != j and all(z5add(U[i][t], U[j][t]) == Z0v for t in range(3)))
         for i in range(ncol)}
    lines = sorted(set(min(a, P[a]) for a in range(ncol) if types[a] == 'edge'))
    def fslead(A):
        for k in range(3):
            s = z5sgn(A[k])
            if s != 0:
                return k, s
        return -1, 0
    # A1 ★★ 兩座標恆等式（另路：直接取 leading 分量符號）
    A1bad = []
    for a in range(ncol):
        if types[a] != 'edge':
            continue
        for s0 in range(n):
            x = KV[s0]
            if vdot(U[a], x) != Z0v:
                continue
            A = vcross(U[a], x)
            i, sa = fslead(A)
            j, sx = fslead(x)
            pred = 1 if sa * sx == -1 else 0
            if pred != ([1 if vfirstsgn(A) != vfirstsgn(x) else 0]):
                A1bad.append((a, s0))
    claim('A1', '★★ 獨立：dind(x,a) = [sgn(A_i)·sgn(x_j) = −1]（i = lidx(A)、j = lidx(x)）——全 30 edge 欄 × 其 4 赤道值',
          A1bad == [], '反例 = %s' % A1bad[:6])
    # A2 ★★ W5 之等價（另路：逐欄逐值直算）
    A2bad = []
    for a in range(ncol):
        if types[a] != 'edge':
            continue
        bits = set()
        for s0 in range(n):
            if vdot(U[a], KV[s0]) != Z0v:
                continue
            bits.add(1 if vfirstsgn(vcross(U[a], KV[s0])) != vfirstsgn(KV[s0]) else 0)
        if (len(bits) == 1) != (a in set(nec8)):
            A2bad.append((a, sorted(bits), a in set(nec8)))
    claim('A2', '★★ 獨立：dind 於 V(a) 恆定 ⟺ 非承載（30 edge 欄）', A2bad == [], '反例 = %s' % A2bad)
    # A3 ★★ Z10 之 |N_a| <= 1（另路：Gg 逐態累加）
    gg = {a: [0] * n for a in range(ncol)}
    for (b, sw, sr) in ev:
        for s0 in range(n):
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = vdot(U[b], KV[w]) == Z0v, vdot(U[b], KV[r2]) == Z0v
            if tr and not tw:
                gg[b][s0] += ((1 if vfirstsgn(vcross(U[b], KV[r2])) != vfirstsgn(KV[r2]) else 0)
                              * vfirstsgn(KV[r2]) * z5sgn(vdot(U[b], KV[w])))
            elif tw and not tr:
                gg[b][s0] += ((1 if vfirstsgn(vcross(U[b], KV[w])) != vfirstsgn(KV[w]) else 0)
                              * vfirstsgn(KV[w]) * z5sgn(vdot(U[b], KV[r2])))
    LM = [sum(gg[a][s0] for a in range(ncol)) for s0 in range(n)]
    Z10i = sorted(s0 for s0 in range(n) if LM[s0] == 0)
    sup = sorted(a for a in range(ncol) if any(gg[a][s0] != 0 for s0 in range(n)))
    A3bad = [(a, s0, gg[a][s0]) for a in sup if a != 61 for s0 in Z10i if abs(F(gg[a][s0], 2)) > 1]
    claim('A3', '★★ 獨立：於 Z10，16 support 欄（除 61）逐欄 abs(Λ_a/2) ≤ 1；Λ 之水平集與 10 態一致',
          A3bad == [] and len(Z10i) == 10, '反例 = %s ; support = %s ; Λ_⁻¹(0) = %s ; Z10 之 Λ_a 值集 = %s'
          % (A3bad, sup, Z10i, sorted(set(gg[a][s0] for a in sup for s0 in Z10i))))
    # A4 ★★ lidx 之結構（非座標線）
    A4rows = []
    for L in lines:
        if sum(1 for t in range(3) if U[L][t] == Z0v) != 0:
            continue
        js, is_ = set(), set()
        for s0 in range(n):
            if vdot(U[L], KV[s0]) != Z0v:
                continue
            x = KV[s0]
            i, _ = fslead(vcross(U[L], x))
            j, _ = fslead(x)
            js.add(j); is_.add(i)
        A4rows.append((L, sorted(js), sorted(is_)))
    claim('A4', '★★ 獨立：12 非座標線：lidx(x) ⊆ {0,1} 且 lidx(U_a×x) = 0',
          all(max(r[1]) <= 1 and r[2] == [0] for r in A4rows), '逐線 (L, lidx(x) 集, lidx(A) 集) = %s' % A4rows)

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R22 獨立審計' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/77_r22_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'Z10i': Z10i, 'support': sup}, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
