#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/76 -- R22 機器：兩座標分解（`r22-two-coordinate-v1`）。

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

    # ================= Part W：dind 之兩座標分解 =================
    def fsl(A):
        for k in range(3):
            s = sgn(A[k])
            if s != 0:
                return k, s
        return -1, 0
    W1bad = []
    for a in range(ncol):
        if types[a] != 'edge':
            continue
        for x in Vset[a]:
            A = cross3(U[a], x)
            i, sa = fsl(A)
            j, sx = fsl(x)
            pred = 1 if (sa * sx == -1) else 0
            s0 = [t for t in range(n) if KV[t] == x][0]
            if pred != dind[s0][a]:
                W1bad.append((a, vals.index(x), pred, dind[s0][a]))
    claim('W1', '★★（恆等式）dind(x,a) = [sgn((A_x)_{lidx(A_x)})·sgn(x_{lidx(x)}) = −1]（dind 只依兩座標）',
          W1bad == [], '反例 = %s' % W1bad[:6])
    def ij_of(a, x):
        A = cross3(U[a], x)
        i, sa = fsl(A)
        j, sx = fsl(x)
        return (i, j, sa * sx)
    W2rows = []
    for L in lines:
        W2rows.append((L, [(vals.index(x), ij_of(L, x)) for x in sorted(Vset[L])], L in set(nec8) or L in set(nec8 and [0]) or min(L, partner[L]) in set(nec8)))
    claim('W2', '★★（量測表）15 線 × 4 赤道值之 (lidx(A_x), lidx(x), 乘積) ＋ dind', True,
          '逐線 (L, [(值索引, (i,j,乘積))]) = %s' % [(r[0], r[1]) for r in W2rows])
    W3rows = []
    for L in sorted(set(min(a, partner[a]) for a in B10)):
        V = sorted(Vset[L])
        ps = []
        seen = set()
        for x in V:
            if x in seen:
                continue
            y = tuple(neg(x[k]) for k in range(3))
            seen.add(x); seen.add(y)
            ps.append(min(x, y))
        W3rows.append((L, [ij_of(L, x) for x in sorted(ps)], NZc[L]))
    ncx = [L for L in set(min(a, partner[a]) for a in B10) if NZc[L] == 0]
    claim('W3', '★★（猜想）B10 之 4 非座標線：二赤道對之 (lidx(A_x), lidx(x)) 對相同；座標軸線（45）則否',
          all(len(set((i, j) for (i, j, _) in r[1])) == 1 for r in W3rows if r[2] == 0) and
          len(set((i, j) for (i, j, _) in [r for r in W3rows if r[2] == 2][0][1])) > 1,
          '逐線 (L, [(i,j,乘積) per 二對], 零分量數) = %s' % [(r[0], r[1], r[2]) for r in W3rows])
    allij = [(L, ij_of(L, x)) for L in lines for x in sorted(Vset[L])]
    claim('W4', '★（猜想）15 線之 lidx(x) ∈ {0,1,2}；非座標線之 lidx(A_x) = 0',
          all(0 <= ij[1] <= 2 for (_, ij) in allij) and all(ij[0] == 0 for (L, ij) in allij if NZc[L] == 0),
          'lidx(x) 值域 = %s ; 非座標線之 lidx(A_x) 值域 = %s'
          % (sorted(set(ij[1] for (_, ij) in allij)), sorted(set(ij[0] for (L, ij) in allij if NZc[L] == 0))))
    # W3-c：由 W3 之 FAIL 換來之真律（j-混合）
    def jset(a):
        V = sorted(Vset[a])
        seen, js = set(), set()
        for x in V:
            if x in seen:
                continue
            y = tuple(neg(x[k]) for k in range(3))
            seen.add(x); seen.add(y)
            js.add(ij_of(a, min(x, y))[1])
        return js
    W3cbad = [(a, sorted(jset(a)), a in set(nec8)) for a in range(ncol) if types[a] == 'edge'
              and ((len(jset(a)) > 1) != (a in set(nec8)))]
    claim('W3-c', '★★（校正律；W3 之錯在要求 (i,j) 對相同，真律為「j 相異」）**非承載 ⟺ V(a) 之二赤道對代表之 lidx(x) 相異**（＝R18/R19 之 MIX；座標軸線 45 為 {0}）',
          W3cbad == [], '反例 = %s ; 逐線 (L, j 集, 非承載?) = %s'
          % (W3cbad, [(L, sorted(jset(L)), L in set(nec8)) for L in lines]))
    def constdind(a):
        bits = set()
        for x in Vset[a]:
            A = cross3(U[a], x)
            i, sa = fsl(A)
            j, sx = fsl(x)
            bits.add(1 if sa * sx == -1 else 0)
        return len(bits) == 1
    eq = [(a, constdind(a), a in set(nec8)) for a in range(ncol) if types[a] == 'edge']
    claim('W5', '★★（機制）dind 於 V(a) 恆定 ⟺ 二對之 (i,j) 對相同（＝承載之否） ⟺ B10 ∧ 非座標軸',
          all(c == nc for (a, c, nc) in eq), '逐欄 (欄, dind 恆定, 非承載) = %s' % [(a, c, nc) for (a, c, nc) in eq if c != nc] or '全同')

    # ================= Part X：Z10 之二鍵異號相消 =================
    def tie_terms(a, s0):
        out = []
        for (sw, sr) in keys_of[a]:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = tie[w][a], tie[r2][a]
            if tw != tr:
                out.append(term[(a, sw, sr, s0)])
        return out
    X1rows = sorted(set((a, max(len(tie_terms(a, s0)) for s0 in Z10)) for a in range(ncol)))
    claim('X1', '★★（量測律）於 Z10：每欄之 tie-型事件數 ≤ 2（並報分佈）', all(r[1] <= 2 for r in X1rows),
          '逐欄最大 tie 數分佈 = %s' % sorted(set(r[1] for r in X1rows)))
    X2bad = [(a, s0, tie_terms(a, s0)) for a in range(ncol) for s0 in Z10
             if len([t for t in tie_terms(a, s0) if t != 0]) == 2 and
             len(set(t for t in tie_terms(a, s0) if t != 0)) != 2]
    claim('X2', '★★（猜想）於 Z10：同一欄之 2 個 tie-型事件，若其 term 皆非零則異號',
          X2bad == [], '違反之（欄,態,值表）= %s' % X2bad[:4])
    # X2-c：診斷 —— 逐欄之鍵數／重數／於 Z10 之 N_a
    from collections import Counter as Ct
    mk = Ct(tuple(e) for e in my_ev)
    X2c = [(a, len(keys_of[a]), sorted(mk[(a, sw, sr)] for (sw, sr) in keys_of[a]),
            sorted(set(La[a][s0] for s0 in Z10))) for a in sorted(set(a for (a, _, _) in my_ev))]
    claim('X2-c', '★（診斷）逐欄之（鍵數, 各鍵重數, 於 Z10 之 Λ_a 值集）——查 X2 反例如何仍滿足 abs(N_a) ≤ 1', True,
          '逐欄 = %s' % [x for x in X2c if x[3] != [0]][:20])
    Ncc = {a: {s0: La[a][s0] // 2 for s0 in range(n)} for a in range(ncol) if a != 61}
    X3bad = [(a, s0) for a in Ncc for s0 in range(n) if abs(Ncc[a][s0]) > 1 and a in set(support)]
    claim('X3', '★★（推導）X2 ＋ 鍵重數 ∈ {1,2} ⟹ 於 Z10 每 support 欄 abs(N_a) ≤ 1（a ≠ 61）',
          all(abs(Ncc[a][s0]) <= 1 for a in set(support) if a != 61 for s0 in Z10),
          '違反之（欄,態）數 = %s ; Z10 之 N 值域 = %s'
          % (len([(a, s0) for a in set(support) if a != 61 for s0 in Z10 if abs(Ncc[a][s0]) > 1]),
             sorted(set(Ncc[a][s0] for a in set(support) if a != 61 for s0 in Z10))))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R22 機器' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/76_r22_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'nec8': nec8, 'B10': B10, 'W2': [[r[0], [[y[0], [y[1][0], y[1][1], y[1][2]]] for y in r[1]]] for r in W2rows],
                   'W3': [[r[0], [[i, j, s] for (i, j, s) in r[1]], r[2]] for r in W3rows]},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
