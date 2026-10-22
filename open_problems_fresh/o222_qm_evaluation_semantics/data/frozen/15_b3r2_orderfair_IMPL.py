#!/usr/bin/env python3
"""O222 scripts/15 -- B3 round 2 machine: order-fair read allocation inside the 44-read budget.

Contract: docs/10_b3r2_contract.md (b3r2-contract-v1, incl. amendment A1: constructibility is
COMPUTED from the enumeration, cov_a/cov_b are diagnostics only -- the coverage equivalence
stated in the original v1 text is false, see amendment A1).

Rules honoured here:
  * machine semantics are IMPORTED (scripts/12_b5_budget.run_pair, wrapping the frozen scripts/09
    L-SEQ read/rollback machine) -- never re-implemented;
  * per-pair cost is COMPUTED by that machine (never assumed);
  * the unrestricted baseline AND every feasible value come from FULL enumeration, no pruning,
    no early exit; the domain size is counted and cross-checked against the frozen A2 record;
  * `NOT CONSTRUCTIBLE` is reported strictly separately from |S| = 0;
  * five pre-registered order rules, all reported;
  * the random-axis null re-runs the WHOLE pipeline under a random axis relabelling.

Usage:  /usr/bin/python3 scripts/15_b3r2_orderfair.py [--nulls N]
"""
import importlib.util
import io
import json
import os
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
RULES = 'b3r2-contract-v1'
ORDER_IDS = ('lex', 'diag', 'antidiag', 'block', 'stride')
MODES = ('raw', 'distinct', 'distinct_anti', 'all4')
CONSTRAINED = ('distinct', 'distinct_anti', 'all4')
N = 62
CLAIMS = []


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _gcd_int(a, b):
    while b:
        a, b = b, a % b
    return a


def order_key(oid, a, b):
    if oid == 'lex':
        return (a, b)
    if oid == 'diag':
        return ((b - a) % 62, a, b)
    if oid == 'antidiag':
        return ((a + b) % 62, a, b)
    if oid == 'block':
        return (max(a, b), min(a, b), a)
    if oid == 'stride':
        return ((b - 13 * a) % 62, b, a)
    raise KeyError(oid)


def order_list(oid):
    pairs = [(a, b) for a in range(N) for b in range(N)]
    pairs.sort(key=lambda p: order_key(oid, p[0], p[1]))
    return pairs


def sweep(M, den, anti, mode):
    """FULL 62^4 enumeration, zero pruning, zero early exit. Returns (best, argmax, domain)."""
    best = 0
    barg = None
    dom = 0
    for a in range(N):
        Na = M[a]
        for a2 in range(N):
            if mode != 'raw' and a2 == a:
                continue
            Na2 = M[a2]
            for i in range(N):
                if mode == 'all4' and (i == a or i == a2):
                    continue
                if mode in ('distinct_anti', 'all4') and (anti[a][i] or anti[a2][i]):
                    continue
                base = Na[i] + Na2[i]
                for j in range(N):
                    if mode != 'raw' and j == i:
                        continue
                    if mode == 'all4' and (j == a or j == a2):
                        continue
                    if mode in ('distinct_anti', 'all4') and (anti[a][j] or anti[a2][j]):
                        continue
                    dom += 1
                    S = base - Na[j] + Na2[j]
                    if S < 0:
                        S = -S
                    if S > best:
                        best = S
                        barg = (a, a2, i, j)
    return best, barg, dom


def simulate(b5, order, K, MUL, hx, budget, top=-1):
    """run the frozen machine pair by pair under the per-read terminal condition (I6)."""
    trail = []
    pairs = []
    rem = budget
    for (a, b) in order:
        try:
            r, rem = b5.run_pair(a, b, 0, top, K, MUL, hx, rem, trail)
        except RuntimeError:
            return pairs, trail, (a, b), rem
        top = r['top']
        pairs.append((a, b))
    return pairs, trail, None, rem


