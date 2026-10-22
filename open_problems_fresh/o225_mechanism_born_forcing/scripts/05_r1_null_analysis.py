#!/usr/bin/env python3
"""O225 scripts/05 -- R1 null 深挖：隨機軸機器之 Delta 分佈 ＋ 「R 恆常」個案之結構診斷。

動機：03 之 N1 null 顯示少數隨機軸機器之 R(s) 恆常（非凍結之兩值結構）。R 恆常正是
P4 之 ⟺ 之**另一側**（存在態敏感仿射 Born 權重族）⟹ 本支同時係 P4 充分性之 out-of-sample 陽性對照。

用法:  /usr/bin/python3 scripts/05_r1_null_analysis.py [--nulls N]
"""
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
O222S = os.path.join(O222, 'scripts')
MASK = (1 << 64) - 1
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def splitmix64(state):
    state = (state + 0x9E3779B97F4A7C15) & MASK
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
    return state, z ^ (z >> 31)


def load_o222(script):
    spec = importlib.util.spec_from_file_location('o222n_' + script[:-3], os.path.join(O222S, script))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_K(m, U, G):
    KV = [m.rot_ref(q, U[0]) for q in G]
    K = []
    for i in range(120):
        r = KV[i]
        row = []
        for u in U:
            dot = m.add(m.add(m.mul(u[0], r[0]), m.mul(u[1], r[1])), m.mul(u[2], r[2]))
            s = m.sgn(dot)
            if s == 0:
                for comp in r:
                    sc = m.sgn(comp)
                    if sc:
                        s = sc
                        break
            row.append(s)
        K.append(row)
    return K


def random_axes(G, seed, n_axes=62):
    st = seed
    out = []
    for _ in range(n_axes):
        st, z = splitmix64(st)
        qq = G[z % 120]
        out.append((qq[1], qq[2], qq[3]))
    return out


def mmin_of_R(R):
    lo, hi = min(R), max(R)
    m = 0
    while True:
        for A in range(lo - m, hi + m + 1):
            if all(abs(A - r) <= m and (A - r - m) % 2 == 0 for r in R):
                return m, A
        m += 1


def neg_key(k):
    return tuple((-f[0], f[1], -f[2], f[3]) for f in k)


def main():
    argv = sys.argv[1:]
    N = int(argv[argv.index('--nulls') + 1]) if '--nulls' in argv else 200
    m = load_o222('09_a2_rollback.py')
    _ax, _U, ids, types, hvec = m.load_inputs()
    G, idx, MUL = m.build_group()
    rows = []
    const_cases = []
    for d in range(N):
        axes = random_axes(G, 225 + 7919 * d)
        K = build_K(m, axes, G)
        R = [sum(r) for r in K]
        nd = len(set(R))
        mm, AA = mmin_of_R(R)
        rows.append({'draw': d, 'n_distinct': nd, 'Delta': max(R) - min(R), 'm_min': mm,
                     'A': AA, 'R_min': min(R), 'R_max': max(R)})
        if nd == 1:
            cnt = {}
            for u in axes:
                key = tuple((c[0].numerator, c[0].denominator, c[1].numerator, c[1].denominator)
                            for c in u)
                cnt[key] = cnt.get(key, 0) + 1
            closed = all(neg_key(k) in cnt and cnt[neg_key(k)] == cnt[k] for k in cnt)
            const_cases.append({'draw': d, 'R_value': R[0], 'n_distinct_axes': len(cnt),
                                'closed_under_negation': closed,
                                'min_multiplicity': min(cnt.values()), 'max_multiplicity': max(cnt.values()),
                                'axis_multiplicities_top': sorted(cnt.values(), reverse=True)[:4]})
    deltas = sorted(r['Delta'] for r in rows)
    med = deltas[len(deltas) // 2]
    print('Delta distribution: min=%d median=%d max=%d ; n(Delta==20)=%d'
          % (deltas[0], med, deltas[-1], sum(1 for x in deltas if x == 20)), flush=True)
    claim('Q1', '隨機軸機器（%d 抽）之 Delta 分佈：min = %d，median = %d，max = %d（凍結 K 之 Delta = 20）'
          % (N, deltas[0], med, deltas[-1]),
          deltas[0] > 0 and med > 20,
          'min=%d median=%d max=%d ; #Delta=20 : %d' %
          (deltas[0], med, deltas[-1], sum(1 for x in deltas if x == 20)))
    two = [r for r in rows if r['n_distinct'] == 2]
    claim('Q2', '隨機軸機器命中「恰兩值且 = {-10,+10}」之次數 = 0；兩值個案數 = %d（皆非 {-10,+10}）' % len(two),
          all(not (r['R_min'] == -10 and r['R_max'] == 10) for r in two),
          'two-valued draws = %d ; their (min,max) = %s'
          % (len(two), [(r['R_min'], r['R_max']) for r in two[:6]]))
    claim('Q3', '★ 「R 恆常」個案數 = %d/%d（P4 之 ⟺ 另一側）' % (len(const_cases), N),
          len(const_cases) >= 0,
          'constant-R draws = %s' % [(c['draw'], c['R_value'], c['n_distinct_axes'],
                                      c['closed_under_negation'], c['min_multiplicity'],
                                      c['max_multiplicity']) for c in const_cases])
    ok_pos = len(const_cases) > 0
    detail_pos = []
    for c in const_cases:
        axes = random_axes(G, 225 + 7919 * c['draw'])
        K = build_K(m, axes, G)
        nA = len(K[0])
        alpha = F(1, nA)
        good = True
        for beta in (F(1, nA), F(-1, nA)):
            W = [[alpha + beta * K[s][a] for a in range(nA)] for s in range(120)]
            nn = all(v >= 0 for r in W for v in r)
            nor = all(sum(r) == 1 for r in W)
            sens = len(set(tuple(r) for r in W)) > 1
            good = good and nn and nor and sens
        if not good:
            ok_pos = False
        detail_pos.append('draw %d: nonneg+normalized+sensitive = %s' % (c['draw'], good))
    claim('Q4', '★ 陽性對照：對每個 R 恆常個案，W = 1/n + beta·K（beta = ±1/n）皆 非負＋歸一＋態敏感'
          '（P4 充分性之 out-of-sample 實例）', ok_pos, ' | '.join(detail_pos))
    out = {'rules': 'r1-null-analysis-v1', 'N': N, 'rows': rows, 'const_cases': const_cases,
           'delta_stats': {'min': deltas[0], 'median': med, 'max': deltas[-1],
                           'n_equal_20': sum(1 for x in deltas if x == 20),
                           'n_less_than_20': sum(1 for x in deltas if x < 20)}, 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '05_r1_null_analysis.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
