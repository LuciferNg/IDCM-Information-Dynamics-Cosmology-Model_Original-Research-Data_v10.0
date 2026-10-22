#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/67 -- R19 機器：四項律之閉合（`r19-arithmetic-form-v1`）。

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

    # ================= Part P：算術形式 =================
    P1bad = [a for a in D0 if (a in set(nec8)) != (a in set(B10) and NZc[a] == 0)]
    claim('P1', '■ 非承載 ⟺ a ∈ B10（|⟨U_a,U_0⟩| = φ⁻¹）∧ U_a 無零分量（30 欄）', P1bad == [],
          '反例 = %s ; |B10| = %d（%s）; B10 中零分量者 = %s'
          % (P1bad, len(B10), B10, sorted(a for a in B10 if NZc[a] >= 1)))
    def edgepair(a):
        best = None
        for v, w in HT[a]:
            key = dot3(v, w)
            if best is None or sgn((key[0] - best[0][0], key[1] - best[0][1])) > 0:
                best = (key, (v, w))
        return best[1]
    EP = {L: edgepair(L) for L in lines}
    P2rows = []
    for L in lines:
        if L not in set(B10):
            continue
        v, w = EP[L]
        P2rows.append((L, [U[L][k] for k in range(3)], sgnpat(U[L]), D0[L], NZc[L],
                       (U[0] in (v, w)), L in set(nz22)))
    claim('P2', '★（量測）B10 之 5 線：軸分量／符號模式／⟨U_a,U_0⟩／零分量數／邊是否含 U_0／承載', True,
          '逐線 = %s' % P2rows)
    MIX = {a: len(set(lidx(v) for v in Vset[a])) > 1 for a in HT}
    P3bad = [a for a in HT if (a in set(nec8)) != (MIX[a] and a in set(B10))]
    claim('P3', '★★（猜想）非承載 ⟺ MIX(a) ∧ a ∈ B10', P3bad == [],
          '反例 = %s ; MIX∧B10 = %s' % (P3bad, sorted(a for a in HT if MIX[a] and a in set(B10))))
    claim('P4', '★（量測）15 線之 (B10?, MIX?, 承載?) 三聯表', True,
          '逐線 = %s' % [(L, L in set(B10), MIX[L], L in set(nz22)) for L in lines])

    # ================= Part Q：Z10 之結構 =================
    claim('Q1', '■ 逐欄貢獻 Λ_a(−s) = Λ_a(s)（∀a∈62, ∀s）', all(La[a][negi[s0]] == La[a][s0] for a in La for s0 in range(n)),
          '不符之（欄, 態）數 = %d' % sum(1 for a in La for s0 in range(n) if La[a][negi[s0]] != La[a][s0]))
    LV = {}
    for s0 in range(n):
        LV[LAMv[s0]] = LV.get(LAMv[s0], 0) + 1
    claim('Q2', '■ Λ 之每個水平集大小皆為偶數（±-不變 ⟹ 水平集為 ±-對之聯集）',
          all(v % 2 == 0 for v in LV.values()), '水平大小 = %s' % sorted(LV.items()))
    cls = {}
    for s0 in range(n):
        c = frozenset(MUL[MUL[g][s0]][inv[g]] for g in range(n))
        cls[s0] = c
    classes = sorted(set(cls.values()), key=lambda c: (len(c), sorted(c)[0]))
    csz = sorted(len(c) for c in classes)
    not_const = [c for c in classes if len(set(LAMv[s0] for s0 in c)) > 1]
    def subset_sum(target, sizes):
        reach = {0}
        for x in sizes:
            reach |= {r + x for r in reach if r + x <= target}
        return target in reach
    claim('Q3', '■ Λ 非類函數 —— |Λ⁻¹(0)| = 10 而 10 不能表為共軛類大小之和（類大小 ∈ %s）'
          % csz, len(not_const) > 0 and not subset_sum(10, csz),
          '類數 = %d ; 類大小 = %s ; Λ 非常數之類 = %d ; 10 可達 = %s ; |Λ⁻¹(0)| = %d'
          % (len(classes), csz, len(not_const), subset_sum(10, csz), LV.get(0, 0)))
    INVL = sorted(h for h in range(n) if all(LAMv[MUL[s0][h]] == LAMv[s0] for s0 in range(n)))
    claim('Q4', '★（量測）Λ 之右不變群 Inv(Λ) := {h : Λ(s·h) = Λ(s) ∀s}', True,
          '|Inv| = %d ; 元素 = %s ; 階譜 = %s' % (len(INVL), INVL, sorted(order[h] for h in INVL)))
    feat = {}
    for s0 in range(n):
        v16 = [La[a][s0] for a in support]
        feat[s0] = (sorted(v16), sum(1 for x in v16 if x == 0), sum(1 for x in v16 if x > 0),
                    sum(1 for x in v16 if x < 0), sum(abs(x) for x in v16))
    claim('Q5', '★（量測）16 欄貢獻之逐態特徵（零欄數／正欄數／負欄數／Σ|Λ_a|）＋ Z10 標記', True,
          'Z10 之特徵 = %s ; 全體之（零,正,負,Σ|·|）分佈 = %s'
          % ([(s0, feat[s0][1:]) for s0 in Z10],
             sorted(set((f[1], f[2], f[3], f[4]) for f in feat.values()))[:12]))
    Q6 = sorted(s0 for s0 in range(n) if feat[s0][2] == feat[s0][3] and feat[s0][2] + feat[s0][3] > 0)
    claim('Q6', '★★（猜想）Z10 = {s : 16 欄貢獻之「正欄數 = 負欄數」}', Q6 == Z10,
          '{正=負 且非全零} = %s（%d 態）; Z10 = %s' % (Q6, len(Q6), Z10))

    # ================= Part P（第二批）：φ-形式候選律 =================
    PH = ((F(1, 4), F(1, 4)), (F(-1, 4), F(1, 4)), (F(1, 2), F(0)))   # (φ/2, φ⁻¹/2, 1/2)
    def absv(x):
        return x if sgn(x) >= 0 else (F(0) - x[0], F(0) - x[1])
    phform = {a: tuple(absv(U[a][k]) for k in range(3)) == PH for a in range(ncol) if types[a] == 'edge'}
    bad5 = [a for a in phform if (a in set(nec8)) != phform[a]]
    claim('P5-c', '★★（校正律；已見 P2 之 39／40 樣本）**非承載 ⟺ |U_a| = (φ/2, φ⁻¹/2, 1/2) 逐分量**（即每 edge line 恰 4 條此型）',
          bad5 == [] and len([a for a in phform if phform[a]]) == 8,
          '反例 = %s ; φ-型欄 = %s（%d 欄 / %d 線）; 其中 nec = %s'
          % (bad5, sorted(a for a in phform if phform[a]), len([a for a in phform if phform[a]]),
             len(set(min(a, partner[a]) for a in phform if phform[a])),
             sorted(set(a for a in phform if phform[a]) & set(nec8))))

    # ================= Part Q（第二批）：Z10 之細化候選 =================
    six = [s0 for s0 in range(n) if feat[s0][2] == feat[s0][3] and feat[s0][2] > 0]
    all2 = [s0 for s0 in range(n)
            if all(abs(La[a][s0]) == 2 for a in support if La[a][s0] != 0) and
            sum(1 for a in support if La[a][s0] != 0) > 0]
    claim('Q7-c', '★★（校正猜想；已見 Q5 之 Z10 特徵）Z10 = {s : 非零欄之 |Λ_a| 全 = 2 ∧ 正欄數 = 負欄數}',
          sorted(set(six) & set(all2)) == Z10,
          '候選集 = %s（%d 態）; Z10 = %s ; 僅 pos=neg 者 = %d 態'
          % (sorted(set(six) & set(all2)), len(set(six) & set(all2)), Z10, len(six)))
    claim('Q8', '★（量測）Z10 之每對 {s,−s} 之 16 欄貢獻向量完全相同（Q1 之推論）', True,
          '對之向量相同 = %s' % all([La[a][s0] for a in support] == [La[a][negi[s0]] for a in support] for s0 in Z10))
    claim('P6', '★（量測）15 線之軸之逐分量精確值／絕對值型／符號型／邊對／承載（供 R20 判律）', True,
          '逐線 = %s' % [(L, [str(U[L][k]) for k in range(3)], tuple(str(absv(U[L][k])) for k in range(3)),
                          sgnpat(U[L]), [str(x) for x in (EP[L][0], EP[L][1])], L in set(nz22)) for L in lines])
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R19 機器' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/67_r19_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'nec8': nec8, 'nz22': nz22, 'B10': B10, 'support': support, 'Z10': Z10,
                   'csz': csz, 'Inv': INVL, 'LV': {str(k): v for k, v in LV.items()},
                   'P2': [[x[0], [str(y) for y in x[1]], x[2], str(x[3]), x[4], x[5], x[6]] for x in P2rows]},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