def feasible_chsh(M, den, mode, pref, anti, ids):
    """FULL enumeration of the feasible prefix's 4-corner domain. None == NOT CONSTRUCTIBLE."""
    A = sorted({a for (a, b) in pref})
    B = sorted({b for (a, b) in pref})
    inpref = set(pref)
    best = None
    barg = None
    dom = 0
    for a in A:
        for a2 in A:
            if mode != 'raw' and a2 == a:
                continue
            for i in B:
                if (a, i) not in inpref or (a2, i) not in inpref:
                    continue
                if mode == 'all4' and (i == a or i == a2):
                    continue
                if mode in ('distinct_anti', 'all4') and (anti[a][i] or anti[a2][i]):
                    continue
                base = M[a][i] + M[a2][i]
                for j in B:
                    if (a, j) not in inpref or (a2, j) not in inpref:
                        continue
                    if mode != 'raw' and j == i:
                        continue
                    if mode == 'all4' and (j == a or j == a2):
                        continue
                    if mode in ('distinct_anti', 'all4') and (anti[a][j] or anti[a2][j]):
                        continue
                    dom += 1
                    S = base - M[a][j] + M[a2][j]
                    if S < 0:
                        S = -S
                    if best is None or S > best:
                        best = S
                        barg = (a, a2, i, j)
    if best is None:
        return None, None, dom
    return F(best, den), barg, dom


def build_anti(m, U):
    anti = [[False] * N for _ in range(N)]
    for a in range(N):
        ua = U[a]
        for b in range(N):
            ub = U[b]
            dot = m.add(m.add(m.mul(ua[0], ub[0]), m.mul(ua[1], ub[1])), m.mul(ua[2], ub[2]))
            na = m.add(m.add(m.mul(ua[0], ua[0]), m.mul(ua[1], ua[1])), m.mul(ua[2], ua[2]))
            nb = m.add(m.add(m.mul(ub[0], ub[0]), m.mul(ub[1], ub[1])), m.mul(ub[2], ub[2]))
            if m.sgn(dot) < 0 and m.mul(dot, dot) == m.mul(na, nb):
                anti[a][b] = True
    return anti


def perm_of(seed, sm64):
    """Fisher-Yates over 0..61 driven by the frozen splitmix64 stream."""
    st = seed & ((1 << 64) - 1)
    p = list(range(N))
    for k in range(N - 1, 0, -1):
        st, r = sm64(st)
        j = r % (k + 1)
        p[k], p[j] = p[j], p[k]
    return p


