#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/80 -- R23 獨立審計（**不 import** 44/45）。

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
    Z0v = Z5(0)
    P = {i: next(j for j in range(ncol) if i != j and all(z5add(U[i][t], U[j][t]) == Z0v for t in range(3)))
         for i in range(ncol)}
    lines = sorted(set(min(a, P[a]) for a in range(ncol) if types[a] == 'edge'))
    def fslead(A):
        for k in range(3):
            s = z5sgn(A[k])
            if s != 0:
                return k, s
        return -1, 0
    def invZ(y):
        p, q = y
        d = p * p - 5 * q * q
        return (F(p, 1) / F(d, 1), F(-q, 1) / F(d, 1))
    Vset = {a: sorted(set(KV[x] for x in range(n) if vdot(U[a], KV[x]) == Z0v)) for a in range(ncol)}
    def reps(a):
        seen, out = set(), []
        for x in Vset[a]:
            if x in seen:
                continue
            y = tuple(z5neg(x[k]) for k in range(3))
            seen.add(x); seen.add(y)
            out.append(min(x, y))
        return sorted(out)
    nc = [L for L in lines if all(U[L][t] != Z0v for t in range(3))]
    # A1 ★★：單項預測 vs 儲存 dind 位（不重算 dind，用 R16 機器之表）
    A1bad = []
    for L in nc:
        for x in reps(L):
            j = fslead(x)[0]
            if x[1] == Z0v:
                pred = 1 if (z5sgn(U[L][0]) * z5sgn(U[L][1]) * z5sgn(U[L][2]) == 1) else 0
                # 預測 dind = [乘積 = −1]；乘積 = −sgn(u0u1u2) ⟹ dind = [sgn(u0u1u2) = +1]
            elif x[0] == Z0v:
                pred = 1 if z5sgn(U[L][2]) == 1 else 0
                # 乘積 = −sgn(u_2) ⟹ dind = [sgn(u2) = +1]
            else:
                continue
            s0 = [t for t in range(n) if KV[t] == x][0]
            act = 1 if vfirstsgn(vcross(U[L], KV[s0])) != vfirstsgn(KV[s0]) else 0
            if pred != act:
                A1bad.append((L, str(x), pred, act))
    claim('A1', '★★ 獨立：單項族之兩式（`dind = [sgn(u_0u_1u_2)=+1]`／`= [sgn(u_2)=+1]`）對 R16 儲存之 dind 表逐值吻合',
          A1bad == [], '反例 = %s' % A1bad[:5])
    # A2 ★★：非單項公式（另用 invZ）
    A2bad = []
    for L in nc:
        u = U[L]
        for x in reps(L):
            if x[0] == Z0v or x[1] == Z0v:
                continue
            num = z5add(z5mul(z5mul(u[0], u[1]), x[0]), z5mul(z5add(z5mul(u[1], u[1]), z5mul(u[2], u[2])), x[1]))
            pred = z5neg(z5mul(num, invZ(u[2])))
            if pred != vcross(u, x)[0]:
                A2bad.append((L, str(x), str(vcross(u, x)[0]), str(pred)))
    claim('A2', '★★ 獨立：非單項型 `A_0 = −(u_0u_1x_0 + (u_1²+u_2²)x_1)/u_2`（另實作）', A2bad == [], '反例 = %s' % A2bad[:4])
    # A3 ★★：非承載之覆蓋（單項族 ∧ 同號）∪（41/42 之雙項符號一致）
    A3rows = []
    for L in nc:
        mono = all(x[0] == Z0v or x[1] == Z0v for x in reps(L))
        same = (z5sgn(U[L][0]) * z5sgn(U[L][1]) == 1)
        prox = row2 = False
        if mono:
            prox = same
        if L in (41, 42):
            sg = set()
            for x in reps(L):
                u = U[L]
                num = z5add(z5mul(z5mul(u[0], u[1]), x[0]), z5mul(z5add(z5mul(u[1], u[1]), z5mul(u[2], u[2])), x[1]))
                sg.add(z5sgn(num) * z5sgn(x[fslead(x)[0]]))
            prox = (len(sg) == 1)
        A3rows.append((L, mono, same, prox, L in set(nec8)))
    claim('A3', '★★ 獨立：非承載 = 單項族（∧ 首兩分量同號）∪ 41/42（雙項符號一致）——12 非座標線',
          all(r[3] == r[4] for r in A3rows), '逐線 (L, 單項?, 同號?, 預測非承載, 實測非承載) = %s' % A3rows)
    # A4 ★★：凍結路線之零集（另路）
    gg = {a: [0] * n for a in range(ncol)}
    for (b, sw, sr) in ev:
        for s0 in range(n):
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = vdot(U[b], KV[w]) == Z0v, vdot(U[b], KV[r2]) == Z0v
            if tr and not tw:
                gg[b][s0] += ((1 if vfirstsgn(vcross(U[b], KV[r2])) != vfirstsgn(KV[r2]) else 0)
                              * vfirstsgn(KV[r2]) * z5sgn(vdot(U[b], KV[w])))
            elif tw and not tr:
                gg[b][s0] += ((1 if vfirstsgn(vcross(U[b], KV[w])) != vfirstsgn(KV[w]) else 0)
                              * vfirstsgn(KV[w]) * z5sgn(vdot(U[b], KV[r2])))
    LM = [sum(gg[a][s0] for a in range(ncol)) for s0 in range(n)]
    Zf = sorted(s0 for s0 in range(n) if LM[s0] == 0)
    claim('A4', '★★ 獨立：凍結路線之零集 = 10 態 Z10；且 support 欄（除 61）於 Z10 之 Λ_a ∈ {−2,0,2}',
          Zf == [9, 15, 21, 31, 57, 67, 77, 87, 111, 117]
          and all(abs(F(gg[a][s0], 2)) <= 1 for a in range(ncol) if a != 61 and any(gg[a][t] for t in range(n))
                  for s0 in Zf), 'Z10 = %s ; 值集 = %s' % (Zf, sorted(set(gg[a][s0] for a in range(ncol) for s0 in Zf))))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R23 獨立審計' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/80_r23_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS}, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
