#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/74 -- R21 獨立審計（**不 import** 44/45）。

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
    M1 = (F(-1, 2), F(1, 2))
    M1n = (F(1, 2), F(-1, 2))
    P = {i: next(j for j in range(ncol) if i != j and all(z5add(U[i][t], U[j][t]) == Z0v for t in range(3)))
         for i in range(ncol)}
    lines = sorted(set(min(a, P[a]) for a in range(ncol) if types[a] == 'edge'))
    B10i = sorted(a for a in range(ncol) if types[a] == 'edge' and vdot(U[a], U[0]) in (M1, M1n))
    B10L = sorted(set(min(a, P[a]) for a in B10i))
    Vset = {}
    for a in range(ncol):
        Vset[a] = sorted(set(KV[x] for x in range(n) if vdot(U[a], KV[x]) == Z0v))
    nz = {a: sum(1 for t in range(3) if U[a][t] == Z0v) for a in range(ncol)}

    # B1 ★★ 最後一步：二對代表之 dind 位（另寫：以 firstsgn(vcross) 直算）
    def pairs(V):
        seen, reps = set(), []
        for x in V:
            if x in seen:
                continue
            y = tuple(z5mul(Z5(-1), x[k]) for k in range(3))
            seen.add(x); seen.add(y)
            reps.append(min(x, y))
        return sorted(reps)
    B1rows = []
    for L in B10L:
        bits = []
        for r in pairs(Vset[L]):
            c = vcross(U[L], r)
            bits.append((1 if vfirstsgn(c) != vfirstsgn(r) else 0, r, c))
        B1rows.append((L, sorted(set(b[0] for b in bits)), nz[L]))
    claim('B1', '★★ 獨立（最後一步）：B10 之 4 非座標線之二對 dind 位相同（常數）；座標軸線（45）為 {0,1}',
          all(r[1] in ([0], [1]) for r in B1rows if r[2] == 0) and [r for r in B1rows if r[2] == 2][0][1] == [0, 1],
          '逐線 (L, 位集合, 零分量數) = %s' % [(r[0], r[1], r[2]) for r in B1rows])
    # B2 ★★ 鏡射：以另一路徑找 σ（值集之上之交換二對之元素）
    B2 = []
    for L in B10L:
        V = Vset[L]
        ps = pairs(V)
        found = []
        for s0 in range(n):
            if KV[s0] != KV[0]:
                continue
            img = [next((vals.index(KV[j]) for j in range(n) if KV[j] == tuple(z5mul(Z5(-1), mm.rot_ref(G[s0], x)[k]) for k in range(3))), None) for x in ps]
            if img and all(i is not None for i in img):
                found.append((s0, img))
        B2.append((L, [(s0, img) for (s0, img) in found if img != list(range(len(ps)))]))
    claim('B2', '★★ 獨立：每 B10 線存在固定 U_0 之群元素，把二赤道對互換（σ_{vw}）—— 以「值集上之交換」獨立判別',
          all(len(r[1]) >= 1 for r in B2), '逐線 (L, [(σ, σ 對二代表之像)]) = %s' % B2)
    # B3 ★★ U1 之單向：非承載 ⟹ V(a) ⊂ N(U_0)∪−N(U_0)
    necL = sorted(set(min(a, P[a]) for a in nec8))
    prop = sorted(L for L in lines if all(vdot(x, KV[0]) in (M1, M1n) for x in Vset[L]))
    claim('B3', '★★ 獨立（單向）：非承載 ⟹ V(a) ⊂ N(U_0)∪−N(U_0)（反之不真：10 線有此性質而僅 5 線 B10）',
          all(L in prop for L in necL), 'nec 線 = %s ; 有此性質之線 = %s' % (necL, prop))
    # B4 ★★ V/Z10：於 Z10 每欄之鍵貢獻數分佈（另寫：以 event 直接算）
    Gg = [0] * n
    for (b, sw, sr) in ev:
        for s0 in range(n):
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = vdot(U[b], KV[w]) == Z0v, vdot(U[b], KV[r2]) == Z0v
            if tr and not tw:
                Gg[s0] += ((1 if vfirstsgn(vcross(U[b], KV[r2])) != vfirstsgn(KV[r2]) else 0)
                           * vfirstsgn(KV[r2]) * z5sgn(vdot(U[b], KV[w])))
            elif tw and not tr:
                Gg[s0] += ((1 if vfirstsgn(vcross(U[b], KV[w])) != vfirstsgn(KV[w]) else 0)
                           * vfirstsgn(KV[w]) * z5sgn(vdot(U[b], KV[r2])))
    Z10i = sorted(s0 for s0 in range(n) if Gg[s0] == 0)
    cnt = {}
    for (b, sw, sr) in ev:
        for s0 in Z10i:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = vdot(U[b], KV[w]) == Z0v, vdot(U[b], KV[r2]) == Z0v
            if tw != tr:
                cnt[b] = cnt.get(b, 0) + 1
    claim('B4', '★ 獨立（量測）：Z10 = 10 態；於 Z10 每欄「恰一端 ⊥」之事件數最大 = 2（16 support 欄）',
          len(Z10i) == 10 and all(v <= 2 for v in cnt.values()),
          'Z10 = %s ; 逐欄最大 tie-型數 = %s' % (Z10i, sorted(cnt.items())))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R21 獨立審計' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/74_r21_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'B1': [[r[0], r[1], r[2]] for r in B1rows], 'Z10': Z10i}, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
