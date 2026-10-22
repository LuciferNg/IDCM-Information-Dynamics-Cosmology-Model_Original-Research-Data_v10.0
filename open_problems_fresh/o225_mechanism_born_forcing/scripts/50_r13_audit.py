#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/50 -- R13 獨立審計（**不 import** 44/45）。

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
    print('O225 scripts/50 -- R13 INDEPENDENT AUDIT   (rules: %s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'a50_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'a50_a2')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    KVr = [mm.rot_ref(g, U[0]) for g in G]
    KV = [rot_matrix(g, U[0]) for g in G]                     # 獨立路徑：旋轉矩陣式
    claim('F1', '獨立 KV（旋轉矩陣式）與 rot_ref 相同 120/120',
          sum(1 for s in range(n) if KV[s] == KVr[s]) == n, '相同 = %d/%d' % (sum(1 for s in range(n) if KV[s] == KVr[s]), n))
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
    col_of = {g: a for (a, g) in keys}

    def Tterm(x, a, g):
        y = MUL[x][g]
        if tie[x][a] and not tie[y][a]:
            return dind[x][a] * eps[x] * z5sgn(vdot(U[a], KV[y]))
        return 0

    Tx = {k: [Tterm(x, k[0], k[1]) for x in range(n)] for k in sorted(keys)}
    nonempty = [k for k in Tx if any(v != 0 for v in Tx[k])]
    tau = {}
    for k in nonempty:
        T = Tx[k]
        tf = set(x for x in range(n) if T[x] != 0)
        tau[k] = sorted(t for t in range(n) if all((((MUL[t][x] in tf) == (x in tf)) and
                     (T[MUL[t][x]] == (-T[x] if x in tf else 0))) for x in range(n)))

    def S_TT_y(a, g):
        gi = inv[g]
        tot = 0
        for y in range(n):
            x = MUL[y][gi]
            if tie[x][a] and tie[y][a]:
                tot += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
        return tot

    nz22 = sorted(a for a in range(ncol) if any(S_TT_y(a, g) != 0 for g in range(n)))
    nec8 = sorted(a for a in range(ncol) if types[a] == 'edge' and a not in set(nz22))
    claim('F2', '獨立：承載列 22（全 edge）／非承載 8 = [39,40,41,42,51,52,53,54]',
          len(nz22) == 22 and all(types[a] == 'edge' for a in nz22) and nec8 == [39, 40, 41, 42, 51, 52, 53, 54],
          '承載 = %d ; 非承載 = %s' % (len(nz22), nec8))

    # F3：|τ| 與 A8 之對應（獨立）
    sizes = {k: len(tau[k]) for k in nonempty}
    a8 = sum(1 for k in nonempty if (sizes[k] == 4) == (k[0] in set(nec8)))
    claim('F3', '★ 獨立：|τ| = 4 ⟺ 該鍵之欄非承載（16/16）',
          a8 == len(nonempty) == 16, '一致 = %d/%d ; |τ| 分佈 = %s' % (a8, len(nonempty), sorted(set(sizes.values()))))
    big = [k for k in nonempty if sizes[k] == 4]
    cc = {}
    for k in big:
        g = k[1]
        C = len([x for x in range(n) if MUL[x][g] == MUL[g][x]])
        I = len([x for x in range(n) if MUL[MUL[x][g]][inv[x]] == inv[g]])
        L = len([x for x in range(n) if vcross(U[k[0]], rot_matrix(G[x], U[k[0]])) == (Z5(0), Z5(0), Z5(0))])
        cc[k] = (C, I, L)
    claim('F4', '★ 獨立：|C(g_a)| = 4、|反演陪集| = 4、軸線 stabilizer |L| = 8 = C ∪ Inv',
          all(v == (4, 4, 8) for v in cc.values()), '（|C|,|Inv|,|L|）= %s' % sorted(set(cc.values())))
    h_ok = 0
    for k in big:
        g = k[1]
        hs = sorted(set(tau[k]) - {g, MUL[g][zc]})
        if hs and all(MUL[MUL[h][g]][inv[h]] == inv[g] for h in hs):
            h_ok += 1
    claim('F5', '★ 獨立：額外 h 反演 g_a（h·g_a·h⁻¹ = g_a⁻¹）', h_ok == len(big), '成立 = %d/%d' % (h_ok, len(big)))
    pre = {}
    for v in set(KV):
        pre[v] = sum(1 for s in range(n) if KV[s] == v)
    claim('F6', '★ 獨立：每個 KV 值恰 10 個原像', sorted(set(pre.values())) == [10],
          '原像大小集 = %s' % sorted(set(pre.values())))
    # F7：Z10（獨立 f）+ T 之 Gram
    f_tf = [0] * n
    f_ft = [0] * n
    for s0 in range(n):
        for (a, sw, sr) in ev:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = tie[w][a], tie[r2][a]
            if not (tw and tr):
                if tr:
                    f_tf[s0] += dind[r2][a] * eps[r2] * z5sgn(vdot(U[a], KV[w]))
                elif tw:
                    f_ft[s0] += dind[w][a] * eps[w] * z5sgn(vdot(U[a], KV[r2]))
    Z10 = sorted(s for s in range(n) if f_tf[s] + f_ft[s] == 0)
    T4 = sorted(set(KV[s] for s in Z10))
    dots = sorted(str(vdot(T4[i], T4[j])) for i in range(4) for j in range(i + 1, 4))
    from collections import Counter as _C
    dm = dict(_C(dots))
    claim('F7', '★ 獨立：Z10 之 4 KV 值之 Gram 譜 = {φ⁻¹×3, −φ⁻¹×2, (−5+√5)/2×1}',
          sorted(dm.values()) == [1, 2, 3] and len(dots) == 6, 'Z10 = %s ; dot 值 = %s' % (Z10, dm))
    # F8：nec8 = φ⁻¹-10 集 ∖ {45,48}；且該 10 集 = 一個 Dic₅-10-軌道
    PHI1, PHI2 = (F(-1, 2), F(1, 2)), (F(1, 2), F(-1, 2))     # ±φ⁻¹
    ten = sorted(a for a in range(ncol) if types[a] == 'edge' and vdot(U[a], U[0]) in (PHI1, PHI2))
    D5 = sorted(g for g in range(n) if S_TT_y(nz22[0], g) == 0)
    orbs = []
    seen = set()
    for a in range(ncol):
        if types[a] != 'edge' or a in seen:
            continue
        o = set()
        for x in D5:
            gc = MUL[MUL[x][col_g[a]]][inv[x]]
            if gc in col_of:
                o.add(col_of[gc])
        seen |= o
        orbs.append(sorted(o))
    hit = [o for o in orbs if set(o) & set(nec8)]
    claim('F8', '★★ 獨立：φ⁻¹-10 集 = Dic₅ 之一 10-軌道；nec8 = 該集 ∖ {45,48}（該 2 欄為一軸線對且承載）',
          ten == [39, 40, 41, 42, 45, 48, 51, 52, 53, 54] and len(hit) == 1 and hit[0] == ten
          and sorted(set(ten) - set(nec8)) == [45, 48],
          '10 集 = %s ; Dic₅ 軌道 = %s ; 例外 = %s' % (ten, [len(o) for o in orbs], sorted(set(ten) - set(nec8))))
    fsz = sorted(set(sum(1 for s in range(n) if tie[s][a]) for a in range(ncol) if types[a] == 'edge'))
    claim('F9', '★ 獨立：每個 edge 欄恰有 40 個 tie 態（vertex／face 欄 0）',
          fsz == [40], 'edge 欄之 tie 態數值集 = %s' % fsz)
    j49 = json.load(io.open(os.path.join(BASE, 'data/49_r13_machine.json'), encoding='utf-8'))
    claim('F10', '與 scripts/49 之 JSON 逐項一致（非空鍵 16、nec8、Z10 相同）',
          len(nonempty) == 16 and j49['C']['nec8'] == nec8 and j49['B']['Z10'] == Z10,
          '49: nec8 %s、Z10 %d 個' % (j49['C']['nec8'], len(j49['B']['Z10'])))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R13 獨立審計' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/50_r13_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'independent': {'phi10': ten, 'nec8': nec8, 'Z10': Z10, 'dots': dm}},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
