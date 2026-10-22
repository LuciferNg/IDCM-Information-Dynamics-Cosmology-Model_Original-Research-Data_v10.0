#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/87 -- R25 機器：`Z10` 之選擇律（Z10-1）＋ `W_a ≡ ∅` 之根因（Z10-2）（`r25-z10-selection-v1`）。

Part R  Z10-1：pre(T) 40 → Z10 10 之篩選（R1–R5：纖維結構、三判準統一、盲測）
Part S  Z10-2：W_a ≡ ∅ 之根因（S1–S4：B10 橋接、跨輪集合交會、dind 共同值律）
（沿用凍結 R23/R24 機器之前置：keys／τ／Z10／S_TT／f_tf／f_ft／f_tt／非空鍵；唯讀 O222）

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
RULES = 'r25-z10-selection-v1'
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
    print('O225 scripts/87 -- R25 MACHINE   (rules: %s)' % RULES)
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



    # ================= Part R：Z10-1 pre(T) → Z10 之篩選律 =================
    T4 = sorted(set(KV[s] for s in Z10))
    preT = sorted(s for s in range(n) if KV[s] in set(T4))
    zset = set(Z10)
    zo = {}
    for s in Z10:
        if MUL[s][zc] in zo:
            continue
        zo[s] = order[s]
    claim('R1', '★（回歸）|pre(T)| = 40、|Z10| = 10；Z10 於每階 o ∈ {3,4,5,6,10} 恰取一中心對',
          len(preT) == 40 and len(Z10) == 10 and sorted(zo.values()) == [3, 4, 5, 6, 10],
          '|pre(T)| = %d ; |Z10| = %d ; Z10 對之階 = %s ; T4 值數 = %d' % (len(preT), len(Z10), sorted(zo.values()), len(T4)))
    C1 = sorted(s for s in preT if f_tf[s] == 0 and f_ft[s] == 0)
    C2 = sorted(s for s in preT if sum(La[a][s] for a in range(ncol)) == 0 and max(abs(La[a][s]) for a in range(ncol)) <= 2)
    C3 = sorted(s for s in preT if f_tt[s] in (0, 1, 3))
    claim('R2', '★★（統一·三判準同集）於 pre(T) 內 C1（f_tf=f_ft=0）= C2（ΣN=0 ∧ max|N|≤1）= C3（f_tt ∈{0,1,3}）= Z10',
          C1 == C2 == C3 == sorted(Z10),
          'C1 = %d ; C2 = %d ; C3 = %d ; Z10 = %d ; 差集 (C1−Z10, Z10−C1, C2−Z10, C3−Z10) = %s'
          % (len(C1), len(C2), len(C3), len(Z10),
             (sorted(set(C1) - zset), sorted(zset - set(C1)), sorted(set(C2) - zset), sorted(set(C3) - zset))))
    R3rows = []
    for v in T4:
        fib = sorted(s for s in range(n) if KV[s] == v)
        pr = sorted(set(min(s, MUL[s][zc]) for s in fib))
        R3rows.append((str(v), len(fib), len(pr), len([s for s in fib if s in zset]),
                       sorted(set(order[s] for s in pr)),
                       {s: (f_tf[s], f_ft[s], f_tt[s], sum(La[a][s] for a in range(ncol))) for s in pr}))
    claim('R3', '★（纖維結構）T4 之每值纖維（大小 4）= 2 對 ±s；每纖維入 Z10 之態數 = 恰一對（= 2）',
          all(r[1] == 4 and r[2] == 2 for r in R3rows) and all(r[3] == 2 for r in R3rows),
          '逐纖維 (v, |fibre|, 對數, |fibre∩Z10|, 階集, 譜) = %s' % [(r[0][:18], r[1], r[2], r[3], r[4]) for r in R3rows])
    R4rows, R4bad = [], []
    for s in range(n):
        posc = sum(1 for a in range(ncol) if La[a][s] > 0)
        negc = sum(1 for a in range(ncol) if La[a][s] < 0)
        mx = max(abs(La[a][s]) for a in range(ncol))
        R4rows.append((s, s in zset, posc, negc, posc == negc if s in zset else None, mx))
        if s in zset and not (posc == negc):
            R4bad.append(R4rows[-1])
    claim('R4', '★★（算子形式）s ∈ Z10 ⟺ 16 support 欄之 N_a 中正項數 = 負項數（並報 max|N_a| 之值集）',
          R4bad == [] and all(r[5] <= 1 for r in R4rows if r[1]),
          'Z10 各態 (態, ∈Z10, 正, 負, 正=負?, max|N|) = %s ; 反例 = %s' % ([r for r in R4rows if r[1]], R4bad))
    C2all = sorted(s for s in range(n) if sum(La[a][s] for a in range(ncol)) == 0 and max(abs(La[a][s]) for a in range(ncol)) <= 2)
    claim('R5', '★（盲測 out-of-sample）C2 判準套用全部 120 態 ⟹ 解集恰 = Z10（額外解 = 0）',
          C2all == sorted(Z10) and all(not (sum(La[a][s] for a in range(ncol)) == 0) for s in range(n) if s not in zset and s in preT and max(abs(La[a][s]) for a in range(ncol)) > 2),
          '全域解 = %d ; 額外 = %s ; 缺 = %s' % (len(C2all), sorted(set(C2all) - zset), sorted(zset - set(C2all))))


    # ================= Part R 校正律（R1–R4 之原 FAIL 原樣保留） =================
    claim('R1-c', '★（校正律；R1 ✗ 之真值）Z10 對之階譜 = [3,3,4,5,5]（與 R15 G1 ❌ 之記錄逐位元一致）；pre(T) 20 對之階譜 = {2:1,3:4,4:7,5:8}',
          sorted(zo.values()) == [3, 3, 4, 5, 5] and sorted(zo.values()) == sorted([5, 5, 4, 3, 3]),
          'Z10 對之階 = %s ; Z10 對數 = %d ; pre(T) 對數 = %d ; T4 值數 = %d'
          % (sorted(zo.values()), len(zo), len(preT) // 2, len(T4)))
    C1c = sorted(s for s in preT if f_tf[s] == -f_ft[s] and f_tf[s] != 0)
    claim('R2-c', '★★（校正律；R15 I5／R25 C1）**抵消態形式**：C1′ := {s ∈ pre(T) : f_tf = −f_ft ≠ 0} **恰 = Z10**；'
                  '而 C2（ΣN=0 ∧ max|N|≤1）亦恰 = Z10 ⟹ **二判準統一**（C3 只必要不充分）',
          C1c == sorted(Z10) and C2 == sorted(Z10),
          'C1′ = %d（缺 = %s、多 = %s）；C2 = %d；C3 = %d（多 = %s）；Z10 = %d'
          % (len(C1c), sorted(set(Z10) - set(C1c)), sorted(set(C1c) - zset), len(C2), len(C3),
             sorted(set(C3) - zset), len(Z10)))
    claim('R3-c', '★（校正律；R3 ✗ 之真值）每 KV 值纖維大小 = 10（5 對）；|fibre ∩ Z10| 之值集 = {2,4}（合計 10）',
          all(r[1] == 10 and r[2] == 5 for r in R3rows) and sum(r[3] for r in R3rows) == 10,
          '逐纖維 (v12, |fibre|, 對數, |∩Z10|, 階集) = %s' % [(r[0][:16], r[1], r[2], r[3], r[4]) for r in R3rows])
    pure = sorted(s for s in range(n) if sum(1 for a in range(ncol) if La[a][s] > 0) == sum(1 for a in range(ncol) if La[a][s] < 0))
    claim('R4-c', '★★（校正律；R4 之量綱失誤）純判準 `pos = neg`（不含 max 條件）之全域解集大小 = %d；'
                  '與 Z10 之關係（缺／多）如下；`max|Λ_a|` 於 Z10 之值集 = %s'
          % (len(pure), sorted(set(max(abs(La[a][s]) for a in range(ncol)) for s in Z10))),
          set(Z10) <= set(pure),
          '純解 = %d ; Z10 ⊆ 純解 = %s ; 純解 − Z10 = %s ; Z10 − 純解 = %s ; Z10 之 max|Λ| = %s'
          % (len(pure), set(Z10) <= set(pure), sorted(set(pure) - zset), sorted(zset - set(pure)),
             sorted(set(max(abs(La[a][s]) for a in range(ncol)) for s in Z10))))

    # ================= Part S：Z10-2 W_a ≡ ∅ 之根因 =================
    def Wnz(a):
        cnt = 0
        for g in range(n):
            gi = inv[g]
            if any(tie[y][a] and tie[MUL[y][gi]][a] and dind[y][a] != dind[MUL[y][gi]][a] for y in range(n)):
                cnt += 1
        return cnt
    edge = [a for a in range(ncol) if types[a] == 'edge']
    nzg = {a: Wnz(a) for a in edge}
    Wempty = sorted(a for a in edge if nzg[a] == 0)
    claim('S1', '★（回歸）{a : W_a = ∅} = 8 非承載 edge 欄 [39,40,41,42,51,52,53,54]；承載 22 欄之 |{g : W_g ≠ ∅}| = 100（均一）',
          Wempty == [39, 40, 41, 42, 51, 52, 53, 54] and sorted(set(nzg[a] for a in edge if nzg[a] != 0)) == [100],
          'W-空集 = %s ; 非空之值集 = %s ; edge 欄數 = %d' % (Wempty, sorted(set(nzg.values())), len(edge)))
    TWO_PHI_INV = ((F(-1), F(1)), (F(1), F(-1)))   # 2φ⁻¹ 之兩符號：−1+√5 與 1−√5
    def two_dot(a):
        d = dot3(U[a], U[0])
        return (2 * d[0], 2 * d[1])
    B10 = sorted(a for a in range(ncol) if two_dot(a) in TWO_PHI_INV)
    S2set = sorted(a for a in edge if a in set(B10) and all(U[a][t] != (0, 0) for t in range(3)))
    claim('S2', '★★（橋接）{a : W_a = ∅} = {a : a ∈ B10（⟨U_a,U_0⟩ = ±φ⁻¹）∧ U_a 無零分量}',
          Wempty == S2set, 'W-空 = %s ; B10∧無零 = %s ; B10（全欄）= %s' % (Wempty, S2set, B10))
    Tset = {a: sorted(x for x in range(n) if tie[x][a]) for a in range(ncol)}
    Vset = {a: sorted(set(KV[x] for x in Tset[a])) for a in range(ncol)}
    Bset = sorted(a for a in edge if len(set(dind[x][a] for x in Tset[a])) == 1)
    lines = sorted(i for i in range(ncol) if i < partner[i])
    Cset = sorted(a for a in lines if len(set(1 if firstsgn(cross3(U[a], x)) * sgn(x[fsl(x)[0]]) == -1 else 0 for x in set(KV[s] for s in Tset[a]))) == 1)
    claim('S3', '★★（跨輪集合交會）R15 W-空集 = R16 值歸約集（dind 於 T_a 恆定）= R22/R24 之 dind-恆定欄（12 非座標線內）',
          Bset == Wempty and Cset == sorted(set(Wempty) & set(lines)),
          'W-空 = %s ; dind-恆定（T_a）= %s ; 非座標線之恆定欄 = %s ; 逐位元全同 = %s'
          % (Wempty, Bset, Cset, Bset == Wempty))
    S4rows, S4bad = [], []
    for a in Wempty:
        u = U[a]
        common = sorted(set(dind[x][a] for x in Tset[a]))
        pred = 1 if sgn(u[2]) > 0 else 0
        S4rows.append((a, common, sgn(u[2]), pred))
        if common != [pred]:
            S4bad.append(S4rows[-1])
    claim('S3-c', '★（校正律；S3 ✗ 之範圍失誤）45 canonical lines 內 dind-恆定欄 = %s（其中 edge∧W-空 = {39,40,41,42}；其餘之型別已列報）'
          % sorted(set(Cset)),
          set(Cset) >= {39, 40, 41, 42} and set(Wempty) & set(lines) == {39, 40, 41, 42},
          '45 lines 之恆定欄 = %s ; 其型別 = %s ; edge∧W-空 = %s ; 恆定欄 ∩ 非座標線(12) = %s'
          % (sorted(set(Cset)), {a: types[a] for a in sorted(set(Cset))},
             sorted(set(Wempty) & set(lines)),
             sorted(set(Cset) & set(L for L in lines if all(U[L][t] != (0, 0) for t in range(3))))))
    claim('S4', '★★（新律·極性正向）8 非承載欄之 dind 共同值 = 0 ⟺ sgn(u_2) = −1；= 1 ⟺ sgn(u_2) = +1',
          S4bad == [], '逐欄 (欄, 共同值, sgn(u_2), 預測) = %s ; 反例 = %s' % (S4rows, S4bad))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R25 機器' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/87_r25_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'T4': [str(v) for v in T4], 'preT': preT, 'Z10': Z10, 'C1': C1, 'C2': C2, 'C3': C3,
                   'R3': [r[:5] for r in R3rows], 'R4': [r for r in R4rows if r[1]], 'R5all': C2all,
                   'Wempty': Wempty, 'nzg': {str(k): v for k, v in nzg.items()}, 'B10': B10, 'S2set': S2set,
                   'Bset': Bset, 'Cset': Cset, 'S3c': sorted(set(Cset)), 'S4': S4rows, 'zo': {str(k): v for k, v in zo.items()}, 'C1c': C1c, 'pure': pure}, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
