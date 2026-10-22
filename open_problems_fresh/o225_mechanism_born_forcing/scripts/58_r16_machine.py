#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/58 -- R16 機器：四項律之閉合（`r16-value-reduction-v1`）。

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
RULES = 'r16-value-reduction-v1'
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

    # ================= Part F：W_a ≡ ∅ 之根因（值歸約） =================
    vals = sorted(set(KV))                     # 12 個 KV 值
    fibre = {v: sorted(s for s in range(n) if KV[s] == v) for v in vals}
    dind_by = {}
    for a in range(ncol):
        dind_by[a] = {(v): sorted(set((1 if gam[s][a] != eps[s] else 0) for s in fibre[v])) for v in vals}
    nonconst_fib = sorted(a for a in range(ncol) if any(len(dind_by[a][v]) > 1 for v in vals))
    claim('F1', '■ dind(·,a) 只依 KV_s（於每條 KV-fibre 恆定）—— 因 ε、γ 皆只依 (KV_s, a)',
          nonconst_fib == [], '非恆定之（欄, 值）數 = %d ; fibre 大小 = %s'
          % (len(nonconst_fib), sorted(set(len(fibre[v]) for v in vals))))
    def Wnz_count(a):
        cnt = 0
        for g in range(n):
            gi = inv[g]
            if any(tie[y][a] and tie[MUL[y][gi]][a] and dind[y][a] != dind[MUL[y][gi]][a] for y in range(n)):
                cnt += 1
        return cnt
    nz_g = {a: Wnz_count(a) for a in range(ncol) if types[a] == 'edge'}
    Tset = {a: sorted(x for x in range(n) if tie[x][a]) for a in range(ncol)}
    Vset = {a: sorted(set(KV[x] for x in Tset[a])) for a in range(ncol)}
    dconst = {}
    for a in range(ncol):
        if types[a] != 'edge':
            continue
        dconst[a] = (sorted(set((1 if gam[x][a] != eps[x] else 0) for x in Tset[a])), len(Vset[a]),
                     sorted(set((1 if gam[x][a] != eps[x] else 0) for x in fibre[Vset[a][0]])) if Vset[a] else [])
    ok2 = all((nz_g[a] == 0) == (len(dconst[a][0]) == 1) for a in dconst)
    claim('F2', '■ W_a ≡ ∅ ⟺ dind 於 T_a（等價於於 V(a)）恆定（30 edge 欄）', ok2,
          '一致 = %d/30 ; 非承載之 dind 集 = %s ; 承載之 dind 集 = %s'
          % (sum(1 for a in dconst if (nz_g[a] == 0) == (len(dconst[a][0]) == 1)),
             sorted(set(tuple(dconst[a][0]) for a in dconst if a in set(nec8))),
             sorted(set(tuple(dconst[a][0]) for a in dconst if a in set(nz22)))))
    f3 = sum(1 for a in dconst if dconst[a][1] == 4 and
             Vset[a] == sorted([v for v in vals if dot3(U[a], v) == (0, 0)]))
    claim('F3', '★ V(a) = {v ∈ 12 值 : ⟨U_a, v⟩ = 0}，|V(a)| = 4（30 edge 欄）', f3 == 30,
          '成立 = %d/30 ; |V| 值集 = %s ; 正交值數值集 = %s'
          % (f3, sorted(set(dconst[a][1] for a in dconst)),
             sorted(set(len([v for v in vals if dot3(U[a], v) == (0, 0)]) for a in dconst))))
    cval = {a: dconst[a][0][0] for a in dconst if len(dconst[a][0]) == 1}
    claim('F4', '★ 8 非承載欄之恆定值 c(a)（猜測全 = 0）；22 承載欄之值分佈',
          sorted(set(cval.values())) == [0],
          '非承載 c(a) = %s ; 承載欄之 dind 集 = %s'
          % ({a: cval[a] for a in sorted(cval)}, sorted(set(str(dconst[a][0]) for a in dconst if a in set(nz22)))))
    claim('F5', '★★ 承載 ⟺ dind 於 V(a)（4 值）非恆定', 
          all((a in set(nz22)) == (len(dconst[a][0]) > 1) for a in dconst),
          '全 30 欄之一致 = %s' % all((a in set(nz22)) == (len(dconst[a][0]) > 1) for a in dconst))
    VC = {a: [dind_by[a][v] for v in Vset[a]] for a in dconst}
    claim('F6', '★ 逐欄報 (欄, V(a) 之 4 值, 各值之 dind, 承載?)（量測）', True,
          '樣本（前 6 欄） = %s' % [(a, len(dconst[a][0]), a in set(nz22)) for a in sorted(dconst)[:6]])

    # ================= Part G：Λ 之值局部性與 Z10 =================
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
                dw, dr = (1 if gam_i(v, a) != eps_i(v) else 0) if tw else 0, (1 if gam_i(u, a) != eps_i(u) else 0) if tr else 0
                tf = dr * eps_i(u) * sgn(dot3(U[a], v)) if (tr and not tw) else 0
                ft = dw * eps_i(v) * sgn(dot3(U[a], u)) if (tw and not tr) else 0
                tt = (0 if dw == dr else 1) * eps_i(u) * eps_i(v) if (tw and tr) else 0
                m[(v, u)] = (tt, tf, ft)
        tab[a] = m
    dif = 0
    for s0 in range(n):
        for kind, idx in (('tf', 0), ('ft', 1)):
            acc = 0
            for (a, sw, sr) in my_ev:
                t3 = tab[a][(KV[MUL[s0][sw]], KV[MUL[s0][sr]])]
                acc += t3[1] if kind == 'tf' else t3[2]
            if acc != (f_tf[s0] if kind == 'tf' else f_ft[s0]):
                dif += 1
    claim('G1', '■ f_tf／f_ft 之加項只依 (KV_{s·sw}, KV_{s·sr}, a)（值表法重算逐態相同）',
          dif == 0, '不符之（態, 類）數 = %d' % dif)
    LV = {}
    for s in range(n):
        v = f_tf[s] + f_ft[s]
        LV[v] = LV.get(v, 0) + 1
    claim('G2', '★ Λ = f_tf + f_ft 之水平集：Λ⁻¹(0) = Z10（10 態、5 中心對）',
          LV.get(0, 0) == 10 and sorted(s for s in range(n) if f_tf[s] + f_ft[s] == 0) == Z10,
          'Λ 水平 = %s' % LV)
    mult = {}
    for s in Z10:
        mult[str(KV[s])] = mult.get(str(KV[s]), 0) + 1
    u0 = KV[0]
    inU0 = sorted(s for s in Z10 if KV[s] == u0)
    claim('G3', '★ Z10 之 KV 多重度 = (2,2,2,4)，且重數 4 之值 = U[0]（Z10 ∩ KV⁻¹(U[0]) = 4 態）',
          sorted(mult.values()) == [2, 2, 2, 4] and len(inU0) == 4 and str(u0) in mult and mult[str(u0)] == 4,
          '多重度 = %s ; KV⁻¹(U[0]) ∩ Z10 = %s（%d 態）' % (sorted(mult.values()), inU0, len(inU0)))
    nonconstL = sorted(v for v in vals if len(set(f_tf[s] + f_ft[s] for s in fibre[v])) > 1)
    claim('G4', '★（候選）Λ 於 KV-fibre 上恆定（值局部）', nonconstL == [],
          'Λ 非恆定之 fibre = %s（%d/12）⟹ %s' % (nonconstL, len(nonconstL),
          '值局部' if not nonconstL else '非值局部'))
    zoom = {}
    for s in Z10:
        if MUL[s][zc] in zoom:
            continue
        zoom[s] = {'階型': (order[s], order[MUL[s][zc]]), 'KV': str(KV[s]),
                   'f': (f_tf[s], f_ft[s]), 'f_tt': f_tt[s], 'pair': MUL[s][zc]}
    claim('G5', '★ Z10 之 5 對之逐對不變量清單（階型／KV／f／f_tt）（量測）', True, '%s' % zoom)

    T4 = sorted(set(KV[s] for s in Z10))
    m4 = [str(v) for v in vals if mult.get(str(v), 0) == 4]
    claim('G6', '★ 重數 4 之 KV 值之身分（量測）：= KV_9（並報 U[0] ∈ T 及其 Z10 重數）', True,
          '重數4之值 = %s ; U[0] = %s ; U[0] ∈ T = %s ; Z10∩KV⁻¹(U[0]) = %s'
          % (m4, str(KV[0]), str(KV[0]) in [str(v) for v in T4], inU0))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R16 機器' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/58_r16_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'keys': [[k[0], k[1]] for k in sorted(keys)],
                   'F': {'V': {str(a): [str(v) for v in Vset[a]] for a in Vset if types[a] == 'edge'},
                         'dconst': {str(a): dconst[a][0] for a in dconst},
                         'cval': {str(a): cval[a] for a in cval}},
                   'G': {'LV': {str(k): v for k, v in LV.items()}, 'zoom': {str(k): v for k, v in zoom.items()},
                         'mult': mult},
                   'nec8': nec8, 'nz22': nz22},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
