#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/84 -- R24 機器：雙項族分群導出（MECH-1）＋ head 定向溯源（MECH-2）（`r24-two-term-family-v1`）。

Part P  MECH-1：非單項族（41/42）雙項式 T_0 + T_1 = −u_2·A_0 與分群律（同號 ⟺ sgn(u_0u_1) = sgn(x_0x_1)）
Part Q  MECH-2：head 之 Tterm/keys（(x,g) 定向）與凍結 f_tf/f_ft 之逐字溯源（零集 44 vs 10 之不等價登錄）
（沿用凍結 R23 機器之前置：keys／τ／Z10／S_TT／非空鍵；唯讀 O222）

精確算術（Z[√5]：(a,b) 表 a+b√5，p² vs 5q²）；唯讀凍結機器（O222）。用法: /usr/bin/python3 scripts/45_r12_machine.py
"""
import hashlib
import importlib.util
import io
import json
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RULES = 'r24-two-term-family-v1'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-7s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def info(s):
    print('[INFO] ' + s, flush=True)


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


def dot3(u, v):
    return add(add(mul(u[0], v[0]), mul(u[1], v[1])), mul(u[2], v[2]))


def cross3(u, v):
    return (add(mul(u[1], v[2]), neg(mul(u[2], v[1]))),
            add(mul(u[2], v[0]), neg(mul(u[0], v[2]))),
            add(mul(u[0], v[1]), neg(mul(u[1], v[0]))))


def firstsgn(v):
    for c in v:
        s = sgn(c)
        if s:
            return s
    return 0


def main():
    print('=' * 118)
    print('O225 scripts/84 -- R24 MACHINE   (rules: %s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r12_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r12_a2')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
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
    tie = [[dot3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    gam = [[firstsgn(cross3(U[a], KV[s])) for a in range(ncol)] for s in range(n)]
    dind = [[(1 if gam[s][a] != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    PAIR = [[(sgn(dot3(U[a], KV[s])), firstsgn(cross3(U[a], KV[s]))) for a in range(ncol)] for s in range(n)]
    c2 = [[sgn(cross3(U[a], KV[s])[1]) for a in range(ncol)] for s in range(n)]
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(add(U[i][t], U[j][t]) == (0, 0) for t in range(3)):
                partner[i] = j
    pairs = sorted(i for i in range(ncol) if i < partner[i])

    # 事件 + 62 鍵（同式；回歸核）
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

    my_ev = events_of(e_state)
    d34 = json.load(io.open(os.path.join(BASE, 'data/34_r9_pairing.json'), encoding='utf-8'))
    sha_ok = hashlib.sha256(repr(my_ev).encode()).hexdigest() == d34['events_sha']
    keys = {}
    for (a, sw, sr) in my_ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1
    info('前置核：事件 %d 條、sha 相符 = %s、鍵 = %d' % (len(my_ev), sha_ok, len(keys)))

    def Tterm(x, a, g):
        y = MUL[x][g]
        if tie[x][a] and not tie[y][a]:
            return dind[x][a] * eps[x] * sgn(dot3(U[a], KV[y]))
        return 0

    Tx = {k: [Tterm(x, k[0], k[1]) for x in range(n)] for k in sorted(keys)}
    empty = [k for k in Tx if all(v == 0 for v in Tx[k])]
    nonempty = [k for k in Tx if any(v != 0 for v in Tx[k])]

    # ================= 前置：keys / tau / Z10 / S_TT（與 R11/R12 同式） =================
    keys = {}
    for (a, sw, sr) in my_ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1

    def Tterm(x, a, g):
        y = MUL[x][g]
        if tie[x][a] and not tie[y][a]:
            return dind[x][a] * eps[x] * sgn(dot3(U[a], KV[y]))
        return 0

    Tx = {k: [Tterm(x, k[0], k[1]) for x in range(n)] for k in sorted(keys)}
    nonempty = [k for k in Tx if any(v != 0 for v in Tx[k])]
    tau = {}
    for k in nonempty:
        T = Tx[k]
        tf = set(x for x in range(n) if T[x] != 0)
        tau[k] = sorted(t for t in range(n) if all((((MUL[t][x] in tf) == (x in tf)) and
                     (T[MUL[t][x]] == (-T[x] if x in tf else 0))) for x in range(n)))

    def S_TT(a, g):
        tot = 0
        for x in range(n):
            y = MUL[x][g]
            if tie[x][a] and tie[y][a]:
                tot += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
        return tot

    f_tf = [0] * n
    f_ft = [0] * n
    f_tt = [0] * n
    for s0 in range(n):
        for (a, sw, sr) in my_ev:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = tie[w][a], tie[r2][a]
            if tw and tr:
                f_tt[s0] += (0 if dind[r2][a] == dind[w][a] else 1) * eps[r2] * eps[w]
            elif tr:
                f_tf[s0] += dind[r2][a] * eps[r2] * sgn(dot3(U[a], KV[w]))
            elif tw:
                f_ft[s0] += dind[w][a] * eps[w] * sgn(dot3(U[a], KV[r2]))
    Z10 = sorted(s for s in range(n) if f_tf[s] + f_ft[s] == 0)
    col_of = {}
    col_g = {}
    for (a, g) in keys:
        col_of[g] = a
        col_g[a] = g
    pairs = sorted(i for i in range(ncol) if i < partner[i])
    nz22 = sorted(a for a in range(ncol) if any(S_TT(a, g) != 0 for g in range(n)))
    nec8 = sorted(a for a in range(ncol) if types[a] == 'edge' and a not in set(nz22))
    info('前置：非空鍵 = %d、|τ| 分佈 = %s、Z10 = %s、承載列 = %d（型別 %s）、非承載 edge 欄 = %s'
         % (len(nonempty), sorted(set(len(tau[k]) for k in nonempty)), Z10, len(nz22),
            sorted(set(types[a] for a in nz22)), nec8))

    # ================= 共用：值/欄/貢獻 =================
    vals = sorted(set(KV))
    Tset = {a: sorted(x for x in range(n) if tie[x][a]) for a in range(ncol)}
    Vset = {a: sorted(set(KV[x] for x in Tset[a])) for a in range(ncol)}
    ell = lambda v: firstsgn(v)
    def lidx(w):
        for k in range(3):
            if w[k] != (0, 0):
                return k
        return -1
    def sgnpat(w):
        return tuple(0 if w[k] == (0, 0) else sgn(w[k]) for k in range(3))
    def ant(u, v):
        return all(add(u[k], v[k]) == (0, 0) for k in range(3))
    def half_pairs(a):
        out = []
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                v, w = vals[i], vals[j]
                if ant(v, w):
                    continue
                if cross3(tuple(add(v[k], w[k]) for k in range(3)), U[a]) == ((0, 0), (0, 0), (0, 0)):
                    out.append((v, w))
        return out
    HT = {a: half_pairs(a) for a in range(ncol) if types[a] == 'edge'}
    lines = sorted(set(min(a, partner[a]) for a in range(ncol) if types[a] == 'edge'))
    gkey = {tuple(tuple(x) for x in G[s]): s for s in range(n)}
    negi = {s: gkey[tuple(tuple((-x[0], -x[1]) for x in G[s]))] for s in range(n)}
    COL = {}
    for (a, sw, sr) in my_ev:
        COL.setdefault(a, []).append((sw, sr))
    La = {}
    for a in sorted(COL):
        La[a] = {}
        for s0 in range(n):
            acc = 0
            for (sw, sr) in COL[a]:
                w, r2 = MUL[s0][sw], MUL[s0][sr]
                tw, tr = tie[w][a], tie[r2][a]
                if tr and not tw:
                    acc += dind[r2][a] * eps[r2] * sgn(dot3(U[a], KV[w]))
                elif tw and not tr:
                    acc += dind[w][a] * eps[w] * sgn(dot3(U[a], KV[r2]))
            La[a][s0] = acc
    LAMv = {s0: sum(La[a][s0] for a in La) for s0 in range(n)}
    support = sorted(a for a in La if any(La[a][s0] != 0 for s0 in range(n)))
    PHI1 = (F(-1, 2), F(1, 2))
    D0 = {a: dot3(U[a], U[0]) for a in range(ncol) if types[a] == 'edge'}
    B10 = sorted(a for a in D0 if D0[a] in (PHI1, (-PHI1[0], -PHI1[1])))
    NZc = {a: sum(1 for k in range(3) if U[a][k] == (0, 0)) for a in D0}

    def edgepair(a):
        best = None
        for v, w in HT[a]:
            key = dot3(v, w)
            if best is None or sgn((key[0] - best[0][0], key[1] - best[0][1])) > 0:
                best = (key, (v, w))
        return best[1]
    EP = {L: edgepair(L) for L in lines}

    def edgepair(a):
        best = None
        for v, w in HT[a]:
            key = dot3(v, w)
            if best is None or sgn((key[0] - best[0][0], key[1] - best[0][1])) > 0:
                best = (key, (v, w))
        return best[1]
    EP = {L: edgepair(L) for L in lines}

    # ================= Part S：B10 之機制（五邊形猜想） =================
    # ================= 共用：鍵／加項 =================
    term = {}
    for (a, sw, sr) in my_ev:
        for s0 in range(n):
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = tie[w][a], tie[r2][a]
            if tr and not tw:
                term[(a, sw, sr, s0)] = dind[r2][a] * eps[r2] * sgn(dot3(U[a], KV[w]))
            elif tw and not tr:
                term[(a, sw, sr, s0)] = dind[w][a] * eps[w] * sgn(dot3(U[a], KV[r2]))
            else:
                term[(a, sw, sr, s0)] = 0
    keys_of = {}
    for (a, sw, sr) in my_ev:
        keys_of.setdefault(a, []).append((sw, sr))
    M1 = (F(-1, 2), F(1, 2))        # φ⁻¹
    M1n = (F(1, 2), F(-1, 2))       # −φ⁻¹
    M2 = (F(3, 2), F(-1, 2))        # φ⁻² = (3−√5)/2
    M3 = (F(-2), F(1))              # φ⁻³ = √5−2
    Z5o = (F(0), F(0))
    O5o = (F(1), F(0))
    vadd3 = lambda u, w: tuple(add(u[k], w[k]) for k in range(3))
    vsub3 = lambda u, w: tuple(add(u[k], neg(w[k])) for k in range(3))
    smul = lambda c, w: tuple(mul(c, w[k]) for k in range(3))

    # ================= 共用：鍵／加項 =================
    term = {}
    for (a, sw, sr) in my_ev:
        for s0 in range(n):
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = tie[w][a], tie[r2][a]
            if tr and not tw:
                term[(a, sw, sr, s0)] = dind[r2][a] * eps[r2] * sgn(dot3(U[a], KV[w]))
            elif tw and not tr:
                term[(a, sw, sr, s0)] = dind[w][a] * eps[w] * sgn(dot3(U[a], KV[r2]))
            else:
                term[(a, sw, sr, s0)] = 0
    keys_of = {}
    for (a, sw, sr) in my_ev:
        keys_of.setdefault(a, []).append((sw, sr))
    M1 = (F(-1, 2), F(1, 2))        # φ⁻¹
    M1n = (F(1, 2), F(-1, 2))       # −φ⁻¹
    M2 = (F(3, 2), F(-1, 2))        # φ⁻² = (3−√5)/2
    M3 = (F(-2), F(1))              # φ⁻³ = √5−2
    Z5o = (F(0), F(0))
    O5o = (F(1), F(0))
    vadd3 = lambda u, w: tuple(add(u[k], w[k]) for k in range(3))
    vsub3 = lambda u, w: tuple(add(u[k], neg(w[k])) for k in range(3))
    smul = lambda c, w: tuple(mul(c, w[k]) for k in range(3))

    # ================= 共用 =================
    def fsl(A):
        for k in range(3):
            s = sgn(A[k])
            if s != 0:
                return k, s
        return -1, 0
    def vadd3(u, w):
        return tuple(add(u[k], w[k]) for k in range(3))
    def smul(c, w):
        return tuple(mul(c, w[k]) for k in range(3))
    def inv5(y):
        p, q = y
        d = p * p - 5 * q * q
        return (F(p, 1) / F(d, 1), F(-q, 1) / F(d, 1))
    def div5(y, z):
        return mul(y, inv5(z))
    Vset = {a: sorted(set(KV[x] for x in range(n) if tie[x][a])) for a in range(ncol)}
    def reps_of(a):
        V, seen, out = sorted(Vset[a]), set(), []
        for x in V:
            if x in seen:
                continue
            y = tuple(neg(x[k]) for k in range(3))
            seen.add(x); seen.add(y)
            out.append(min(x, y))
        return sorted(out)
    nclines = [L for L in lines if sum(1 for t in range(3) if U[L][t] == (0, 0)) == 0]


    # ================= Part P：MECH-1 非單項族（41/42）雙項式符號 =================
    def terms_of(u, x):
        T0 = mul(mul(u[0], u[1]), x[0])
        T1 = mul(add(mul(u[1], u[1]), mul(u[2], u[2])), x[1])
        return T0, T1
    P1rows, P2bad, P3rows, P3bad, P4rows = [], [], [], [], []
    for L in [41, 42]:
        u = U[L]
        for x in reps_of(L):
            T0, T1 = terms_of(u, x)
            s0p, s1p = sgn(T0), sgn(T1)
            A0, j = cross3(u, x)[0], fsl(x)[0]
            P1rows.append((L, vals.index(x), str(x), str(T0), str(T1), s0p, s1p, sgn(add(T0, T1)),
                           j, sgn(x[j]), sgn(A0), sgn(mul(u[0], u[1])), sgn(mul(x[0], x[1]))))
            if add(T0, T1) != neg(mul(u[2], A0)):
                P2bad.append((L, str(x), str(add(T0, T1)), str(neg(mul(u[2], A0)))))
            same = (s0p == s1p)
            pred = (sgn(mul(u[0], u[1])) == sgn(mul(x[0], x[1])))
            P3rows.append((L, vals.index(x), same, pred, s0p, s1p, sgn(mul(u[0], u[1])), sgn(mul(x[0], x[1]))))
            if same != pred:
                P3bad.append(P3rows[-1])
    claim('P1', '★（量測）41/42 逐值雙項表（T_0, T_1, 兩項符號, sgn(A_0), sgn(x_j), sgn(u_0u_1), sgn(x_0x_1)）',
          True, '逐值 = %s' % P1rows)
    claim('P2', '★★（推導／恆等式）T_0 + T_1 = −u_2·A_0（逐值精確，Z[√5] 元素相等）',
          P2bad == [], '反例 = %s' % P2bad)
    claim('P3', '★★（猜測·極性正向）41/42：兩項同號 ⟺ sgn(u_0u_1) = sgn(x_0x_1)',
          P3bad == [], '逐值 (L,值索引,同號?,預測,sgnT0,sgnT1,sgn u01,sgn x01) = %s' % P3rows)
    for L in [41, 42]:
        u = U[L]
        xs = reps_of(L)
        P4rows.append((L, sorted(set(sgn(mul(x[0], x[1])) for x in xs)), sgn(mul(u[0], u[1])), sgn(u[2]),
                       sorted(set(sgn(x[j]) for x in xs for j in [fsl(x)[0]])), len(xs)))
    claim('P4', '★（量測＋結構）41/42 之 V(a) 上 sgn(x_0x_1) 恆定？並報 sgn(u_0u_1)、sgn(u_2)、sgn(x_j) 之集合',
          True, '逐線 (L, {sgn x01}, sgn u01, sgn u2, {sgn x_j}, |V|) = %s' % P4rows)
    P5rows = []
    for L in nclines:
        u = U[L]
        bits = sorted(set(1 if sgn(cross3(u, x)[0]) * sgn(x[fsl(x)[0]]) == -1 else 0 for x in reps_of(L)))
        P5rows.append((L, bits, L in set(nz22), L in (39, 40, 41, 42)))
    P5const = [r[0] for r in P5rows if len(r[1]) == 1]
    claim('P5', '★★（機制連結／回歸）12 非座標線上「sgn(A_0)·sgn(x_j) 於 V(a) 恆定」之欄 = 非承載集 {39,40,41,42}',
          set(P5const) == {39, 40, 41, 42} and all(not r[2] for r in P5rows if r[0] in (39, 40, 41, 42)),
          '逐線 (L, 位元集, 承載?, ∈{39..42}?) = %s ; 恆定欄 = %s' % (P5rows, P5const))

    # ================= Part Q：MECH-2 head 路線 vs 凍結路線 =================
    def keyroute(s0):
        out = {}
        for (a, g) in keys:
            out[a] = out.get(a, 0) + keys[(a, g)] * Tterm(s0, a, g)
        return out
    Hk = sorted(s0 for s0 in range(n) if sum(keyroute(s0).get(a, 0) for a in range(ncol)) == 0)
    f_tf2, f_ft2 = [0] * n, [0] * n
    for s0 in range(n):
        for (a, sw, sr) in my_ev:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = tie[w][a], tie[r2][a]
            if tr and not tw:
                f_tf2[s0] += dind[r2][a] * eps[r2] * sgn(dot3(U[a], KV[w]))
            elif tw and not tr:
                f_ft2[s0] += dind[w][a] * eps[w] * sgn(dot3(U[a], KV[r2]))
    Zf2 = sorted(s0 for s0 in range(n) if f_tf2[s0] + f_ft2[s0] == 0)
    claim('Q1', '★（量測／回歸）head 路線（Σ_鍵 重數·Tterm）之零集 = 44 態（R23 Z4 ✗ 之值）',
          len(Hk) == 44, '零集大小 = %d ; 首 12 = %s' % (len(Hk), Hk[:12]))
    claim('Q2', '★（猜測·極性正向）head 路線零集 ⊇ 凍結路線零集（Z10）',
          set(Zf2) <= set(Hk), 'Z10 ⊆ Hk = %s ; |Hk − Z10| = %d ; |Z10| = %d'
          % (set(Zf2) <= set(Hk), len(set(Hk) - set(Zf2)), len(Zf2)))
    nscols = sorted(set(a for (a, g) in keys))
    gmap = {}
    for (a, sw, sr) in my_ev:
        gmap.setdefault(a, {}).setdefault(MUL[inv[sr]][sw], []).append((sw, sr))
    Q3rows, Q3bad = [], []
    for a in nscols:
        gk = sorted(g for (a2, g) in keys if a2 == a)
        gf = sorted(gmap.get(a, {}).keys())
        Q3rows.append((a, len(gk), len(gf), gk == gf, {g: len(v) for g, v in sorted(gmap.get(a, {}).items())},
                       sorted(set(keys[(a, g)] for g in set(gk)))))
        if gk != gf:
            Q3bad.append((a, gk, gf))
    claim('Q3', '★★（結構）head 鍵集之 g 支撐 = 凍結事件以 g = MUL[inv[sr]][sw] 所導之 g 集（逐欄），並報一 g 對多 (sw,sr) 之重數',
          Q3bad == [], '逐欄 (欄, |g_鍵|, |g_凍結|, 集相同?, 一 g→多事件重數, 鍵重數集) = %s ; 反例 = %s'
          % (Q3rows[:8], Q3bad))
    diffcnt = sum(1 for a in range(ncol) for s0 in range(n) if keyroute(s0).get(a, 0) != La[a][s0])
    claim('Q4', '★★（定讞）不等價以可驗證形式登錄：head／凍結兩路線之逐（欄,態）加項矩陣不相等數 = %d > 0；零集 44 ≠ 10；既有 Λ／Z10 結論依凍結路線不變' % diffcnt,
          diffcnt > 0 and len(Hk) == 44 and len(Zf2) == 10,
          '不相等（欄,態）數 = %d ; |Hk| = %d ; |Zf| = %d ; 支撐欄數 = %d'
          % (diffcnt, len(Hk), len(Zf2), len(nscols)))


    # ================= Part P 校正律（P3 於 41/42 之兩代表上「同號」恆假 ⟹ 判據未被正例檢驗） =================
    def abs_cmp2(y):                      # y ∈ Z[√5]：符號之精確比較用「平方」：|T_0| ≠ |T_1| ⟺ T_0² ≠ T_1²
        return mul(y, y)
    P6rows, P6bad = [], []
    for L in [41, 42]:
        u = U[L]
        for x in reps_of(L):
            T0, T1 = terms_of(u, x)
            opp = (sgn(T0) * sgn(T1) <= 0)                 # 異號或一項為零
            neq = (abs_cmp2(T0) != abs_cmp2(T1))           # |T_0| ≠ |T_1|（精確）
            nz = (add(T0, T1) != (0, 0))
            P6rows.append((L, vals.index(x), sgn(T0), sgn(T1), opp, neq, nz, str(add(T0, T1))))
            if not (opp and neq and nz):
                P6bad.append(P6rows[-1])
    claim('P3-c', '★★（校正律）41/42 之雙項**異號（或一項為零）**且 **|T_0| ≠ |T_1|** ⟹ `T_0 + T_1 ≠ 0`（R23 `Y3-c` 之「符號一致」措辭應更正為「異號不對消」）',
          P6bad == [], '逐值 (L,值索引,sgnT0,sgnT1,異號?,|T0|≠|T1|?,和≠0?,和) = %s ; 反例 = %s' % (P6rows, P6bad))
    claim('Q2-c', '★（校正律；Q2 ✗ 之真值）head 零集與凍結零集之關係 = **交集 8**（非包含），|Hk| = 44、|Z10| = 10',
          len(set(Hk) & set(Zf2)) == 8, '交集 = %d ; Hk∩Z10 = %s ; Hk−Z10 大小 = %d ; Z10−Hk = %s'
          % (len(set(Hk) & set(Zf2)), sorted(set(Hk) & set(Zf2)), len(set(Hk) - set(Zf2)), sorted(set(Zf2) - set(Hk))))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R24 機器' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/84_r24_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'P1': P1rows, 'P3': P3rows, 'P3c': P6rows, 'P4': P4rows, 'P5': P5rows, 'Hk': Hk, 'Zf': Zf2, 'Q3': Q3rows},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
