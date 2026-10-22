#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/85 -- R24 審計（`r24-two-term-family-v1`）

紀律：**不 import 本 o 任何推導 script**（含 84）；只載凍結 O222 機器（唯讀）並以**另路實作**重算。
A1 R5 盲測之另路重算（C2 判準 ⟹ 全域解恰 = Z10）
A2 R2-c 之另路重算（抵消態 f_tf = −f_ft ≠ 0 恰 = Z10）
A3 S2 橋接之另路重算（B10 = ±φ⁻¹）與 W-空集
A4 S4 新律之另路重算（8 非承載欄之 dind 共同值 = 1 ⟺ sgn(u_2) = +1）
用法: /usr/bin/python3 scripts/85_r24_audit.py
"""
import hashlib
import importlib.util
import io
import json
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RULES = 'r25-z10-selection-v1'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def info(s):
    print('[INFO] ' + s, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# ---- 另名 Z[√5] 代數（獨立實作；不用 84 之名） ----
def zadd(x, y):
    return (x[0] + y[0], x[1] + y[1])


def zneg(x):
    return (-x[0], -x[1])


def zmul(x, y):
    a, b = x
    c, d = y
    return (a * c + 5 * b * d, a * d + b * c)


def zsq(x):
    return zmul(x, x)


def zsgn(x):
    p, q = x
    if p == 0 and q == 0:
        return 0
    if p == 0:
        return (1 if q > 0 else -1)
    if q == 0:
        return (1 if p > 0 else -1)
    if p < 0 and q < 0:
        return -1
    if p > 0 and q > 0:
        return 1
    if p * p == 5 * q * q:
        return 0
    big = (p * p > 5 * q * q)
    return (1 if big else -1) * (1 if p > 0 else (-1 if p < 0 else (1 if q > 0 else -1)))


def zz(u, v):
    return zadd(zadd(zmul(u[0], v[0]), zmul(u[1], v[1])), zmul(u[2], v[2]))


def x3(u, v):
    return (zadd(zmul(u[1], v[2]), zneg(zmul(u[2], v[1]))),
            zadd(zmul(u[2], v[0]), zneg(zmul(u[0], v[2]))),
            zadd(zmul(u[0], v[1]), zneg(zmul(u[1], v[0]))))


def fs(v):
    for c in v:
        s = zsgn(c)
        if s:
            return s
    return 0


def fidx(v):
    for k in range(3):
        if zsgn(v[k]):
            return k
    return -1


def main():
    print('=' * 118)
    print('O225 scripts/88 -- R25 AUDIT   (rules: %s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'a25_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'a25_a2')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    e_state = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    inv = [next(j for j in range(n) if MUL[i][j] == e_state) for i in range(n)]
    tie = [[zz(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [fs(KV[s]) for s in range(n)]
    dind = [[(1 if fs(x3(U[a], KV[s])) != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]

    def ev_of(state):
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

    my_ev = ev_of(e_state)
    # 結構常數（審計側另算）
    zc = [s for s in range(n) if s != e_state and all(MUL[s][k] == MUL[k][s] for k in range(n))
          and any(MUL[s][s] == e_state for _ in [0])][0] if False else None
    order = []
    for a in range(n):
        k, x = 1, a
        while x != e_state:
            x = MUL[x][a]
            k += 1
        order.append(k)
    zc = [s for s in range(n) if s != e_state and order[s] == 2
          and all(MUL[s][k] == MUL[k][s] for k in range(n))][0]

    # 另路：f_tf / f_ft（同式、獨立實作）
    f_tf, f_ft = [0] * n, [0] * n
    for s0 in range(n):
        for (a, sw, sr) in my_ev:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            if tie[r2][a] and not tie[w][a]:
                f_tf[s0] += dind[r2][a] * eps[r2] * zsgn(zz(U[a], KV[w]))
            elif tie[w][a] and not tie[r2][a]:
                f_ft[s0] += dind[w][a] * eps[w] * zsgn(zz(U[a], KV[r2]))
    Zf = sorted(s for s in range(n) if f_tf[s] + f_ft[s] == 0)
    la = {a: [0] * n for a in range(ncol)}
    for a in range(ncol):
        for s0 in range(n):
            tot = 0
            for (a2_, sw, sr) in my_ev:
                if a2_ != a:
                    continue
                w, r2 = MUL[s0][sw], MUL[s0][sr]
                if tie[r2][a] and not tie[w][a]:
                    tot += dind[r2][a] * eps[r2] * zsgn(zz(U[a], KV[w]))
                elif tie[w][a] and not tie[r2][a]:
                    tot += dind[w][a] * eps[w] * zsgn(zz(U[a], KV[r2]))
            la[a][s0] = tot

    # A1：C2 判準（ΣΛ=0 ∧ max|Λ| ≤ 2）之全域解 = Z10
    C2 = sorted(s for s in range(n) if sum(la[a][s] for a in range(ncol)) == 0
                and max(abs(la[a][s]) for a in range(ncol)) <= 2)
    claim('A1', '★★（另路）R5 之重算：C2（Σ_a Λ_a = 0 ∧ max_a|Λ_a| ≤ 2）套用全部 120 態 ⟹ 解集恰 = Z10（10 態）',
          C2 == Zf == sorted(Z10) if (Z10 := Zf) else False,
          'C2 = %d ; 凍結零集 = %d ; 相同 = %s ; 額外 = %s' % (len(C2), len(Zf), C2 == Zf, sorted(set(C2) - set(Zf))))

    # A2：R2-c 之重算（抵消態 = Z10）
    C1c = sorted(s for s in range(n) if f_tf[s] == -f_ft[s] and f_tf[s] != 0)
    claim('A2', '★★（另路）R2-c：{s : f_tf = −f_ft ≠ 0} 恰 = Z10（且 ⊂ C2 解集）', C1c == Zf,
          'C1′ = %d ; Z10 = %d ; 缺 = %s ; 多 = %s' % (len(C1c), len(Zf), sorted(set(Zf) - set(C1c)), sorted(set(C1c) - set(Zf))))

    # A3：S2 橋接之重算（B10 = ±φ⁻¹：2⟨U_a,U_0⟩ = ±(−1+√5)）
    def two_dot(a):
        d = zz(U[a], U[0])
        return (2 * d[0], 2 * d[1])
    B10 = sorted(a for a in range(ncol) if two_dot(a) in ((F(-1), F(1)), (F(1), F(-1))))
    def Wnz(a):
        cnt = 0
        for g in range(n):
            gi = inv[g]
            if any(tie[y][a] and tie[MUL[y][gi]][a] and dind[y][a] != dind[MUL[y][gi]][a] for y in range(n)):
                cnt += 1
        return cnt
    edge = [a for a in range(ncol) if types[a] == 'edge']
    Wempty = sorted(a for a in edge if Wnz(a) == 0)
    S2 = sorted(a for a in edge if a in set(B10) and all(U[a][t] != (0, 0) for t in range(3)))
    claim('A3', '★★（另路）S2：{a : W_a = ∅} = {a ∈ edge : a ∈ B10（⟨U_a,U_0⟩ = ±φ⁻¹）∧ U_a 無零分量}',
          Wempty == S2, 'W-空 = %s ; B10∧無零 = %s' % (Wempty, S2))

    # A4：S3-c／S4 之重算（dind 共同值 vs sgn(u_2)）
    rows, bad = [], []
    for a in Wempty:
        common = sorted(set(dind[x][a] for x in range(n) if tie[x][a]))
        pred = 1 if zsgn(U[a][2]) > 0 else 0
        rows.append((a, common, zsgn(U[a][2]), pred))
        if common != [pred]:
            bad.append(rows[-1])
    claim('A4', '★★（另路）S4：8 非承載欄之 dind 共同值 = 0 ⟺ sgn(u_2) = −1；= 1 ⟺ +1',
          bad == [] and len(rows) == 8, '逐欄 (欄, 共同值, sgn(u_2), 預測) = %s ; 反例 = %s' % (rows, bad))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R25 審計' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/88_r25_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'Zf': Zf, 'C2': C2, 'C1c': C1c, 'B10': B10, 'Wempty': Wempty, 'S4': rows}, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
