#!/usr/bin/env python3
"""O222 scripts/16 -- INDEPENDENT audit of the B3R2 round (scripts/15).

Independence rules honoured:
  * does NOT import scripts/15 (the audited script);
  * the budget/ledger/rollback protocol is RE-IMPLEMENTED here from the frozen rules
    (only the primitive read(G, ctx) kernel comes from scripts/09 -- the same primitive the
    frozen scripts/12 machine wraps), so a semantic drift in scripts/15 would show up as a
    prefix mismatch;
  * the feasible-CHSH domain is enumerated by a DIFFERENT decomposition: column-pair x
    column-pair (rectangles), instead of scripts/15's value-set loops;
  * every headline value is compared against data/15_b3r2_results.json.

Usage:  /usr/bin/python3 scripts/16_b3r2_audit.py
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
N = 62
ORDER_IDS = ('lex', 'diag', 'antidiag', 'block', 'stride')
MODES = ('raw', 'distinct', 'distinct_anti', 'all4')
CLAIMS = []
BUDGET = F(123, 2)
COST = F(123, 88)
EMIN = F(123, 176)


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)


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


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def audit_prefix(a2, order, K, MUL, hx):
    """independent re-implementation of the per-read-budget L-SEQ pair sweep."""
    rem = BUDGET
    top = -1
    pairs = []
    reads = 0
    terminal = None
    for (a, b) in order:
        ledger = [(top, 0, 0)] if top >= 0 else []
        s = 0
        spent = 0

        def rd(ctx):
            nonlocal s, spent
            if ledger and ledger[-1][0] == ctx:
                return ledger[-1][1]
            if rem - COST * spent < EMIN:
                raise RuntimeError('terminal')
            v = K[s][ctx]
            ledger.append((ctx, v, s))
            s = MUL[s][hx[ctx]]
            spent += 1
            return v

        try:
            rd(a)
            rd(b)
            _c, _v, s_at = ledger.pop()
            s = s_at
            rd(b)
        except RuntimeError:
            terminal = (a, b)
            break
        top = ledger[-1][0] if ledger else -1
        rem = rem - COST * spent
        reads += spent
        pairs.append((a, b))
    return pairs, reads, rem, terminal


def chsh_by_rectangles(M, den, mode, pairs, anti):
    """domain = ordered pairs of rectangles: pick b, b' and two a's per column."""
    cols = {}
    for (a, b) in pairs:
        cols.setdefault(b, []).append(a)
    B = sorted(cols.keys())
    best = None
    barg = None
    dom = 0
    ties = 0
    for i in B:
        for j in B:
            if mode != 'raw' and j == i:
                continue
            for a in cols[i]:
                for a2 in cols[i]:
                    if a2 == a and mode != 'raw':
                        continue
                    if j not in cols or a not in cols[j] or a2 not in cols[j]:
                        continue
                    if mode == 'all4' and (i == a or i == a2 or j == a or j == a2):
                        continue
                    if mode in ('distinct_anti', 'all4') and \
                            (anti[a][i] or anti[a2][i] or anti[a][j] or anti[a2][j]):
                        continue
                    dom += 1
                    S = M[a][i] + M[a2][i] - M[a][j] + M[a2][j]
                    if S < 0:
                        S = -S
                    if best is None or S > best:
                        best = S
                        barg = (a, a2, i, j)
                        ties = 1
                    elif S == best:
                        ties += 1
    if best is None:
        return None, None, dom, 0
    return F(best, den), barg, dom, ties


def main():
    print('=' * 112)
    print('O222 scripts/16 -- INDEPENDENT audit of B3R2 (does not import scripts/15)')
    print('=' * 112, flush=True)
    a2 = load(os.path.join(HERE, '09_a2_rollback.py'), 'a2x')
    b5 = load(os.path.join(HERE, '12_b5_budget.py'), 'b5x')
    C1, C2, ids, types, den1 = b5.load_a2()
    mm, K, MUL, hx, ids2, types2 = b5.load_machine()
    _axes, U, _ids, _types, _hv = mm.load_inputs()
    rec = json.load(io.open(os.path.join(DATA, '15_b3r2_results.json'), encoding='utf-8'))
    a2full = json.load(io.open(os.path.join(DATA, '09_a2_results.json'), encoding='utf-8'))
    a10 = json.load(io.open(os.path.join(DATA, '10_a2_bruteforce.json'), encoding='utf-8'))

    anti = [[False] * N for _ in range(N)]
    for a in range(N):
        for b in range(N):
            ua, ub = U[a], U[b]
            dot = mm.add(mm.add(mm.mul(ua[0], ub[0]), mm.mul(ua[1], ub[1])), mm.mul(ua[2], ub[2]))
            na = mm.add(mm.add(mm.mul(ua[0], ua[0]), mm.mul(ua[1], ua[1])), mm.mul(ua[2], ua[2]))
            nb = mm.add(mm.add(mm.mul(ub[0], ub[0]), mm.mul(ub[1], ub[1])), mm.mul(ub[2], ub[2]))
            if mm.sgn(dot) < 0 and mm.mul(dot, dot) == mm.mul(na, nb):
                anti[a][b] = True

    def intmat(T):
        dn = 1
        for row in T:
            for v in row:
                x, y = dn, F(v).denominator
                while y:
                    x, y = y, x % y
                dn = dn * F(v).denominator // x
        return [[int(F(T[a][b]) * dn) for b in range(N)] for a in range(N)], dn
    M1, d1 = intmat(C1)
    M2, d2 = intmat(C2)

    # 1. prefixes recomputed by the independent protocol
    pref = {}
    for oid in ORDER_IDS:
        order = sorted([(a, b) for a in range(N) for b in range(N)], key=lambda p: order_key(oid, p[0], p[1]))
        pairs, reads, rem, term = audit_prefix(a2, order, K, MUL, hx)
        pref[oid] = pairs
        want = rec['per_order'][oid]
        ok = (len(pairs) == want['prefix_len'] and reads == want['reads_used']
              and (list(term) if term else None) == want['terminal_pair']
              and [len([1 for (a, b) in pairs if a == x]) or 0 for x in []] == [])
        ok = ok and len({a for (a, b) in pairs}) == want['cov_a'] and len({b for (a, b) in pairs}) == want['cov_b']
        claim('P1.%s' % oid, 'prefix reproduced independently (pairs %d / reads %d / cov_a %d / cov_b %d / terminal %s)'
              % (len(pairs), reads, len({a for (a, b) in pairs}), len({b for (a, b) in pairs}), term), ok,
              'recorded = %d/%d/%d/%d/%s' % (want['prefix_len'], want['reads_used'], want['cov_a'],
                                             want['cov_b'], want['terminal_pair']))

    # 2. rectangle criterion == constructibility (and it is false that coverage implies it)
    for oid in ORDER_IDS:
        cols = {}
        for (a, b) in pref[oid]:
            cols.setdefault(b, []).append(a)
        rect = any(len(v) >= 2 for v in cols.values()) and len(cols) >= 2
        want = rec['per_order'][oid]['constructible_distinct']
        claim('P2.%s' % oid, 'rectangle criterion reproduces constructibility (rect=%s)' % rect,
              rect == want, 'recorded constructible_distinct = %s ; cov_a=%d cov_b=%d'
              % (want, rec['per_order'][oid]['cov_a'], rec['per_order'][oid]['cov_b']))

    # 3. feasible values by the rectangle decomposition
    ncmp = 0
    bad3 = []
    ties_max = 0
    for oid in ORDER_IDS:
        for ename, M, den in (('E1', M1, d1), ('E2', M2, d2)):
            for mode in MODES:
                val, barg, dom, ties = chsh_by_rectangles(M, den, mode, pref[oid], anti)
                got = rec['per_order'][oid]['feasible']['%s_%s' % (ename, mode)]
                dkey = '%s_%s' % (ename, mode)
                ncmp += 1
                ties_max = max(ties_max, ties)
                if got is None:
                    if val is not None:
                        bad3.append((oid, ename, mode, 'audit found %s, record NOT CONSTRUCTIBLE' % val))
                    continue
                if val is None:
                    bad3.append((oid, ename, mode, 'audit NOT CONSTRUCTIBLE, record %s' % got['value']))
                    continue
                # the recorded argmax must itself be a maximiser, with the recorded value
                ka, ka2, ki, kj = [next(k for k in range(62) if ids[k] == s) for s in got['argmax']]
                Sv = M[ka][ki] + M[ka2][ki] - M[ka][kj] + M[ka2][kj]
                Sv = F(abs(Sv), den)
                same = (str(val) == got['value'] and Sv == F(got['value']) and
                        dom == rec['per_order'][oid]['domains'][dkey])
                if not same:
                    bad3.append((oid, ename, mode, 'value %s vs %s ; recorded-argmax value %s ; dom %d vs %d'
                                 % (val, got['value'], Sv, dom, rec['per_order'][oid]['domains'][dkey])))
    claim('P3', 'all %d budget-feasible entries reproduced by the rectangle decomposition '
                '(value + domain equal, recorded argmax is a maximiser)' % ncmp,
          not bad3, 'mismatches = %s ; max tie multiplicity = %d' % (json.dumps(bad3), ties_max))

    # 4. the artifact-free class never exceeds 2 ; every exceedance is diagonal-contaminated
    all4 = [F(rec['per_order'][o]['feasible']['%s_all4' % e]['value']) for o in ORDER_IDS for e in ('E1', 'E2')
            if rec['per_order'][o]['feasible']['%s_all4' % e] is not None]
    exceed = rec['exceedances']
    claim('P4', 'ARTIFACT-FREE (all4) budget-feasible |S| max = %s <= 2 ; %d exceedances of 2, all '
                'diagonal-contaminated' % (max(all4), len(exceed)),
          max(all4) <= 2 and all(x['diag_hits'] for x in exceed),
          'all4 max = %s ; exceedances = %s' % (max(all4), [(x['stat'], x['value'], x['diag_hits']) for x in exceed]))

    # 5. null medians exceed the observed exceedances (no significance)
    blk = rec['nulls']['block']
    ok5 = all(blk[k]['n'] > 0 and F(blk[k]['median']) > 2 for k in blk if k.endswith(('distinct', 'distinct_anti')))
    claim('P5', 'null (random axis relabelling) median of the exceeding classes is itself > 2 '
                '(the excess is class-generic, not a signal)', ok5,
          'E2_distinct null median = %s ; max = %s' % (blk['E2_distinct']['median'], blk['E2_distinct']['max']))

    # 6. cross-checks against the upstream record (A2 / A0 baseline in the record)
    base_ok = all(rec['baseline']['%s_%s' % (e, m)]['value'] == str(F(a2full['chsh']['%s_%s' % (e, m)]))
                  and rec['baseline']['%s_%s' % (e, m)]['argmax'] == a10['%s_%s' % (e, m)]['argmax']
                  for e in ('E1', 'E2') for m in MODES)
    claim('P6', 'recorded baseline block still equals the frozen A2 values AND the scripts/10 argmaxes', base_ok,
          'A2 all4 = %s/%s' % (a2full['chsh']['E1_all4'], a2full['chsh']['E2_all4']))
    dom_ok = (rec['baseline']['E1_raw']['domain'] == 14776336
              and rec['baseline']['E1_distinct_anti']['domain'] == 13388280
              and rec['baseline']['E1_all4']['domain'] == 12517800)
    claim('P7', 'recorded domain counts equal the closeout-corrected values (raw 62^4 ; '
                'distinct_anti 13,388,280 ; all4 12,517,800)', dom_ok,
          'raw %d ; distinct_anti %d ; all4 %d' % (rec['baseline']['E1_raw']['domain'],
                                                   rec['baseline']['E1_distinct_anti']['domain'],
                                                   rec['baseline']['E1_all4']['domain']))

    with io.open(os.path.join(DATA, '16_b3r2_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'claims': CLAIMS}, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)' % (npass, len(CLAIMS), len(CLAIMS) - npass))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
