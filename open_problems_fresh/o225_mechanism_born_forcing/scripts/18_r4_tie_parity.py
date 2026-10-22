#!/usr/bin/env python3
"""O225 scripts/18 -- R4 機器：tie 宇稱之代數來源（`r4-tie-parity-v1`）。

P1 軸對結構 / P2 對消-相加 / P3 R1 重導（R = 2·τ·n_tie ⟹ Δ=20, m_min=10）
P4 正則性（乘積層讀出 vs M-b vs 機器）/ P5 u-宇稱充要（候選族逐個算 R）
P6 6 軸商 / P7 子表 + 200 旋轉機器 / P8 tie 位之分解（障礙位 vs R-中性位）
精確算術（Z[√5]，Fraction）；零浮點；上游 O222 唯讀。
用法: /usr/bin/python3 scripts/18_r4_tie_parity.py
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
RULES = 'r4-tie-parity-v1'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-6s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def mul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])


def neg(x):
    return (-x[0], -x[1])


def sgn(x):
    """Z[√5] 精確符號（p² vs 5q²），與 O222 09_a2_rollback.sgn 同義。"""
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


def dot3(u, r):
    return add(add(mul(u[0], r[0]), mul(u[1], r[1])), mul(u[2], r[2]))


def cross3(u, r):
    return (add(mul(u[1], r[2]), neg(mul(u[2], r[1]))),
            add(mul(u[2], r[0]), neg(mul(u[0], r[2]))),
            add(mul(u[0], r[1]), neg(mul(u[1], r[0]))))


def negv(w):
    return tuple(neg(c) for c in w)


def vsub(u, r):
    return (add(u[0], neg(r[0])), add(u[1], neg(r[1])), add(u[2], neg(r[2])))


def firstsgn(v):
    for c in v:
        s = sgn(c)
        if s:
            return s
    return 0


def splitmix64(state):
    state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return state, z ^ (z >> 31)


def m_min_of(R):
    """R1 之 D5：min m ≥ 0 s.t. ∃A 整數：|A − R(s)| ≤ m 且 A − R(s) ≡ m (mod 2) ∀s。"""
    lo, hi = min(R), max(R)
    for m in range(0, 40):
        for A in range(lo - 2, hi + 3):
            if all(abs(A - x) <= m and (A - x - m) % 2 == 0 for x in R):
                return m, A
    return None, None


def main():
    os.makedirs(DATA, exist_ok=True)
    print('=' * 112)
    print('O225 scripts/18 -- R4 MACHINE: algebraic origin of the tie parity   (rules: %s)' % RULES)
    print('=' * 112, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r4_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r4_a2')
    G, _idx, MUL2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]

    # ---- 軸對 ----
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(sgn(add(U[i][t], U[j][t])) == 0 for t in range(3)):
                partner[i] = j
    keys = sorted(set(min(i, partner[i]) for i in range(ncol)))
    tcomp = collections.Counter(types[k] for k in keys)
    claim('P1', '★ 62 軸恰成 31 對精確負（U[ā] = −U[a]），型別分解 15 edge + 10 face + 6 vertex',
          len(partner) == ncol and len(keys) == 31 and tcomp == collections.Counter({'edge': 15, 'face': 10, 'vertex': 6}),
          'paired = %d/62 ; pairs = %d ; types = %s' % (len(partner), len(keys), dict(tcomp)))

    # ---- 每 row 之 dot/tie 快取 ----
    DOT = [[dot3(U[a], KV[s]) for a in range(ncol)] for s in range(n)]
    TIE = [[sgn(DOT[s][a]) == 0 for a in range(ncol)] for s in range(n)]
    n_tie_pairs = [sum(1 for a in range(ncol) if TIE[s][a]) // 2 for s in range(n)]
    tau = [firstsgn(KV[s]) for s in range(n)]
    R = [sum(K[s]) for s in range(n)]

    off_ok = True
    tie_same = True
    for s in range(n):
        for a in range(ncol):
            b = partner[a]
            if TIE[s][a]:
                if not (K[s][b] == K[s][a]):
                    tie_same = False
            else:
                if K[s][b] != -K[s][a]:
                    off_ok = False
    claim('P2', '★ 非 tie 條目 K[s][ā] = −K[s][a]（對消）；tie 條目 K[s][ā] = +K[s][a]（相加）'
                '（因凍結 tie 分支只依 r_s，唔依 U[a]）', off_ok and tie_same,
          'off-tie antisymmetry = %s ; tie same-sign = %s ; ties/row = %s ; τ 值域 = %s'
          % (off_ok, tie_same, sorted(set(n_tie_pairs)), sorted(set(tau))))
    R_formula = all(R[s] == 2 * tau[s] * n_tie_pairs[s] for s in range(n))
    claim('P3a', '★ R(s) = 2·τ(s)·n_tie(s) 逐 row 精確（R1 障礙之代數機制）', R_formula,
          'R 值域 = %s ; n_tie ≡ %s' % (sorted(set(R)), sorted(set(n_tie_pairs))))
    mmin, A = m_min_of(R)
    Delta = max(R) - min(R)
    claim('P3b', '★ R1 重導：n_tie ≡ 5 ⟹ R = ±10、Δ = 20、m_min = ceil(Δ/2) = 10 = 2×5',
          sorted(set(n_tie_pairs)) == [5] and sorted(set(R)) == [-10, 10] and Delta == 20 and mmin == 10 and A == 0,
          'n_tie = %s ; R = %s ; Δ = %d ; m_min = %s (A = %s)' % (sorted(set(n_tie_pairs)), sorted(set(R)), Delta, mmin, A))

    # ---- P4：乘積層讀出 vs M-b vs 機器 ----
    Kcan = []
    Kmb = []
    for s in range(n):
        rc, rm = [], []
        for a in range(ncol):
            d = DOT[s][a]
            cr = cross3(U[a], KV[s])
            rc.append(sgn(d) if sgn(d) != 0 else firstsgn(cr))
            rm.append(firstsgn((d, cr[0], cr[1], cr[2])))
        Kcan.append(rc)
        Kmb.append(rm)
    can_eq_mb = sum(1 for s in range(n) for a in range(ncol) if Kcan[s][a] == Kmb[s][a])
    can_eq_machine_off = sum(1 for s in range(n) for a in range(ncol)
                             if not TIE[s][a] and Kcan[s][a] == K[s][a])
    n_off = sum(1 for s in range(n) for a in range(ncol) if not TIE[s][a])
    can_eq_machine_tie = sum(1 for s in range(n) for a in range(ncol) if TIE[s][a] and Kcan[s][a] == K[s][a])
    n_tie = sum(1 for s in range(n) for a in range(ncol) if TIE[s][a])
    claim('P4a', '★★ 乘積層讀出 Λ(conj(r)·u) = Λ(⟨u,r⟩, u×r) 在全部 7440 條目上 == M-b（0 例外）',
          can_eq_mb == n * ncol, 'matches = %d / %d' % (can_eq_mb, n * ncol))
    claim('P4b', '★ 同規則在全部非 tie 條目上 == 機器 K（0 例外）', can_eq_machine_off == n_off,
          'matches = %d / %d' % (can_eq_machine_off, n_off))
    claim('P4c', '★ 在 tie 條目上只部分一致 ⟹ 機器 tie 分支非「單一物件之首非零分量」函數',
          can_eq_machine_tie < n_tie,
          'matches = %d / %d（機器讀 r、乘積層讀 u×r）' % (can_eq_machine_tie, n_tie))

    # ---- P5：候選族之 u-宇稱 ----
    cands = {
        'r (機器型)': lambda u, r: r,
        'u': lambda u, r: u,
        'u×r': lambda u, r: cross3(u, r),
        'u+r': lambda u, r: (add(u[0], r[0]), add(u[1], r[1]), add(u[2], r[2])),
        'u−r': lambda u, r: vsub(u, r),
        'conj(r)·u = (⟨u,r⟩, u×r)': lambda u, r: (dot3(u, r), cross3(u, r)[0], cross3(u, r)[1], cross3(u, r)[2]),
    }
    p5rows = {}
    p5_ok = True
    for name, f in cands.items():
        Kx = []
        for s in range(n):
            r = KV[s]
            row = []
            for a in range(ncol):
                row.append(sgn(DOT[s][a]) if not TIE[s][a] else firstsgn(f(U[a], r)))
            Kx.append(row)
        Rx = sorted(set(sum(row) for row in Kx))
        odd = all(sgn(add(f(negv(U[a]), KV[s])[t], f(U[a], KV[s])[t])) == 0
                  for s in range(n) for a in range(ncol) for t in range(len(f(U[a], KV[s]))))
        even = all(sgn(add(negv(f(U[a], KV[s]))[t], f(negv(U[a]), KV[s])[t])) == 0
                   for s in range(n) for a in range(ncol) for t in range(len(f(U[a], KV[s]))))
        p5rows[name] = {'R_range': Rx, 'R_zero': Rx == [0], 'u_odd': odd, 'u_even': even}
        if (Rx == [0]) != odd:
            p5_ok = False
    claim('P5', '★ u-宇稱充要：R ≡ 0 ⟺ 該規則在 tie 上 u-奇（候選族 6 個逐個驗）', p5_ok,
          '; '.join('%s: R=%s u_odd=%s' % (k, v['R_range'], v['u_odd']) for k, v in p5rows.items()))

    # ---- P6：6 軸商 ----
    axof = []
    for s in range(n):
        r = KV[s]
        hit = None
        for a in range(ncol):
            lam = None
            ok = True
            for t in range(3):
                if sgn(U[a][t]) == 0:
                    if sgn(r[t]) != 0:
                        ok = False
                        break
                    continue
                v = mul(r[t], (U[a][t][0], -U[a][t][1]))
                den = U[a][t][0] * U[a][t][0] - 5 * U[a][t][1] * U[a][t][1]
                if den == 0:
                    ok = False
                    break
                q = (v[0] / den, v[1] / den)
                if lam is None:
                    lam = q
                elif sgn(add(lam, neg(q))) != 0:
                    ok = False
                    break
            if ok and lam is not None and sgn(lam) != 0:
                hit = min(a, partner[a])
                break
        axof.append(hit)
    axc = collections.Counter(axof)
    tieset = {}
    for s in range(n):
        tieset[s] = tuple(sorted(min(a, partner[a]) for a in range(ncol) if TIE[s][a]))
    byax = collections.defaultdict(set)
    for s in range(n):
        byax[axof[s]].add(tieset[s])
    tie_types = {}
    for k, v in byax.items():
        ts = next(iter(v))
        tie_types[k] = dict(collections.Counter(types[t] for t in ts))
    claim('P6', '★ 商：ax(s)（r_s 之二十面體軸線）恰 6 值、每值 20 態；tie 集合係 ax 之函數'
                '（6 個相異 tie 集）⟹ 障礙之表住喺 6 條軸上', len(axc) == 6 and set(axc.values()) == {20}
          and all(len(v) == 1 for v in byax.values()) and len(set(tieset.values())) == 6,
          'states/axis = %s ; distinct tie sets = %d ; tie types per axis = %s'
          % (sorted(axc.values()), len(set(tieset.values())), tie_types))

    # ---- P7：子表 + 200 旋轉機器 ----
    subs = {}
    for tp in ('edge', 'face', 'vertex'):
        cols = [a for a in range(ncol) if types[a] == tp]
        Rs = []
        ntp = []
        for s in range(n):
            row = [K[s][a] for a in cols]
            Rs.append(sum(row))
            ntp.append(sum(1 for a in cols if TIE[s][a]) // 2)
        subs[tp] = {'n_axes': len(cols), 'R': sorted(set(Rs)), 'n_tie': sorted(set(ntp)),
                    'm_min': m_min_of(Rs)[0]}
        # 子表之 u-奇規則
        Kodd = []
        for s in range(n):
            Kodd.append([sgn(DOT[s][a]) if not TIE[s][a] else firstsgn(cross3(U[a], KV[s])) for a in cols])
        subs[tp]['u_odd_R'] = sorted(set(sum(r) for r in Kodd))
    claim('P7a', '★ 子表 edge(30)/face(20)/vertex(12)：各表之 n_tie 與 R、u-奇規則下 R ≡ 0',
          all(set(v['u_odd_R']) == {0} for v in subs.values()),
          '; '.join('%s: n=%d n_tie=%s R=%s m_min=%s u-odd R=%s' % (k, v['n_axes'], v['n_tie'], v['R'], v['m_min'], v['u_odd_R'])
                    for k, v in subs.items()))

    seed = 20261001
    ok_even = ok_odd = 0
    bad = []
    nz = []
    for m in range(200):
        seed, r1 = splitmix64(seed)
        seed, r2 = splitmix64(seed)
        h = G[r1 % n]
        Um = [mm.rot_ref(h, U[a]) for a in range(ncol)]
        nm = Um[r2 % ncol]
        nref = Um[0]
        KVm = [mm.rot_ref(g, nref) for g in G]
        tot_even = []
        tot_odd = []
        ntr = []
        for s in range(n):
            acc_e = acc_o = 0
            nt = 0
            for a in range(ncol):
                d = dot3(Um[a], KVm[s])
                sd = sgn(d)
                if sd != 0:
                    acc_e += sd
                    acc_o += sd
                else:
                    nt += 1
                    acc_e += firstsgn(KVm[s])
                    acc_o += firstsgn(cross3(Um[a], KVm[s]))
            tot_even.append(acc_e)
            tot_odd.append(acc_o)
            ntr.append(nt // 2)
        nz.append(tuple(sorted(set(ntr))))
        if all(abs(tot_even[s]) == 2 * ntr[s] and abs(tot_even[s]) > 0 for s in range(n)) \
                and len(set(tot_even)) <= 2:
            ok_even += 1
        else:
            bad.append(('even', m, sorted(set(tot_even)), sorted(set(ntr))))
        if set(tot_odd) == {0}:
            ok_odd += 1
        else:
            bad.append(('odd', m, sorted(set(tot_odd)), ntp))
    claim('P7b', '★ 200 旋轉機器：u-偶規則 ⟹ |R| = 2·n_tie（每 row 一致）；u-奇規則 ⟹ R ≡ 0（逐個驗）',
          ok_even == 200 and ok_odd == 200,
          'u-even ok = %d/200 ; u-odd ok = %d/200 ; n_tie 值域 = %s ; 例外 = %s'
          % (ok_even, ok_odd, sorted(set(nz)), bad[:3]))

    # ---- P8：tie 位之分解 ----
    Kneg = []
    for s in range(n):
        Kneg.append([sgn(DOT[s][a]) if not TIE[s][a] else firstsgn((DOT[s][a], neg(cross3(U[a], KV[s])[0]),
                    neg(cross3(U[a], KV[s])[1]), neg(cross3(U[a], KV[s])[2]))) for a in range(ncol)])
    R_neg = sorted(set(sum(r) for r in Kneg))
    tie_diff = sum(1 for s in range(n) for a in range(ncol) if TIE[s][a] and Kneg[s][a] != Kcan[s][a])
    prod_cands = {'conj(r)·u = (⟨u,r⟩, +u×r)': Kcan, 'conj(u)·r = (⟨u,r⟩, −u×r)': Kneg}
    both_zero = all(sorted(set(sum(r) for r in Kx)) == [0] for Kx in prod_cands.values())
    claim('P8a', '★ tie 位分解（障礙位）：候選族中 R ≡ 0 ⟺ u-奇；u-偶（含機器之 r-only）⟹ |R| = 2n_tie > 0',
          p5_ok and p5rows['r (機器型)']['R_range'] == [-10, 10], '機器型 = %s' % p5rows['r (機器型)'])
    claim('P8b', '★ R-中性位：兩個「乘積層且非 tie 一致」候選（+u×r 與 −u×r）皆 R ≡ 0，但 tie 值不同'
                 ' ⟹ 「乘積層 + 非 tie 一致」唔足以唯一固定 tie 位（本輪預註冊之唯一性被否證，誠實報）',
          both_zero and tie_diff > 0,
          'R(+cross) = %s ; R(−cross) = %s ; tie 值相異條目 = %d' % (sorted(set(sum(r) for r in Kcan)), R_neg, tie_diff))
    claim('P8c', '判決：障礙完全由「讀出物件」之宇稱位決定（乘積層 vs r-only）；餘下之向量部符號位係 R-中性約定'
                 ' ⟹ M-b 之「1 bit」= 讀出約定，唔係新增物理輸入',
          p5_ok and both_zero and p5rows['r (機器型)']['R_range'] == [-10, 10], '見 P5/P8a/P8b')

    out = {'rules': RULES, 'P1_axis_pairs': {'n_pairs': len(keys), 'types': dict(tcomp)},
           'P2': {'off_antisym': off_ok, 'tie_same': tie_same},
           'P3': {'n_tie': sorted(set(n_tie_pairs)), 'R': sorted(set(R)), 'Delta': Delta, 'm_min': mmin, 'A': A,
                  'identity_R_eq_2tau_ntie': R_formula},
           'P4': {'canon_eq_Mb': can_eq_mb, 'canon_eq_machine_offtie': can_eq_machine_off,
                  'n_offtie': n_off, 'canon_eq_machine_tie': can_eq_machine_tie, 'n_tie': n_tie},
           'P5_candidates': p5rows, 'P6': {'states_per_axis': dict(axc), 'tie_types_per_axis': tie_types},
           'P7_subtables': subs, 'P7_random': {'ok_even': ok_even, 'ok_odd': ok_odd, 'exceptions': bad[:5]},
           'P8': {'tie_diff': tie_diff, 'R_plus': sorted(set(sum(r) for r in Kcan)), 'R_minus': R_neg},
           'claims': CLAIMS}
    with io.open(os.path.join(DATA, '18_r4_tie_parity.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
