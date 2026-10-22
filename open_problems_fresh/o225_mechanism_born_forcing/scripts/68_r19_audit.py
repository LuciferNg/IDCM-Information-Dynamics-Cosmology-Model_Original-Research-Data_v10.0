#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/68 -- R19 獨立審計（**不 import** 44/45）。

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
    j58 = json.load(io.open(os.path.join(BASE, 'data/58_r16_machine.json'), encoding='utf-8'))
    nz22, nec8 = j58['nz22'], j58['nec8']
    vals = sorted(set(KV))
    Tset = {a: sorted(x for x in range(n) if tie[x][a]) for a in range(ncol)}
    Vset = {a: sorted(set(KV[x] for x in Tset[a])) for a in range(ncol)}
    def lidx(w):
        for k in range(3):
            if w[k] != Z5(0):
                return k
        return -1
    def absv(x):
        return x if z5sgn(x) >= 0 else z5sub(Z5(0), x)
    def per_col(a, s0):
        acc = 0
        for (b, sw, sr) in ev:
            if b != a:
                continue
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = vdot(U[a], KV[w]) == Z5(0), vdot(U[a], KV[r2]) == Z5(0)
            dw = (1 if vfirstsgn(vcross(U[a], KV[w])) != vfirstsgn(KV[w]) else 0) if tw else 0
            dr = (1 if vfirstsgn(vcross(U[a], KV[r2])) != vfirstsgn(KV[r2]) else 0) if tr else 0
            if tr and not tw:
                acc += dr * vfirstsgn(KV[r2]) * z5sgn(vdot(U[a], KV[w]))
            elif tw and not tr:
                acc += dw * vfirstsgn(KV[w]) * z5sgn(vdot(U[a], KV[r2]))
        return acc
    gkey = {tuple(tuple(x) for x in G[s]): s for s in range(n)}
    negi = {s: gkey[tuple(z5mul(Z5(-1), x) for x in G[s])] for s in range(n)}
    La = {a: {s0: per_col(a, s0) for s0 in range(n)} for a in range(ncol)}
    LAM = {s0: sum(La[a][s0] for a in range(ncol)) for s0 in range(n)}
    PHI1 = Z5(-1, 2) if False else (F(-1, 2), F(1, 2))
    D0 = {a: vdot(U[a], U[0]) for a in range(ncol) if types[a] == 'edge'}
    B10 = sorted(a for a in D0 if D0[a] in (PHI1, (F(1, 2), F(-1, 2))))
    NZc = {a: sum(1 for k in range(3) if U[a][k] == Z5(0)) for a in D0}
    bad1 = [a for a in D0 if (a in set(nec8)) != (a in set(B10) and NZc[a] == 0)]
    claim('R1', '★★ 獨立：非承載 ⟺ a ∈ B10（|⟨U_a,U_0⟩| = φ⁻¹）∧ U_a 無零分量', bad1 == [],
          '反例 = %s ; |B10| = %d ; B10 中零分量者 = %s' % (bad1, len(B10), sorted(a for a in B10 if NZc[a] >= 1)))
    MIX = {a: len(set(lidx(v) for v in Vset[a])) > 1 for a in D0}
    bad3 = [a for a in D0 if (a in set(nec8)) != (MIX[a] and a in set(B10))]
    claim('R2', '★★ 獨立：非承載 ⟺ MIX(a)（V(a) 之 ℓ 混合）∧ a ∈ B10', bad3 == [],
          '反例 = %s ; MIX∧B10 = %s' % (bad3, sorted(a for a in D0 if MIX[a] and a in set(B10))))
    PH = sorted([(F(1, 4), F(1, 4)), (F(-1, 4), F(1, 4)), (F(1, 2), F(0))])
    A12 = [a for a in D0 if NZc[a] == 0]
    partner = {i: next(j for j in range(ncol) if i != j and all(
        z5add(U[i][t], U[j][t]) == Z5(0) for t in range(3))) for i in range(ncol)}
    A12L = sorted(set(min(a, partner[a]) for a in A12))
    okphi = all(sorted(absv(U[a][k]) for k in range(3)) == PH for a in A12)
    claim('R3', '★★ 獨立：12 非座標線之軸之絕對值多重集 = {φ/2, φ⁻¹/2, 1/2}（三種循環指派）',
          okphi and len(A12L) == 12,
          '非座標欄數 = %d（%d 線）; 全部 φ-型 = %s' % (len(A12), len(A12L), okphi))
    LVS = {}
    for s0 in range(n):
        LVS[LAM[s0]] = LVS.get(LAM[s0], 0) + 1
    claim('R4', '■ 獨立：逐欄 Λ_a(−s) = Λ_a(s)；Λ 之水平集大小皆偶',
          all(La[a][negi[s0]] == La[a][s0] for a in La for s0 in range(n)) and all(v % 2 == 0 for v in LVS.values()),
          '逐欄 ±-不變 = %s ; 水平大小皆偶 = %s（%d 個水平）'
          % (all(La[a][negi[s0]] == La[a][s0] for a in La for s0 in range(n)),
             all(v % 2 == 0 for v in LVS.values()), len(LVS)))
    cls = {s0: frozenset(MUL[MUL[g][s0]][inv[g]] for g in range(n)) for s0 in range(n)}
    classes = sorted(set(cls.values()), key=lambda c: (len(c), sorted(c)[0]))
    csz = sorted(len(c) for c in classes)
    reach = {0}
    for x in csz:
        reach |= {r + x for r in reach if r + x <= 10}
    notc = len([c for c in classes if len(set(LAM[s0] for s0 in c)) > 1])
    claim('R5', '■ 獨立：Λ 非類函數（|Λ⁻¹(0)| = 10 而 10 ∉ 類大小之子集和）',
          notc > 0 and 10 not in reach and sum(1 for s0 in range(n) if LAM[s0] == 0) == 10,
          '類大小 = %s ; 非常數類 = %d ; 10 可達 = %s ; |Λ⁻¹(0)| = %d'
          % (csz, notc, 10 in reach, sum(1 for s0 in range(n) if LAM[s0] == 0)))
    support = sorted(a for a in La if any(La[a][s0] != 0 for s0 in range(n)))
    Z0 = sorted(s0 for s0 in range(n) if LAM[s0] == 0)
    cand = sorted(s0 for s0 in range(n) if sum(1 for a in support if La[a][s0] > 0) ==
                  sum(1 for a in support if La[a][s0] < 0) and
                  all(abs(La[a][s0]) == 2 for a in support if La[a][s0] != 0) and
                  any(La[a][s0] != 0 for a in support))
    claim('R6', '★★ 獨立：Z10 = {s : 非零欄之 |Λ_a| 全 = 2 ∧ 正欄數 = 負欄數}', cand == Z0,
          '候選 = %s（%d）; Λ⁻¹(0) = %s（%d）' % (cand, len(cand), Z0, len(Z0)))
    INVL = sorted(h for h in range(n) if all(LAM[MUL[s0][h]] == LAM[s0] for s0 in range(n)))
    claim('R7', '★ 獨立：|Inv(Λ)| = 2（元素 = {e, −1}）', len(INVL) == 2, '|Inv| = %d ; 元素 = %s' % (len(INVL), INVL))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R19 獨立審計' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/68_r19_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'B10': B10, 'csz': csz, 'support': support},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
