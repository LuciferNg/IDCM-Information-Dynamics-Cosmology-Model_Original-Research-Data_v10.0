#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/99 -- 審計缺口補完（GAP-1/2）：獨立重算 Λ_a(s)／Z10 選擇律、f 三重、三支和。

缺口（docs/57 §六）：(i) Λ_a(s) 逐欄貢獻、(ii) f_tf／f_ft／f_tt 之事件三元配對 —— 兩者定義僅存在於
R20／R9 機器碼內。本支由**凍結定義**（事件堆疊協議、tie/dind/ε、逐欄分支式）自行實作重算，並作
**兩條獨立路線互證**（Λ-判據 vs f-判據），並核 R9 之 A2／A2c／A5ac／A5bc 與 R25 之 C2／R4-c。

精確算術；唯讀 O222 機器。用法: /usr/bin/python3 scripts/99_gap_blind.py
"""
import hashlib
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RES = []


def check(tag, name, ok, detail=''):
    RES.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
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


def dot3(u, v):
    return add(add(mul(u[0], v[0]), mul(u[1], v[1])), mul(u[2], v[2]))


def cross3(u, v):
    return (add(mul(u[1], v[2]), neg(mul(u[2], v[1]))),
            add(mul(u[2], v[0]), neg(mul(u[0], v[2]))),
            add(mul(u[0], v[1]), neg(mul(u[1], v[0]))))


def firstsgn(v):
    for c in v:
        s = sgn(c)
        if s:
            return s
    return 0


def main():
    print('=' * 118)
    print('O225 scripts/99 -- 缺口補完（Λ/Z10、f 三重、三支和；兩路線互證）')
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'b99')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'b99a')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    e = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    inv = [next(j for j in range(n) if MUL[i][j] == e) for i in range(n)]
    tie = [[dot3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    dind = [[(1 if firstsgn(cross3(U[a], KV[s])) != eps[s] else 0) if tie[s][a] else 0
             for a in range(ncol)] for s in range(n)]

    def events_own(state):
        st, stk, ev = state, [], []
        for c1 in range(ncol):
            for c2_ in range(ncol):
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

    my_ev = events_own(e)
    d34 = json.load(io.open(os.path.join(BASE, 'data/34_r9_pairing.json'), encoding='utf-8'))
    sha = hashlib.sha256(repr(my_ev).encode()).hexdigest()
    check('G0', '事件協議重現：自寫事件集 sha256 符 data/34（%d 條）' % len(my_ev), sha == d34['events_sha'],
          'sha…%s' % sha[:16])

    # ---- GAP-1：Λ_a(s) 獨立重算 ----
    Lam = [[0] * n for _ in range(ncol)]
    f = {'tf': [0] * n, 'ft': [0] * n, 'tt': [0] * n}
    for s0 in range(n):
        for (a, sw, sr) in my_ev:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = tie[w][a], tie[r2][a]
            if tw and tr:
                f['tt'][s0] += (0 if dind[r2][a] == dind[w][a] else 1) * eps[r2] * eps[w]
            elif tr:
                v = dind[r2][a] * eps[r2] * sgn(dot3(U[a], KV[w]))
                f['tf'][s0] += v
                Lam[a][s0] += v
            elif tw:
                v = dind[w][a] * eps[w] * sgn(dot3(U[a], KV[r2]))
                f['ft'][s0] += v
                Lam[a][s0] += v
    odd = [(a, s0) for a in range(ncol) for s0 in range(n) if Lam[a][s0] % 2 != 0]
    check('G1', 'Λ_a(s) 奇偶律：奇異 (欄,態) = 64 且全屬第 61 欄（R20 T1／T1-c）',
          len(odd) == 64 and sorted(set(a for a, _ in odd)) == [61], '奇數單元 = %d；欄集 = %s'
          % (len(odd), sorted(set(a for a, _ in odd))))
    support = sorted(a for a in range(ncol) if any(Lam[a][s] != 0 for s in range(n)))
    d70 = json.load(io.open(os.path.join(BASE, 'data/70_r20_machine.json'), encoding='utf-8'))
    check('G2', 'Λ 支撐 = 16 欄，且與凍結 data/70 之 support 逐字相同', support == d70['support'],
          '支撐 = %s' % support)
    Zl = sorted(s for s in range(n) if sum(Lam[a][s] for a in range(ncol)) == 0
                and max(abs(Lam[a][s]) for a in range(ncol)) <= 2)
    check('G3', '★ Z10 選擇律（Λ-判據；C2 = Σ_a Λ_a = 0 ∧ max|Λ| ≤ 2）：120 態解集恰 10 態，且 = 凍結 Z10',
          len(Zl) == 10 and Zl == d70['Z10'], '解集（%d）= %s' % (len(Zl), Zl))

    # ---- GAP-2：f 三重（與凍結 R8 陣列對帳） ----
    d31 = json.load(io.open(os.path.join(BASE, 'data/31_r8_group.json'), encoding='utf-8'))
    diff = {k: sum(1 for s in range(n) if f[k][s] != d31['f_' + k][s]) for k in ('tf', 'ft', 'tt')}
    check('G4', 'f_tf／f_ft／f_tt 獨立重算：與凍結 data/31 之三陣列**逐態全同**（120×3）',
          all(v == 0 for v in diff.values()), '逐態差異 = %s' % diff)
    Zf = sorted(s for s in range(n) if f['tf'][s] + f['ft'][s] == 0)
    Zfc = sorted(s for s in range(n) if f['tf'][s] == -f['ft'][s] and f['tf'][s] != 0)
    check('G5', '★ 兩路線互證：{f_tf + f_ft = 0} = {f_tf = −f_ft ≠ 0} = Z10（Λ-判據）—— 同一 10 態',
          Zf == Zl == Zfc, 'f 路線 = %d、抵消態路線 = %d' % (len(Zf), len(Zfc)))
    check('G6', 'Σ_{s0} f_tf = Σ f_ft = 0、Σ f_tt = 64（R9 A2／A2c 之值）',
          (sum(f['tf']), sum(f['ft']), sum(f['tt'])) == (0, 0, 64),
          'Σ = (%d, %d, %d)' % (sum(f['tf']), sum(f['ft']), sum(f['tt'])))

    # ---- 三支和（(a,g) 鍵、逐 x 分類；R9 校正版 = R26 之 S_TT） ----
    keys = {}
    for (a, sw, sr) in my_ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1
    S = {}
    for (a, g) in keys:
        kv_g = KV[g]
        sTF = sFT = sTT = 0
        for x in range(n):
            y = MUL[x][g]
            tx = tie[x][a]
            ty = tie[y][a]
            if tx and ty:
                sTT += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
            elif tx and not ty:
                sTF += dind[x][a] * eps[x] * sgn(dot3(U[a], mm.rot_ref(G[x], kv_g)))
            elif ty and not tx:
                sFT += dind[y][a] * eps[y] * sgn(dot3(U[a], KV[x]))
        S[(a, g)] = (sTF, sFT, sTT)
    sumTF = sum(keys[k] * S[k][0] for k in keys)
    sumFT = sum(keys[k] * S[k][1] for k in keys)
    sumTT = sum(keys[k] * S[k][2] for k in keys)
    nzTF = [k for k in keys if S[k][0] != 0]
    nzFT = [k for k in keys if S[k][1] != 0]
    nzTT = [k for k in keys if S[k][2] != 0]
    check('G7', '★ A5ac：S_TF ≡ 0 且 S_FT ≡ 0（逐鍵局部消失；%d 鍵全檢）' % len(keys),
          not nzTF and not nzFT, '非零鍵 = %d／%d' % (len(nzTF), len(nzFT)))
    check('G8', '★ A5bc：S_TT 值集 = {−8,0,8}、非零鍵 12、Σ n·S_TT = 64',
          sorted(set(v[2] for v in S.values())) == [-8, 0, 8] and len(nzTT) == 12 and sumTT == 64,
          '值集 = %s；非零鍵 = %d；Σ n·S_TT = %d' % (sorted(set(v[2] for v in S.values())), len(nzTT), sumTT))
    check('G9', '★ A2c 恆等式：Σ n·S_TF = Σ_{s0} f_tf、Σ n·S_FT = Σ f_ft、Σ n·S_TT = Σ f_tt（= 0／0／64）',
          (sumTF, sumFT, sumTT) == (sum(f['tf']), sum(f['ft']), sum(f['tt'])),
          '鍵側 = (%d, %d, %d)；態側 = (%d, %d, %d)' % (sumTF, sumFT, sumTT, sum(f['tf']), sum(f['ft']), sum(f['tt'])))

    # ---- R25 R4／R4-c：算子形式與界條件必要性 ----
    posneg = sorted(s for s in range(n)
                    if sum(1 for a in support if Lam[a][s] > 0) == sum(1 for a in support if Lam[a][s] < 0)
                    and any(Lam[a][s] != 0 for a in support))
    check('G10', '★ R25 R4／R4-c：support 16 欄之（正項數 = 負項數 ∧ 非零）解集 = %d ⊋ Z10（10）' % len(posneg),
          set(Zl) <= set(posneg) and len(posneg) > 10, '解集 = %d；多出 = %s' % (len(posneg), sorted(set(posneg) - set(Zl))))

    io.open(os.path.join(BASE, 'data', '99_gap_blind.json'), 'w', encoding='utf-8').write(json.dumps(
        {'script': '99_gap_blind', 'checks': RES, 'Z10': Zl, 'support': support, 'sum_f': [sum(f['tf']), sum(f['ft']), sum(f['tt'])],
         'S_TT_nonzero_keys': len(nzTT), 'posneg_set': posneg}, indent=1, ensure_ascii=False))
    p = sum(1 for r in RES if r['ok'])
    print('\nRESULT: %d/%d PASS' % (p, len(RES)))
    return 0 if p == len(RES) else 1


if __name__ == '__main__':
    raise SystemExit(main())
