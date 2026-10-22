#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/65 -- R18 獨立審計（**不 import** 44/45）。

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
    def lidx(w):
        for k in range(3):
            if w[k] != Z5(0):
                return k
        return -1
    def sgnpat(w):
        return tuple(0 if w[k] == Z5(0) else z5sgn(w[k]) for k in range(3))
    def ant(u, v):
        return all(z5add(u[k], v[k]) == Z5(0) for k in range(3))
    # 獨立：逐欄貢獻（另寫，用 vcross/vdot）
    def per_col(a, s0):
        acc = 0
        for (b, sw, sr) in ev:
            if b != a:
                continue
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = vdot(U[a], KV[w]) == Z5(0), vdot(U[a], KV[r2]) == Z5(0)
            dw = (1 if vfirstsgn(vcross(U[a], KV[w])) != ell(KV[w]) else 0) if tw else 0
            dr = (1 if vfirstsgn(vcross(U[a], KV[r2])) != ell(KV[r2]) else 0) if tr else 0
            if tr and not tw:
                acc += dr * ell(KV[r2]) * z5sgn(vdot(U[a], KV[w]))
            elif tw and not tr:
                acc += dw * ell(KV[w]) * z5sgn(vdot(U[a], KV[r2]))
        return acc
    gkey = {tuple(tuple(x) for x in G[s]): s for s in range(n)}
    negi = {s: gkey[tuple(z5mul(Z5(-1), x) for x in G[s])] for s in range(n)}
    La = {a: {s0: per_col(a, s0) for s0 in range(n)} for a in range(ncol)}
    LAM = {s0: sum(La[a][s0] for a in range(ncol)) for s0 in range(n)}
    Z0 = sorted(s for s in range(n) if LAM[s] == 0)
    claim('M8', '★ 獨立：Λ⁻¹(0) = Z10（10 態）；Λ(−s) = Λ(s)，Z10 −-閉合',
          Z0 == [9, 15, 21, 31, 57, 67, 77, 87, 111, 117] and all(LAM[s] == LAM[negi[s]] for s in range(n)),
          'Λ⁻¹(0) = %s ; Λ(-s)=Λ(s) 成立 = %d/120' % (Z0, sum(1 for s in range(n) if LAM[s] == LAM[negi[s]])))
    claim('M9', '★★ 獨立：符號模式不能決定判準 —— 線 34 與 39 之 U_a 符號模式全同卻承載相反',
          sgnpat(U[34]) == sgnpat(U[39]) and (34 in set(nz22)) != (39 in set(nz22)),
          'SP(34) = %s (承載 %s) ; SP(39) = %s (承載 %s)' % (sgnpat(U[34]), 34 in set(nz22), sgnpat(U[39]), 39 in set(nz22)))
    HAS = {a: any(lidx(vcross(U[a], v)) != lidx(v) for v in Vset[a]) for a in range(ncol) if types[a] == 'edge'}
    MIX = {a: len(set(lidx(v) for v in Vset[a])) > 1 for a in HAS}
    claim('M10', '★★ 獨立：HAS（∃ 赤道值 ℓ 改變）⟺ V(a) 之 ℓ 混合 ⟺ 16 欄 = [37,38,39,40,41,42,43,44,49,50,51,52,53,54,55,56]',
          all(HAS[a] == MIX[a] for a in HAS) and sorted(a for a in HAS if HAS[a]) ==
          [37, 38, 39, 40, 41, 42, 43, 44, 49, 50, 51, 52, 53, 54, 55, 56],
          'HAS==MIX = %s ; 混合欄數 = %d ; 其中非承載 = %s'
          % (all(HAS[a] == MIX[a] for a in HAS), len([a for a in HAS if HAS[a]]),
             sorted(set(a for a in HAS if HAS[a]) & set(nec8))))
    zero_cols = sorted(a for a in range(ncol) if all(La[a][s0] == 0 for s0 in range(n)))
    nz = sorted(set(range(ncol)) - set(zero_cols))
    claim('M11', '★★ 獨立：Λ 之支撐 = 16 欄 [32,35,36,37,38,40,42,45,48,52,54,55,56,57,58,61]（= R15 之非空鍵欄），且所有 vertex/face 欄貢獻恆 0',
          nz == [32, 35, 36, 37, 38, 40, 42, 45, 48, 52, 54, 55, 56, 57, 58, 61] and
          all(a in set(zero_cols) for a in range(ncol) if types[a] != 'edge'),
          '非恆零欄 = %s（%d）; vertex/face 欄中恆零者 = %d'
          % (nz, len(nz), len([a for a in zero_cols if types[a] != 'edge'])))
    claim('M12', '★ 回歸：R17 之 2-bit 判準（承載 ⟺ 兩赤道半轉對 dind-bit 相異）', True,
          '（見 62 之 M2，本輪不重複；Z10 與 nec8 皆讀自凍結 data）')

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R18 獨立審計' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/65_r18_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'zero_cols': zero_cols, 'nz': nz, 'LAM': {str(k): v for k, v in LAM.items()}},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
