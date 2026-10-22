#!/usr/bin/env python3
"""O225 scripts/19 -- R4 獨立審計（唔 import scripts/18；自建 K、自建乘積、自算 R、自建軸商）。

A1 自建 K == 機器 K（0 例外；若用粗糙符號則必然唔等 —— 反證審計須用精確 Z[√5] 符號）
A2 軸對 62 = 31×2，型別 15/10/6（用元組精確比較，唔用除法）
A3 R ∈ {−10,+10}；tie 每 row 5 對；R = 2τ·n_tie
A4 乘積層讀出 == M-b（全部條目）；非 tie == 機器 K
A5 u-宇稱二分（50 個用另一生成器造嘅旋轉機器）
A6 6 軸商（用 KV 值之精確 ± 分群，另一路線；每軸 20 態、tie 集恆定）
用法: /usr/bin/python3 scripts/19_r4_audit.py
"""
import collections
import importlib.util
import io
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def A(x, y):
    return (x[0] + y[0], x[1] + y[1])


def M(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])


def Ng(x):
    return (-x[0], -x[1])


def sg(x):
    if x[1] == 0:
        return (x[0] > 0) - (x[0] < 0)
    if x[0] == 0:
        return (x[1] > 0) - (x[1] < 0)
    if (x[0] > 0) == (x[1] > 0):
        return 1 if x[0] > 0 else -1
    lhs, rhs = x[0] * x[0], 5 * x[1] * x[1]
    if lhs == rhs:
        return 0
    return (1 if lhs > rhs else -1) * (1 if x[0] > 0 else -1)


def crude(x):
    """故意用「首個非零分量」——錯語義，用嚟反證審計必須精確。"""
    return (x[0] > 0) - (x[0] < 0) if x[0] != 0 else ((x[1] > 0) - (x[1] < 0))


def D(u, r):
    return A(A(M(u[0], r[0]), M(u[1], r[1])), M(u[2], r[2]))


def X(u, r):
    return (A(M(u[1], r[2]), Ng(M(u[2], r[1]))),
            A(M(u[2], r[0]), Ng(M(u[0], r[2]))),
            A(M(u[0], r[1]), Ng(M(u[1], r[0]))))


def fs(v):
    for c in v:
        s = sg(c)
        if s:
            return s
    return 0


def splitmix64(state):
    state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return state, z ^ (z >> 31)


