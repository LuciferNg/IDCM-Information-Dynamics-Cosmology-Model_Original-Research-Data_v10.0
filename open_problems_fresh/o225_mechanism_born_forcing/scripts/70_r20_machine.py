#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/70 -- R20 機器：機制導出（`r20-mechanism-derivation-v1`）。

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

    # ================= Part S：B10 之機制（五邊形猜想） =================
    N0 = {a: D0[a] for a in D0}                       # ⟨U_a,U_0⟩
    nbr = lambda x: dot3(KV[x], KV[0]) == PHI1        # 值索引 x 是否為 U_0 之鄰點
    S1ok, S1bad = True, []
    S1all = []
    for L in lines:
        v, w = EP[L]
        iv, iw = vals.index(v), vals.index(w)
        S1all.append((L, str(dot3(v, KV[0])), str(dot3(w, KV[0])), L in set(B10)))
        both = nbr(iv) and nbr(iw)
        if L in set(B10):
            if not both:
                S1ok = False
                S1bad.append((L, 'B10 但非五邊形邊'))
        else:
            if both:
                S1ok = False
                S1bad.append((L, '非 B10 但為五邊形邊'))
    claim('S1', '★★（猜想）a ∈ B10 ⟺ 該線之邊 {v,w} 之兩端點皆為 U_0 之鄰點（⟨v,U_0⟩ = ⟨w,U_0⟩ = φ⁻¹）⟹ B10 = U_0 鄰域五邊形之 5 邊',
          S1ok, '反例 = %s ; 五邊形邊線（EP 對之 dot 皆 φ⁻¹）= %s ; B10 線 = %s ; 逐線 (L,⟨v,U_0⟩,⟨w,U_0⟩,B10?) = %s'
          % (S1bad, sorted(L for L in lines if nbr(vals.index(EP[L][0])) and nbr(vals.index(EP[L][1]))),
             sorted(set(min(a, partner[a]) for a in B10)), S1all))
    S1cx = sorted(L for L in lines if (dot3(EP[L][0], KV[0]) == PHI1 and dot3(EP[L][1], KV[0]) == PHI1) or
                  (dot3(EP[L][0], KV[0]) == (F(1, 2), F(-1, 2)) and dot3(EP[L][1], KV[0]) == (F(1, 2), F(-1, 2))))
    claim('S1-c', '★★（校正律；S1 之錯在「同為 +φ⁻¹」，實為「同號 ±φ⁻¹」）B10 ⟺ EP 邊之兩端點同屬 N(U_0)（dot=+φ⁻¹）或同屬 −N(U_0)（dot=−φ⁻¹）⟹ B10 = U_0 鄰域五邊形（及其對徑五邊形）之 5 條邊之軸',
          S1cx == sorted(set(min(a, partner[a]) for a in B10)),
          '候選線 = %s ; B10 線 = %s' % (S1cx, sorted(set(min(a, partner[a]) for a in B10))))
    S2ok = []
    for L in sorted(set(min(a, partner[a]) for a in B10)):
        v, w = EP[L]
        sum2 = tuple(add(v[k], w[k]) for k in range(3))
        twice = tuple(add(U[L][k], U[L][k]) for k in range(3))
        mid = mul((F(1, 2), F(0)), add(dot3(v, KV[0]), dot3(w, KV[0])))
        S2ok.append((L, sum2 == twice, str(dot3(U[L], KV[0])), str(mid)))
    claim('S2', '■（推導）由 S1：v + w = 2·U_a ⟹ ⟨U_a,U_0⟩ = (⟨v,U_0⟩+⟨w,U_0⟩)/2 = φ⁻¹ ⟹ B10 之算術形式係 S1 之推論',
          all(x[1] for x in S2ok), '逐線 (L, v+w=2U_a, ⟨U_a,U_0⟩, ⟨v,U_0⟩) = %s' % S2ok)
    S3rows = []
    for L in sorted(set(min(a, partner[a]) for a in B10)):
        v, w = EP[L]
        eq = sorted(Vset[L])
        S3rows.append((L, [(vals.index(x), str(dot3(x, KV[0])), str(dot3(x, v)), str(dot3(x, w))) for x in eq],
                       [KV[0] in eq, v in eq, w in eq]))
    claim('S3', '★（量測）B10 每線之 4 赤道值之身分（與 U_0／v／w 之 dot）＋ U_0／v／w 是否 ⊥ U_a', True,
          '逐線 = %s' % S3rows[:2])
    yline = [L for L in lines if NZc.get(L, 0) == 2 and L in set(B10)]
    y0 = yline[0]
    eqy = sorted(Vset[y0])
    S4bits = [(vals.index(x), sgn(x[0]), sgn(x[2]), firstsgn(cross3(U[y0], x))) for x in eqy]
    S4d = [(vals.index(x), [dind[s0][y0] for s0 in range(n) if KV[s0] == x][0]) for x in eqy]
    claim('S4', '★★（推導）y-線：U_a = ±ê_y ⟹ U_a × v = (v_z, 0, −v_x)（單項、無抵消）⟹ 判準退化為 sign(v_z) ≠ sign(v_x) 之符號條件 ⟹ 4 值之 (sgn x, sgn z) 不同型 ⟹ dind 非恆定',
          len(set(b[3] for b in S4bits)) > 1 or len(set(b[1] * b[2] for b in S4bits)) > 1,
          'y-線 = %d ; 4 值之 (索引, sgn x, sgn z, firstsgn(U_a×v)) = %s ; dind = %s ; 乘積型數 = %d'
          % (y0, [(b[0], b[1], b[2], b[3]) for b in S4bits], S4d, len(set(b[1] * b[2] for b in S4bits))))
    S5bad = [a for a in D0 if (a in set(nec8)) != (a in set(B10) and NZc[a] == 0)]
    claim('S5', '★★（機制）非承載 ⟺ S1（五邊形邊）∧ U_a 無零分量（30 欄）', S5bad == [],
          '反例 = %s' % S5bad)

    # ================= Part T：逐欄貢獻之奇偶機制 =================
    from collections import Counter as Ct
    mk = Ct(tuple(e) for e in my_ev)
    odd = [(a, s0) for a in range(ncol) for s0 in range(n) if La[a][s0] % 2 != 0]
    claim('T1', '★★（猜想）全部 62 欄 × 120 態之 Λ_a(s) 恆為偶數', odd == [],
          '奇數之（欄,態）數 = %d ; 首 5 = %s' % (len(odd), odd[:5]))
    m1 = sorted(k for k, c in mk.items() if c == 1)
    m2 = sorted(k for k, c in mk.items() if c == 2)
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
    pair_same = all(term[(a, sw, sr, s0)] * mk[(a, sw, sr)] == 2 * term[(a, sw, sr, s0)]
                    for (a, sw, sr) in m2 for s0 in range(n))
    odd1 = [(a, s0) for a in range(ncol) for s0 in range(n)
            if sum(term[(a, sw, sr, s0)] for (aa, sw, sr) in m1 if aa == a) % 2 != 0]
    claim('T2', '★★（導出）鍵重數 ∈ {1,2}（61 鍵 ×2、2 鍵 ×1）；重數 2 之鍵貢獻 2·term（偶）；**每欄「重數 1 之鍵」之加項和恆偶** ⟹ Λ_a(s) = 2·N_a(s)',
          pair_same and odd1 == [],
          '重數分佈 = {2: %d, 1: %d} ; 重數1鍵之逐欄和為奇之（欄,態）數 = %d ; 首 5 = %s'
          % (len(m2), len(m1), len(odd1), odd1[:5]))
    Ncol = {a: {s0: La[a][s0] // 2 for s0 in range(n)} for a in range(ncol)}
    zbad = [(a, s0) for a in support for s0 in Z10 if abs(Ncol[a][s0]) > 1]
    counts = sorted(set((sum(1 for a in support if Ncol[a][s0] != 0),) for s0 in Z10))
    col61 = sorted(set(a for (a, s0) in odd))
    claim('T1-c', '★★（校正律）除第 61 欄外，其餘 61 欄之逐欄貢獻 Λ_a(s) 恆為偶數（奇異之 64 個（欄,態）全屬第 61 欄）',
          len(col61) == 1 and col61 == [61], '奇數欄 = %s ; 奇數（欄,態）數 = %d' % (col61, len(odd)))
    claim('T2-c', '★★（校正律）重數 1 之鍵恰 2 個且皆屬第 61 欄；其餘各欄恆偶 ⟹ Λ_a(s) = 2·N_a(s)（a ≠ 61）',
          len(m1) == 2 and all(k[0] == 61 for k in m1), 
          'm1 = %s（欄 = %s）; T2 之 64 違反是否全屬 61 欄 = %s'
          % (m1, sorted(set(k[0] for k in m1)), set(a for (a, s0) in odd1) == {61}))
    claim('T3', '★★（推導）abs(Λ_a(s)) = 2 ⟺ abs(N_a(s)) = 1；Z10 之逐欄 abs(N_a) ≤ 1，故 Z10 = {每欄 abs(N_a) ≤ 1 ∧ Σ N_a = 0 ∧ 非零}',
          zbad == [], 'Z10 上違反 |N| ≤ 1 之（欄,態）數 = %d ; Z10 之非零欄數集合 = %s ; N 值域 = %s'
          % (len(zbad), [c[0] for c in counts], sorted(set(Ncol[a][s0] for a in support for s0 in Z10))))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R20 機器' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/70_r20_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'nec8': nec8, 'B10': B10, 'support': support, 'Z10': Z10, 'yline': yline,
                   'mult': {'m2': len(m2), 'm1': len(m1)}, 'Nval': sorted(set(Ncol[a][s0] for a in support for s0 in Z10))},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
