#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/46 -- R12 獨立審計（**不 import** 44/45）。

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
    print('O225 scripts/46 -- R12 INDEPENDENT AUDIT   (rules: %s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'a46_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'a46_a2')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    KVref = [mm.rot_ref(g, U[0]) for g in G]
    KV = [rot_matrix(g, U[0]) for g in G]
    same = sum(1 for s in range(n) if KV[s] == KVref[s])
    claim('A1', '獨立 KV（旋轉矩陣式，不經 sandwich）與 rot_ref 相同 120/120', same == n, '相同 = %d/%d' % (same, n))
    j45 = json.load(io.open(os.path.join(BASE, 'data/45_r12_machine.json'), encoding='utf-8'))
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
    tie = [[vdot(U[a], KV[s]) == Z5(0) for a in range(ncol)] for s in range(n)]
    eps = [vfirstsgn(KV[s]) for s in range(n)]
    gam = [[vfirstsgn(vcross(U[a], KV[s])) for a in range(ncol)] for s in range(n)]
    dind = [[(1 if gam[s][a] != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    dgen = [[1 if gam[s][a] != eps[s] else 0 for a in range(ncol)] for s in range(n)]

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
    d34 = json.load(io.open(os.path.join(BASE, 'data/34_r9_pairing.json'), encoding='utf-8'))
    sha_ok = hashlib.sha256(repr(ev).encode()).hexdigest() == d34['events_sha']
    keys = {}
    for (a, sw, sr) in ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1
    claim('A2', '事件 sha 相符、62 鍵', sha_ok and len(keys) == 62, 'sha = %s ; 鍵 = %d' % (sha_ok, len(keys)))

    def Tterm(x, a, g):
        y = MUL[x][g]
        if tie[x][a] and not tie[y][a]:
            return dind[x][a] * eps[x] * z5sgn(vdot(U[a], KV[y]))
        return 0

    Tx = {k: [Tterm(x, k[0], k[1]) for x in range(n)] for k in sorted(keys)}
    nonempty = [k for k in Tx if any(v != 0 for v in Tx[k])]
    tau_law = 0
    sizes = Counter()
    for k in nonempty:
        T = Tx[k]
        tf = set(x for x in range(n) if T[x] != 0)
        g = k[1]
        hits = [t for t in range(n) if all((((MUL[t][x] in tf) == (x in tf)) and
                                            (T[MUL[t][x]] == (-T[x] if x in tf else 0))) for x in range(n))]
        sizes[len(hits)] += 1
        if g in hits and MUL[g][zc] in hits:
            tau_law += 1
    claim('A3', '★ 獨立：16 非空鍵之 τ 集皆 ⊇ {g_a, −g_a}，大小 ∈ {2,4}',
          tau_law == 16 and set(sizes) <= {2, 4}, 'τ ⊇ {±g_a} 之鍵 = %d/16 ; 大小分佈 = %s' % (tau_law, dict(sizes)))

    # 補集（獨立：y-索引寫 S_TT）
    def S_TT_y(a, g):
        gi = inv[g]
        tot = 0
        for y in range(n):
            x = MUL[y][gi]
            if tie[x][a] and tie[y][a]:
                tot += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
        return tot

    nz22 = [a for a in range(ncol) if any(S_TT_y(a, g) != 0 for g in range(n))]
    a0 = nz22[0]                                   # 必須取**承載欄**（否則 S_TT ≡ 0）
    comp = sorted(g for g in range(n) if S_TT_y(a0, g) == 0)
    cs = set(comp)
    closed = all(MUL[x][y] in cs for x in comp for y in comp)
    spec = Counter(order[x] for x in comp)
    # 表現：a 階 10、b 階 4、b⁻¹ab = a⁻¹
    pres = False
    for a10 in (x for x in comp if order[x] == 10):
        for b4 in (x for x in comp if order[x] == 4):
            if MUL[MUL[inv[b4]][a10]][b4] == inv[a10]:
                pres = True
                break
        if pres:
            break
    claim('A4', '★★ 獨立：補集 = 20 階群（含 e、封閉、階譜 {1:1,2:1,4:10,5:4,10:4}）且滿足 Dic₅ 表現 b⁻¹ab = a⁻¹',
          len(comp) == 20 and e_state in cs and closed and spec == Counter({1: 1, 2: 1, 4: 10, 5: 4, 10: 4}) and pres,
          '|補集| = %d ; 封閉 = %s ; 階譜 = %s ; Dic₅ 表現 = %s' % (len(comp), closed, dict(spec), pres))
    claim('A5', '獨立：以 7440 全域判之承載列 = 22 且全屬 edge；非承載 8 edge 欄 = [39,40,41,42,51,52,53,54]',
          len(nz22) == 22 and all(types[a] == 'edge' for a in nz22)
          and sorted(a for a in range(ncol) if types[a] == 'edge' and a not in set(nz22)) == [39, 40, 41, 42, 51, 52, 53, 54],
          '承載列 = %d（型別值集 %s）' % (len(nz22), sorted(set(types[a] for a in nz22))))

    # Z10（獨立 f，y-索引）
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
    Z10 = sorted(s for s in range(n) if f_tf[s] + f_ft[s] == 0)
    kvc = Counter(KV[s] for s in Z10)
    samekv = sum(1 for s in Z10 if KV[s] == KV[MUL[s][zc]])
    vneg = lambda v: tuple(z5neg(c) for c in v)
    anti = all(vneg(x) in set(kvc) for x in kvc)
    claim('A6', '獨立 Z10：10 元素、重數 {2,2,2,4}、每對同 KV、★對反封閉 = False（更正 42 V3-c 之誤算）',
          len(Z10) == 10 and sorted(kvc.values()) == [2, 2, 2, 4] and samekv == 10 and not anti,
          'Z10 = %s ; 重數 = %s ; 同 KV = %d ; 對反封閉 = %s' % (Z10, sorted(kvc.values()), samekv, anti))
    if len(set(kvc)) == 4:
        kv = sorted(set(kvc))
        d01 = vdot(kv[0], kv[1])
        n0 = vdot(kv[0], kv[0])
        ok_adj = (z5mul(Z5(5), z5mul(d01, d01)) == z5mul(n0, n0))
    else:
        d01 = n0 = None
        ok_adj = False
    claim('A7', '獨立：Z10 之 KV 值（4 個）中最小兩者相鄰（5·(dot)² = |v|⁴）', ok_adj,
          '|KV| = %d ; 最小兩者之 dot = %s ; |v|² = %s' % (len(set(kvc)), d01 if len(set(kvc)) == 4 else None,
                                                         n0 if len(set(kvc)) == 4 else None))
    # 與 45 之 JSON 逐項一致
    nec62 = sorted(a for a in range(ncol) if types[a] == 'edge' and a not in
                   set(a for (a, gg) in keys if S_TT_y(a, gg) != 0))
    ok = (sorted(j45['Y']['Z10']) == Z10 and sorted(j45['Z']['complement']) == comp
          and sorted(j45['Q']['noncarrier_edge']) == nec62
          and j45['Z']['inter_Z10'] == sorted(set(Z10) & cs))
    claim('A8', '與 scripts/45 之 JSON 逐項一致（Z10／補集／非承載 8 欄／補集∩Z10）', ok,
          '45: Z10 %d、補集 %d、非承載 %d、∩ %d' % (len(j45['Y']['Z10']), len(j45['Z']['complement']),
                                                  len(j45['Q']['noncarrier_edge']), len(j45['Z']['inter_Z10'])))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R12 獨立審計' % (npass, len(CLAIMS)))
    out = {'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
           'independent': {'KV_route': 'rotation-matrix', 'complement': comp, 'complement_spec': dict(spec),
                           'Z10': Z10, 'anti_closed': anti, 'tau_sizes': dict(sizes)}}
    with io.open(os.path.join(BASE, 'data/46_r12_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
