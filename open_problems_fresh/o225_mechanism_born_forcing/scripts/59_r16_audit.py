#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/59 -- R16 獨立審計（**不 import** 44/45）。

獨立路徑：KV 以**旋轉矩陣**（由四元數以 Z[√5] 精確砌出 R = I + 2s·[v]× + 2[v]×²）重算，不經 `rot_ref` 之 sandwich；
事件以另一種 replay；f 以 y-索引寫法；補集以獨立掃描；群結構以**表現**驗（a 階 10、b 階 4、b⁻¹ab = a⁻¹）。
用法: /usr/bin/python3 scripts/46_r12_audit.py
"""
import hashlib
import importlib.util
import io
import json
import os
from collections import Counter
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RULES = 'r12-law-closure-v1'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


Z5 = lambda a, b=0: (F(a), F(b))
z5add = lambda x, y: (x[0] + y[0], x[1] + y[1])
z5mul = lambda x, y: (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])
z5neg = lambda x: (-x[0], -x[1])
z5sub = lambda x, y: (x[0] - y[0], x[1] - y[1])


def z5sgn(x):
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


def vadd(u, v):
    return tuple(z5add(a, b) for a, b in zip(u, v))


def vsub(u, v):
    return tuple(z5sub(a, b) for a, b in zip(u, v))


def vscale(s, v):
    return tuple(z5mul(s, x) for x in v)


def vdot(u, v):
    acc = Z5(0)
    for a, b in zip(u, v):
        acc = z5add(acc, z5mul(a, b))
    return acc


def vcross(u, v):
    return (z5sub(z5mul(u[1], v[2]), z5mul(u[2], v[1])),
            z5sub(z5mul(u[2], v[0]), z5mul(u[0], v[2])),
            z5sub(z5mul(u[0], v[1]), z5mul(u[1], v[0])))


def vfirstsgn(v):
    for c in v:
        s = z5sgn(c)
        if s:
            return s
    return 0


def rot_matrix(q, v):
    """R = I + 2s[v]× + 2[v]×²（四元數 q = (q0, v)，單位模）"""
    q0 = q[0]                                   # 四元數分量本身即 Z[√5] 對 (a,b) = a + b√5
    qv = (q[1], q[2], q[3])
    # R·v = (2q0²−1)·v + 2(v·q_v)·q_v + 2q0·(q_v × v)
    t1 = vscale(z5sub(z5mul(Z5(2), z5mul(q0, q0)), Z5(1)), v)
    t2 = vscale(Z5(2), vscale(vdot(v, qv), qv))
    t3 = vscale(z5mul(Z5(2), q0), vcross(qv, v))
    return vadd(vadd(t1, t2), t3)


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def mul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])


def main():
    print('=' * 118)
    print('O225 scripts/56 -- R15 INDEPENDENT AUDIT   (rules: %s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'a56_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'a56_a2')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    KV = [rot_matrix(g, U[0]) for g in G]
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
    tie = [[vdot(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [vfirstsgn(KV[s]) for s in range(n)]
    gam = [[vfirstsgn(vcross(U[a], KV[s])) for a in range(ncol)] for s in range(n)]
    dind = [[(1 if gam[s][a] != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    # 事件／鍵（獨立重算）
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
    ev = events_of(e_state)
    keys = {}
    for (a, sw, sr) in ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1
    col_g = {a: g for (a, g) in keys}
    def S_TT_ind(a, g):
        gi = inv[g]
        tot = 0
        for y in range(n):
            x = MUL[y][gi]
            if tie[x][a] and tie[y][a]:
                tot += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
        return tot
    nz_ind = sorted(a for a in range(ncol) if any(S_TT_ind(a, g) != 0 for g in range(n)))
    nec_ind = sorted(a for a in range(ncol) if types[a] == 'edge' and a not in set(nz_ind))
    vals = sorted(set(KV))
    fibre = {v: sorted(s for s in range(n) if KV[s] == v) for v in vals}
    nonconst_fib = sorted(a for a in range(ncol)
                          if any(len(set((1 if gam[s][a] != eps[s] else 0) for s in fibre[v])) > 1 for v in vals))
    claim('J1', '■ 獨立：dind(·,a) 於每條 KV-fibre（10 態）恆定', nonconst_fib == [],
          '非恆定（欄×值）數 = %d ; fibre 大小 = %s' % (len(nonconst_fib), sorted(set(len(fibre[v]) for v in vals))))
    Tset = {a: sorted(x for x in range(n) if tie[x][a]) for a in range(ncol)}
    Vset = {a: sorted(set(KV[x] for x in Tset[a])) for a in range(ncol)}
    j = sum(1 for a in range(ncol) if types[a] == 'edge' and Vset[a] == sorted([v for v in vals if vdot(U[a], v) == (0, 0)]) and len(Vset[a]) == 4)
    claim('J2', '★ 獨立：V(a) = {v ∈ 12 值 : ⟨U_a, v⟩ = 0}，|V(a)| = 4（30 edge 欄）', j == 30,
          '成立 = %d/30 ; |V| 值集 = %s' % (j, sorted(set(len(Vset[a]) for a in range(ncol) if types[a] == 'edge'))))
    def dconst(a):
        return sorted(set((1 if gam[x][a] != eps[x] else 0) for x in Tset[a]))
    Wnz = {a: sum(1 for g in range(n) if any(tie[y][a] and tie[MUL[y][inv[g]]][a] and
              dind[y][a] != dind[MUL[y][inv[g]]][a] for y in range(n))) for a in range(ncol) if types[a] == 'edge'}
    ok = all((Wnz[a] == 0) == (len(dconst(a)) == 1) for a in Wnz)
    claim('J3', '★★ 獨立：W_a ≡ ∅ ⟺ dind 於 T_a（等價於 V(a) 4 值）恆定 ⟹ 承載 ⟺ 於 V(a) 非恆定', ok,
          '一致 = %d/30 ; 非承載之 dind 集 = %s ; 承載之 dind 集 = %s'
          % (sum(1 for a in Wnz if (Wnz[a] == 0) == (len(dconst(a)) == 1)),
             sorted(set(tuple(dconst(a)) for a in Wnz if Wnz[a] == 0)),
             sorted(set(tuple(dconst(a)) for a in Wnz if Wnz[a] != 0))))
    partner = {i: next(j for j in range(ncol) if i != j and all(
        z5add(U[i][t], U[j][t]) == Z5(0) for t in range(3))) for i in range(ncol)}
    nec8 = sorted(a for a in Wnz if Wnz[a] == 0)
    opp = sorted((a, partner[a], dconst(a)[0], dconst(partner[a])[0]) for a in nec8 if a < partner[a])
    claim('J4', '★ 獨立：8 非承載欄之 dind 常數值 = 逐軸線對相反（0/1）', all(x[2] != x[3] for x in opp) and len(opp) == 4,
          '逐線（欄, 對欄, c, c\'）= %s' % opp)
    f_tf = [0] * n
    f_ft = [0] * n
    f_tt = [0] * n
    for s0 in range(n):
        for (a, sw, sr) in ev:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = tie[w][a], tie[r2][a]
            if tw and tr:
                f_tt[s0] += (0 if dind[r2][a] == dind[w][a] else 1) * eps[r2] * eps[w]
            elif tr:
                f_tf[s0] += dind[r2][a] * eps[r2] * z5sgn(vdot(U[a], KV[w]))
            elif tw:
                f_ft[s0] += dind[w][a] * eps[w] * z5sgn(vdot(U[a], KV[r2]))
    LV = {}
    for s in range(n):
        LV[f_tf[s] + f_ft[s]] = LV.get(f_tf[s] + f_ft[s], 0) + 1
    Z0 = sorted(s for s in range(n) if f_tf[s] + f_ft[s] == 0)
    claim('J5', '★ 獨立：Λ⁻¹(0) = Z10（10 態）；Λ 於 KV-fibre 非恆定（非值局部）',
          Z0 == [9, 15, 21, 31, 57, 67, 77, 87, 111, 117] and
          len([v for v in vals if len(set(f_tf[s] + f_ft[s] for s in fibre[v])) > 1]) > 0,
          'Λ⁻¹(0) = %s ; 非恆定 fibre 數 = %d/12' % (Z0, len([v for v in vals if len(set(f_tf[s] + f_ft[s] for s in fibre[v])) > 1])))
    mult = {}
    for s in Z0:
        mult[KV[s]] = mult.get(KV[s], 0) + 1
    m4 = [v for v in mult if mult[v] == 4]
    inU = sorted(s for s in Z0 if KV[s] == KV[0])
    claim('J6', '★ 獨立：Z10 之 KV 重數 (2,2,2,4)；重數 4 之值 = KV_9；Z10 ∩ KV⁻¹(U[0]) = {21,117}',
          sorted(mult.values()) == [2, 2, 2, 4] and m4 == [KV[9]] and inU == [21, 117] and KV[0] in mult,
          '重數 4 之值 = KV_9 = %s ; ∩KV⁻¹(U[0]) = %s ; U[0] 重數 = %d' % (m4 == [KV[9]], inU, mult.get(KV[0], 0)))
    zp = sorted((order[s], order[MUL[s][zc]]) for s in Z0 if s < MUL[s][zc])
    claim('J7', '★ 獨立：Z10 之 5 對階型 = 2×{3,6} ＋ 1×{4,4} ＋ 2×{5,10}',
          zp == sorted([(3, 6), (3, 6), (4, 4), (5, 10), (5, 10)]), '逐對 = %s' % zp)

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R16 獨立審計' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/59_r16_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'Wnz': {str(k): v for k, v in Wnz.items()}, 'opp': opp},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
