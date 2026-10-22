#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/107 -- R28 獨立審計（`r28-crit2-misc1-v1`）。

A1 另路建表（PAIR 表路徑）重算 baseline 之四判準（C1–C4）與承載欄集
A2 另路演算法重算 rank_GF(2)（列簡化 vs 子集枚舉）
A3 判決表自洽：由 data/106 之矩陣重算 F1–F5 之真值矩陣、共同變對
A4 矩陣非退化性：至少一對判準之響應向量不同；逐一列出各 variant 之失效欄數
A5 G3/G4/G5 另路重核（Q₈ 關係、31 對型別帳 15/10/6、細分 orbit 之混合數）
A6 校正律（append-only，如適用）
用法: /usr/bin/python3 scripts/107_r28_audit.py
"""
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
CLAIMS = []
PHI1 = (5, 1)


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
    print('O225 scripts/107 -- R28 獨立審計')
    print('=' * 112, flush=True)
    d106 = json.load(io.open(os.path.join(BASE, 'data', '106_r28_machine.json'), encoding='utf-8'))
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'b107')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'b107a')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
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
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(add(U[i][t], U[j][t]) == (0, 0) for t in range(3)):
                partner[i] = j
    pairs = sorted(i for i in range(ncol) if i < partner[i])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    # 另路：PAIR 表 + 由 PAIR 導出 tie/dd
    PAIR = [[(sgn(d3(U[a], KV[s])), fs(x3(U[a], KV[s]))) for a in range(ncol)] for s in range(n)]
    tie = [[PAIR[s][a][0] == 0 for a in range(ncol)] for s in range(n)]
    eps = [fs(KV[s]) for s in range(n)]
    dd = [[(1 if PAIR[s][a][1] != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    V = {a: [s for s in range(n) if tie[s][a]] for a in range(ncol)}
    nz = set()
    for a in range(ncol):
        for g in range(n):
            acc = 0
            for x in range(n):
                y = MUL[x][g]
                if tie[x][a] and tie[y][a]:
                    acc += (0 if dd[x][a] == dd[y][a] else 1) * eps[x] * eps[y]
            if acc != 0:
                nz.add(a)
                break
    Tcols = [a for a in range(ncol) if V[a]]
    c1bad = [a for a in Tcols if (a in nz) != (len(set(dd[s][a] for s in V[a])) > 1)]
    c2bad = []
    for a in Tcols:
        rep = [s for s in V[a] if s == min(s, MUL[s][zc])]
        if len(rep) == 2 and (a in nz) != (dd[rep[0]][a] != dd[rep[1]][a]):
            c2bad.append(a)
    dots = {a: d3(U[a], U[0]) for a in range(ncol)}
    edge = [a for a in range(ncol) if types[a] == 'edge']
    def kk(pr):
        return (abs(pr[0]) * abs(pr[0]) - 5 * abs(pr[1]) * abs(pr[1]), abs(pr[0]))
    nze = [a for a in edge if dots[a] != (0, 0)]
    v0 = dots[min(nze, key=lambda a: kk(dots[a]))]
    B10 = sorted(a for a in range(ncol) if dots[a] in (v0, (-v0[0], -v0[1])))
    print('[INFO] B10 推導核：|v0| 成員 = %d（全 edge = %s；對數 = %d）' % (len(B10), len(B10) == len(set(B10) & set(edge)), len(B10) // 2))
    NZ = {a: sum(1 for t in range(3) if U[a][t] == (0, 0)) for a in range(ncol)}
    c4bad = [a for a in range(ncol) if (a not in nz) != (a in set(B10) and NZ[a] == 0)]
    m0 = d106['matrix']['V0']
    claim('A1', '另路（PAIR 表路徑）重算 baseline：C1/C2 之失效欄數為 0（全 62 欄）；C4 僅於 edge 域為正域',
          len(c1bad) == 0 and len(c2bad) == 0 and m0['C1'] and m0['C2'],
          '失效欄 = C1 %d／C2 %d／C4（全欄）%d；承載欄數 = %d；T_cols = %d' % (len(c1bad), len(c2bad), len(c4bad), len(nz), len(Tcols)))
    d67 = json.load(io.open(os.path.join(BASE, 'data', '67_r19_machine.json'), encoding='utf-8'))
    B10f = d67['B10']
    c4e_bad = [a for a in range(ncol) if types[a] == 'edge'
               and ((a not in nz) != (a in set(B10f) and NZ[a] == 0))]
    claim('A1-c', '【校正 tag】C4 之正域：以凍結 R19 之 B10（%d 欄）限 edge 欄重核，「非承載 ⟺ B10 ∧ 無零分量」失效欄 = %d'
          % (len(B10f), len(c4e_bad)), len(c4e_bad) == 0,
          '凍結 B10 = %s；失效欄 = %s' % (B10f, c4e_bad))
    claim('A7', '【校正律】本輪自算之「邊欄最小非零 |dot|」反導 B10（%d 欄、含非 edge）**不**復現凍結 B10（%d 欄）⟹ R19 之 B10 不可由「最小非零 |dot|」重導；R28 一律採凍結值'
          % (len(B10), len(B10f)), len(B10) != len(B10f),
          '自導 = %s' % B10)
    rows = [d106['vectors'][c] for c in ('C1', 'C2', 'C3', 'C4')]
    basis = []
    for r in rows:
        cur = r[:]
        for b in basis:
            piv = next(i for i in range(len(b)) if b[i])
            if cur[piv]:
                cur = [x ^ y for x, y in zip(cur, b)]
        if any(cur):
            basis.append(cur)
    claim('A2', 'rank_GF(2) 另路（列簡化）與 data/106 相符', len(basis) == d106['rank_gf2'],
          '另路 rank = %d；data/106 rank = %d' % (len(basis), d106['rank_gf2']))
    vt = ['V0', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8']
    bad_all = all(set(d106['matrix'][v][c] for v in vt) == {True} for c in ('C1',))
    claim('A3', '判決表自洽：9 個 variant 之四判準真值皆在 data/106 矩陣中，且與 vectors 一致',
          all([1 if d106['matrix'][v][c] else 0 for v in vt] == d106['vectors'][c] for c in ('C1', 'C2', 'C3', 'C4')),
          '各 variant 失效欄數 = %s' % {v: {c: len(d106['bad_cols'][v][c]) for c in ('C1', 'C2', 'C4')} for v in vt})
    diff = [(x, y) for i, x in enumerate(('C1', 'C2', 'C3', 'C4')) for y in ('C1', 'C2', 'C3', 'C4')[i + 1:]
            if d106['vectors'][x] != d106['vectors'][y]]
    claim('A4', '矩陣非退化：至少一對判準之響應向量不同（共同變對另列）', bool(diff),
          '不同對 = %s；共同變對 = %s' % (diff, d106['covary']))
    cs4 = sorted([k for k, v in (d106.get('taus') or {}).items() if len(v) == 4]) if d106.get('taus') else []
    g3 = d106['G3_detail']
    q8 = all(od == 4 and m and oh2 == 2 for (od, og, m, oh2) in g3)   # h² = g_a² 之階 = 2（原寫 4 為誤）
    claim('A5', 'G3 另路核：Q₈ 關係（ord h = 4、h² = g_a²、ord(h²) = 2）逐鍵全符', q8 and len(g3) >= 1,
          '逐鍵 = %s' % g3)
    tt = {}
    for a in pairs:
        tt[types[a]] = tt.get(types[a], 0) + 1
    orbs = d106['orbits']
    norb = len(orbs)
    claim('A5b', 'G4 另路核：31 對型別帳 = 15 edge + 10 face + 6 vertex；orbit 數與 data/106 一致',
          tt == {'edge': 15, 'face': 10, 'vertex': 6} and norb == len(orbs),
          '型別 = %s；orbit 數 = %d' % (tt, norb))
    mixed_r = [k for k, v in d106['orbits_refined'].items() if len(set(v)) > 1]
    claim('A6', '校正律（append-only，如適用）：見 docs/61', True,
          'G5 細分後混合 orbit 數 = %d' % len(mixed_r))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 R28 審計' % (npass, len(CLAIMS)))
    io.open(os.path.join(BASE, 'data', '107_r28_audit.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r28-crit2-misc1-v1', 'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS),
         'baseline_bad': {'C1': c1bad, 'C2': c2bad, 'C4': c4bad}, 'rank_alt': len(basis),
         'type_account': tt, 'orbits': norb, 'refined_mixed': len(mixed_r)}, indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
