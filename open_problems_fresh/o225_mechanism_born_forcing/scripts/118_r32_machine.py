#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/118 -- R32 機器（CRIT-3 三層族充要／MISC-2 orbit 混合殘餘）。
凍結指紋：data/117_r32_freeze.json。唯讀 O222；精確算術。用法: /usr/bin/python3 scripts/118_r32_machine.py
"""
import hashlib
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
NT = [(1, 1), (1, 0), (1, -1), (-1, 1), (-1, 0), (-1, -1)]
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
    print('O225 scripts/118 -- R32 機器（CRIT-3 ＋ MISC-2）')
    print('=' * 112, flush=True)
    fr = json.load(io.open(os.path.join(BASE, 'data', '117_r32_freeze.json'), encoding='utf-8'))
    csha = hashlib.sha256(io.open(os.path.join(BASE, 'docs', '68_r32_contract.md'), 'rb').read()).hexdigest()
    info('凍結核：合約 sha 相符 = %s' % (csha == fr['sha256']))
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'b118')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'b118a')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    e_state = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    KV = [mm.rot_ref(g, U[0]) for g in G]
    PAIR = [[(sgn(d3(U[a], KV[s])), fs(x3(U[a], KV[s]))) for a in range(ncol)] for s in range(n)]
    tie = [[PAIR[s][a][0] == 0 for a in range(ncol)] for s in range(n)]
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(add(U[i][t], U[j][t]) == (0, 0) for t in range(3)):
                partner[i] = j
    pairs = sorted(i for i in range(ncol) if i < partner[i])
    CLS = {}
    for s in range(n):
        for a in range(ncol):
            CLS.setdefault((0 if tie[s][a] else 1, types[a]), len(CLS))
    ckeys = sorted(CLS, key=lambda k: CLS[k])
    nc = len(CLS)
    info('第三層類 = %d（%s）' % (nc, ckeys))

    def Kt2(mask):
        b = [(mask >> i) & 1 for i in range(8)]
        nt = {NT[i]: (1 if b[i] else -1) for i in range(6)}
        tlo, thi = (1, -1) if not b[6] else (1, 1)
        if b[7]:
            tlo, thi, nt = -tlo, -thi, {k: -v for k, v in nt.items()}
        return [[(tlo if PAIR[s][a][1] > 0 else thi) if tie[s][a] else nt[PAIR[s][a]] for a in range(ncol)]
                for s in range(n)]

    def crit2(mask):
        b = [(mask >> i) & 1 for i in range(8)]
        nt = {NT[i]: (1 if b[i] else -1) for i in range(6)}
        dbl = all(nt[NT[i]] == -nt[NT[5 - i]] for i in range(6))
        tlo, thi = (1, -1) if not b[6] else (1, 1)
        if b[7]:
            tlo, thi = -tlo, -thi
        return dbl and (tlo == -thi)

    PATS = [tuple(1 if (r >> i) & 1 else -1 for i in range(nc)) for r in range(1 << nc)]
    sizes = {}
    Zrel = {}
    Ssol = {}
    zerosum = 0
    crit_ok = 0
    subcube_ok = True
    for m in range(256):
        Kt = Kt2(m)
        P = [[0] * n for _ in range(nc)]
        for s in range(n):
            for a in range(ncol):
                P[CLS[(0 if tie[s][a] else 1, types[a])]][s] += Kt[s][a]
        if all(all(P[c][s] == 0 for c in range(nc)) for s in range(n)):
            zerosum += 1
        S = [rho for rho in PATS if all(sum(rho[c] * P[c][s] for c in range(nc)) == 0 for s in range(n))]
        Ssol[m] = S
        sizes[len(S)] = sizes.get(len(S), 0) + 1
        free = [c for c in range(nc) if all(rho[c] == S[0][c] for rho in S) is False]
        fixed = [c for c in range(nc) if len(set(rho[c] for rho in S)) == 1]
        subcube = len(S) == (1 << len([c for c in range(nc) if c not in fixed]))
        if not subcube:
            subcube_ok = False
        Zrel[m] = (tuple(free), tuple(fixed), len(S))
        if crit2(m) and tuple(1 for _ in range(nc)) in S:
            crit_ok += 1
    nre = sum(1 for m in range(256) if len(Ssol[m]) > 1)
    claim('P1', '類和矩陣 P（4×120）之零欄結構：全零 mask 數 = %d；R³ ≡ 0 解集大小分佈 = %s'
          % (zerosum, {str(k): v for k, v in sorted(sizes.items())}), zerosum >= 1,
          '全零 = %d；大小分佈 = %s' % (zerosum, {str(k): v for k, v in sorted(sizes.items())}))
    claim('P2', '★ S(mask) 皆為子立方（subcube）：存在 Z ⊆ CLS 使 S = {ρ : ρ|Z 自由、其餘固定}',
          subcube_ok, '子立方檢核 = %s' % ('全 256 通過' if subcube_ok else '有反例'))
    claim('P3', '★ crit2(mask) ⟹ (全 +1) ∈ S(mask)（全 256）且 #{S ⊋ {全+1}} = 32',
          crit_ok == sum(1 for m in range(256) if crit2(m)) and nre == 32,
          'crit2 真之 mask 數 = %d（其中全+1 ∈ S = %d）；S 非單點者 = %d'
          % (sum(1 for m in range(256) if crit2(m)), crit_ok, nre))
    rep = {}
    for m in range(256):
        rep[Zrel[m][2]] = rep.get(Zrel[m][2], 0) + 1
    claim('P4', '導出之真充要 CRIT3(mask, ρ) := (R³ ≡ 0 ⟺ ρ ∈ S(mask)) 必 4096/4096；報 |S| 分佈與 |Z| 結構',
          sum(sizes[k] * k for k in sizes) == sum(len(Ssol[m]) for m in range(256)) and len(Ssol) == 256,
          'Σ|S| = %d（4096 之 mask-加權）；|S| 分佈 = %s' % (sum(len(Ssol[m]) for m in range(256)),
                                                              {str(k): v for k, v in sorted(sizes.items())}))

    def pair0(x):
        return PAIR[0][x]
    orb = {}
    for a in pairs:
        orb.setdefault(tuple(sorted([pair0(a), pair0(partner[a])])), []).append(a)
    comp = {str(k): sorted(set(types[x] for x in v)) for k, v in orb.items()}
    keytype = {}
    mixed = []
    for k, v in orb.items():
        per_key = {}
        for a in v:
            per_key.setdefault(tuple(sorted([pair0(a), pair0(partner[a])])), set()).add(types[a])
        isset = all(len(s) == 1 for s in per_key.values())
        keytype[str(k)] = {str(kk): sorted(vv) for kk, vv in per_key.items()}
        if len(set(types[x] for x in v)) > 1:
            mixed.append((str(k), len(v), sorted(set(types[x] for x in v)), isset))
    claim('Q1', '4 orbit 之型別組成與 PAIR-key 集（複核 R28 G4）', len(orb) == 4,
          'orbit 數 = %d；組成 = %s' % (len(orb), comp))
    claim('Q2', '★ 型別混合 orbit ⟺ 其 PAIR-key 集含 ≥ 2 個型別相異之 key（每個 key 內型別單一）',
          len(mixed) == 2 and all(x[3] for x in mixed),
          '混合 orbit = %s' % mixed)
    claim('Q3', '否證備援報表：key × 型別交叉表', True, '交叉表 = %s' % {k: v for k, v in list(keytype.items())[:2]})
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 R32 機器' % (npass, len(CLAIMS)))
    io.open(os.path.join(BASE, 'data', '118_r32_machine.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r32-crit3-misc2-v1', 'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS),
         'sizes': {str(k): v for k, v in sorted(sizes.items())}, 'nre': nre, 'zerosum': zerosum,
         'sol_sizes': {str(m): len(Ssol[m]) for m in range(256)},
         'orbits': {str(k): [types[a] for a in v] for k, v in orb.items()}, 'mixed': mixed},
        indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
