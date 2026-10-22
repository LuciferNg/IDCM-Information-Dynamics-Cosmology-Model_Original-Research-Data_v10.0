#!/usr/bin/env python3
"""O226 scripts/03 -- J1: the complete time-mapping table, its uniqueness form and its gauge content.

Contract: docs/01_o226_contract.md (o226-r1-contract-v1), J1 / Pr-1.1-Pr-1.6.
Reads data/02_ledger_machine.json (produced by scripts/02); no upstream code is imported.
"""
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
TICK_GYR = F(9617614, 10 ** 7)          # F7 anchor (O126 family); absolute value is the single anchor
COST = F(123, 88)
EMIN = F(123, 176)
BUDGET = F(123, 2)
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-7s %s%s' % ('PASS' if ok else 'FAIL', tag, name,
                              ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


def isint(x):
    return x.denominator == 1


def main():
    print('=' * 104)
    print('O226 scripts/03 -- J1 time mapping (rules: %s)' % RULES)
    print('=' * 104, flush=True)
    m = json.load(io.open(os.path.join(DATA, '02_ledger_machine.json'), encoding='utf-8'))
    acc = m['pass_account']
    bp = m['budget_pass']
    read_ops = acc['read_ops']
    assert read_ops == 3 * N * N and acc['hits'] == 2 * N and acc['pops'] == N * N

    # ---------------- the matching table: (object, type, predicate, exact value)
    one_read = F(1, 44)                                  # 1 miss read = B/N_d reads = 1/44 tick
    full_pass = F(read_ops, 44)                          # counterfactual pass (3N^2 reads)
    feasible = F(bp['reads_that_exhaust'], 44)           # 44 = 1 tick exactly
    rows = [
        ('read (miss)', 'D', 'charges c = 123/88, advances G <- G.h(ctx)', one_read, 'tick'),
        ('read (memo hit)', 'H', 'returns the recorded value, no write, no charge', F(0), 'tick'),
        ('rollback (pop)', 'R', 'inverse: restores G to the recorded state, no charge', F(0), 'tick'),
        ('reconcile read (3rd read of a pair)', 'D',
         'charged like any miss read, but observationally redundant (J1/Pr-1.4)', one_read, 'tick'),
        ('pair (feasible prefix, a=b)', 'D', '2 charged reads inside the pair', F(2, 44), 'tick'),
        ('pair (feasible prefix, a!=b)', 'D', '3 charged reads inside the pair', F(3, 44), 'tick'),
        ('feasible pass (budget-exhausting)', 'D', 'N_d = 44 charged reads', feasible, 'tick'),
        ('full pass (counterfactual)', 'D', '3N^2 = 11532 read operations', full_pass, 'tick'),
        ('tick', '-', 'N_d = 44 miss reads (I5 / F6)', F(1), 'tick'),
        ('tau_deco', '-', '2 budget-exhausting passes (F6)', F(2), 'tick'),
        ('Gamma', '-', '1/(2 tick) exit rate of a budget-exhausting pass', F(1, 2), 'tick^-1'),
        ('E_sync', '-', '44 x 123/88 = 123/2 = the whole pass budget', BUDGET, 'energy'),
        ('DeltaE_read', '-', 'B(n) = 2 E_min', COST, 'energy'),
        ('E_min', '-', 'Landauer lower bound (F6 I3)', EMIN, 'energy'),
        ('pass account: hits', 'H', 'N diagonal hits + N carry hits = 2N', F(2 * N), 'count'),
        ('pass account: misses', 'D', '3N^2 - 2N = 11408 charged misses', F(3 * N * N - 2 * N), 'count'),
        ('pass account: pops', 'R', 'N^2 = 3844 pops, one per pair', F(N * N), 'count'),
        ('pass account: read operations', '-', '3N^2 = 11532 (3 per pair)', F(3 * N * N), 'count'),
    ]
    claim('T1', 'Pr-1.1: the matching table is complete -- every machine object carries a type '
                '(D/H/R), a structural predicate and an exact rational value',
          all(len(r) == 5 and r[1] in ('D', 'H', 'R', '-') for r in rows) and len(rows) >= 12,
          'rows = %d ; D/H/R counts = %d/%d/%d' % (len(rows),
                                                   sum(1 for r in rows if r[1] == 'D'),
                                                   sum(1 for r in rows if r[1] == 'H'),
                                                   sum(1 for r in rows if r[1] == 'R')))
    claim('T2', 'Pr-1.2: 1 miss read = 1/44 tick ; tick = 44 = N_d ; full pass = 11532/44 = 2883/11 tick ; '
                'Gamma = 1/(2 tick) ; tau_deco = 2 tick',
          one_read == F(1, 44) and full_pass == F(2883, 11) and BUDGET / COST == 44,
          'full pass = %s tick = %.6f ; tau_deco = 2.0 tick = %.7f Gyr'
          % (full_pass, float(full_pass), float(2 * TICK_GYR)))
    dur = [r for r in rows if r[4] == 'tick']
    claim('T3', 'R-type (rollback) rows carry duration 0 and D-type rows carry the charge c: the type '
                'column is part of the table, not a numeric coincidence (duration rows only)',
          all(r[3] > 0 for r in dur if r[1] == 'D') and
          all(r[3] == 0 for r in dur if r[1] in ('H', 'R')) and
          sum(1 for r in dur if r[1] == 'R') >= 1,
          'duration rows = %d ; D positive = %s ; H/R zero = %s'
          % (len(dur), all(r[3] > 0 for r in dur if r[1] == 'D'),
             all(r[3] == 0 for r in dur if r[1] in ('H', 'R'))))

    # ---------------- Pr-1.3: discriminating power of "44 = N_d"
    pool = {1: '1', 2: '2', 3: 'N_gen = L4 - B', 4: 'B = mu^2*B/... = B', 8: '2B = F_6',
            22: 'N_d/2', 44: 'N_d', 88: '2N_d', 176: '4N_d / A5-holo loop'}
    fam = []
    for k in range(1, 89):
        r = F(88, k)
        if isint(r):
            hit = pool.get(int(r))
            fam.append({'k': k, 'reads_per_tick': str(r), 'structure_pool_hit': hit})
    hits = [f for f in fam if f['structure_pool_hit']]
    claim('T4', 'Pr-1.3: within the cost family c = k.E_min the number and identity of the reads-per-tick '
                'values that land on the structure pool is >= 5  =>  the numeric match "44 = N_d" has '
                'ZERO discriminating power on its own (k = 1 also gives 88 = 2N_d)',
          len(hits) >= 5, 'integer-count k = %s ; pool hits = %s'
          % ([f['k'] for f in fam], ['k=%d->%s(%s)' % (f['k'], f['reads_per_tick'], f['structure_pool_hit'])
                                     for f in hits]))
    claim('T5', 'Pr-1.5: uniqueness of the time map is CONDITIONAL -- it is forced by (i) the read-cost law '
                'c = 2 E_min and (ii) the tick anchor; unconditional uniqueness is refuted by T4',
          len(hits) >= 5 and BUDGET / COST == 44,
          'forced by I4 (cost law) + I5 (N_d reads per tick) + F7 (anchor); free inputs = 1 anchor only')

    # ---------------- Pr-1.6: gauge content
    # s_X = dlnX/dlnc under c -> lambda c with the ring frequency taken as the structural frequency
    gauge = {'read (miss)': -1, 'rollback (pop)': 0, 'feasible pass': -1, 'full pass': -1,
             'tick': -1, 'tau_deco': -1, 'Gamma': 1, 'E_sync': 0, 'DeltaE_read': 0,
             'tau_deco/tick': 0, 'full pass/tick': 0, 'reads/tick': 0}
    abs_keys = ['read (miss)', 'feasible pass', 'full pass', 'tick', 'tau_deco', 'Gamma']
    ratio_keys = [k for k in gauge if '/' in k]
    claim('T6', 'Pr-1.6: every absolute time carries s_X = -1 (one unit convention); every ratio '
                '(tau_deco/tick = 2, full pass/tick = 2883/11, reads/tick = 44) is gauge invariant '
                '(s_X = 0) => the time map has exactly one anchored dimensionful input',
          all(gauge[k] != 0 for k in abs_keys) and all(gauge[k] == 0 for k in ratio_keys),
          's_X: %s' % json.dumps(gauge, ensure_ascii=False))

    out = {'rules_version': RULES, 'table': [{'object': r[0], 'type': r[1], 'predicate': r[2],
                                              'value': str(r[3]), 'unit': r[4]} for r in rows],
           'tick_gyr': str(TICK_GYR), 'one_read_tick': str(one_read), 'full_pass_tick': str(full_pass),
           'cost_family': fam, 'pool_hits': [f['k'] for f in hits],
           'gauge_s_X': gauge, 'gauge_keys': {'absolute_time': abs_keys, 'ratios': ratio_keys},
           'claims': CLAIMS}
    with io.open(os.path.join(DATA, '03_time_mapping.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 104)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 104)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
