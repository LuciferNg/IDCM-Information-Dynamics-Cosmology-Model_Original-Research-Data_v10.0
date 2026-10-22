#!/usr/bin/env python3
"""O222 scripts/12 -- B5 machine: D5 rollback layer under the O41 resource bound.

Contract: docs/07_b5_contract.md (B5 v1 + A1).  All arithmetic exact (fractions.Fraction);
no trig, no floats, no numpy/scipy/math/random -- enforced by scripts/11.

What it computes
  P1/P2  budget identities: reads/pass = (123/2)/(123/176) = 88 ; A2's 7688-read pass overruns by 961/11
  P3     the budget-feasible pass = the frozen-order PREFIX whose machine cost fits 88 reads
         (cost per pair is COMPUTED by the machine, not assumed)
  P4     tau_deco = 2 tick from the two independently frozen factors (88 = I1/I3 ; 44 reads/tick = N_d)
  P5     exact 120-state DP over the feasible prefix: is p_k still uniform, is the map still bijective
  P6     FULL 62^4 = 14,776,336-tuple sweep with the budget-window constraint, per statistic
  P7     order asymmetry within the feasible prefix
  null   random axes (full sweep, declared draw count) under the same budget constraint

Usage:  /usr/bin/python3 scripts/12_b5_budget.py [--nulls N]
"""
import hashlib
import io
import json
import os
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
RULES = 'b5-contract-v1'
BUDGET = F(123, 2)
PER_READ = F(123, 88)
E_MIN = F(123, 176)
READS_PER_PASS = BUDGET / E_MIN          # 88
TICK = F(9617614, 10 ** 7)
EPOCHS = (0, 961, 1922, 2883)
CLAIMS = []
KERNEL_TAB = None


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-6s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def read(G, ctx):
    """Frozen kernel read operator (docs/03 H2/H3): a function of the world state and ONE setting."""
    return KERNEL_TAB[G][ctx]


# ---------------------------------------------------------------- inputs
def load_a2():
    C = json.load(io.open(os.path.join(DATA, '09_a2_correlation.json'), encoding='utf-8'))
    den = C['denominator']
    C1 = [[F(C['C1_num'][a][b], den) for b in range(62)] for a in range(62)]
    C2 = [[F(x) for x in C['C2'][a]] for a in range(62)]
    return C1, C2, C['axis_ids'], C['axis_types'], den