def main():
    print('=' * 112)
    print('O225 scripts/19 -- R4 INDEPENDENT AUDIT')
    print('=' * 112, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r4a_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    G, _idx, _M = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r4a_a2').build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]

    # A1：自建 K（精確 sgn）vs 機器 K；並示粗糙符號必然唔等
    Kown = []
    Kbad = []
    for s in range(n):
        r = KV[s]
        row = []
        rowbad = []
        for a in range(ncol):
            d = D(U[a], r)
            sd = sg(d)
            if sd == 0:
                sd = fs(r)
            row.append(sd)
            dbad = crude(d)
            if dbad == 0:
                dbad = fs(r)
            rowbad.append(dbad)
        Kown.append(row)
        Kbad.append(rowbad)
    mm_own = sum(1 for s in range(n) for a in range(ncol) if Kown[s][a] != K[s][a])
    mm_bad = sum(1 for s in range(n) for a in range(ncol) if Kbad[s][a] != K[s][a])
    claim('A1', '自建 K（精確 Z[√5] 符號）== 機器 K（0 例外）；粗糙「首非零分量」符號必然唔等（反證審計須精確）',
          mm_own == 0 and mm_bad > 0,
          'exact mismatches = %d ; crude mismatches = %d / %d' % (mm_own, mm_bad, n * ncol))

    # A2：軸對（元組精確負）
    pr = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and U[i][0] == Ng(U[j][0]) and U[i][1] == Ng(U[j][1]) and U[i][2] == Ng(U[j][2]):
                pr[i] = j
    kk = sorted(set(min(i, pr[i]) for i in range(ncol)))
    tc = collections.Counter(types[k] for k in kk)
    claim('A2', '62 軸恰成 31 對精確負（元組比較）；型別 15 edge + 10 face + 6 vertex',
          len(pr) == 62 and len(kk) == 31 and tc == collections.Counter({'edge': 15, 'face': 10, 'vertex': 6}),
          'paired=%d pairs=%d types=%s' % (len(pr), len(kk), dict(tc)))

    # A3：R、tie、τ
    tie = {}
    ntp = []
    tau = []
    for s in range(n):
        t = [a for a in range(ncol) if sg(D(U[a], KV[s])) == 0]
        tie[s] = t
        ntp.append(len(t) // 2)
        tau.append(fs(KV[s]))
    R = [sum(K[s]) for s in range(n)]
    claim('A3', 'tie 每 row 恰 5 對；R ∈ {−10,+10}；R = 2·τ·n_tie 逐 row',
          sorted(set(ntp)) == [5] and sorted(set(R)) == [-10, 10]
          and all(R[s] == 2 * tau[s] * ntp[s] for s in range(n)),
          'n_tie=%s R=%s' % (sorted(set(ntp)), sorted(set(R))))

    # A4：乘積層 vs M-b vs 機器
    Kcan = [[(sg(D(U[a], KV[s])) if sg(D(U[a], KV[s])) != 0 else fs(X(U[a], KV[s]))) for a in range(ncol)]
            for s in range(n)]
    Kmb = [[fs((D(U[a], KV[s]),) + X(U[a], KV[s])) for a in range(ncol)] for s in range(n)]
    eq_mb = sum(1 for s in range(n) for a in range(ncol) if Kcan[s][a] == Kmb[s][a])
    off = [(s, a) for s in range(n) for a in range(ncol) if tie[s].count(a) == 0]
    eq_off = sum(1 for (s, a) in off if Kcan[s][a] == K[s][a])
    eq_tie = sum(1 for s in range(n) for a in tie[s] if Kcan[s][a] == K[s][a])
    n_tie_tot = sum(len(v) for v in tie.values())
    claim('A4', '乘積層讀出 == M-b 全部條目；非 tie == 機器 K；tie 只部分一致',
          eq_mb == n * ncol and eq_off == len(off) and eq_tie < n_tie_tot,
          'canon=Mb %d/%d ; off %d/%d ; tie %d/%d' % (eq_mb, n * ncol, eq_off, len(off), eq_tie, n_tie_tot))

    # A5：u-宇稱二分（另一生成器：旋轉 KV 而非軸表）
    seed = 777123
    ok_e = ok_o = 0
    for m in range(50):
        seed, r1 = splitmix64(seed)
        h = G[r1 % n]
        KVm = [mm.rot_ref(g, U[0]) for g in G]
        KVm = [mm.rot_ref(h, v) for v in KVm]
        te = to = 0
        good_e = good_o = True
        for s in range(n):
            acc_e = acc_o = 0
            ntp2 = 0
            for a in range(ncol):
                d = D(U[a], KVm[s])
                sd = sg(d)
                if sd:
                    acc_e += sd
                    acc_o += sd
                else:
                    ntp2 += 1
                    acc_e += fs(KVm[s])
                    acc_o += fs(X(U[a], KVm[s]))
            if ntp2 % 2:
                good_e = False
            if acc_e != 2 * (ntp2 // 2) * fs(KVm[s]):
                good_e = False
            if acc_o != 0:
                good_o = False
        ok_e += 1 if good_e else 0
        ok_o += 1 if good_o else 0
    claim('A5', '50 個（另一生成器）旋轉機器：u-偶 ⟹ R = 2·τ·n_tie；u-奇 ⟹ R ≡ 0',
          ok_e == 50 and ok_o == 50, 'u-even ok = %d/50 ; u-odd ok = %d/50' % (ok_e, ok_o))

    # A6：6 軸商（由 KV 值之 ± 分群，另一路線）
    lines = {}
    seen = set()
    for s in range(n):
        if s in seen:
            continue
        lines[s] = [s]
        seen.add(s)
        for t in range(s + 1, n):
            same = (KV[t][0] == KV[s][0] and KV[t][1] == KV[s][1] and KV[t][2] == KV[s][2])
            oppo = (KV[t][0] == Ng(KV[s][0]) and KV[t][1] == Ng(KV[s][1]) and KV[t][2] == Ng(KV[s][2]))
            if same or oppo:
                lines[s].append(t)
                seen.add(t)
    sizes = collections.Counter(len(v) for v in lines.values())
    tiesets_by_line = {}
    for s, grp in lines.items():
        tiesets_by_line[s] = set(tuple(sorted(min(a, pr[a]) for a in tie[t])) for t in grp)
    claim('A6', '軸商（KV 之精確 ± 分群）：6 條線、每線 20 態、tie 集恆定於線',
          len(lines) == 6 and sizes == collections.Counter({20: 6})
          and all(len(v) == 1 for v in tiesets_by_line.values()),
          'lines = %d ; sizes = %s ; tie set 數 = %d'
          % (len(lines), dict(sizes), len(set(next(iter(v)) for v in tiesets_by_line.values()))))

    out = {'audit_of': '18_r4_tie_parity.py', 'A1': {'exact_mismatch': mm_own, 'crude_mismatch': mm_bad},
           'A2': {'pairs': len(kk), 'types': dict(tc)}, 'A3': {'n_tie': sorted(set(ntp)), 'R': sorted(set(R))},
           'A4': {'canon_eq_Mb': eq_mb, 'off_match': eq_off, 'n_off': len(off), 'tie_match': eq_tie, 'n_tie': n_tie_tot},
           'A5': {'even_ok': ok_e, 'odd_ok': ok_o}, 'A6': {'lines': len(lines), 'sizes': dict(sizes)},
           'claims': CLAIMS}
    with io.open(os.path.join(DATA, '19_r4_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
