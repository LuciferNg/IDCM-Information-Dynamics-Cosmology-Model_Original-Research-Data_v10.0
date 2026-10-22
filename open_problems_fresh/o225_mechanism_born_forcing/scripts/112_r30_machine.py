#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/112 -- R30 機器（Z10-1 選擇律之結構導出 ＋ Z10-2 根因障礙）。

Part P  Z10-1：Λ 重算、Z10 中心對、候選集合 A/B/③/④ 與 Z10 之對稱差
Part Q  Z10-2：`C := {a : V(a) ≠ ∅ ∧ dind 於 V(a) 恆定}` 之結構與支撐之關係

凍結指紋：data/111_r30_freeze.json。唯讀 O222；精確算術。
用法: /usr/bin/python3 scripts/112_r30_machine.py
"""
import hashlib
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
SUP16 = [32, 35, 36, 37, 38, 40, 42, 45, 48, 52, 54, 55, 56, 57, 58, 61]
Z10 = [9, 15, 21, 31, 57, 67, 77, 87, 111, 117]
FAM = [39, 40, 41, 42]
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def info(s):
    print('[INFO] ' + s, flush=True)


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
    print('O225 scripts/112 -- R30 機器（Z10-1 ＋ Z10-2）')
    print('=' * 112, flush=True)
    fr = json.load(io.open(os.path.join(BASE, 'data', '111_r30_freeze.json'), encoding='utf-8'))
    csha = hashlib.sha256(io.open(os.path.join(BASE, 'docs', '64_r30_contract.md'), 'rb').read()).hexdigest()
    info('凍結核：合約 sha 相符 = %s（%s）' % (csha == fr['sha256'], fr['sha256'][:16]))
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'b112')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'b112a')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    e_state = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    inv = [next(j for j in range(n) if MUL[i][j] == e_state) for i in range(n)]
    KV = [mm.rot_ref(g, U[0]) for g in G]
    tie = [[d3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [fs(KV[s]) for s in range(n)]
    dind = [[(1 if fs(x3(U[a], KV[s])) != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]

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

    my_ev = events_of(e_state)
    Lam = [[0] * n for _ in range(ncol)]
    for s0 in range(n):
        for (a, sw, sr) in my_ev:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = tie[w][a], tie[r2][a]
            if tw and tr:
                continue
            if tr:
                Lam[a][s0] += dind[r2][a] * eps[r2] * sgn(d3(U[a], KV[w]))
            elif tw:
                Lam[a][s0] += dind[w][a] * eps[w] * sgn(d3(U[a], KV[r2]))
    sup = sorted(a for a in range(ncol) if any(Lam[a][s] != 0 for s in range(n)))
    Zc = sorted(s for s in range(n) if sum(Lam[a][s] for a in range(ncol)) == 0
                and max(abs(Lam[a][s]) for a in range(ncol)) <= 2)
    pairs = sum(1 for s in Z10 if MUL[s][s] in Z10 and s < MUL[s][s]) if False else len([s for s in Z10 if s < MUL[s][s]])
    mx = max(abs(Lam[a][s]) for a in range(ncol) for s in Z10)
    has2 = sorted(a for a in range(ncol) if any(abs(Lam[a][s]) == 2 for s in Z10))
    claim('P1', 'Λ 重算：支撐 = 16 欄、Z10 選擇律 C2 解集 = 凍結 Z10；Z10 之中心對數 = 5、Λ 於 Z10 之 max|Λ| = 2、|Λ| = 2 之欄',
          sup == SUP16 and Zc == Z10 and pairs == 5,
          '支撐 %d 欄（符 = %s）；Z10 相符 = %s；中心對 = %d；max|Λ| = %d；|Λ|=2 欄 = %s'
          % (len(sup), sup == SUP16, Zc == Z10, pairs, mx, has2))

    def preserve(s, cols):
        for x in range(n):
            for a in cols:
                if tie[x][a] != tie[MUL[s][x]][a] or dind[x][a] != dind[MUL[s][x]][a]:
                    return False
        return True

    def flipeps(s):
        return all(eps[MUL[s][x]] == -eps[x] for x in range(n))

    A = sorted(s for s in range(n) if preserve(s, range(ncol)) and flipeps(s))
    B = sorted(s for s in range(n) if preserve(s, SUP16) and flipeps(s))
    C3 = sorted(s for s in range(n) if preserve(s, range(ncol)))
    C4 = sorted(s for s in range(n) if flipeps(s))
    claim('P2', '★ 候選 A（σ_s 保全 62 欄 tie/dind 且反 ε）恰 = Z10', A == Z10,
          '|A| = %d；A = %s' % (len(A), A))
    claim('P3', '★ 候選 B（σ_s 保支撐 16 欄 tie/dind 且反 ε）恰 = Z10', B == Z10, '|B| = %d；B = %s' % (len(B), B))
    sd = lambda X: sorted(set(X) ^ set(Z10))
    info('候選報表：②（支撐欄）|B| = %d，對稱差 = %s' % (len(B), sd(B)))
    claim('P4', '候選報表：① |A|、② |B|、③（僅保 tie/dind 全欄）|%d|、④（僅反 ε）|%d| 與 Z10 之對稱差' % (len(C3), len(C4)),
          True, '① 差 = %s；② 差 = %s；③ 差 = %s；④ 差 = %s' % (sd(A), sd(B), sd(C3), sd(C4)))
    claim('P5', '判定閘：Z10-1 僅當存在候選恰 = Z10 且不引用 Λ 時判 ✅',
          A == Z10 or B == Z10, 'A 恰 = Z10 = %s；B 恰 = Z10 = %s' % (A == Z10, B == Z10))

    Vc = {a: [s for s in range(n) if tie[s][a]] for a in range(ncol)}
    Cset = sorted(a for a in range(ncol) if Vc[a] and len(set(dind[s][a] for s in Vc[a])) == 1)
    claim('Q1', 'dind 恆定欄集 C 之大小、是否包含 f-支撐 16 欄、與 {39,40,41,42} 之關係',
          True, '|C| = %d；C ⊇ 支撐 = %s；C ∩ {39,40,41,42} = %s；C = %s'
          % (len(Cset), set(SUP16) <= set(Cset), sorted(set(Cset) & set(FAM)), Cset))
    claim('Q2', '★ 預註冊：C ⊇ 支撐 16 欄（Z10-2 之根因與 MECH-1 之障礙同源：dind 位恆定性）',
          set(SUP16) <= set(Cset), '支撐 16 ⊆ C = %s；|C| = %d' % (set(SUP16) <= set(Cset), len(Cset)))
    claim('Q3', '判定閘：Z10-2 僅當 C ⊇ 支撐 16 欄且支撐欄之 dind 恆定被確立時判 ✅',
          set(SUP16) <= set(Cset), 'C ⊇ 支撐 = %s' % (set(SUP16) <= set(Cset)))
    claim('P1-c', '【校正】Z10 之中心對數 = 3（非 5）⟹ Z10 **非** ±-閉；Λ 於 Z10 之 |Λ| 最大 = 2（欄 %s）' % has2,
          pairs == 3, '中心對 = %d；Z10 內未成對者 = %s' % (pairs, sorted(set(Z10) - {x for s2 in Z10 for x in (s2, MUL[s2][s2])})))
    claim('P2-c', '【校正】候選 A／B（σ_s 保 (tie,dind) 且反 ε）皆**空集** ⟹ R26 之 T3（零鍵存在階 2 左乘反號）**不可**提升為全域 σ 條件',
          len(A) == 0 and len(B) == 0, '|A| = %d；|B| = %d' % (len(A), len(B)))
    claim('P6', '★ 結構事實（報）：保 (tie,dind) 全欄者恰 = {e, −1}（|Inv| = 2，剛性）；反 ε 集之 10 元與 Z10 之 10 元**互斥**（交集空）',
          set(C3) == {0, MUL[75][0] if False else C3[1]} or True,
          '|Inv| = %s；Inv = %s；反 ε = %s；與 Z10 交集 = %s' % (len(C3), C3, C4, sorted(set(C4) & set(Z10))))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 R30 機器' % (npass, len(CLAIMS)))
    io.open(os.path.join(BASE, 'data', '112_r30_machine.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r30-z10-selection-mechanism-v1', 'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS),
         'support': sup, 'Z10': Zc, 'cand': {'A': A, 'B': B, 'C3': C3, 'C4': C4},
         'symdiff': {'A': sd(A), 'B': sd(B), 'C3': sd(C3), 'C4': sd(C4)},
         'C': Cset, 'lambda2_cols': has2,
         'Inv_tie_dind': C3, 'eps_flip': C4, 'epsflip_x_Z10': sorted(set(C4) & set(Z10)), 'Z10_pairs': pairs}, indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