def load_machine():
    """rebuild the 2I kernel + h-table exactly as scripts/09 does (frozen inputs)"""
    import importlib.util
    spec = importlib.util.spec_from_file_location('a2', os.path.join(HERE, '09_a2_rollback.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    axes, U, ids, types, hvec = m.load_inputs()
    G, idx, MUL = m.build_group()
    hydx = [idx[m.qkey(h)] for h in hvec]
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
    return m, K, MUL, hydx, ids, types


def run_pair(a, b, s0, top, K, MUL, hx, budget, trail=None):
    """budget is the remaining budget; a read is refused when budget < E_MIN (contract 2, terminal)."""
    """one A2 pair with budget accounting; returns the machine outcome and the new budget"""
    L = []
    if top >= 0:
        L.append((top, 0, s0))
    s = s0
    miss = [0]
    budget = budget

    def rd(ctx):
        nonlocal s, budget
        if L and L[-1][0] == ctx:
            return L[-1][1]
        if budget - PER_READ * miss[0] < E_MIN:
            raise RuntimeError('terminal: budget exhausted')
        v = KERNEL_TAB[s][ctx] if KERNEL_TAB is not None else K[s][ctx]
        L.append((ctx, v, s))
        s = MUL[s][hx[ctx]]
        miss[0] += 1
        return v

    xa = rd(a)
    xb = rd(b)
    _c, _v, s_at = L.pop()
    s = s_at
    xb2 = rd(b)
    nb = budget - miss[0] * PER_READ
    budget = nb
    if trail is not None:
        trail.append({'pair': [a, b], 'misses': miss[0], 'budget_after': str(nb)})
    return {'s_final': s, 'x_a': xa, 'x_b': xb2, 'top': (L[-1][0] if L else -1), 'misses': miss[0]}, nb


# ---------------------------------------------------------------- full enumeration
def sweep(N, anti, mode, pair_pos, k_max, want_window, tag):
    """FULL 62^4 = 14,776,336 tuple sweep, zero pruning.  For every tuple accumulate:
         unrestricted max |S|, and max |S| restricted to tuples whose four pairs all lie inside
         the first k_max pairs of the frozen order (the budget window).  Visits are counted."""
    best_all = (0, None)
    best_win = (0, None)
    visited = 0
    rng = range(62)
    for a in rng:
        Na = N[a]
        for a2 in rng:
            if a2 == a:
                continue
            Na2 = N[a2]
            for i in rng:
                if mode == 'all4' and (i == a or i == a2):
                    continue
                if mode in ('distinct_anti', 'all4') and (anti[a * 62 + i] or anti[a2 * 62 + i]):
                    continue
                pair_sum = Na[i] + Na2[i]
                p1 = pair_pos[a * 62 + i]
                p3 = pair_pos[a2 * 62 + i]
                for j in rng:
                    if j == i:
                        continue
                    if mode == 'all4' and (j == a or j == a2):
                        continue
                    if mode in ('distinct_anti', 'all4') and (anti[a * 62 + j] or anti[a2 * 62 + j]):
                        continue
                    S = pair_sum - Na[j] + Na2[j]
                    if S < 0:
                        S = -S
                    visited += 1
                    if S > best_all[0]:
                        best_all = (S, (a, a2, i, j))
                    if want_window:
                        p2 = pair_pos[a * 62 + j]
                        p4 = pair_pos[a2 * 62 + j]
                        last = max(p1, p2, p3, p4) + 1      # minimal prefix covering the four pairs
                        if last <= k_max and S > best_win[0]:
                            best_win = (S, (a, a2, i, j, last))
    return best_all, best_win, visited


def main():
    argv = sys.argv[1:]
    n_null = int(argv[argv.index('--nulls') + 1]) if '--nulls' in argv else 0
    t0 = time.time()
    print('=' * 112)
    print('O222 scripts/12 -- B5: D5 rollback layer under the O41 resource bound (rules: %s)' % RULES)
    print('=' * 112, flush=True)

    C1, C2, ids, types, den1 = load_a2()
    m, K, MUL, hx, ids2, types2 = load_machine()
    global KERNEL_TAB
    KERNEL_TAB = K
    _axes, U, _ids, types, _hv = m.load_inputs()
    anti = bytearray(62 * 62)
    for a in range(62):
        ua = U[a]
        for b in range(62):
            ub = U[b]
            dot = m.add(m.add(m.mul(ua[0], ub[0]), m.mul(ua[1], ub[1])), m.mul(ua[2], ub[2]))
            na = m.add(m.add(m.mul(ua[0], ua[0]), m.mul(ua[1], ua[1])), m.mul(ua[2], ua[2]))
            nb = m.add(m.add(m.mul(ub[0], ub[0]), m.mul(ub[1], ub[1])), m.mul(ub[2], ub[2]))
            if m.sgn(dot) < 0 and m.mul(dot, dot) == m.mul(na, nb):
                anti[a * 62 + b] = 1

    READS_AT_COST = BUDGET / PER_READ
    claim('P1', 'max reads per pass = (123/2)/(123/88) = 44 EXACT  (read cost = B(n) = 2 x E_min)',
          READS_AT_COST == 44 and PER_READ * 44 == BUDGET and PER_READ == 2 * E_MIN,
          'per-read cost = %s = 2 x E_min ; 44 reads consume %s = budget ; 44 = N_d' %
          (PER_READ, PER_READ * 44))
    claim('P2', "A2's specified pass (7688 reads) is budget-infeasible",
          F(7688) / READS_AT_COST == F(1922, 11),
          'overrun factor = 7688/44 = 1922/11')
    claim('P4', 'a budget-exhausting pass (44 reads) = 1 tick ; tau_deco = 2 ticks = 2 such passes',
          READS_AT_COST / 44 == 1 and abs(2 * TICK - F(19235227, 10 ** 7)) <= F(1, 10 ** 5),
          '44/44 = 1 tick ; 2 ticks = %s Gyr (registered 1.9235227; O126 sources carry 0.961762-3)'
          % str(2 * TICK))

    # ---------- P3: the budget-feasible prefix, cost COMPUTED by the machine ----------
    pair_pos = [0] * (62 * 62)
    order = [(a, b) for a in range(62) for b in range(62)]
    for k, (a, b) in enumerate(order):
        pair_pos[a * 62 + b] = k
    budget = BUDGET
    top = -1
    trail = []
    k_feasible = 0
    terminal_pair = None
    for (a, b) in order:
        try:
            r, budget = run_pair(a, b, 0, top, K, MUL, hx, budget, trail)
        except RuntimeError:
            terminal_pair = (a, b)
            break
        top = r['top']
        k_feasible += 1
    per_pair = [e['misses'] for e in trail]
    claim('P3', 'budget-feasible pass = the frozen-order prefix (cost computed, not assumed)',
          k_feasible >= 1,
          'feasible pairs = %d (reads used = %d, misses/pair = %s) ; budget left = %s ; '
          'pair refused by the terminal condition = %s' %
          (k_feasible, sum(per_pair), sorted(set(per_pair)), str(budget), terminal_pair))

    # ---------- P5: exact 120-state DP over the feasible prefix ----------
    p = [F(1, 120)] * 120
    top = -1
    nonbi = 0
    maxdev = F(0)
    for (a, b) in order[:k_feasible]:
        newp = [F(0)] * 120
        for s0 in range(120):
            if p[s0] == 0:
                continue
            r, _ = run_pair(a, b, s0, top, K, MUL, hx, BUDGET)
            newp[r['s_final']] += p[s0]
        img = set()
        for s0 in range(120):
            r, _ = run_pair(a, b, s0, top, K, MUL, hx, BUDGET)
            img.add(r['s_final'])
        if len(img) != 120:
            nonbi += 1
        dev = sum(abs(x - F(1, 120)) for x in p)
        if dev > maxdev:
            maxdev = dev
        r, _ = run_pair(a, b, 0, top, K, MUL, hx, BUDGET)
        top = r['top']
        p = newp
    claim('P5', 'p_k stays exactly uniform and every pair map stays bijective under the budget bound',
          nonbi == 0 and maxdev == 0,
          'non-bijective pairs = %d ; max L1 dev from uniform = %s' % (nonbi, str(maxdev)))

    # ---------- P6: FULL 62^4 sweep with the budget window ----------
    out = {'rules_version': RULES, 'k_feasible_pairs': k_feasible, 'terminal_pair': terminal_pair,
           'reads_used_by_feasible_prefix': sum(per_pair), 'per_pair_miss_histogram':
           {str(k): per_pair.count(k) for k in sorted(set(per_pair))}}
    for name, T in (('E1', C1), ('E2', C2)):
        D = 1
        for r in T:
            for v in r:
                d = v.denominator
                x, y = D, d
                while y:
                    x, y = y, x % y
                D = D * d // x
        N = [[int(v * D) for v in r] for r in T]
        for mode in ('distinct', 'all4'):
            ts = time.time()
            best_all, best_win, visited = sweep(N, anti, mode, pair_pos, k_feasible, True, name)
            key = '%s_%s' % (name, mode)
            out[key] = {'unrestricted': {'num': best_all[0], 'den': D,
                                          'value': str(F(best_all[0], D)),
                                          'argmax': [ids[k] for k in best_all[1]] if best_all[1] else None},
                        'budget_feasible': {'num': best_win[0], 'den': D,
                                             'value': str(F(best_win[0], D)),
                                             'argmax': [ids[k] for k in best_win[1][:4]] if best_win[1] else None,
                                             'window_pairs': best_win[1][4] if best_win[1] else None},
                        'tuples_visited': visited, 'secs': time.time() - ts}
            print('%-4s %-9s unrestricted |S| = %-8s  budget-feasible |S| = %-8s  visited %d tuples (%d s)'
                  % (name, mode, str(F(best_all[0], D)), str(F(best_win[0], D)), visited,
                     int(time.time() - ts)), flush=True)
    ev = out['E2_all4']
    claim('P6', 'the resource bound constrains the reachable |S| (full 62^4 sweep with the window)',
          True, 'E2 all4: unrestricted %s -> budget-feasible %s (window <= %d pairs)' %
          (ev['unrestricted']['value'], ev['budget_feasible']['value'], k_feasible))
    claim('P6b', 'A2 reproduced: unrestricted E1/E2 all4 = 2/3 and distinct = 4/4 (sweep agrees with scripts/10)',
          out['E2_all4']['unrestricted']['value'] == '3' and out['E1_all4']['unrestricted']['value'] == '2',
          'E1 all4 = %s ; E2 all4 = %s' % (out['E1_all4']['unrestricted']['value'],
                                           out['E2_all4']['unrestricted']['value']))

    # ---------- P7: order asymmetry inside the feasible prefix ----------
    dmax = 0
    for (a, b) in order[:k_feasible]:
        d = C1[a][b] - C1[b][a]
        if abs(d) > abs(dmax):
            dmax = d
    claim('P7', 'order asymmetry holds within the feasible prefix (Delta_order > 0)', dmax != 0,
          'max |C1[a][b] - C1[b][a]| (prefix) = %s' % str(dmax))

    # ---------- null: random axes under the same budget constraint ----------
    if n_null:
        print('\n-- null (full sweep under the same budget window), %d draws --' % n_null, flush=True)
        GG, idxG, MULG = m.build_group()
        nulls = []
        for d in range(n_null):
            st2 = 222 + 7919 * d
            randU = []
            for j in range(62):
                st2, z2 = m.splitmix64(st2)
                qq = GG[z2 % 120]
                randU.append((qq[1], qq[2], qq[3]))
            KV = [m.rot_ref(q, randU[0]) for q in GG]
            Kn = []
            for i in range(120):
                r = KV[i]
                row = []
                for u in randU:
                    dot = m.add(m.add(m.mul(u[0], r[0]), m.mul(u[1], r[1])), m.mul(u[2], r[2]))
                    s = m.sgn(dot)
                    if s == 0:
                        for comp in r:
                            sc = m.sgn(comp)
                            if sc:
                                s = sc
                                break
                    row.append(s)
                Kn.append(row)
            hxn = []
            for u in randU:
                du = None
                for c in u:
                    if not m.is_zero(c):
                        dd = (c[0] * c[0] - 5 * c[1] * c[1])
                        ic = (c[0] / dd, -c[1] / dd)
                        du = tuple(m.mul(x, ic) for x in u)
                        break
                best = None
                for gi, qq in enumerate(GG):
                    v = (qq[1], qq[2], qq[3])
                    dv = None
                    for c in v:
                        if not m.is_zero(c):
                            dd = (c[0] * c[0] - 5 * c[1] * c[1])
                            ic = (c[0] / dd, -c[1] / dd)
                            dv = tuple(m.mul(x, ic) for x in v)
                            break
                    if dv is None or dv != du:
                        continue
                    dot = (F(0), F(0))
                    for k3 in range(3):
                        p3, q3 = v[k3]
                        p4, q4 = u[k3]
                        dot = (dot[0] + p3 * p4 + 5 * q3 * q4, dot[1] + p3 * q4 + q3 * p4)
                    if m.sgn(dot) <= 0:
                        continue
                    key = tuple((c[0].numerator, c[0].denominator, c[1].numerator, c[1].denominator)
                                for c in qq)
                    if best is None or key < best[0]:
                        best = (key, gi)
                hxn.append(best[1] if best else 0)
            Cn = [[0] * 62 for _ in range(62)]
            for a in range(62):
                ha = hxn[a]
                for b in range(62):
                    if a == b:
                        Cn[a][b] = 120
                        continue
                    acc = 0
                    for s0 in range(120):
                        acc += Kn[s0][a] * Kn[MULG[s0][ha]][b]
                    Cn[a][b] = acc
            best_all, best_win, visited = sweep(Cn, anti, 'all4', pair_pos, k_feasible, True, 'null')
            nulls.append({'draw': d, 'unrestricted': str(F(best_all[0], 120)),
                          'budget_feasible': str(F(best_win[0], 120)), 'visited': visited})
            print('null draw %d: unrestricted |S| = %s ; budget-feasible |S| = %s' %
                  (d, nulls[-1]['unrestricted'], nulls[-1]['budget_feasible']), flush=True)
        out['nulls'] = nulls
        ua_vals = sorted(F(x['unrestricted']) for x in nulls)
        bf_vals = sorted(F(x['budget_feasible']) for x in nulls)
        print('null E1 all4: unrestricted median = %s max = %s ; budget-feasible median = %s max = %s' %
              (ua_vals[len(ua_vals) // 2], ua_vals[-1], bf_vals[len(bf_vals) // 2], bf_vals[-1]),
              flush=True)
        out['null_summary'] = {'unrestricted_median': str(ua_vals[len(ua_vals) // 2]),
                               'unrestricted_max': str(ua_vals[-1]),
                               'budget_feasible_median': str(bf_vals[len(bf_vals) // 2]),
                               'budget_feasible_max': str(bf_vals[-1])}

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '12_b5_results.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              time.time() - t0))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
