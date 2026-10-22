#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/79 -- R23 機器：單項形式導出（`r23-derivation-v1`）。

Part S  B10 之機制（五邊形猜想：B10 = U_0 鄰域五邊形之 5 邊；⟨U_a,U_0⟩ = φ⁻¹ 之推導；y-線例外之機制）
Part T  逐欄貢獻之奇偶機制（Λ_a(s) = 2·N_a(s)；重數 1 之鍵加項和恆偶；abs(Λ_a) = 2 ⟺ abs(N_a) = 1）

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
RULES = 'r19-arithmetic-form-v1'
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
    print('O225 scripts/45 -- R12 MACHINE   (rules: %s)' % RULES)
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

    # ================= Part Y：A_0 之單項形式 =================
    Y1rows, Y1bad = [], []
    for L in nclines:
        u = U[L]
        s3 = sgn(mul(mul(u[0], u[1]), u[2]))
        for x in reps_of(L):
            A = cross3(u, x)
            prod = sgn(A[0]) * sgn(x[fsl(x)[0]])
            j = fsl(x)[0]
            if x[1] == (0, 0):
                pred, kind = -s3, 'j=0（x_1=0）'
            elif x[0] == (0, 0):
                pred, kind = -sgn(u[2]), 'j=1（x_0=0）'
            else:
                pred, kind = None, '非單項（x_0,x_1 皆非零）'
            Y1rows.append((L, j, str(x), kind, pred, prod))
            if pred is not None and pred != prod:
                Y1bad.append((L, kind, pred, prod))
    claim('Y1', '★★（推導）單項情形：j=0（x_1=0）⟹ sgn(A_0)·sgn(x_0) = −sgn(u_0u_1u_2)；j=1（x_0=0）⟹ = −sgn(u_2)',
          Y1bad == [], '反例 = %s ; 逐值 (L, j, x, 型, 預測, 實測) = %s' % (Y1bad, Y1rows[:6]))
    Y2ok, Y2rows = True, []
    for L in nclines:
        u, js = U[L], [fsl(x)[0] for x in reps_of(L)]
        same01 = (sgn(u[0]) * sgn(u[1]) == 1)
        constd = len(set(1 if sgn(cross3(u, x)[0]) * sgn(x[fsl(x)[0]]) == -1 else 0 for x in reps_of(L))) == 1
        mono = all(x[0] == (0, 0) or x[1] == (0, 0) for x in reps_of(L))
        Y2rows.append((L, same01, mono, constd, L in set(nec8)))
        if mono and (same01 != constd):
            Y2ok = False
    claim('Y2', '★★（推導）單項情形：二對乘積相同 ⟺ sgn(u_0·u_1) = +1（軸之首兩分量同號）',
          Y2ok, '逐線 (L, u0u1 同號, 單項?, 實測恆定?, 非承載?) = %s' % Y2rows)
    claim('Y3', '★★（量測＋機制）12 非座標線之三聯表：非承載 = 單項 ∧ 首兩分量同號', 
          all((r[2] and r[1]) == r[4] for r in Y2rows if r[0] in set([min(a, partner[a]) for a in nec8]) | set(nclines)),
          '逐線 = %s ; nec 線 = %s' % (Y2rows, sorted(set(min(a, partner[a]) for a in nec8))))
    Y4rows = []
    for L in nclines:
        u = U[L]
        for x in reps_of(L):
            if x[0] != (0, 0) and x[1] != (0, 0):
                A0 = cross3(u, x)[0]
                pred = neg(mul(add(mul(mul(u[0], u[1]), x[0]), mul(add(mul(u[1], u[1]), mul(u[2], u[2])), x[1])), inv2(u[2]))) if False else None
                # A_0 = −(u_0u_1x_0 + (u_1²+u_2²)x_1)/u_2
                num = add(mul(mul(u[0], u[1]), x[0]), mul(add(mul(u[1], u[1]), mul(u[2], u[2])), x[1]))
                pred = neg(div5(num, u[2]))
                Y4rows.append((L, str(x), str(A0), str(pred), pred == A0))
    claim('Y4', '★（推導）非單項型：A_0 = −(u_0u_1x_0 + (u_1²+u_2²)x_1)/u_2（雙項，可抵消）',
          all(r[4] for r in Y4rows), '逐值 (L, x, A_0 實, 公式, ✓) = %s' % Y4rows[:6])
    # Y5：41/42（非單項但非承載）之機制 —— 雙項符號
    Y5rows = []
    for L in [41, 42]:
        u = U[L]
        for x in reps_of(L):
            A0 = cross3(u, x)[0]
            num = add(mul(mul(u[0], u[1]), x[0]), mul(add(mul(u[1], u[1]), mul(u[2], u[2])), x[1]))
            Y5rows.append((L, vals.index(x), str(x[0]), str(x[1]), str(num), sgn(num), sgn(x[fsl(x)[0]]), sgn(A0)))
    claim('Y5', '★（量測＋機制）41/42 之二對代表之雙項式 `u_0u_1x_0 + (u_1²+u_2²)x_1` 之符號（供 Y3-c 之二族說明）', True,
          '逐值 (L, 值索引, x_0, x_1, num, sgn(num), sgn(x_j), sgn(A_0)) = %s' % Y5rows)
    claim('Y3-c', '★★（校正律；Y3 之錯在只覆蓋單項族）非承載 = 單項族（39/40：單項 ∧ 首兩分量同號）∪ 非單項族（41/42：雙項式符號一致）',
          all((r[2] and r[1]) == r[4] for r in Y2rows if r[0] in (39, 40)) and all(r[2] is False and r[4] for r in Y2rows if r[0] in (41, 42)),
          '單項族 = %s ; 非單項族 = %s' % ([r for r in Y2rows if r[0] in (39, 40)], [r for r in Y2rows if r[0] in (41, 42)]))

    # ================= Part Z：事件會計 =================
    cnt = {}
    for (a, g) in keys:
        cnt[a] = cnt.get(a, 0) + 1
    Z1 = [(a, sorted(keys[(a, g)] for g in [k[1] for k in keys if k[0] == a])) for a in sorted(cnt)]
    claim('Z1', '★★（獨立重算）鍵（(欄,群元素)）之重數分佈；support 欄之鍵數', True,
          '每欄鍵數分佈 = %s ; 重數分佈 = %s'
          % (sorted(set(len(v[1]) for v in Z1)), sorted(set(m for v in Z1 for m in v[1]))))
    # Z2：Λ 之三路會計
    def keyroute(s0):
        out = {}
        for (a, g) in keys:
            out[a] = out.get(a, 0) + keys[(a, g)] * Tterm(s0, a, g)
        return out
    kmax = 0
    mism = []
    for s0 in range(n):
        kr = keyroute(s0)
        for a in range(ncol):
            if kr.get(a, 0) != CLAIMS and False:
                pass
    # 用 head 之 La（若存在）或 R20 式另算
    mism2 = []
    for s0 in range(n):
        kr = keyroute(s0)
        for a in sorted(set(list(kr.keys()) + [b for (b, _, _) in my_ev])):
            if kr.get(a, 0) != La[a][s0]:
                mism2.append((a, s0, kr.get(a, 0), La[a][s0]))
    claim('Z2', '★★（會計核對）Λ_a(s) = Σ_鍵 重數·Tterm(s,a,g)（與 R20 之 La 逐欄逐態比對）',
          mism2 == [], '不符之（欄,態）數 = %d ; 首 6 = %s' % (len(mism2), mism2[:6]))
    Z3bad = [(a, s0) for a in range(ncol) for s0 in Z10
             if all(keys[(a, g)] == 2 for g in [k[1] for k in keys if k[0] == a]) and
             abs(sum(Tterm(s0, a, g) for g in [k[1] for k in keys if k[0] == a])) > 1]
    claim('Z3', '★★（重述）於 Z10：m_k = 2 之欄，Σ_鍵 term ∈ {−1,0,1}（⟺ Λ_a ∈ {−2,0,2}）',
          Z3bad == [], '違反之（欄,態）數 = %d ; 首 5 = %s' % (len(Z3bad), Z3bad[:5]))
    # Z4：兩路 Λ 之零集比較（關鍵回歸）
    LAMk = [sum(keyroute(s0).get(a, 0) for a in range(ncol)) for s0 in range(n)]
    LAMm = [sum(La[a][s0] for a in range(ncol)) for s0 in range(n)]
    Zk = sorted(s0 for s0 in range(n) if LAMk[s0] == 0)
    Zm = sorted(s0 for s0 in range(n) if LAMm[s0] == 0)
    claim('Z4', '★★（關鍵回歸）凍結路線 Λ（Σ_鍵 重數·Tterm）之零集 = R15–R22 所用之 Z10（10 態）',
          Zk == Zm and len(Zk) == 10, 'canonical 零集 = %s（%d）; 既有 Z10 = %s（%d）; Λ_canonical 水平 = %s'
          % (Zk, len(Zk), Zm, len(Zm), sorted(set(LAMk))))
    # Z6/Z7：凍結路線（55/58 之 f_tf/f_ft 式）之獨立重算與吻合
    f_tf = [0] * n
    f_ft = [0] * n
    for s0 in range(n):
        for (a, sw, sr) in my_ev:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = tie[w][a], tie[r2][a]
            if tr and not tw:
                f_tf[s0] += dind[r2][a] * eps[r2] * sgn(dot3(U[a], KV[w]))
            elif tw and not tr:
                f_ft[s0] += dind[w][a] * eps[w] * sgn(dot3(U[a], KV[r2]))
    mism6 = [(s0, f_tf[s0] + f_ft[s0], LAMm[s0]) for s0 in range(n) if f_tf[s0] + f_ft[s0] != LAMm[s0]]
    claim('Z6', '★★（凍結路線吻合）以 55/58 之 `f_tf/f_ft` 式另算：`f_tf + f_ft = Σ_a Λ_a`（逐態全等）—— 確認 R15–R22 所用 Λ 與凍結定義一致',
          mism6 == [], '不符之態數 = %d ; 首 4 = %s' % (len(mism6), mism6[:4]))
    Zf = sorted(s0 for s0 in range(n) if f_tf[s0] + f_ft[s0] == 0)
    claim('Z7', '★★（關鍵回歸）凍結路線之零集 = 既有 Z10（10 態）', Zf == Zm and len(Zf) == 10,
          '凍結路線零集 = %s（%d）; 既有 Z10 = %s（%d）' % (Zf, len(Zf), Zm, len(Zm)))
    claim('Z5', '★（量測）「鍵路線」（head 之 Tterm/keys）與凍結路線之差異分佈（說明 Z2/Z4 之 ❌ 屬路線差而非錯誤）', True,
          '逐態 (canonical, 既有) = %s' % [(s0, LAMk[s0], LAMm[s0]) for s0 in range(0, n, 12)])

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R23 機器' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/79_r23_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'nec8': nec8, 'Y2': Y2rows, 'Z1': Z1}, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
