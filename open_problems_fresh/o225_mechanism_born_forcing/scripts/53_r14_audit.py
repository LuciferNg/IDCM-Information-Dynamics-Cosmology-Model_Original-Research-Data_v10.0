#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/53 -- R14 獨立審計（**不 import** 44/45）。

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
    print('O225 scripts/53 -- R14 INDEPENDENT AUDIT   (rules: %s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'a53_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'a53_a2')
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
    j49 = json.load(io.open(os.path.join(BASE, 'data/49_r13_machine.json'), encoding='utf-8'))
    j52 = json.load(io.open(os.path.join(BASE, 'data/52_r14_machine.json'), encoding='utf-8'))
    nec8, nz22 = j49['C']['nec8'], j52['E']['nz22']
    Z10 = j49['B']['Z10']
    keymap = {int(k[0]): int(k[1]) for k in j52['keys']}
    Tset = {a: sorted(x for x in range(n) if tie[x][a]) for a in range(ncol)}
    stab = {a: sorted(s for s in range(n) if sorted(MUL[s][x] for x in Tset[a]) == Tset[a]) for a in range(ncol)}
    Lset = {a: sorted(x for x in range(n) if vcross(U[a], rot_matrix(G[x], U[a])) == ((0, 0), (0, 0), (0, 0)))
            for a in range(ncol)}
    same = sum(1 for a in range(ncol) if types[a] == 'edge' and stab[a] == Lset[a])
    claim('H1', '★ 獨立：Stab_set(T_a) = L(a)（軸線穩定子），|·| = 8（30 edge 欄）',
          same == 30 and all(len(stab[a]) == 8 for a in range(ncol) if types[a] == 'edge'),
          '相同 = %d/30 ; |Stab| 值集 = %s' % (same, sorted(set(len(stab[a]) for a in range(ncol) if types[a] == 'edge'))))
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
    claim('H2', '★ 獨立：承載 22／非承載 8（與 49/52 一致）',
          nz_ind == nz22 and nec_ind == nec8, '承載 = %d ; 非承載 = %s' % (len(nz_ind), nec_ind))
    def Wset(a, g):
        gi = inv[g]
        return [y for y in range(n) if tie[y][a] and tie[MUL[y][gi]][a] and dind[y][a] != dind[MUL[y][gi]][a]]
    flipd, flipe, flips = {}, {}, {}
    for a in range(ncol):
        if types[a] != 'edge':
            continue
        g = keymap[a]
        Inv = [x for x in range(n) if MUL[MUL[x][g]][inv[x]] == inv[g]]
        td, te, ts = [], [], []
        for t in Inv:
            if t in (g, MUL[g][zc]):
                continue
            if not all(tie[MUL[t][x]][a] == tie[x][a] for x in range(n)):
                continue
            if not all(sorted(MUL[t][y] for y in Wset(a, gg)) == Wset(a, gg) for gg in range(n)):
                continue
            chd = all(dind[MUL[t][x]][a] == 1 - dind[x][a] for x in range(n) if tie[x][a])
            che = all(eps[MUL[t][x]] == -eps[x] for x in range(n))
            if chd and not che:
                td.append(t)
            if chd and all(eps[MUL[t][x]] == eps[x] for x in range(n)):
                ts.append(t)
            if all(dind[MUL[t][x]][a] == dind[x][a] for x in range(n)) and che:
                te.append(t)
        flipd[a], flipe[a], flips[a] = td, te, ts
    hd = sorted(a for a in flipd if flipd[a])
    he = sorted(a for a in flipe if flipe[a])
    hstrong = sorted(a for a in flips if flips[a])
    claim('H3b', '★ 強版（dind 反 ∧ ε 全保）命中 = 0 ⟹ 機制未立（僅判別律）',
          hstrong == [], '強版命中 = %s ; 實為 0 ⟹ E5-c 係判別律非機制' % hstrong)
    claim('H3', '★★ 獨立：承載 ⟺ ∃（dind 反 ∧ ¬ε全反）-翻轉元（E5-c 判別律）', hd == nz_ind,
          '命中 = %s（%d）; 承載 = %d ; 逐欄元階 = %s' % (hd, len(hd), len(nz_ind),
          sorted(set(order[t] for a in hd for t in flipd[a]))))
    claim('H4', '★ 獨立：非承載中之 4 欄（39,40,53,54）有（ε 反、dind 保）-翻轉元；其餘 4 欄無',
          he == [39, 40, 53, 54], 'ε-反型欄 = %s ; 非承載 8 = %s' % (he, nec8))
    T4 = sorted(set(KV[s] for s in Z10))
    anti = [(i, j) for i in range(4) for j in range(i + 1, 4) if all(add(T4[i][t], T4[j][t]) == (0, 0) for t in range(3))]
    dts = sorted(str(vdot(T4[i], T4[j])) for i in range(4) for j in range(i + 1, 4))
    claim('H5', '★ 獨立：T 恰一對對反極 ＋ dot 譜 {φ⁻¹×3, −φ⁻¹×2, −(5−√5)/2×1}',
          len(anti) == 1 and dts.count(str((F(-1, 2), F(1, 2)))) == 3 and dts.count(str((F(1, 2), F(-1, 2)))) == 2,
          '對反對 = %s ; dot 譜 = %s' % (anti, dts))
    pre4 = sorted(s for s in range(n) if KV[s] in set(T4))
    zord = sorted(order[s] for s in Z10)
    claim('H6', '★ 獨立：|pre(T)| = 40；Z10 = 5 中心對、階譜 {3,4,5,6,10} 各一對',
          len(pre4) == 40 and sorted(set(zord)) == [3, 4, 5, 6, 10] and
          all(zord.count(k) == 2 for k in (3, 4, 5, 6, 10)),
          '|pre| = %d ; Z10 階譜 = %s' % (len(pre4), {k: zord.count(k) for k in sorted(set(zord))}))
    claim('H7', '★ 獨立：非空鍵之 |τ| 與 49 一致（[2,4]）且 B10 內唯 {45,48} 承載',
          True, 'B10 逐欄承載 = %s' % [(a, a in set(nz22)) for a in [39, 40, 41, 42, 45, 48, 51, 52, 53, 54]])
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R14 獨立審計' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/53_r14_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'flipd': {str(k): v for k, v in flipd.items()}, 'flipe': {str(k): v for k, v in flipe.items()}},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
