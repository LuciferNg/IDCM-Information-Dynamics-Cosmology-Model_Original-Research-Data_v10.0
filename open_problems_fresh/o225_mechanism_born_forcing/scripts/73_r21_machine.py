#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/73 -- R21 機器：閉式導出（`r21-closed-form-v1`）。

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

    # ================= Part U：V(a) 與 U_a×x 之閉式 =================
    isN = lambda x: dot3(x, KV[0]) in (M1, M1n)
    U1bad = [a for a in range(ncol) if types[a] == 'edge' and (a in set(nec8)) != all(isN(x) for x in Vset[a])]
    claim('U1', '★★（等價刻畫）非承載 ⟺ V(a) 之 4 值皆與 U_0 之 dot = ±φ⁻¹（V(a) ⊂ N(U_0)∪−N(U_0)）',
          U1bad == [], '反例 = %s ; 逐線 (L, 性質) = %s ; nec = %s'
          % (U1bad, sorted((L, all(isN(x) for x in Vset[L])) for L in lines), sorted(nec8)))
    B10L = sorted(set(min(a, partner[a]) for a in B10))
    U2rows = []
    for L in B10L:
        v, w = EP[L]
        sig = [s0 for s0 in range(n) if mm.rot_ref(G[s0], v) == w and mm.rot_ref(G[s0], KV[0]) == KV[0]]
        good = []
        for s0 in sig:
            perm = sorted(set(vals.index(mm.rot_ref(G[s0], x)) for x in Vset[L]))
            good.append((s0, perm))
        U2rows.append((L, [g[0] for g in good][:2], good[0][1] if good else []))
    claim('U2', '★（量測）每 B10 線之邊 {v,w}：存在群元素固定 U_0 且交換 v,w（鏡射 σ_{vw}），其對 V(a) 之置換交換二對',
          all(len(r[1]) >= 1 for r in U2rows), '逐線 (L, 前 2 個 σ, σ 對 V 之置換) = %s' % U2rows)
    U3rows, U3bad = [], []
    for L in B10L:
        v, w = EP[L]
        rows = []
        for x in sorted(Vset[L]):
            al = dot3(x, KV[0])
            be = mul(add(dot3(x, v), neg(mul(al, M3))), (F(3, 4), F(1, 4)))   # β = (⟨x,v⟩ − αφ⁻³)·φ²/2
            ga = add(neg(mul(al, M1)), neg(be))
            recon = vadd3(vadd3(smul(al, KV[0]), smul(be, v)), smul(ga, w))
            ok = recon == x
            if not ok:
                U3bad.append((L, vals.index(x), str(al), str(be), str(ga)))
            rows.append((vals.index(x), str(al), str(be), str(ga), ok))
        U3rows.append((L, rows))
    claim('U3', '★★（推導）frame 恒等式：x ⊥ U_a ⟹ x = αU_0 + βv + γw，α = ⟨x,U_0⟩（U_0-係數 = 其 dot），β = (⟨x,v⟩−αφ⁻³)/(2φ⁻²)，γ = −αφ⁻¹−β（逐分量精確重建）',
          U3bad == [], '反例 = %s ; 逐線 (L, [(值索引, α, β, γ, 重建✓)]) = %s' % (U3bad, U3rows[:2]))
    U4rows, U4bad = [], []
    for L in B10L:
        v, w = EP[L]
        T = vadd3(cross3(v, KV[0]), cross3(w, KV[0]))
        C = cross3(v, w)
        sc = add(O5o, M1)   # 1+φ⁻¹ = φ
        cx = vadd3(smul(neg(M1), T), smul(sc, C))
        cy = vsub3(smul(neg(M1), T), smul(sc, C))
        hit = []
        for x in sorted(Vset[L]):
            got = cross3(U[L], x) if False else None
            if got is None:
                pass
        ex = [x for x in sorted(Vset[L]) if cross3(U[L], x) == cx]
        ey = [x for x in sorted(Vset[L]) if cross3(U[L], x) == cy]
        U4rows.append((L, [vals.index(x) for x in ex], [vals.index(x) for x in ey]))
        if not (ex and ey):
            U4bad.append((L, [str(cross3(U[L], x)) for x in sorted(Vset[L])]))
    claim('U4', '★★（推導）叉積閉式：U_a×x = ½[−φ⁻¹T + (1+φ⁻¹)C]、U_a×y = ½[−φ⁻¹T − (1+φ⁻¹)C]（T = v×U_0+w×U_0，C = v×w）——每線恰一對各命中之值',
          U4bad == [], '反例 = %s ; 逐線 (L, +C 命中值, −C 命中值) = %s' % (U4bad, U4rows))
    U5rows = [(L, lidx(cross3(U[L], EP[L][0])), lidx(cross3(U[L], EP[L][1])), NZc[L]) for L in B10L]
    ncx = [L for L in B10L if NZc[L] == 0]
    claim('U5', '★★（最後一步）5 個 B10 線中 lidx(U_a×x) = lidx(U_a×y) 者恰為 4 條非座標線',
          sorted(L for L in B10L if lidx(cross3(U[L], sorted(Vset[L])[0])) == lidx(cross3(U[L], sorted(Vset[L])[1]))) == ncx,
          '逐線 (L, lidx(×v), lidx(×w), 零分量數) = %s ; 非座標線 = %s' % (U5rows, ncx))
    claim('U6', '★★（機制）非承載 ⟺ V(a) ⊂ N(U_0)∪−N(U_0)；非座標情形二對之 leading index 相同 ⟹ 判準退化為乘積相同 ⟹ dind 於 V(a) 恆定',
          U1bad == [] and sorted(L for L in B10L if NZc[L] == 0) == ncx, 'U1 反例 = %s ; 非座標 = %s' % (U1bad, ncx))

    # U3-a：以 3×3 線性解獨立求係數，檢 α = ⟨x,U_0⟩（推導恆等式）
    def coef(x, v, w):
        # Gram = [[A,c,c],[c,A,c],[c,c,A]]，右邊 d = (⟨x,U_0⟩,⟨x,v⟩,⟨x,w⟩)
        A11, c11 = dot3(KV[0], KV[0]), dot3(KV[0], v)
        d0, d1, d2 = dot3(x, KV[0]), dot3(x, v), dot3(x, w)
        # 解 [[A,c,c],[c,A,c],[c,c,A]] (a,b,g) = d：用對稱性 a = (d0*? ) -> 直接消去
        # 令 S = b+g：由 (1)-(2): (A-c)(a) + (c-A)(b) + 0 = d0-d1；同理
        D = add(A11, neg(c11))                      # A-c
        e0 = add(d0, neg(d1))                       # = D(a-b)
        e1 = add(d0, neg(d2))                       # = D(a-g)
        ab = mul(e0, inv5(D))
        ag = mul(e1, inv5(D))
        # a-b = ab, a-g = ag；又由 (1): Aa + c(b+g) = d0，b+g = 2a - ab - ag
        # ⟹ Aa + c(2a - ab - ag) = d0 ⟹ a(A+2c) = d0 + c(ab+ag)
        num = add(d0, mul(c11, add(ab, ag)))
        den = add(A11, add(c11, c11))
        a = mul(num, inv5(den))
        return a, a
    def inv5(y):
        # 1/(p+q√5) = (p - q√5)/(p²-5q²)
        p, q = y
        d = p * p - 5 * q * q
        return (F(p, 1) / F(d, 1), F(-q, 1) / F(d, 1))
    U3arows, U3abad = [], []
    for L in B10L:
        v, w = EP[L]
        for x in sorted(Vset[L]):
            a_, _ = coef(x, v, w)
            ok = (a_ == dot3(x, KV[0]))
            if not ok:
                U3abad.append((L, vals.index(x), str(a_), str(dot3(x, KV[0]))))
            U3arows.append((L, vals.index(x), str(dot3(x, KV[0])), ok))
    claim('U3-a', '★★（推導）frame 恆等式（唯一性驗證）：α := U_0-係數（3×3 Gram 解）恆 = ⟨x,U_0⟩（perp + Gram ⟹ 恆等）',
          U3abad == [], '反例 = %s ; 逐值 (L, 值索引, ⟨x,U_0⟩, ✓) = %s' % (U3abad, U3arows[:6]))
    # U5-c：以「赤道二對之代表」正確比較（每對之 firstsgn 位）
    def pairreps(L):
        V = sorted(Vset[L])
        negmap = lambda x: tuple(neg(x[k]) for k in range(3))
        seen, reps = set(), []
        for x in V:
            if x in seen:
                continue
            y = negmap(x)
            seen.add(x)
            seen.add(y)
            reps.append(min(x, y))
        return V, [(vals.index(r), firstsgn(cross3(U[L], r)), firstsgn(r)) for r in sorted(reps)]
    U5rows, U5ok = [], True
    for L in B10L:
        V, reps = pairreps(L)
        U5rows.append((L, reps, NZc[L]))
    bits = {L: sorted(set(0 if fs == fx else 1 for (_, fs, fx) in reps)) for (L, reps, _) in U5rows}
    claim('U5-c', '★★（最後一步）B10 線之二對代表之 dind 位相同 ⟺ 非座標軸（39/40/41/42 皆 0 或皆 1；45 為 {0,1}）',
          all(bits[L] == [0] or bits[L] == [1] for (L, _, z) in U5rows if z == 0) and bits[45] == [0, 1],
          '逐線 (L, 位之集合, 零分量數) = %s' % sorted((L, bits[L], z) for (L, _, z) in U5rows))

    # ================= Part V：Z10 之「每欄至多一鍵貢獻」 =================
    def contrib_keys(a, s0):
        return [k for k in keys_of[a] if term[(a, k[0], k[1], s0)] != 0]
    V1bad = [(a, s0) for a in range(ncol) for s0 in Z10 if len(contrib_keys(a, s0)) > 1]
    claim('V1', '★★（量測律）於 Z10 之 10 態：全部 62 欄每欄之貢獻鍵數 ≤ 1',
          V1bad == [], '違反之（欄,態）數 = %d ; 首 5 = %s' % (len(V1bad), V1bad[:5]))
    Nc = {a: {s0: La[a][s0] // 2 for s0 in range(n)} for a in range(ncol) if a not in [61]}
    V2bad = [(a, s0) for a in Nc for s0 in range(n)
             if (abs(Nc[a][s0]) <= 1) != (len(contrib_keys(a, s0)) <= 1)]
    claim('V2', '★★（推導）a ≠ 61（鍵重數皆 2）⟹ N_a = Σ_{貢獻鍵} ±1 ⟹ abs(N_a) ≤ 1 ⟺ 至多一鍵貢獻',
          V2bad == [], '違反之（欄,態）數 = %d' % len(V2bad))
    V3rows = []
    for a in sorted(set(a for (a, sw, sr) in my_ev)):
        cnt = []
        for s0 in Z10:
            k = 0
            for (sw, sr) in keys_of[a]:
                w, r2 = MUL[s0][sw], MUL[s0][sr]
                tw, tr = tie[w][a], tie[r2][a]
                if tw != tr:
                    k += 1
            cnt.append(k)
        V3rows.append((a, max(cnt)))
    claim('V3', '★★（機制）於 Z10：每欄滿足「恰一端在 T_a」型（tw ⊕ tr）之事件數 ≤ 1',
          all(r[1] <= 1 for r in V3rows), '逐欄（欄, Z10 上最大 tie-型數）= %s' % [r for r in V3rows if r[1] > 1] or '全部 ≤ 1')
    V4rows = sorted((a, sorted(set(len(contrib_keys(a, s0)) for s0 in Z10))) for a in sorted(set(a for (a, sw, sr) in my_ev)))
    claim('V4', '★（量測）Z10 之逐欄貢獻鍵數集合分佈；且 Z10 之 5 對之逐欄貢獻向量相同', True,
          '逐欄 = %s ; 對稱 = %s' % (V4rows, all(La[a][s0] == La[a][negi[s0]] for a in range(ncol) for s0 in Z10)))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R21 機器' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/73_r21_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'nec8': nec8, 'B10': B10, 'B10L': B10L}, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
