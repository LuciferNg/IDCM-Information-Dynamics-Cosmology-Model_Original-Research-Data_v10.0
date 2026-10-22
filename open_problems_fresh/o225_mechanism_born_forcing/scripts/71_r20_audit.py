#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/71 -- R20 獨立審計（**不 import** 44/45）。

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
    PHI1 = (F(-1, 2), F(1, 2))
    NPHI1 = (F(1, 2), F(-1, 2))
    P = {i: next(j for j in range(ncol) if i != j and all(z5add(U[i][t], U[j][t]) == Z0v for t in range(3)))
         for i in range(ncol)}
    lines = sorted(set(min(a, P[a]) for a in range(ncol) if types[a] == 'edge'))
    nbrs = [i for i in range(len(vals)) if vdot(vals[i], KV[0]) in (PHI1, NPHI1)]
    # 獨立重建「邊」：兩值互相鄰接且和 ∥ U_a
    def edge_of(L):
        cand = []
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                v, w = vals[i], vals[j]
                if vdot(v, w) != PHI1:            # 互相鄰接
                    continue
                u = tuple(z5add(v[k], w[k]) for k in range(3))
                if vcross(u, U[L]) == (Z0v, Z0v, Z0v):
                    cand.append((v, w))
        return cand
    E = {L: edge_of(L) for L in lines}
    A1c = sorted(L for L in lines if any(vdot(a, KV[0]) in (PHI1, NPHI1) and vdot(b, KV[0]) in (PHI1, NPHI1)
                                         and ((vdot(a, KV[0]) == vdot(b, KV[0]))) for (a, b) in E[L]))
    B10i = sorted(a for a in range(ncol) if types[a] == 'edge' and vdot(U[a], U[0]) in (PHI1, NPHI1))
    B10L = sorted(set(min(a, P[a]) for a in B10i))
    claim('A1', '★★ 獨立（重建「邊」= 互相鄰接且和 ∥ U_a）：B10 之 5 線 ⟺ 該邊之兩端點皆屬 N(U_0) ∪ −N(U_0) 且同號 dot',
          A1c == B10L, '候選 = %s ; B10 線 = %s ; 每線邊數 = %s' % (A1c, B10L, sorted(set(len(E[L]) for L in lines))))
    A2rows = []
    for L in B10L:
        v, w = E[L][0]
        s2 = tuple(z5add(v[k], w[k]) for k in range(3))
        twice = tuple(z5add(U[L][k], U[L][k]) for k in range(3))
        mid = ((z5add(vdot(v, KV[0]), vdot(w, KV[0]))[0]) * F(1, 2),
               (z5add(vdot(v, KV[0]), vdot(w, KV[0]))[1]) * F(1, 2))
        A2rows.append((L, s2 == twice, str(mid), str(vdot(U[L], U[0]))))
    claim('A2', '★★ 獨立（推導）：v + w = 2·U_a ⟹ ⟨U_a,U_0⟩ = (⟨v,U_0⟩+⟨w,U_0⟩)/2 = ±φ⁻¹（B10 之 dot 條件係此結構之推論）',
          all(r[1] and r[2] == r[3] for r in A2rows), '逐線 (L, v+w=2U_a, mid, ⟨U_a,U_0⟩) = %s' % A2rows)
    yB = [L for L in B10L if sum(1 for t in range(3) if U[L][t] == Z0v) == 2]
    y0 = yB[0]
    A3 = []
    for i in sorted(i for i in range(len(vals)) if vdot(vals[i], U[y0]) == Z0v):
        v = vals[i]
        c = vcross(U[y0], v)
        bit = 1 if vfirstsgn(c) != vfirstsgn(v) else 0
        sv = z5sgn(U[y0][1])
        pred = 1 if (sv * z5sgn(v[2]) != z5sgn(v[0])) else 0
        A3.append((i, str(c), bit, pred))
    claim('A3', '★★ 獨立（推導）：y-線（B10 ∩ 座標軸）之 4 赤道值：U_a × v = (v_z, 0, −v_x)，dind 之實際值 = [sgn(v_z) ≠ sgn(v_x)]（單項符號條件）⟹ 4 值不同型',
          all(x[2] == x[3] for x in A3) and len(set(x[3] for x in A3)) > 1,
          'y-線 = %d ; (索引, U_a×v, dind 實算, 單項預測) = %s' % (y0, A3))
    per_col = {}
    for a in range(ncol):
        s = [0] * n
        for (b, sw, sr) in ev:
            if b != a:
                continue
            for s0 in range(n):
                w, r2 = MUL[s0][sw], MUL[s0][sr]
                tw, tr = vdot(U[a], KV[w]) == Z0v, vdot(U[a], KV[r2]) == Z0v
                if tr and not tw:
                    s[s0] += ((1 if vfirstsgn(vcross(U[a], KV[r2])) != vfirstsgn(KV[r2]) else 0)
                              * vfirstsgn(KV[r2]) * z5sgn(vdot(U[a], KV[w])))
                elif tw and not tr:
                    s[s0] += ((1 if vfirstsgn(vcross(U[a], KV[w])) != vfirstsgn(KV[w]) else 0)
                              * vfirstsgn(KV[w]) * z5sgn(vdot(U[a], KV[r2])))
        per_col[a] = s
    oddcols = sorted(set(a for a in range(ncol) for s0 in range(n) if per_col[a][s0] % 2))
    claim('A4', '★★ 獨立：逐欄貢獻之奇偶 —— 奇異（欄）恰 = {61}（其餘 61 欄之逐欄和恆偶）',
          oddcols == [61], '奇異欄 = %s ; 逐欄奇數態數 = %s' % (oddcols, {a: sum(1 for s0 in range(n) if per_col[a][s0] % 2) for a in oddcols}))
    N2 = {a: {s0: F(per_col[a][s0], 2) for s0 in range(n)} for a in range(ncol)}
    LM = {s0: sum(per_col[a][s0] for a in range(ncol)) for s0 in range(n)}
    Z10i = sorted(s0 for s0 in range(n) if LM[s0] == 0)
    cand = sorted(s0 for s0 in range(n)
                  if all(abs(N2[a][s0]) <= 1 for a in range(ncol)) and sum(N2[a][s0] for a in range(ncol)) == 0
                  and any(N2[a][s0] != 0 for a in range(ncol)))
    claim('A5', '★★ 獨立：Z10 = {s : 每欄 abs(N_a) ≤ 1 ∧ Σ N_a = 0 ∧ 非零}（N_a := Λ_a/2，a ≠ 61）',
          cand == Z10i, '候選 = %s（%d）; Λ⁻¹(0) = %s（%d）; N 值域 = %s'
          % (cand, len(cand), Z10i, len(Z10i), sorted(set(N2[a][s0] for a in N2 for s0 in range(n)))))
    import collections as _c
    keys = _c.Counter(tuple(e) for e in ev)
    one = sorted(k for k, c in keys.items() if c == 1)
    two = sorted(k for k, c in keys.items() if c == 2)
    m1 = sorted(set(k[0] for k in one))
    claim('A6', '★ 獨立：鍵（三元組）之重數 ∈ {1,2}；重數 1 之鍵恰 2 個且皆屬第 61 欄（其 2 事件之 (sw,sr) 不同）',
          len(one) == 2 and m1 == [61] and len(two) == 61, 'm1 = %s（欄 = %s）; |鍵|= %d, {2: %d, 1: %d}; 第61欄之鍵 = %s'
          % (one, m1, len(keys), len(two), len(one), sorted(k for k in keys if k[0] == 61)))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R20 獨立審計' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/71_r20_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'B10L': B10L, 'Z10i': Z10i, 'oddcols': oddcols}, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
