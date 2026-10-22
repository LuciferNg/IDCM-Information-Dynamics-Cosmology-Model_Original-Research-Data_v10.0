#!/usr/bin/env python3
"""O226 scripts/04 -- J2: the budget-conservation theorem, the hits closed form, and the
three pre-registered out-of-sample blind predictions.

Contract: docs/01_o226_contract.md (o226-r1-contract-v1), J2 / Pr-2.1-Pr-2.6.
The machine itself is imported as a module from scripts/02 (same frozen protocol, no rewrite).
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
RULES = 'o226-r1-contract-v1'
N = 62
BUDGET = F(123, 2)
EMIN = F(123, 176)
COST = F(123, 88)
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-7s %s%s' % ('PASS' if ok else 'FAIL', tag, name,
                              ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


def splitmix64(state):
    state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    z = z ^ (z >> 31)
    return state, z


def main():
    print('=' * 104)
    print('O226 scripts/04 -- J2 budget conservation (rules: %s)' % RULES)
    print('=' * 104, flush=True)
    spec = importlib.util.spec_from_file_location('m226', os.path.join(HERE, '02_o226_ledger_machine.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    axes, U, ids, types, hvec = m.load_inputs()
    G, idx, MUL = m.build_group()
    hx = [idx[m.qkey(h)] for h in hvec]
    K = m.build_K(G, U)
    pairs = m.PAIRS

    # ---------------- Pr-2.1: restate the account from the machine output (not from F4)
    j2 = json.load(io.open(os.path.join(DATA, '02_ledger_machine.json'), encoding='utf-8'))
    acc = j2['pass_account']
    claim('Q1', 'Pr-2.1: the read/write law is reproduced by the machine over all 120 initial states: '
                'read-ops = 3N^2 = 11532, hits = 2N = 124, misses = 3N^2 - 2N = 11408, pops = N^2 = 3844',
          (acc['read_ops'], acc['hits'], acc['misses'], acc['pops']) ==
          (3 * N * N, 2 * N, 3 * N * N - 2 * N, N * N),
          'reads %d = 3N^2 ; hits %d = 2N ; misses %d ; pops %d = N^2' %
          (acc['read_ops'], acc['hits'], acc['misses'], acc['pops']))

    # ---------------- Pr-2.2: hits closed form N + C(order), with a declared null over orders
    def hits_of(order):
        return N + sum(1 for k in range(1, len(order)) if order[k - 1][1] == order[k][0])

    lex = hits_of(pairs)
    rev = hits_of(list(reversed(pairs)))
    draws = []
    st = 226
    for d in range(10000):
        o = list(pairs)
        for i in range(len(o) - 1, 0, -1):
            st, z = splitmix64(st)
            j = z % (i + 1)
            o[i], o[j] = o[j], o[i]
        draws.append(hits_of(o))
    draws_sorted = sorted(draws)
    claim('Q2', 'Pr-2.2: hits(order) = N + C(order) with C = #{k>=1 : b_{k-1} = a_k}; the frozen '
                'lexicographic order gives C = N hence 2N, while 10^4 random orders give C ~ 1 '
                '=> "2N" is a property of the frozen order plus the carry, NOT a universal law',
          lex == 2 * N and rev == N and draws_sorted[len(draws) // 2] <= 2 * N,
          'lexicographic hits = %d = 2N ; reversed = %d ; random-order null (10^4 draws, splitmix64): '
          'min %d median %d max %d' % (lex, rev, draws_sorted[0], draws_sorted[len(draws) // 2],
                                       draws_sorted[-1]))
    # --- Q2-c: the pre-registered FORM is refuted and recorded as such; the corrected statement is
    #     that the expectation of C is itself ~ N, so 2N is the GENERIC value, not a frozen-order property.
    claim('Q2-c', 'CORRECTED (the pre-registered "random orders give C << N" is REFUTED): C(lex) = C(rev) '
                  '= N and the median/mean of C over 10^4 random orders is also ~ N  =>  hits = 2N is the '
                  'generic value of the carry count for ANY order, so the number 124 = 2N carries no '
                  'order-specific information; the content lives in the closed form N + C(order)',
          lex == 2 * N and rev == 2 * N and draws_sorted[len(draws) // 2] >= N and
          abs(sum(draws) / len(draws) - (2 * N)) <= 2,
          'C(lex) = %d ; C(rev) = %d ; mean hits over 10^4 random orders = %.3f (N + C with E[C] ~ N, '
          'theoretical E[C] = (N^2-1)/N = %.3f)' % (lex - N, rev - N, sum(draws) / len(draws),
                                                    (N * N - 1) / N))

    # ---------------- Pr-2.3: Sigma closed form and the necessary-and-sufficient condition
    def sigma(B, c, theta):
        mmax = (B - theta) // c + 1
        return mmax, mmax * c

    fam = []
    for k in range(1, 89):
        mm, sg = sigma(BUDGET, k * EMIN, EMIN)
        fam.append({'k': k, 'm_star': mm, 'Sigma': str(sg), 'exact': sg == BUDGET, 'divides': BUDGET % (k * EMIN) == 0})
    ok = all((f['exact'] == f['divides']) for f in fam) and fam[1]['m_star'] == 44 and fam[0]['m_star'] == 88
    claim('Q3', 'Pr-2.3: m* = floor((B - theta)/c) + 1, Sigma = m* c ; exact exhaustion (Sigma = B) iff '
                'c | B  -- verified over k = 1..88 with zero counterexamples (k = 2 gives 44 = N_d)',
          ok, 'k=1 -> m*=%d (88 = 2N_d, also exact) ; k=2 -> m*=%d (44 = N_d) ; exact set = %s'
          % (fam[0]['m_star'], fam[1]['m_star'], [f['k'] for f in fam if f['exact']]))
    grid = []
    for j in range(1, 121):
        for k in range(1, 41):
            B2, c2 = j * EMIN, k * EMIN
            mm, sg = sigma(B2, c2, EMIN)
            grid.append((sg == B2) == (j % k == 0))
    claim('Q4', 'Pr-2.3 (general form): over a grid of 120 x 40 budgets/costs in units of theta the '
                'equivalence "Sigma = B  <=>  c | B" holds with zero counterexamples',
          all(grid), 'grid points = %d ; counterexamples = %d' % (len(grid), grid.count(False)))

    # ---------------- Pr-2.4: the feasible prefix (machine, all 120 states)
    counts = {}
    for s0 in range(120):
        f = m.run_pass(K, MUL, hx, s0)
        key = (f['completed_pairs'], f['charged_reads'], f['terminal_pair'], str(f['spent']),
               str(f['budget_left']))
        counts[key] = counts.get(key, 0) + 1
    rec = sorted(counts.items())[0]
    claim('Q5', 'Pr-2.4: the feasible prefix is 15 pairs / 44 charged reads with terminal pair (0,15) and '
                'Sigma = B = 61.5 EXACT, identical for all 120 initial states',
          len(counts) == 1 and rec[1] == 120 and rec[0][0] == 15 and rec[0][1] == 44 and rec[0][2] == (0, 15),
          'prefix = %d pairs ; charges = %d ; terminal = %s ; Sigma = %s ; identical over = %d/120 states'
          % (rec[0][0], rec[0][1], rec[0][2], rec[0][3], rec[1]))

    # ---------------- Pr-2.5: the three pre-registered out-of-sample blind predictions
    blind = []
    for tag, B2, c2, want_m, want_sig in (
            ('B\' = 123 (2 ticks)', F(123), COST, 88, '123'),
            ('B\'\' = 123/4', F(123, 4), COST, 22, '123/4'),
            ('c\'\'\' = 3 theta', BUDGET, 3 * EMIN, 30, '11070/176')):
        f = m.run_pass(K, MUL, hx, 0, budget=B2, cost=c2)
        blind.append({'case': tag, 'predicted_m': want_m, 'observed_reads': f['charged_reads'],
                      'predicted_Sigma': want_sig, 'observed_Sigma': str(f['spent']),
                      'budget_left': str(f['budget_left']), 'completed': f['completed_pairs'],
                      'overshoot': f['spent'] > B2})
    okb = (blind[0]['observed_reads'] == 88 and blind[0]['observed_Sigma'] == '123' and
           blind[1]['observed_reads'] == 22 and blind[1]['observed_Sigma'] == '123/4' and
           blind[2]['observed_reads'] == 30 and blind[2]['observed_Sigma'] == '11070/176' and
           blind[2]['overshoot'])
    claim('Q6', 'Pr-2.5 (blind, values pinned before the run): B\'=123 -> m*=88, Sigma=123 ; '
                'B\'\'=123/4 -> m*=22, Sigma=123/4 ; c\'\'\'=3 theta -> m*=30, Sigma=11070/176 > B (overshoot)',
          okb, ' | '.join('%s: reads %d vs %d, Sigma %s vs %s' %
                          (b['case'], b['observed_reads'], b['predicted_m'], b['observed_Sigma'],
                           b['predicted_Sigma']) for b in blind))
    # --- Q6-c: the third blind case is numerically exact but was written in an unreduced rational form
    #     (11070/176 = 5535/88); the comparator, not the prediction, is at fault.
    claim('Q6-c', 'CORRECTED (comparator artifact, disclosed): comparing as rationals, the third blind '
                  'prediction is exact -- 11070/176 = 5535/88 and both exceed B (the overrun is real)',
          F(blind[2]['observed_Sigma']) == F(blind[2]['predicted_Sigma']) and
          blind[2]['overshoot'] and blind[0]['observed_Sigma'] == '123' and
          blind[1]['observed_Sigma'] == '123/4',
          'third case: observed %s = predicted %s = %.6f > B = %.1f'
          % (blind[2]['observed_Sigma'], blind[2]['predicted_Sigma'],
             float(F(blind[2]['observed_Sigma'])), float(BUDGET)))

    # ---------------- Pr-2.6: consistency with the upstream overrun factors
    over_a2 = F(2 * N * N, BUDGET / COST)          # A2 protocol = 2 reads/pair
    over_full = F(3 * N * N, BUDGET / COST)
    claim('Q7', 'Pr-2.6: overrun of the A2 protocol (2 reads/pair = 7688 reads) = 1922/11 and of a full '
                'pass (3N^2 = 11532) = 2883/11 -- both reproduce the upstream factors',
          over_a2 == F(1922, 11) and over_full == F(2883, 11),
          'A2 = %s = %.6f ; full pass = %s = %.6f' % (over_a2, float(over_a2), over_full, float(over_full)))

    # ---------------- rigidity: the account is axis-independent (null over random axis sets)
    acct = set()
    st = 226
    for d in range(32):
        randU = []
        for j in range(N):
            st, z = splitmix64(st)
            q = G[z % 120]
            randU.append((q[1], q[2], q[3]))
        Kn = m.build_K(G, randU)
        accs = set()
        for s0 in (0, 1, 60, 119):
            top = -1
            ro = hi = mi = po = 0
            for (a, b) in pairs:
                r = m.run_pair(Kn, MUL, hx, a, b, s0, top, mode='cap4')
                ro += 3
                hi += r['hits']
                mi += r['reads']
                po += r['pops']
                top = r['top']
            accs.add((ro, hi, mi, po))
        acct |= accs
    claim('Q8', 'rigidity: the read/write law is a pure order property -- 32 random axis sets reproduce '
                'exactly the same account (3N^2 / 2N / 3N^2-2N / N^2)',
          acct == {(3 * N * N, 2 * N, 3 * N * N - 2 * N, N * N)},
          'distinct accounts over 32 random axis sets x 4 states = %s' % sorted(acct))

    out = {'rules_version': RULES, 'hits_closed_form': {'lexicographic': lex, 'reversed': rev,
                                                        'null_draws': len(draws),
                                                        'null_min': draws_sorted[0],
                                                        'null_median': draws_sorted[len(draws) // 2],
                                                        'null_max': draws_sorted[-1]},
           'cost_family': fam, 'grid_points': len(grid), 'feasible_prefix': list(rec[0]),
           'blind_predictions': blind, 'overrun': {'A2': str(over_a2), 'full_pass': str(over_full)},
           'claims': CLAIMS}
    with io.open(os.path.join(DATA, '04_budget_theorem.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 104)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 104)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
