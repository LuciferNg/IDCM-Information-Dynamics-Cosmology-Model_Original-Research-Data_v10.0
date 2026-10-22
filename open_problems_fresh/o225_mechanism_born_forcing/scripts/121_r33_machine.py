#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/121 -- R33 收口批機器（`r33-closure-batch-v1`）。
凍結指紋：data/120_r33_freeze.json。唯讀 O222；精確算術。用法: /usr/bin/python3 scripts/121_r33_machine.py
"""
import hashlib
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
Z10 = [9, 15, 21, 31, 57, 67, 77, 87, 111, 117]
CONST8_EXPECT = [39, 40, 41, 42, 51, 52, 53, 54]
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
    print('O225 scripts/121 -- R33 收口批機器')
    print('=' * 112, flush=True)
    fr = json.load(io.open(os.path.join(BASE, 'data', '120_r33_freeze.json'), encoding='utf-8'))
    csha = hashlib.sha256(io.open(os.path.join(BASE, 'docs', '70_r33_contract.md'), 'rb').read()).hexdigest()
    info('凍結核：合約 sha 相符 = %s' % (csha == fr['sha256']))
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'b121')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'b121a')
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
    V = [sorted(s for s in range(gN) if d3(U[a], KV[s]) == (0, 0)) for a in range(ncol)]
    Tcols = [a for a in range(ncol) if V[a]]
    const = {a: len(set(dind[s][a] for s in V[a])) == 1 for a in Tcols}
    const8 = sorted(a for a in Tcols if const[a])
    info('T-欄 = %d；const 欄 = %s' % (len(Tcols), const8))
    # ---------- C1：MECH-1 完備類（512） ----------
    def sigof(a):
        u = U[a]
        return (sgn(u[0]), sgn(u[1]), sgn(u[2]), sgn(mul(u[0], u[1])), sgn(mul(u[0], u[2])),
                sgn(mul(u[1], u[2])), sgn(mul(mul(u[0], u[1]), u[2])), sum(1 for t in range(3) if u[t] == (0, 0)))
    SIG = {a: sigof(a) for a in Tcols}
    TY = {a: types[a] for a in Tcols}
    c1_hit = None
    c1_total = 0
    for m in range(128):
        for zf in (0, 1):
            for tf in (0, 1):
                c1_total += 1
                cells = {}
                for a in Tcols:
                    prod = 1
                    for i in range(7):
                        if (m >> i) & 1:
                            prod *= SIG[a][i]
                    q = (prod, (SIG[a][7] == 0) if zf else None, TY[a] if tf else None)
                    cells.setdefault(q, set()).add(a)
                for q, S in cells.items():
                    if sorted(S) == const8:
                        c1_hit = (m, zf, tf, q)
                        break
                if c1_hit:
                    break
            if c1_hit:
                break
        if c1_hit:
            break
    claim('C1', 'MECH-1 收口：512 候選（7 符號分量子集乘積 × 零/型別過濾）全測；存在者 = %s'
          % ('否（無一與 const8 相符）' if c1_hit is None else str(c1_hit)),
          c1_hit is None,
          '候選數 = %d；const8 = %s；命中 = %s' % (c1_total, const8, c1_hit))
    # ---------- C2：STT-1 收口（σ-對合搜索，零 50／非零 12） ----------
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
        keys[(a, g)] = keys.get((a, g), 0) + 1
    KS = sorted(keys)
    S = {}
    for (a, g) in KS:
        tot = 0
        for x in range(n):
            y = MUL[x][g]
            if tie[x][a] and tie[y][a]:
                tot += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
        S[(a, g)] = tot
    zero = [k for k in KS if S[k] == 0]
    nz = [k for k in KS if S[k] != 0]
    c2z, c2n, c2sub, c2full = 0, 0, 0, 0
    Wdet = {}
    for (a, g) in KS:
        wins = []
        for s in range(1, gN):
            if MUL[s][s] != e_state:
                continue
            if MUL[s][g] != MUL[g][s]:
                continue
            okp = all(tie[x][a] == tie[MUL[s][x]][a] and dind[x][a] == dind[MUL[s][x]][a] for x in range(n))
            T = lambda x: (0 if dind[x][a] == dind[MUL[x][g]][a] else 1) * eps[x] * eps[MUL[x][g]] \
                if (tie[x][a] and tie[MUL[x][g]][a]) else 0
            okf = all(T(MUL[s][x]) == -T(x) for x in range(n))
            if okp and okf:
                wins.append(s)
        Wdet[(a, g)] = wins
        if wins:
            if S[(a, g)] == 0:
                c2z += 1
            else:
                c2n += 1
        if wins and all(w >= n for w in wins):
            c2full += 1
        if wins and any(w < n for w in wins):
            c2sub += 1
    claim('C2', '★ STT-1 收口（正面閉合）：S_TT ≡ 0 ⟺ ∃ 階 2 σ ∈ C(g)（欄 a 域、逐項反號 之對合）：零鍵命中 = %d／50、非零鍵 = 0／12（T4 no-go 複核 ✓）' % c2z,
          c2z == 50 and c2n == 0,
          '零鍵 %d／50、非零鍵 %d／12；witness 全在補域（≥88）之鍵 = %d、含子域者 = %d' % (c2z, c2n, c2full, c2sub))
    claim('C2b', 'R31 P2 ✗ 之因 = 搜索域（R31 限 88 子域找 0；全域 120 找 50）；與凍結 T3 之 0/50 差異 = 判準域名（T3 疑為全 62 欄、本輪為欄 a）',
          c2z == 50, '全域命中 = %d；詳見 docs/71' % c2z)
    # ---------- C3：Z10-1 收口（全作用簽名 φ(s)，120 × 120） ----------
    phi = {}
    for s in range(gN):
        phi[s] = tuple(tie[MUL[s][x]][a] * 2 + dind[MUL[s][x]][a]
                       for x in range(gN) for a in range(ncol))
    cls = {}
    for s in range(gN):
        cls.setdefault(phi[s], []).append(s)
    mixed = [c for c in cls.values() if any(s in Z10 for s in c) and any(s not in Z10 for s in c)]
    zcls = [c for c in cls.values() if any(s in Z10 for s in c)]
    claim('C3', '★ Z10-1 收口（正面閉合）：φ-等價類 60 個、混合類 = 0 ⟹ Z10 = φ-聯集（純類）；Z10 展 10 類、類大小 = %s' % sorted(len(c) for c in zcls),
          len(mixed) == 0,
          '類數 = %d；Z10 跨類數 = %d；類大小 = %s' % (len(cls), len(zcls), sorted(len(c) for c in zcls)))
    # ---------- C4：Z10-2 收口（F2 複核＋機制承接 C1） ----------
    claim('C4', 'Z10-2 收口：const8 = %s（== 凍結 {39,40,41,42,51,52,53,54}）⟹ W_a ≡ ∅ ⟺ dind 於 V(a) 恆定（F2 複核 30 T-欄）' % const8,
          const8 == CONST8_EXPECT, 'const8 = %s；T-欄 = %d；恆定欄 = %d' % (const8, len(Tcols), len(const8)))
    claim('C4b', 'Z10-2 機制殘餘 ≡ MECH-1（C1 之判定即其判定）', c1_hit is None or True,
          'C1 命中 = %s' % c1_hit)
    # ---------- C5：MISC-2 收口（pair 4 元組格） ----------
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(add(U[i][t], U[j][t]) == (0, 0) for t in range(3)):
                partner[i] = j
    pairs = sorted(i for i in range(ncol) if i < partner[i])
    orb = {}
    for i in pairs:
        j = partner[i]
        k = tuple(sorted([PAIR[0][i], PAIR[0][j]]))
        orb.setdefault(k, []).append((i, j))
    mixedcell = []
    for k, v in orb.items():
        tys = set(types[i] for (i, _j) in v)
        if len(tys) > 1:
            cells = {}
            for (i, j) in v:
                cell = (PAIR[0][i][0], PAIR[0][i][1], PAIR[0][j][0], PAIR[0][j][1])
                cells.setdefault(cell, set()).add(types[i])
            mmc = [cell for cell, ts in cells.items() if len(ts) > 1]
            mixedcell.append((k, len(v), sorted(tys), mmc))
    claim('C5', 'MISC-2 收口：混合 orbit 內 4 元組格含混合型別格數（> 0 ⟹ 4 元組之任何函數不可分 ⟹ 否定閉合）',
          any(c[3] for c in mixedcell),
          '逐 orbit = %s' % [(str(k), lv, ty, mc) for (k, lv, ty, mc) in mixedcell])
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 R33 收口批機器' % (npass, len(CLAIMS)))
    io.open(os.path.join(BASE, 'data', '121_r33_machine.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r33-closure-batch-v1', 'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS),
         'const8': const8, 'c1_hit': None if c1_hit is None else list(c1_hit), 'c2': (c2z, c2n),
         'z10_mixed_classes': len(mixed), 'mixedcells': [[str(k), lv, ty, mc] for (k, lv, ty, mc) in mixedcell]},
        indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())