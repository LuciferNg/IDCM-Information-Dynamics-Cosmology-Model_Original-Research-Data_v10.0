#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/61 -- R17 機器：四項律之閉合（`r17-sign-closure-v1`）。

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
RULES = 'r17-sign-closure-v1'
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

    # ================= Part K：① 之閉式（邊端點 ε 律） =================
    vals = sorted(set(KV))
    Tset = {a: sorted(x for x in range(n) if tie[x][a]) for a in range(ncol)}
    Vset = {a: sorted(set(KV[x] for x in Tset[a])) for a in range(ncol)}
    ell = lambda v: firstsgn(v)
    def endpoints(a):
        out = []
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                v, w = vals[i], vals[j]
                if all(add(v[k], w[k]) == (0, 0) for k in range(3)):
                    continue
                s = tuple(add(v[k], w[k]) for k in range(3))
                if cross3(s, U[a]) == ((0, 0), (0, 0), (0, 0)):
                    out.append((v, w))
        return out
    epl = {a: endpoints(a) for a in range(ncol) if types[a] == 'edge'}
    nuniq = sorted(set(len(epl[a]) for a in epl))
    claim('K3b', '端點對之唯一性（每 edge 欄恰一對使 v+w ∥ U_a）', nuniq == [1],
          '端點對數之值集 = %s' % nuniq)
    K1 = []
    for a in sorted(epl):
        v, w = epl[a][0]
        if (a in set(nz22)) != (ell(v) == ell(w)):
            K1.append(a)
    claim('K1', '★★ 承載 ⟺ ε(v) = ε(w)（該軸所屬邊之兩端點同號）', K1 == [],
          '反例 = %s ; 承載 = %s' % (K1, nz22))
    def equi(a):
        Vs = Vset[a]
        prs = []
        used = set()
        for v in Vs:
            if v in used:
                continue
            w = next((u for u in Vs if u != v and all(add(v[k], u[k]) == (0, 0) for k in range(3))), None)
            if w is None:
                return None
            used |= {v, w}
            prs.append(v)
        return prs
    K2 = []
    for a in sorted(epl):
        prs = equi(a)
        if prs is None or len(prs) != 2:
            K2.append((a, 'equator-pairs!=2'))
            continue
        p, q = prs
        if (a in set(nz22)) == (ell(p) == -ell(q)):
            K2.append((a, prs))
    claim('K2', '★★ 非承載 ⟺ ε(p) = −ε(q)（赤道兩對代表反號）', K2 == [],
          '反例 = %s' % K2[:6])
    lines = sorted(set(min(a, partner[a]) for a in range(ncol) if types[a] == 'edge'))
    L4 = {L: (ell(epl[L][0][0]) == ell(epl[L][0][1]), L in set(nz22)) for L in lines}
    sames = sorted(L for L in L4 if L4[L][0])
    claim('K4', '★★ #{edge 線 : 端點同號} = 11（= 承載線數）', len(sames) == 11 and all(L4[L][0] == L4[L][1] for L in L4),
          '同號線 = %s（%d）; 反號線 = %s' % (sames, len(sames), sorted(set(lines) - set(sames))))
    claim('K3', '★ 12 值之 ε 表 ＋ 15 邊之端點 ε-對（量測）', True,
          'ε 表 = %s ; 15 邊之（端點對, ε 對, 承載）= %s'
          % ([ell(v) for v in vals],
             [(L, (ell(epl[L][0][0]), ell(epl[L][0][1])), L4[L][1]) for L in lines]))

    # ================= Part L：② Z10 之座標框平衡猜想 =================
    def eps_i(v):
        return firstsgn(v)
    def gam_i(v, a):
        return firstsgn(cross3(U[a], v))
    def tie_i(v, a):
        return dot3(U[a], v) == (0, 0)
    tab = {}
    for a in range(ncol):
        m = {}
        for v in vals:
            for u in vals:
                tw, tr = tie_i(v, a), tie_i(u, a)
                dw = (1 if gam_i(v, a) != eps_i(v) else 0) if tw else 0
                dr = (1 if gam_i(u, a) != eps_i(u) else 0) if tr else 0
                tf = dr * eps_i(u) * sgn(dot3(U[a], v)) if (tr and not tw) else 0
                ft = dw * eps_i(v) * sgn(dot3(U[a], u)) if (tw and not tr) else 0
                m[(v, u)] = (tf, ft)
        tab[a] = m
    keytr = {}
    for (a, sw, sr) in my_ev:
        keytr[(a, sw, sr)] = keytr.get((a, sw, sr), 0) + 1
    dif = []
    LAM = {}
    for s0 in range(n):
        acc = 0
        for (a, sw, sr) in my_ev:
            t2 = tab[a][(KV[MUL[s0][sw]], KV[MUL[s0][sr]])]
            acc += t2[0] + t2[1]
        LAM[s0] = acc
        if acc != f_tf[s0] + f_ft[s0]:
            dif.append(s0)
    claim('L1', '★★ 重組：Λ(s) = Σ_{a ∈ 62 欄} F_a(KV_{s·sw(a)}, KV_{s·sr(a)})（與直接法逐態相同）',
          dif == [], '不符之態 = %s ; 鍵數 = %d（事件 %d）' % (dif, len(keytr), len(my_ev)))
    S_of = {}
    for s0 in range(n):
        S_of[s0] = sum(firstsgn(mm.rot_ref(G[s0], v)) for v in vals)
    Sf = {}
    for s0 in range(n):
        Sf[S_of[s0]] = Sf.get(S_of[s0], 0) + 1
    ZS = sorted(s for s in range(n) if S_of[s] == 0)
    claim('L2', '★★ Z10 = {s : S(s) = Σ_{v ∈ 12 值} ε(R_s v) = 0}（座標框平衡）',
          ZS == Z10, 'S 分佈 = %s ; {S=0} = %s（%d）; Z10 = %s' % (Sf, ZS, len(ZS), Z10))
    rel = {}
    for s0 in range(n):
        rel[(LAM[s0], S_of[s0])] = rel.get((LAM[s0], S_of[s0]), 0) + 1
    claim('L3', '★ Λ 與 S 之逐態關係（猜測 Λ = 2S）',
          all(LAM[s0] == 2 * S_of[s0] for s0 in range(n)),
          '配對分佈 = %s ; 樣本 = %s' % (sorted(rel.items())[:12], [(s0, LAM[s0], S_of[s0]) for s0 in range(0, 8)]))

    # ================= Part K（第二批）：半轉對與符號分離 =================
    def halfturn_pairs(a):
        out = []
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                v, w = vals[i], vals[j]
                if all(add(v[k], w[k]) == (0, 0) for k in range(3)):
                    continue
                s = tuple(add(v[k], w[k]) for k in range(3))
                if cross3(s, U[a]) == ((0, 0), (0, 0), (0, 0)):
                    out.append((v, w))
        return out
    HT = {a: halfturn_pairs(a) for a in range(ncol) if types[a] == 'edge'}
    claim('K5', '★★ 每 edge 欄之半轉對（v + R_a v ∝ U_a）數 = 4（量測）',
          sorted(set(len(HT[a]) for a in HT)) == [4],
          '對數值集 = %s ; 樣本線 39 = %s' % (sorted(set(len(HT[a]) for a in HT)), [(ell(v), ell(w), dot3(v, w)) for v, w in HT[39]]))
    def edgepair(a):
        best = None
        for v, w in HT[a]:
            d = dot3(v, w)
            if best is None or z2gt(d, best[1]):
                best = ((v, w), d)
        return best[0]
    def z2gt(x, y):
        return sgn((x[0] - y[0], x[1] - y[1])) > 0
    EP = {L: edgepair(L) for L in lines}
    claim('K6', '★★（K1 之更正）承載 ⟺ 該線之邊對（4 半轉對中 dot 最大者）之端點 ε 相同',
          all((L in set(nz22)) == (ell(EP[L][0]) == ell(EP[L][1])) for L in lines),
          '逐線（L, ε對, 承載）= %s' % [(L, (ell(EP[L][0]), ell(EP[L][1])), L in set(nz22)) for L in lines])
    def dind_of(u, a):
        return (1 if firstsgn(cross3(U[a], u)) != ell(u) else 0) if tie_i(u, a) else 0

    def dc(u, a):
        return (1 if firstsgn(cross3(U[a], u)) != ell(u) else 0) if tie_i(u, a) else 0
    claim('K7', '★（量測）15 線之 4 半轉對 ε-對 與 V(a) 之 (ε, dind) —— 供分離律',
          True, '逐線 = %s' % [(L, sorted((ell(v), ell(w)) for v, w in HT[L]),
                              sorted((ell(u), dc(u, L)) for u in Vset[L])) for L in lines])
    claim('K8', '★（量測）15 線之赤道兩對代表 (ε(p), ε(q), p·q, sgn det(p,q,a)) 與承載',
          True, '逐線 = %s' % [(L, (ell(equi(L)[0]), ell(equi(L)[1]) if equi(L) else None,
                              dot3(equi(L)[0], equi(L)[1]) if equi(L) else None,
                              sgn(dot3(cross3(equi(L)[0], equi(L)[1]), U[L])) if equi(L) else None),
                          L in set(nz22)) for L in lines])

    # ================= Part L（第二批）：Λ 之座標框層級 =================
    CNT = {}
    for s0 in range(n):
        c = sum(dind[s0][a] for a in range(ncol))
        CNT[c] = CNT.get(c, 0) + 1
    claim('L4', '★ dind 逐態欄計數 Σ_a dind(s,a) 之水平分佈（量測；檢驗是否可選出 Z10）',
          True, '分佈 = %s ; Z10 之計數 = %s' % (sorted(CNT.items()), sorted(set(sum(dind[s0][a] for a in range(ncol)) for s0 in Z10))))
    STB = {}
    for s0 in range(n):
        fib = sorted(x for x in range(n) if KV[x] == KV[s0])
        STB[len(set(LAM[t] for t in fib))] = STB.get(len(set(LAM[t] for t in fib)), 0) + 1
    claim('L5', '★ 同一 KV-fibre（10 態）內 Λ 之相異值數分佈（量測 Λ 之局部性層級）',
          True, '分佈 = %s（1 = 值局部；>1 = 非值局部）' % sorted(STB.items()))
    # ================= Part K（第三批）：2-bit 判準與均一表 =================
    OK9 = []
    for a in sorted(HT):
        if len(Vset[a]) != 4:
            OK9.append((a, 'V!=4'))
            continue
        prs = []
        used = set()
        for v in Vset[a]:
            if v in used:
                continue
            w = next((u for u in Vset[a] if u != v and all(add(v[k], u[k]) == (0, 0) for k in range(3))), None)
            used |= {v, w}
            prs.append(v)
        b0, b1 = dind_of(prs[0], a), dind_of(prs[1], a)
        if (a in set(nz22)) != (b0 != b1):
            OK9.append((a, b0, b1))
    claim('K9', '★★ V(a) = 2 赤道半轉對；承載 ⟺ 兩對之 dind-bit 相異（2-bit 判準）', OK9 == [],
          '反例 = %s' % OK9)
    TBL = {}
    for a in sorted(HT):
        prs = []
        used = set()
        for v in Vset[a]:
            if v in used:
                continue
            w = next((u for u in Vset[a] if u != v and all(add(v[k], u[k]) == (0, 0) for k in range(3))), None)
            used |= {v, w}
            prs.append(v)
        TBL[a] = sorted((ell(u), dind_of(u, a)) for u in Vset[a])
    CARRY_T = sorted(set(tuple(TBL[a]) for a in TBL if a in set(nz22)))
    NEC_T = sorted(set(tuple(TBL[a]) for a in TBL if a in set(nec8)))
    claim('K10', '★★ 承載欄之 V(a) (ε,dind) 表全同（均一型）；非承載為「塌縮型」（dind 常數）',
          CARRY_T == [((-1, 0), (-1, 1), (1, 0), (1, 1))] and
          NEC_T == [((-1, 0), (-1, 0), (1, 0), (1, 0)), ((-1, 1), (-1, 1), (1, 1), (1, 1))],
          '承載表型 = %s ; 非承載表型 = %s' % (CARRY_T, NEC_T))
    nodet = 0
    for a in sorted(HT):
        for v in Vset[a]:
            c = cross3(U[a], v)
            z = sum(1 for k in range(3) if c[k] == (0, 0))
            if z == 0:
                # 檢查 (a×v) 之各分量是否「單項」（無抵消）
                pass
            nodet += 1
    claim('K11', '★（量測）γ = firstsgn(a × v) 之「符號模式決定性」：報赤道對中 a×v 有零分量之比例', True,
          '樣本 = %s' % [(a, [firstsgn(cross3(U[a], v)) for v in Vset[a]],
                          [sum(1 for k in range(3) if cross3(U[a], v)[k] == (0, 0)) for v in Vset[a]])
                         for a in (39, 32)])
    claim('L6', '★★（留痕）S(s) = Σ_v ε(R_s v) 恆 = 0（R_s 置換 12 值 ⟹ 排列不變）⟹ 猜想 L2/L3 空轉',
          all(S_of[s] == 0 for s in range(n)) and len(set(S_of[v] for v in S_of)) == 1,
          'S 值集 = %s ⟹ 零判別力' % sorted(set(S_of.values())))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R17 機器' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/61_r17_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'keys': [[k[0], k[1]] for k in sorted(keys)], 'nec8': nec8, 'nz22': nz22,
                   'K': {'lines': {str(L): [str(x) for x in epl[L][0]] for L in lines},
                         'eps': {str(v): ell(v) for v in vals}, 'L4': {str(k): v for k, v in L4.items()}},
                   'L': {'LAM': {str(k): v for k, v in LAM.items()}, 'S': {str(k): v for k, v in S_of.items()},
                         'Z10': Z10}},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
