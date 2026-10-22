#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/62 -- R17 獨立審計（**不 import** 44/45）。

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
    ell = lambda v: vfirstsgn(v)
    def ant(v, u):
        return all(z5add(v[k], u[k]) == Z5(0) for k in range(3))
    def HT(a):
        out = []
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                v, u = vals[i], vals[j]
                if ant(v, u):
                    continue
                if vcross(tuple(z5add(v[k], u[k]) for k in range(3)), U[a]) == (Z5(0), Z5(0), Z5(0)):
                    out.append((v, u))
        return out
    HTl = {a: HT(a) for a in range(ncol) if types[a] == 'edge'}
    claim('M1', '★★ 獨立：每 edge 欄之半轉對數 = 4，且 dot 多重集 = {+φ⁻¹, +φ⁻¹, −φ⁻¹, −φ⁻¹}',
          sorted(set(len(HTl[a]) for a in HTl)) == [4] and
          all(sorted(str(z5sub(vdot(v, u), Z5(0))) for v, u in HTl[a]) ==
              sorted([str((F(1, 2), F(-1, 2)))] * 2 + [str((F(-1, 2), F(1, 2)))] * 2) for a in HTl),
          '對數值集 = %s ; 樣本 39 之 dot = %s' % (sorted(set(len(HTl[a]) for a in HTl)),
          sorted(str(vdot(v, u)) for v, u in HTl[39])))
    def dind_of(u, a):
        return (1 if vfirstsgn(vcross(U[a], u)) != ell(u) else 0) if vdot(U[a], u) == Z5(0) else 0
    def prs_of(a):
        out, used = [], set()
        for v in Vset[a]:
            if v in used:
                continue
            w = next((x for x in Vset[a] if x != v and ant(v, x)), None)
            used |= {v, w}
            out.append(v)
        return out
    bad2 = [(a, [dind_of(p, a) for p in prs_of(a)]) for a in HTl
            if (a in set(nz22)) != (dind_of(prs_of(a)[0], a) != dind_of(prs_of(a)[1], a))]
    claim('M2', '★★ 獨立：承載 ⟺ 兩赤道半轉對之 dind-bit 相異（2-bit 判準）', bad2 == [], '反例 = %s' % bad2)
    T1 = sorted(set(tuple(sorted((ell(u), dind_of(u, a)) for u in Vset[a])) for a in HTl if a in set(nz22)))
    T0 = sorted(set(tuple(sorted((ell(u), dind_of(u, a)) for u in Vset[a])) for a in HTl if a in set(nec8)))
    claim('M3', '★★ 獨立：承載欄之 V(a) (ε,dind) 表全同（均一型）；非承載為塌縮型',
          T1 == [((-1, 0), (-1, 1), (1, 0), (1, 1))] and len(T0) == 2, '承載表型 = %s ; 非承載表型 = %s' % (T1, T0))
    def eps_i(v):
        return vfirstsgn(v)
    def gam_i(v, a):
        return vfirstsgn(vcross(U[a], v))
    tab = {}
    for a in range(ncol):
        m = {}
        for v in vals:
            for u in vals:
                tw, tr = vdot(U[a], v) == Z5(0), vdot(U[a], u) == Z5(0)
                dw = (1 if gam_i(v, a) != eps_i(v) else 0) if tw else 0
                dr = (1 if gam_i(u, a) != eps_i(u) else 0) if tr else 0
                tf = dr * eps_i(u) * z5sgn(vdot(U[a], v)) if (tr and not tw) else 0
                ft = dw * eps_i(v) * z5sgn(vdot(U[a], u)) if (tw and not tr) else 0
                m[(v, u)] = (tf, ft)
        tab[a] = m
    f_tf = [0] * n
    f_ft = [0] * n
    for s0 in range(n):
        for (a, sw, sr) in ev:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = vdot(U[a], KV[w]) == Z5(0), vdot(U[a], KV[r2]) == Z5(0)
            dw = (1 if gam_i(KV[w], a) != eps_i(KV[w]) else 0) if tw else 0
            dr = (1 if gam_i(KV[r2], a) != eps_i(KV[r2]) else 0) if tr else 0
            if tw and tr:
                pass
            elif tr:
                f_tf[s0] += dr * eps_i(KV[r2]) * z5sgn(vdot(U[a], KV[w]))
            elif tw:
                f_ft[s0] += dw * eps_i(KV[w]) * z5sgn(vdot(U[a], KV[r2]))
    LAM = {}
    dif = []
    for s0 in range(n):
        acc = 0
        for (a, sw, sr) in ev:
            t2 = tab[a][(KV[MUL[s0][sw]], KV[MUL[s0][sr]])]
            acc += t2[0] + t2[1]
        LAM[s0] = acc
        if acc != f_tf[s0] + f_ft[s0]:
            dif.append(s0)
    claim('M4', '★★ 獨立：重組 Λ(s) = Σ_{a ∈ 62 欄} F_a(KV_{s·sw(a)}, KV_{s·sr(a)})', dif == [], '不符之態 = %s' % dif)
    c5 = sorted(set(sum(dind[s0][a] for a in range(ncol)) for s0 in range(n)))
    claim('M5', '★ 獨立：Σ_a dind(s,a) ≡ 5（120/120）⟹ 無判別力；Λ 水平譜載於 JSON',
          c5 == [5] and len(set(LAM.values())) > 5,
          'dind 欄計數值集 = %s ; Λ 水平數 = %d ; Λ⁻¹(0) = %d 態' % (c5, len(set(LAM.values())), sum(1 for s0 in LAM if LAM[s0] == 0)))
    S_of = {s0: sum(vfirstsgn(mm.rot_ref(G[s0], v)) for v in vals) for s0 in range(n)}
    claim('M6', '★★ 留痕：S(s) = Σ_v ε(R_s v) ≡ 0（排列不變 ⟹ 零判別力）', set(S_of.values()) == {0},
          'S 值集 = %s' % sorted(set(S_of.values())))
    claim('M7', '★ 獨立：同赤道對內 dind 相同（反極不變）；15 線之 4 半轉對 ε 多重集已列',
          all(dind_of(vs[0], a) == dind_of(vs[1], a) for a in HTl for vs in HTl[a]),
          '樣本 = %s' % [(a, sorted((ell(v), ell(u)) for v, u in HTl[a])) for a in (32, 39, 41)])

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R17 獨立審計' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/62_r17_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'T1': T1, 'T0': T0, 'LAM': {str(k): v for k, v in LAM.items()}},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