def main():
    argv = sys.argv[1:]
    n_null = int(argv[argv.index('--nulls') + 1]) if '--nulls' in argv else 0
    t0 = time.time()
    print('=' * 112)
    print('O222 scripts/15 -- B3R2: order-fair allocation inside the 44-read budget (rules: %s)' % RULES)
    print('=' * 112, flush=True)

    a2m = load_module(os.path.join(HERE, '09_a2_rollback.py'), 'a2m')
    b5 = load_module(os.path.join(HERE, '12_b5_budget.py'), 'b5')
    C1, C2, ids, types, den1 = b5.load_a2()
    mm, K, MUL, hx, ids2, types2 = b5.load_machine()
    b5.KERNEL_TAB = None          # always pass K explicitly (the null permutes K)
    _axes, U, _ids, _types, _hv = mm.load_inputs()
    anti = build_anti(mm, U)

    def to_int_matrix(M):
        dn = 1
        for row in M:
            for v in row:
                dn = dn * F(v).denominator // _gcd_int(dn, F(v).denominator)
        return [[int(F(M[a][b]) * dn) for b in range(N)] for a in range(N)], dn
    M1, den1 = to_int_matrix(C1)
    M2, den2 = to_int_matrix(C2)

    # ---- A0: unrestricted baseline by FULL 62^4 enumeration must reproduce the recorded values ----
    a2full = json.load(io.open(os.path.join(DATA, '09_a2_results.json'), encoding='utf-8'))
    a2r = a2full['chsh']
    a10 = json.load(io.open(os.path.join(DATA, '10_a2_bruteforce.json'), encoding='utf-8'))
    base = {}
    for ename, M, den in (('E1', M1, den1), ('E2', M2, den2)):
        for mode in MODES:
            v, arg, dom = sweep(M, den, anti, mode)
            base['%s_%s' % (ename, mode)] = {'value': str(F(v, den)), 'argmax': [ids[k] for k in arg],
                                             'domain': dom}
            print('  baseline %-16s |S|max = %-5s  argmax = %-26s domain = %d'
                  % ('%s_%s' % (ename, mode), F(v, den), [ids[k] for k in arg], dom), flush=True)
    okv = all(base['%s_%s' % (e, m)]['value'] == str(a2r['%s_%s' % (e, m)]) for e in ('E1', 'E2') for m in MODES)
    oka = all(base['%s_%s' % (e, m)]['argmax'] == a10['%s_%s' % (e, m)]['argmax'] for e in ('E1', 'E2') for m in MODES)
    CLAIMS.append({'tag': 'A0', 'name': 'unrestricted baseline: FULL 62^4 enumeration reproduces the '
                                        'recorded eight |S|max values AND argmaxes',
                   'ok': okv and oka, 'detail': 'values=%s argmaxes=%s' % (okv, oka)})
    print('[%s] A0 full-sweep baseline reproduces the recorded 8 values + argmaxes' %
          ('PASS' if (okv and oka) else 'FAIL'), flush=True)
    # A0b: the same sweep re-derives the corrected (closeout G3) DOMAIN counts
    dom_ok = (base['E1_raw']['domain'] == 14776336 and base['E1_distinct_anti']['domain'] == 13388280
              and base['E1_all4']['domain'] == 12517800 and base['E1_distinct']['domain'] == 14303524)
    CLAIMS.append({'tag': 'A0b', 'name': 'domain counts independently re-derived: raw 14,776,336 ; '
                                         'distinct 14,303,524 ; distinct_anti 13,388,280 ; all4 12,517,800 '
                                         '(the closeout-corrected values)',
                   'ok': dom_ok, 'detail': json.dumps({m: base['E1_%s' % m]['domain'] for m in MODES})})
    print('[%s] A0b domain counts re-derived (raw %d, distinct %d, distinct_anti %d, all4 %d)'
          % ('PASS' if dom_ok else 'FAIL', base['E1_raw']['domain'], base['E1_distinct']['domain'],
             base['E1_distinct_anti']['domain'], base['E1_all4']['domain']), flush=True)

    # ---- per-order pipeline (per-pair cost COMPUTED by the frozen machine) ----
    results = {}
    for oid in ORDER_IDS:
        pairs, trail, terminal, rem = simulate(b5, order_list(oid), K, MUL, hx, F(123, 2))
        cov_a = len({a for (a, b) in pairs})
        cov_b = len({b for (a, b) in pairs})
        rows = {'prefix_len': len(pairs), 'reads_used': sum(e['misses'] for e in trail),
                'budget_left': str(rem), 'terminal_pair': list(terminal) if terminal else None,
                'cov_a': cov_a, 'cov_b': cov_b, 'per_pair_misses': [e['misses'] for e in trail],
                'feasible': {}, 'domains': {}}
        for ename, M, den in (('E1', M1, den1), ('E2', M2, den2)):
            for mode in MODES:
                val, barg, dom = feasible_chsh(M, den, mode, pairs, anti, ids)
                if val is None:
                    rows['feasible']['%s_%s' % (ename, mode)] = None
                else:
                    aa, aa2, ii, jj = barg
                    hits = [nm for nm, cond in (('i=a', ii == aa), ('i=a2', ii == aa2),
                                                ('j=a', jj == aa), ('j=a2', jj == aa2),
                                                ('j=i', jj == ii)) if cond]
                    rows['feasible']['%s_%s' % (ename, mode)] = {
                        'value': str(val), 'argmax': [ids[k] for k in barg], 'diag_hits': hits}
                rows['domains']['%s_%s' % (ename, mode)] = dom
        for mode in CONSTRAINED:
            rows['constructible_%s' % mode] = any(
                rows['feasible']['%s_%s' % (e, mode)] is not None for e in ('E1', 'E2'))
        results[oid] = rows
        print('  %-9s pairs=%-3d reads=%-3d cov_a=%-2d cov_b=%-2d  E1_all4=%-18s E2_all4=%-18s '
              'distinct_constr=%s'
              % (oid, rows['prefix_len'], rows['reads_used'], cov_a, cov_b,
                 (rows['feasible']['E1_all4'] or {}).get('value', 'NOT CONSTRUCTIBLE'),
                 (rows['feasible']['E2_all4'] or {}).get('value', 'NOT CONSTRUCTIBLE'),
                 rows['constructible_distinct']), flush=True)
        print('            misses=%s  terminal=%s  E1_raw=%s  E1_distinct=%s'
              % (rows['per_pair_misses'], rows['terminal_pair'],
                 (rows['feasible']['E1_raw'] or {}).get('value', 'NOT CONSTRUCTIBLE'),
                 (rows['feasible']['E1_distinct'] or {}).get('value', 'NOT CONSTRUCTIBLE')), flush=True)

    lex_ok = (results['lex']['prefix_len'] == 15 and results['lex']['reads_used'] == 43
              and results['lex']['cov_a'] == 1
              and all(not results['lex']['constructible_%s' % m] for m in CONSTRAINED)
              and (results['lex']['feasible']['E1_raw'] or {}).get('value') == '2')
    CLAIMS.append({'tag': 'A1', 'name': 'lex baseline reproduces B5 exactly (15 pairs / 43 reads / cov_a = 1 ; '
                                        'no constrained class constructible ; raw = 2 = the trivial bound)',
                   'ok': lex_ok, 'detail': json.dumps({k: results['lex'][k] for k in
                                                       ('prefix_len', 'reads_used', 'cov_a', 'cov_b')})})
    print('[%s] A1 lex baseline reproduces B5 (15/43, cov_a=1, constrained classes NOT CONSTRUCTIBLE)'
          % ('PASS' if lex_ok else 'FAIL'), flush=True)

    all4_orders = [o for o in ORDER_IDS if results[o]['constructible_all4']]
    any_constr = [o for o in ORDER_IDS if any(results[o]['constructible_%s' % m] for m in CONSTRAINED)]
    CLAIMS.append({'tag': 'A2', 'name': 'at least one order makes a CONSTRAINED statistic constructible '
                                        'inside the same 44-read budget (amendment A1 criterion: computed)',
                   'ok': bool(any_constr),
                   'detail': 'constrained-constructible = %s ; all4-constructible = %s' % (any_constr, all4_orders)})
    print('[%s] A2 constrained-constructible orders = %s ; all4-constructible = %s'
          % ('PASS' if any_constr else 'FAIL', any_constr, all4_orders), flush=True)

    feas_vals = []
    for o in ORDER_IDS:
        for e in ('E1', 'E2'):
            for m in CONSTRAINED:
                got = results[o]['feasible']['%s_%s' % (e, m)]
                if got is not None:
                    feas_vals.append((o, e, m, F(got['value']), got['argmax'], got['diag_hits']))
    mx = max((v for (_o, _e, _m, v, _a, _h) in feas_vals), default=None)
    print('  budget-feasible constrained statistics (FULL enumeration inside each prefix):', flush=True)
    for o, e, m, v, arg, hits in sorted(feas_vals, key=lambda z: -z[3]):
        print('        %-9s %-3s %-14s |S| = %-6s argmax = %-26s diag = %s'
              % (o, e, m, v, arg, hits or 'none'), flush=True)
    all4_max = max((F(results[o]['feasible']['%s_all4' % e]['value']) for o in ORDER_IDS
                    for e in ('E1', 'E2') if results[o]['feasible']['%s_all4' % e] is not None),
                   default=None)
    ok3 = all4_max is not None and all4_max <= 2
    CLAIMS.append({'tag': 'A3', 'name': 'the ARTIFACT-FREE statistic (all4 = six pairwise-distinct settings) '
                                        'never exceeds the LHV bound 2 inside the 44-read budget',
                   'ok': ok3, 'detail': 'max budget-feasible all4 |S| = %s ; max over ALL constrained '
                                        'classes = %s' % (all4_max, mx)})
    print('[%s] A3 max budget-feasible all4 |S| = %s  (max over all constrained classes = %s)'
          % ('PASS' if ok3 else 'FAIL', all4_max, mx), flush=True)

    # ---- Q4 checks: marginal balance (no-signalling), order effect, ablation ----
    bal = all(sum(K[s][a] for s in range(120)) == 0 for a in range(N))
    CLAIMS.append({'tag': 'B1', 'name': 'marginal balance Sigma_s K[s][a] = 0 on all 62 axes '
                                        '(marginal = 1/2 EXACT -> no-signalling)',
                   'ok': bal, 'detail': '62/62 balanced = %s' % bal})
    print('[%s] B1 marginal balance 62/62 (no-signalling)' % ('PASS' if bal else 'FAIL'), flush=True)
    a2j = json.load(io.open(os.path.join(DATA, '09_a2_correlation.json'), encoding='utf-8'))
    rev = a2j['C1rev_num']
    dmax = max(abs(int(a2j['C1_num'][a][b]) - int(rev[a][b])) for a in range(N) for b in range(N))
    CLAIMS.append({'tag': 'B2', 'name': 'order-effect diagnostic Delta_order = 160/120 (A2 verbatim)',
                   'ok': dmax == 160, 'detail': 'max |C1 - C1_rev| = %d/120' % dmax})
    print('[%s] B2 Delta_order = %d/120 (recorded 160/120)' % ('PASS' if dmax == 160 else 'FAIL', dmax), flush=True)
    abl = a2full.get('ablation_abs_sum')
    abl_ok = (abl == 0)
    CLAIMS.append({'tag': 'B3', 'name': 'ablation (independent draws) is exactly 0 in the frozen A2 record',
                   'ok': abl_ok, 'detail': 'recorded ablation_abs_sum = %s' % abl})
    print('[%s] B3 ablation_abs_sum = %s (frozen A2 record)' % ('PASS' if abl_ok else 'FAIL', abl), flush=True)

    # ---- Q3 null: random axis relabelling, the WHOLE pipeline re-run, per class ----
    nulls = {}
    keys = ['%s_%s' % (e, m) for e in ('E1', 'E2') for m in CONSTRAINED]
    if n_null > 0:
        sm64 = a2m.splitmix64
        for oid in ORDER_IDS:
            agg = dict((k, []) for k in keys)
            nconstr = dict((k, 0) for k in keys)
            plen = []
            for d in range(n_null):
                perm = perm_of(911 + 7 * d, sm64)
                U2 = [U[perm[i]] for i in range(N)]
                K2 = [[K[s][perm[i]] for i in range(N)] for s in range(120)]
                hx2 = [hx[perm[i]] for i in range(N)]
                M1p = [[M1[perm[i]][perm[j]] for j in range(N)] for i in range(N)]
                M2p = [[M2[perm[i]][perm[j]] for j in range(N)] for i in range(N)]
                anti2 = [[anti[perm[i]][perm[j]] for j in range(N)] for i in range(N)]
                pairs2, _t2, _term2, _r2 = simulate(b5, order_list(oid), K2, MUL, hx2, F(123, 2))
                plen.append(len(pairs2))
                for ename, Mp, den in (('E1', M1p, den1), ('E2', M2p, den2)):
                    for mode in CONSTRAINED:
                        val, _b, _d = feasible_chsh(Mp, den, mode, pairs2, anti2, ids)
                        if val is not None:
                            agg['%s_%s' % (ename, mode)].append(val)
                            nconstr['%s_%s' % (ename, mode)] += 1
            summ = {'n_draws': n_null, 'prefix_len_min': min(plen), 'prefix_len_max': max(plen)}
            for k in keys:
                arr = sorted(agg[k])
                obs = results[oid]['feasible'][k]
                ov = None if obs is None else F(obs['value'])
                if arr:
                    ge = sum(1 for x in arr if ov is not None and x >= ov)
                    summ[k] = {'constructible_draws': nconstr[k], 'n': len(arr), 'min': str(arr[0]),
                               'median': str(arr[len(arr) // 2]), 'max': str(arr[-1]),
                               'ge_observed': ge, 'p_permille': (1000 * ge) // len(arr),
                               'observed': None if ov is None else str(ov)}
                else:
                    summ[k] = {'constructible_draws': 0, 'n': 0, 'min': None, 'median': None,
                               'max': None, 'ge_observed': 0, 'p_permille': None,
                               'observed': None if ov is None else str(ov)}
            nulls[oid] = summ
            print('  null %-9s prefix_len [%d..%d]' % (oid, summ['prefix_len_min'], summ['prefix_len_max']),
                  flush=True)
            for k in keys:
                if summ[k]['n']:
                    print('        %-16s constr=%-3d [%s..%s] med=%-7s obs=%-7s p=%s permille'
                          % (k, summ[k]['constructible_draws'], summ[k]['min'], summ[k]['max'],
                             summ[k]['median'], summ[k]['observed'], summ[k]['p_permille']), flush=True)
            s1 = summ['E1_all4']
            CLAIMS.append({'tag': 'C1', 'name': 'null %s: E1_all4 constructible in %d/%d draws, range [%s..%s]'
                           % (oid, s1['constructible_draws'], n_null, s1['min'], s1['max']),
                           'ok': True, 'detail': json.dumps(s1)})

    # ---- A4: significance of ANY budget-feasible |S| > 2 (artifact test) ----
    exceed = []
    for o in ORDER_IDS:
        for e in ('E1', 'E2'):
            for m in CONSTRAINED:
                key = '%s_%s' % (e, m)
                got = results[o]['feasible'][key]
                if got is None or F(got['value']) <= 2:
                    continue
                ns = (nulls.get(o) or {}).get(key) or {}
                exceed.append({'order': o, 'stat': key, 'value': got['value'], 'argmax': got['argmax'],
                               'diag_hits': got['diag_hits'], 'null_n': ns.get('n'),
                               'null_min': ns.get('min'), 'null_median': ns.get('median'),
                               'null_max': ns.get('max'), 'p_permille': ns.get('p_permille')})
    bad = [x for x in exceed if (not x['diag_hits'])
           and (x['p_permille'] is None or x['p_permille'] <= 50)]
    CLAIMS.append({'tag': 'A4', 'name': 'every budget-feasible |S| > 2 is either diagonal-contaminated or '
                                        'not significant against the random-axis null (p > 50 permille)',
                   'ok': not bad, 'detail': 'exceedances = %d ; unexplained = %s'
                   % (len(exceed), json.dumps(bad))})
    print('[%s] A4 budget-feasible exceedances of 2 = %d ; unexplained = %d'
          % ('PASS' if not bad else 'FAIL', len(exceed), len(bad)), flush=True)
    for x in exceed:
        print('        >2  %-9s %-16s |S| = %-6s diag = %-20s null [%s..%s] med=%-7s p = %s permille'
              % (x['order'], x['stat'], x['value'], str(x['diag_hits']) or 'none', x['null_min'],
                 x['null_max'], x['null_median'], x['p_permille']), flush=True)

    out = {'rules_version': RULES, 'order_ids': list(ORDER_IDS), 'baseline': base,
           'per_order': results, 'nulls': nulls, 'exceedances': exceed, 'claims': CLAIMS, 'null_seed_base': 911,
           'null_seed_step': 7, 'elapsed_s': time.time() - t0}
    with io.open(os.path.join(DATA, '15_b3r2_results.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)  [%.1f s]' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                       time.time() - t0))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
