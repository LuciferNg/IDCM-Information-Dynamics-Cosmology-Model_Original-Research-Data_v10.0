#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/64 -- R18 機器：四項律之閉合（`r18-frame-criterion-v1`）。

Part X  τ 之刻畫（16 非空 TF 鍵；中心不變／大小／階／中心化子）
Part Y  Z10 選擇律（KV 相鄰性精確核／重數／∩{g_a}／每對同 KV／f_tt）
Part Z  補集 20（成群？／∩{g_a} 型別／∩Z10）
Part Q  orbit 分類（型別單一性／31 對型別／非承載 8 edge 欄之 U 結構／承載列 g_a 階）

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
RULES = 'r18-frame-criterion-v1'
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

    # ================= Part N：座標框層判準 =================
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
    SP = {a: sgnpat(U[a]) for a in range(ncol) if types[a] == 'edge'}
    LX = {a: lidx(U[a]) for a in range(ncol) if types[a] == 'edge'}
    NZ = {a: sum(1 for k in range(3) if U[a][k] == (0, 0)) for a in range(ncol) if types[a] == 'edge'}
    coordpar = {a: (NZ[a] == 2) for a in range(ncol) if types[a] == 'edge'}
    claim('N1', '★（量測）15 線之 U_a 座標符號模式、leading index、零分量數、承載',
          True, '逐線 = %s' % [(L, SP[L], LX[L], NZ[L], L in set(nz22)) for L in lines])
    pred_nec = sorted(a for a in HT if NZ[a] >= 1 and not coordpar[a])
    claim('N2', '★★（猜想）非承載 ⟺ U_a 落於某座標平面內（有零分量）且不平行座標軸',
          pred_nec == sorted(nec8) and all(NZ[a] == 0 or coordpar[a] for a in HT if a in set(nz22)),
          '預測之非承載 = %s ; 實測 nec8 = %s ; 承載欄中有零分量者 = %s'
          % (pred_nec, sorted(nec8), [a for a in HT if a in set(nz22) and NZ[a] >= 1]))
    N3 = []
    for a in sorted(HT):
        has = any(lidx(cross3(U[a], v)) != lidx(v) for v in Vset[a])
        if (a in set(nz22)) != has:
            N3.append((a, has))
    claim('N3', '★★（猜想）承載 ⟺ ∃ 赤道值 v 使 ℓ(U_a × v) ≠ ℓ(v)', N3 == [], '反例 = %s' % N3)
    claim('N4', '★（量測）每線 4 赤道值之 (ℓ(v), ℓ(cross), sgn, sgn_cross, dind) 交叉表', True,
          '逐線 = %s' % [(L, [(lidx(v), lidx(cross3(U[L], v)), ell(v), firstsgn(cross3(U[L], v)),
                              (1 if firstsgn(cross3(U[L], v)) != ell(v) else 0)) for v in Vset[L]]) for L in lines])
    N5 = [L for L in lines if L in set(nec8) and len(set(lidx(v) for v in Vset[L])) != 1]
    claim('N5', '★★（猜想）非承載線之 V(a) 之 4 值 leading index 全同', N5 == [],
          '反例 = %s ; 各線 ℓ 分佈 = %s' % (N5, [(L, sorted(set(lidx(v) for v in Vset[L]))) for L in lines]))

    # ================= Part O：Z10 之群論篩選 =================
    gkey = {tuple(tuple(x) for x in G[s]): s for s in range(n)}
    negi = {}
    for s0 in range(n):
        k = tuple(tuple(neg(x) for x in G[s0])) if False else tuple(tuple((-x[0], -x[1]) for x in G[s0]))
        negi[s0] = gkey[k]
    LAMv = {}
    for s0 in range(n):
        acc = 0
        for (a, sw, sr) in my_ev:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = tie[w][a], tie[r2][a]
            if tw and tr:
                acc += 0
            elif tr:
                acc += dind[r2][a] * eps[r2] * sgn(dot3(U[a], KV[w]))
            elif tw:
                acc += dind[w][a] * eps[w] * sgn(dot3(U[a], KV[r2]))
        LAMv[s0] = acc
    claim('O1', '■ Λ(−s) = Λ(s)（因 R_{−x} = R_x ⟹ KV_{−x} = KV_x）⟹ Z10 為 ±-不變集',
          all(LAMv[s0] == LAMv[negi[s0]] for s0 in range(n)) and
          all(negi[s0] in set(Z10) for s0 in Z10),
          'Λ(-s)=Λ(s) 成立數 = %d/120 ; Z10 之 −-閉合 = %s ; −1 之索引 = %d'
          % (sum(1 for s0 in range(n) if LAMv[s0] == LAMv[negi[s0]]),
             all(negi[s0] in set(Z10) for s0 in Z10), negi[0]))
    ix = inv  # 群反演置換
    def mul(x, y):
        return MUL[x][y]
    x0 = Z10[0]
    H = sorted(set(MUL[z][ix[x0]] for z in Z10))
    closed = all(MUL[h1][h2] in set(H) for h1 in H for h2 in H)
    hasiden = 0 in H
    coset_ok = sorted(set(MUL[h][x0] for h in H)) == Z10
    claim('O2', '★★（猜想）Z10 係 2I 之某 10 階子群 H 之左陪集（Z10 = H·x, |H| = 10）',
          closed and hasiden and coset_ok and len(H) == 10,
          'H = %s ; |H| = %d ; 封閉 = %s ; e ∈ H = %s ; H·x = Z10 = %s ; H 之階譜 = %s'
          % (H, len(H), closed, hasiden, coset_ok, sorted(order[h] for h in H)))
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
    pairrel = {}
    for a in sorted(COL):
        b = partner[a]
        if b not in COL:
            continue
        for s0 in range(n):
            k = (La[a][s0], La[b][s0])
            key = 'zero' if k[0] == k[1] == 0 else ('same' if k[0] == k[1] else ('neg' if k[0] == -k[1] else 'other'))
            pairrel[key] = pairrel.get(key, 0) + 1
    claim('O3', '★（量測）逐欄配對律：Λ_{partner[a]}(s) 與 Λ_a(s) 之關係分佈', True,
          '分佈 = %s ; 樣本（線 39 之兩欄）= %s' % (pairrel, [(s0, La[39][s0], La[partner[39]][s0]) for s0 in range(6)]))
    SUMok = all(LAMv[s0] == sum(La[a][s0] for a in La) for s0 in range(n))
    zp = sorted((order[s], order[MUL[s][zc]]) for s in Z10 if s < MUL[s][zc])
    claim('O4', '★（回歸）Λ = Σ_a Λ_a 逐態成立；Λ⁻¹(0) = Z10；5 對階型 2×{3,6}＋1×{4,4}＋2×{5,10}',
          SUMok and sorted(s for s in range(n) if LAMv[s] == 0) == Z10 and
          zp == sorted([(3, 6), (3, 6), (4, 4), (5, 10), (5, 10)]),
          'Σ_a = Λ 成立 = %s ; {Λ=0} = %s ; 逐對 = %s' % (SUMok, sorted(s for s in range(n) if LAMv[s] == 0), zp))

    # ================= Part N（第二批）：關鍵否證素材與 ℓ-律 =================
    p34, p39 = SP[34], SP[39]
    claim('N6', '★★（關鍵否證素材）線 34 與 39 之 U_a 座標符號模式全同而承載相反 ⟹ 符號模式不能決定判準',
          p34 == p39 and (34 in set(nz22)) != (39 in set(nz22)),
          'SP(34) = %s (承載 %s) ; SP(39) = %s (承載 %s)' % (p34, 34 in set(nz22), p39, 39 in set(nz22)))
    MIX = {a: (len(set(lidx(v) for v in Vset[a])) > 1) for a in HT}
    HAS = {a: any(lidx(cross3(U[a], v)) != lidx(v) for v in Vset[a]) for a in HT}
    claim('N7-c', '★★（校正律；N3/N5 之修正，已見 N5 樣本）HAS ⟺ V(a) 之 ℓ 混合 ⟺ 8 線 {37,38,39,40,41,42,43,44} ∪ {49,50,51,52,53,54,55,56}',
          all(HAS[a] == MIX[a] for a in HT) and
          sorted(set(a for a in HT if MIX[a])) == [37, 38, 39, 40, 41, 42, 43, 44, 49, 50, 51, 52, 53, 54, 55, 56],
          'HAS==MIX = %s ; 混合欄 = %s ; 其中非承載 = %s'
          % (all(HAS[a] == MIX[a] for a in HT), sorted(set(a for a in HT if MIX[a])),
             sorted(set(a for a in HT if MIX[a]) & set(nec8))))

    # ================= Part O（第二批）：逐欄恆零清單 =================
    zero_cols = sorted(a for a in La if all(La[a][s0] == 0 for s0 in range(n)))
    nzc_cols = sorted(a for a in La if a not in set(zero_cols))
    lines_z = sorted(set(min(a, partner[a]) for a in zero_cols))
    claim('O5', '★（量測）62 欄之逐欄貢獻 Λ_a 之恆零清單（及其所屬線）', True,
          '恆零欄 = %s（%d 欄，%d 線）; 非恆零欄數 = %d' % (zero_cols, len(zero_cols), len(lines_z), len(nzc_cols)))
    perline = {}
    for a in La:
        L = min(a, partner[a])
        perline.setdefault(L, []).append(a in set(zero_cols))
    claim('O6-c', '★★（校正猜想，已見 39 之樣本）每線之兩欄：承載線兩欄皆非恆零；非承載線恰一欄恆零',
          all((any(perline[L]) if L in set(nec8) else not any(perline[L])) and
              (sum(perline[L]) == 1 if L in set(nec8) else sum(perline[L]) == 0) for L in perline),
          '逐線（線, 兩欄是否恆零, 承載）= %s' % [(L, perline[L], L in set(nz22)) for L in sorted(perline)])
    Zsum = sorted(set(sum(1 for a in La if La[a][s0] == 0) for s0 in range(n)))
    claim('O7', '★（量測）逐態「貢獻為零之欄數」分佈；Z10 之該值', True,
          '分佈 = %s ; Z10 之值 = %s' % (Zsum, sorted(set(sum(1 for a in La if La[a][s0] == 0) for s0 in Z10))))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R18 機器' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/64_r18_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'nec8': nec8, 'nz22': nz22,
                   'N': {'SP': {str(a): SP[a] for a in SP}, 'LX': {str(a): LX[a] for a in LX},
                         'NZ': {str(a): NZ[a] for a in NZ}},
                   'H': H, 'Z10': Z10, 'pairrel': pairrel, 'zero_cols': zero_cols,
                   'perline': {str(k): v for k, v in perline.items()}},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
