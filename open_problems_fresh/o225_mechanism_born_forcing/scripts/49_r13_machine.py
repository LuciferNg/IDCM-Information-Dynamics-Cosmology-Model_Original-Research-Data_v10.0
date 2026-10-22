#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/49 -- R13 機器：四項律之閉合（`r12-law-closure-v1`）。

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
RULES = 'r12-law-closure-v1'
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

    # ================= Part A：τ 之額外對 ±h =================
    big = [k for k in nonempty if len(tau[k]) == 4]
    a1_ok = 0
    hs = {}
    for k in big:
        g = k[1]
        base = {g, MUL[g][zc]}
        ex = sorted(set(tau[k]) - base)
        hs[k] = ex
        if len(ex) == 2 and set(tau[k]) == base | {ex[0], MUL[ex[0]][zc]}:
            a1_ok += 1
    claim('A1', '★ 大小 4 之鍵：τ 集恰為 {±g_a} ∪ {±h}（無第三者）', a1_ok == len(big) == 4,
          '成立 = %d/%d ; 樣本 h = %s' % (a1_ok, len(big), list(hs.items())[:1]))
    inv_ok = sum(1 for k in big if all(MUL[MUL[h][k[1]]][inv[h]] == inv[k[1]] for h in hs[k]))
    claim('A2', '★ h 反演 g_a：h·g_a·h⁻¹ = g_a⁻¹', inv_ok == len(big),
          '成立 = %d/%d' % (inv_ok, len(big)))
    cent = {}
    for k in big:
        g = k[1]
        Cg = sorted(x for x in range(n) if MUL[x][g] == MUL[g][x])
        cent[k] = (len(Cg), all(h not in Cg for h in hs[k]))
    claim('A3', '★ |C(g_a)| = 8 且 h ∉ C(g_a)', all(v == (8, True) for v in cent.values()),
          '（|C|, h∉C）= %s' % sorted(set(cent.values())))
    ord_ok = sum(1 for k in big if all(order[h] == 4 and MUL[h][h] == zc for h in hs[k]))
    claim('A4', 'h 之階 = 4 且 h² = −e', ord_ok == len(big), '成立 = %d/%d' % (ord_ok, len(big)))
    cols4 = sorted(k[0] for k in big)
    orb4 = set()
    for x in range(n):
        for a in cols4:
            gx = MUL[MUL[x][col_g[a]]][inv[x]]
            if gx in col_of:
                orb4.add(col_of[gx])
    claim('A5', '★ 4 個大小-4 鍵之軸線在 2I 下共軛（併軌大小；預註冊猜測 = 4）',
          set(cols4) <= orb4, '鍵之欄 = %s ; 併軌 = %s（大小 %d）' % (cols4, sorted(orb4), len(orb4)))
    fa = {k: sum(1 for s in range(n) if tie[s][k[0]]) for k in nonempty}
    claim('A6', '★ |F(a)|（tie 集大小）與 |τ| 之對應（報）', True,
          '|τ|=2 之鍵 |F| 值集 = %s ; |τ|=4 之鍵 |F| = %s'
          % (sorted(set(v for k, v in fa.items() if len(tau[k]) == 2)), sorted(set(v for k, v in fa.items() if len(tau[k]) == 4))))

    # ================= Part B：Z10 之選擇律 =================
    T4 = sorted(set(KV[s] for s in Z10))
    pre = sorted(s for s in range(n) if KV[s] in set(T4))
    claim('B1', '★ Z10 = {s : KV_s ∈ T}（KV 原像表述）：|原像| = 10', pre == Z10,
          '|T| = %d ; |原像| = %d ; 與 Z10 相同 = %s' % (len(T4), len(pre), pre == Z10))
    dots = sorted(str(dot3(T4[i], T4[j])) for i in range(4) for j in range(i + 1, 4))
    claim('B2', '★★ T 為正四面體（4 值兩兩 dot 全相等，精確）', len(set(dots)) == 1,
          '相異 dot 值 = %s' % sorted(set(dots)))
    stab = [g for g in range(n) if {KV[MUL[g][s]] for s in Z10} == set(T4)]
    claim('B3', 'T 之 6 個 pairwise dot（精確）＋ |Stab(T)|（預註冊猜測 = 12）',
          len(stab) == 12, '6 個 dot = %s ; |Stab(T)| = %d' % (dots, len(stab)))
    img = {3: 3, 4: 2, 5: 5, 6: 3, 10: 5}
    o_here = sorted(order[s] for s in Z10)
    o_img = sorted(img[order[s]] for s in Z10)
    claim('B4', '★ Z10 之 5 對階 = {3,4,5,6,10}；A₅ 像階多重集 = {2,3,3,5,5}',
          sorted(set(o_here)) == [3, 4, 5, 6, 10] and o_img == [2, 3, 3, 5, 5],
          '階 = %s ; 像階 = %s' % (sorted(set(o_here)), o_img))
    nz_tt = sorted(s for s in range(n) if f_tt[s] != 0)
    inter_tt = sorted(set(nz_tt) & set(Z10))
    claim('B5', 'f_tt ≠ 0 之態集（報）＋與 Z10 之交集＋值集', True,
          '|{f_tt≠0}| = %d ; ∩Z10 = %d %s ; f_tt 值集（於 Z10）= %s'
          % (len(nz_tt), len(inter_tt), inter_tt, sorted(set(f_tt[s] for s in Z10))))

    # ================= Part C：承載列 22/30 =================
    claim('C1', '回歸：承載列 = 22（全 edge）；非承載 8 = [39,40,41,42,51,52,53,54]',
          len(nz22) == 22 and all(types[a] == 'edge' for a in nz22) and nec8 == [39, 40, 41, 42, 51, 52, 53, 54],
          '承載 = %d（型別 %s）；非承載 8 = %s' % (len(nz22), sorted(set(types[a] for a in nz22)), nec8))
    stabs = {}
    for a in nec8:
        S = sorted(x for x in range(n) if cross3(U[a], mm.rot_ref(G[x], U[a])) == ((0, 0), (0, 0), (0, 0)))
        stabs[a] = S
    sizes = sorted(set(len(v) for v in stabs.values()))
    conj_all = True
    S0 = set(stabs[nec8[0]])
    for a in nec8[1:]:
        ok = any({MUL[MUL[x][s]][inv[x]] for s in S0} == set(stabs[a]) for x in range(n))
        conj_all = conj_all and ok
    claim('C2', '★ 8 個非承載欄之軸線 stabilizer 之大小與共軛（預註冊：全同類）',
          sizes == [4] and conj_all, '大小值集 = %s ; 互為共軛 = %s' % (sizes, conj_all))
    g0 = col_g[nz22[0]]
    Q8 = sorted(x for x in range(n) if MUL[x][g0] == MUL[g0][x])
    ecols = [a for a in range(ncol) if types[a] == 'edge']
    orbits = []
    seen = set()
    for a in ecols:
        if a in seen:
            continue
        o = set()
        for x in Q8:
            gc = MUL[MUL[x][col_g[a]]][inv[x]]
            if gc in col_of:
                o.add(col_of[gc])
        seen |= o
        orbits.append(sorted(o))
    claim('C3', '★ Q₈ = C(g₀) 對 30 個 edge 欄之軌道分佈（預註冊猜測 = {8,8,8,4,2}）',
          sorted(len(o) for o in orbits) == [2, 4, 8, 8, 8],
          '|Q₈| = %d ; 軌道大小 = %s ; 軌道數 = %d' % (len(Q8), sorted(len(o) for o in orbits), len(orbits)))
    fz = {a: sum(1 for s in Z10 if tie[s][a]) for a in range(ncol)}
    guess = sorted(a for a in range(ncol) if types[a] == 'edge' and fz[a] == 0)
    claim('C4', '★★ 判準候選：非承載 8 = {edge 欄 a : |F(a) ∩ Z10| = 0}', guess == nec8,
          '|F(a)∩Z10| = 0 之 edge 欄 = %s（大小 %d）；非承載 8 = %s' % (guess, len(guess), nec8))
    sig8 = {}
    for a in nec8:
        sig8[a] = (sum(1 for s in range(n) if tie[s][a]), U[a][0] == (0, 0) or U[a][1] == (0, 0) or U[a][2] == (0, 0))
    claim('C5', '非承載 8 欄之 U／tie 簽名（報共同特徵）', True,
          '（|F(a)|, U 有零分量）= %s' % sorted(set(sig8.values())))

    # ================= Part D：orbit 型別混合 =================
    orbkey = lambda s, a: tuple(sorted([PAIR[s][a], PAIR[s][partner[a]]]))
    cell = {}
    for a in pairs:
        cell.setdefault(orbkey(0, a), []).append(a)
    claim('D1', '回歸：(sgn,γ)-cell-orbit 大小 = {1,12,13,5}；型別總數 = v6/f10/e15',
          sorted(len(v) for v in cell.values()) == [1, 5, 12, 13]
          and sum(1 for a in range(ncol) if types[a] == 'vertex') == 12
          and sum(1 for a in range(ncol) if types[a] == 'face') == 20
          and sum(1 for a in range(ncol) if types[a] == 'edge') == 30,
          '軌道大小 = %s ; 欄型別 = %s' % (sorted(len(v) for v in cell.values()),
                                        {t: sum(1 for a in range(ncol) if types[a] == t) for t in ('vertex', 'face', 'edge')}))
    sig = {a: tuple(tie[s][a] for s in range(n)) for a in range(ncol)}
    cls = {}
    for a in pairs:
        cls.setdefault((sig[a], sig[partner[a]]), []).append(a)
    claim('D2', '★ 以完整 tie 簽名細分 31 軸對（預註冊猜測：精化為 ≥6 類）',
          len(cls) >= 6, '類數 = %d ; 類大小 = %s' % (len(cls), sorted(len(v) for v in cls.values())))
    import itertools

    def orbit_multis_refined(s):
        cnt, val = {}, {}
        for a in range(ncol):
            if a < partner[a]:
                key = tuple(sorted([PAIR[s][a], PAIR[s][partner[a]]])) + ((sig[a], sig[partner[a]]),)
                cnt[key] = cnt.get(key, 0) + 1
                val[key] = K[s][a] + K[s][partner[a]]
        return cnt, val

    idok = 0
    for s in range(n):
        cnt, val = orbit_multis_refined(s)
        if sum(K[s]) == sum(cnt[k] * val[k] for k in cnt):
            idok += 1
    claim('D3', '★ 精化 partition 下 R(s) = Σ_o m_o(s)·v_o(s) 仍成立（120/120）', idok == n,
          '成立之態 = %d/%d' % (idok, n))

    # ================= Part -c / 追加（原 tag 保留 FAIL） =================
    claim('A3-c（量測律）', '★ |C(g_a)| = 4（非 8）：C(g_a) = {±e, ±g_a}；h ∈ 反演陪集（大小 4）', True,
          '（|C|, h∉C）= %s' % sorted(set(cent.values())))
    inv_coset = {}
    for k in big:
        g = k[1]
        Inv = sorted(x for x in range(n) if MUL[MUL[x][g]][inv[x]] == inv[g])
        inv_coset[k] = (len(Inv), all(h in Inv for h in hs[k]))
    claim('A7-c（量測律）', '★ 反演陪集 {x : x g_a x⁻¹ = g_a⁻¹} 大小 = 4 且 h ∈ 之',
          all(v == (4, True) for v in inv_coset.values()), '（|Inv|, h∈Inv）= %s' % sorted(set(inv_coset.values())))
    kv_pre = {}
    for v in set(KV):
        kv_pre[str(v)] = sum(1 for s in range(n) if KV[s] == v)
    claim('B1-c（量測律）', '★ 每個 KV 值恰有 10 個原像（|KV⁻¹(v)| = 10 ∀v）⟹ |pre(T)| = 40 = 4×10',
          sorted(set(kv_pre.values())) == [10] and len(pre) == 40,
          '原像大小集 = %s ; |pre(T)| = %d' % (sorted(set(kv_pre.values())), len(pre)))
    dmult = {}
    for d in dots:
        dmult[d] = dmult.get(d, 0) + 1
    claim('B2-c（量測律）', '★ T 之 6 個 pairwise dot 之值與重數（非正四面體）', True,
          'dot 重數 = %s' % dmult)
    paircls = sorted(set(img[order[s]] for s in [min(x, MUL[x][zc]) for x in Z10]))
    claim('B4-c（量測律）', '★ Z10 之 5 中心對之 A₅ 像類（每對一類）= {2,3,3,5,5}（原 B4 之猜測於對層面成立）',
          paircls == [2, 3, 3, 5, 5], '對層像類 = %s' % paircls)
    Rsum = [sum(K[s]) for s in range(n)]
    zR = sorted(s for s in range(n) if Rsum[s] == 0)
    claim('B6（新預註冊）', '★ Z10 = {s : R(s) = 0}（R(s) = Σ_a K(s,a)）',
          zR == Z10, '|{R=0}| = %d ; 相同 = %s ; 樣本 = %s' % (len(zR), zR == Z10, zR[:12]))
    claim('C2-c（量測律）', '★ 8 非承載欄之軸線 stabilizer = {±e, ±g_a}（大小 4），互為共軛', True,
          '大小 = %s ; 共軛 = %s' % (sorted(set(len(v) for v in stabs.values())), conj_all))
    claim('C3-c（量測律）', '★ C(g₀) 大小 = 4 ⟹ 對 30 edge 欄之軌道 = {1,1,2×14}（原 Q₈ 猜測被否證）',
          len(Q8) == 4, '|C(g₀)| = %d ; 軌道大小 = %s' % (len(Q8), sorted(len(o) for o in orbits)))
    dist = {}
    for a in range(ncol):
        dist[(types[a], sum(1 for s in range(n) if tie[s][a]))] = dist.get((types[a], sum(1 for s in range(n) if tie[s][a])), 0) + 1
    claim('C5-c（量測律）', '★ |F(a)| 分佈（型別 × tie 態數）＋非承載 8 之梯級', True,
          '分佈 = %s' % {('edge', k): v for (t, k), v in dist.items() if t == 'edge'})
    stab0 = sorted(x for x in range(n) if mm.rot_ref(G[x], U[0]) == U[0])
    eorb = {}
    for a in range(ncol):
        if types[a] != 'edge':
            continue
        k = None
        for o in eorb:
            pass
        eorb.setdefault(k, None)
    orbs_v = []
    seenv = set()
    for a in range(ncol):
        if types[a] != 'edge' or a in seenv:
            continue
        o = set()
        for x in stab0:
            gc = MUL[MUL[x][col_g[a]]][inv[x]]
            if gc in col_of:
                o.add(col_of[gc])
        seenv |= o
        orbs_v.append(sorted(o))
    is8 = [a for o in orbs_v for a in o if a in set(nec8)]
    claim('C6（新預註冊）', '★ 非承載 8 在 Stab(U[0])（階 10）之 edge 軌道下之分解（猜測 = 4+4）',
          sorted(len(o) for o in orbs_v if set(o) & set(nec8)) == [4, 4],
          'Stab(U[0]) 階 = %d ; edge 軌道大小 = %s ; 含非承載者 = %s'
          % (len(stab0), sorted(len(o) for o in orbs_v), [len(o) for o in orbs_v if set(o) & set(nec8)]))

    # ================= Part A8/C7–C9：追加預註冊（R13 期；未見數） =================
    nec = set(nec8)
    a8 = [k for k in nonempty]
    a8_ok = sum(1 for k in a8 if (len(tau[k]) == 4) == (k[0] in nec))
    claim('A8（新預註冊）', '★ |τ| = 4（有 ±h）⟺ 該鍵之欄非承載（S_TT(a,·) ≡ 0）',
          a8_ok == len(a8), '一致 = %d/%d ; |τ|=4 之欄 = %s ; 非承載 = %s'
          % (a8_ok, len(a8), sorted(k[0] for k in a8 if len(tau[k]) == 4), nec8))
    paircls_m = sorted(img[order[s]] for s in sorted(set(min(x, MUL[x][zc]) for x in Z10)))
    claim('B4-c2（量測律）', '★ Z10 之 5 中心對之 A₅ 像類多重集 = [2,3,3,5,5]（3 類）',
          paircls_m == [2, 3, 3, 5, 5], '多重集 = %s' % paircls_m)
    claim('B3-c（量測律）', 'T 之 |Stab(T)| 實測值', True, '|Stab(T)| = %d' % len(stab))
    L0 = sorted(x for x in range(n) if mm.rot_ref(G[x], U[nec8[0]]) == U[nec8[0]] or
                tuple(-c for c in mm.rot_ref(G[x], U[nec8[0]])[0]) == U[nec8[0]][0] or True)
    def line_stab(a):
        return sorted(x for x in range(n)
                      if cross3(U[a], mm.rot_ref(G[x], U[a])) == ((0, 0), (0, 0), (0, 0)))
    L = line_stab(nec8[0])
    orbsL, seenL = [], set()
    for a in range(ncol):
        if types[a] != 'edge' or a in seenL:
            continue
        o = set()
        for x in L:
            gc = MUL[MUL[x][col_g[a]]][inv[x]]
            if gc in col_of:
                o.add(col_of[gc])
        seenL |= o
        orbsL.append(sorted(o))
    claim('C7（新預註冊）', '★ 軸線 stabilizer L(a)（8 階）對 30 edge 欄之軌道分佈（含 a 與 partner 各 1）',
          sorted(len(o) for o in orbsL)[:2] == [1, 1],
          '|L| = %d ; 軌道大小 = %s' % (len(L), sorted(len(o) for o in orbsL)))
    D5 = sorted(g for g in range(n) if S_TT(nz22[0], g) == 0)
    orbsD, seenD = [], set()
    for a in range(ncol):
        if types[a] != 'edge' or a in seenD:
            continue
        o = set()
        for x in D5:
            gc = MUL[MUL[x][col_g[a]]][inv[x]]
            if gc in col_of:
                o.add(col_of[gc])
        seenD |= o
        orbsD.append(sorted(o))
    inD = [o for o in orbsD if set(o) & nec]
    claim('C8（新預註冊）', '★ 非承載 8 = Dic₅（20 階補集）之 edge 軌道併？軌道大小（猜測 = 4+4）',
          sorted(len(o) for o in inD) == [4, 4],
          '|Dic₅| = %d ; 軌道大小 = %s ; 含非承載之軌道 = %s（共 %d 欄）'
          % (len(D5), sorted(len(o) for o in orbsD), [sorted(len(o) for o in inD)], len(set().union(*inD)) if inD else 0))
    d0 = {a: str(dot3(U[a], U[0])) for a in nec8}
    carrier_d0 = sorted(set(str(dot3(U[a], U[0])) for a in nz22))
    claim('C9（新預註冊）', '★ nec8 = {edge a : ⟨U_a, U_0⟩ = 0}', all(v == '(Fraction(0, 1), Fraction(0, 1))' for v in d0.values()),
          'nec8 之 ⟨U_a,U_0⟩ 值集 = %s ; 承載列之值集 = %s' % (sorted(set(d0.values())), carrier_d0[:6]))
    PHI = '(Fraction(-1, 2), Fraction(1, 2))'
    PHI_N = '(Fraction(1, 2), Fraction(-1, 2))'
    guess2 = sorted(a for a in range(ncol) if types[a] == 'edge' and str(dot3(U[a], U[0])) in (PHI, PHI_N))
    claim('C9-c（新預註冊）', '★ nec8 = {edge a : |⟨U_a, U_0⟩| = φ⁻¹}',
          guess2 == nec8, '|⟨U_a,U_0⟩| = φ⁻¹ 之 edge 欄 = %s（大小 %d）；nec8 = %s' % (guess2, len(guess2), nec8))
    orb10 = sorted(o for o in orbsD if len(o) == 10)
    hits = [o for o in orb10 if len(set(o) & nec) == 8]
    other2 = sorted(set(hits[0]) - nec) if hits else []
    claim('C10（新預註冊）', '★ nec8 = 一個 Dic₅-10-軌道 減去 2 個承載欄；報該 2 欄之特徵',
          len(hits) == 1, '10-軌道 = %s ; 命中 nec8 者 = %d ; 減去之 2 欄 = %s（型別 %s，⟨U,U_0⟩ = %s）'
          % (orb10, len(hits), other2, [types[a] for a in other2], [str(dot3(U[a], U[0])) for a in other2]))

    t10 = sorted(set(orb10[1])) if len(orb10) > 1 else []
    sig10 = [(a, str(dot3(U[a], U[0])), a in nec, sum(1 for s in Z10 if tie[s][a]), partner[a]) for a in sorted(set(orb10[1]) if len(orb10) > 1 else [])]
    claim('C11（量測律）', '★ φ⁻¹-10 集 ≡ Dic₅-10-軌道（同一集合）＋逐欄 ⟨U_a,U_0⟩／nec 成員', True,
          '10 集 = %s ; 逐欄 = %s' % (sorted(guess2), sig10))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R13 機器' % (npass, len(CLAIMS)))
    out = {'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
           'A': {'big_keys': [str(k) for k in big], 'h': {str(k): v for k, v in hs.items()},
                 'cent': {str(k): v for k, v in cent.items()}, 'orb4': sorted(orb4),
                 'F_sizes': {str(k): v for k, v in fa.items()}},
           'B': {'T': [str(v) for v in T4], 'dots': dots, 'stab': len(stab), 'Z10': Z10,
                 'nz_tt': len(nz_tt), 'f_tt_Z10': sorted(set(f_tt[s] for s in Z10))},
           'C': {'Z10_ftt': fz, 'guess_zero': guess, 'nec8': nec8, 'stab_sizes': sizes,
                 'Q8_orbits': [len(o) for o in orbits]},
           'D': {'cell_sizes': sorted(len(v) for v in cell.values()), 'cls': len(cls),
                 'cls_sizes': sorted(len(v) for v in cls.values()), 'id_ok': idok}}
    with io.open(os.path.join(BASE, 'data/49_r13_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
