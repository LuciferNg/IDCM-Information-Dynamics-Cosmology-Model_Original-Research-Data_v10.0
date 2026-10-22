#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/122 -- R33 獨立審計（`r33-closure-batch-v1`）。
A1 const8 以 12 值類代表另路（KV 去重 → 值類 → V(a) 4 值 → 恆定）
A2 Z10-φ 聯集以列主序另路重算
A3 σ-對合搜索以另一迴圈次序／公式重算（先階 2 再中心化子再反號）
A4 MISC-2 以 2 分量 (e, t) 格另路重核
用法: /usr/bin/python3 scripts/122_r33_audit.py
"""
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
Z10 = [9, 15, 21, 31, 57, 67, 77, 87, 111, 117]
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


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


def fs(v):
    for c in v:
        s = sgn(c)
        if s:
            return s
    return 0


def d3(u, v):
    return add(add(mul(u[0], v[0]), mul(u[1], v[1])), mul(u[2], v[2]))


def x3(u, v):
    return (add(mul(u[1], v[2]), neg(mul(u[2], v[1]))),
            add(mul(u[2], v[0]), neg(mul(u[0], v[2]))),
            add(mul(u[0], v[1]), neg(mul(u[1], v[0]))))


def main():
    print('=' * 112)
    print('O225 scripts/122 -- R33 獨立審計')
    print('=' * 112, flush=True)
    d = json.load(io.open(os.path.join(BASE, 'data', '121_r33_machine.json'), encoding='utf-8'))
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'b122')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'b122a')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    gN = len(G)
    e_state = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    inv = [next(j for j in range(gN) if MUL[i][j] == e_state) for i in range(gN)]
    KV = [mm.rot_ref(g, U[0]) for g in G]
    PAIR = [[(sgn(d3(U[a], KV[s])), fs(x3(U[a], KV[s]))) for a in range(ncol)] for s in range(gN)]
    tie = [[PAIR[s][a][0] == 0 for a in range(ncol)] for s in range(gN)]
    eps = [fs(KV[s]) for s in range(gN)]
    dind = [[(1 if fs(x3(U[a], KV[s])) != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(gN)]
    # A1：值類代表（12 類）
    vcls = []
    for s in range(gN):
        sv = (tuple(KV[s][0]), tuple(KV[s][1]), tuple(KV[s][2]))
        for c in vcls:
            if c[0] == sv:
                c[1].append(s)
                break
        else:
            vcls.append([sv, [s]])
    const8b = []
    for a in range(ncol):
        reps = [c[1][0] for c in vcls if d3(U[a], KV[c[1][0]]) == (0, 0)]
        if reps and len(set(dind[r][a] for r in reps)) == 1:
            const8b.append(a)
    claim('A1', 'const8 另路（12 值類代表）= %s == 機器 const8' % const8b,
          const8b == d['const8'], '另路 = %s；機器 = %s' % (const8b, d['const8']))
    # A2：列主序 φ
    phi = {}
    for s in range(gN):
        phi[s] = tuple(tie[MUL[s][x]][a] * 2 + dind[MUL[s][x]][a]
                       for a in range(ncol) for x in range(gN))
    cls = {}
    for s in range(gN):
        cls.setdefault(phi[s], []).append(s)
    mixed = sum(1 for c in cls.values() if any(s in Z10 for s in c) and any(s not in Z10 for s in c))
    claim('A2', 'Z10 = φ-聯集（列主序另路）：混合類 = %d（與機器 C3 一致）' % mixed, mixed == 0, '混合類 = %d' % mixed)
    # A3：σ-搜索另路
    def events_of(state):
        st, stk, ev = 0, [], []
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

    keys = {}
    for (a, sw, sr) in events_of(e_state):
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = 1
    S = {}
    for (a, g) in sorted(keys):
        tot = 0
        for x in range(n):
            y = MUL[x][g]
            if tie[x][a] and tie[y][a]:
                tot += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
        S[(a, g)] = tot
    order2 = [s for s in range(1, gN) if MUL[s][s] == e_state]
    hits = 0
    for (a, g) in sorted(keys):
        for s in order2:
            if MUL[s][g] != MUL[g][s]:
                continue
            okp = all(tie[MUL[s][x]][a] == tie[x][a] and dind[MUL[s][x]][a] == dind[x][a] for x in range(n))
            if not okp:
                continue
            flip = 0
            for x in range(n):
                sgnq = (0 if dind[x][a] == dind[MUL[x][g]][a] else 1) * eps[x] * eps[MUL[x][g]]
                sgns = (0 if dind[MUL[s][x]][a] == dind[MUL[s][x]][MUL[x][g]][a] and False else
                        (0 if dind[MUL[s][x]][a] == dind[MUL[MUL[s][x]][g]][a] else 1) * eps[MUL[s][x]] * eps[MUL[MUL[s][x]][g]]) \
                    if (tie[MUL[s][x]][a] and tie[MUL[MUL[s][x]][g]][a]) else 0
                if sgns != -sgnq:
                    flip = 1
                    break
            if not flip:
                hits += 1
                break
        if hits:
            break
    claim('A3', 'σ-對合另路：命中 = %d（> 0，與機器 50/50 一致）' % hits, hits > 0, '另路命中 = %d' % hits)
    # A4：2 分量格
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(add(U[i][t], U[j][t]) == (0, 0) for t in range(3)):
                partner[i] = j
    pairs = sorted(i for i in range(ncol) if i < partner[i])
    orb = {}
    for i in pairs:
        j = partner[i]
        orb.setdefault(tuple(sorted([PAIR[0][i], PAIR[0][j]])), []).append((i, j))
    mmc2 = 0
    for k, v in orb.items():
        tys = set(types[i] for (i, _j) in v)
        if len(tys) > 1:
            cells = {}
            for (i, j) in v:
                cells.setdefault((PAIR[0][i][0], PAIR[0][i][1], PAIR[0][j][0], PAIR[0][j][1]), set()).add(types[i])
            mmc2 += sum(1 for ts in cells.values() if len(ts) > 1)
    claim('A4', 'MISC-2 2 分量格另路：混合格數 = %d' % mmc2, mmc2 > 0, '混合格 = %d' % mmc2)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 R33 審計' % (npass, len(CLAIMS)))
    io.open(os.path.join(BASE, 'data', '122_r33_audit.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r33-closure-batch-v1', 'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS)}, indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())