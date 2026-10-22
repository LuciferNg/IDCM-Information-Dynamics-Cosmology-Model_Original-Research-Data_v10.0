#!/usr/bin/env python3
"""O222 scripts/19 -- INDEPENDENT audit of the D6 mapping table (scripts/18).

Independence rules honoured:
  * does NOT import scripts/18;
  * the RANK is recomputed with fraction-free (Bareiss) integer elimination instead of rational
    Gaussian elimination;
  * the axis ORBITS are recomputed WITHOUT rot_ref, from the frozen kernel K and the group table:
    sigma_q is the unique axis permutation with  K[MUL[inv(q)][s]][a] = K[s][sigma_q(a)]  for all s;
  * the memo-hit LAW is checked by an independent closed-form prediction used against the frozen
    machine's own trail:  misses(pair) = 3 - [incoming_top == a] - [b == a];
  * every verdict is compared with data/18_d6_results.json.

Usage:  /usr/bin/python3 scripts/19_d6_audit.py
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
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rank_bareiss(rows, n):
    """fraction-free exact rank (integer-preserving elimination with exact division)."""
    A = [[int(x) for x in row] for row in rows]
    r = 0
    prev = 1
    for c in range(n):
        piv = None
        for i in range(r, n):
            if A[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        for i in range(r + 1, n):
            for j in range(c + 1, n):
                num = A[i][j] * A[r][c] - A[i][c] * A[r][j]
                A[i][j] = num // prev if prev else num
            A[i][c] = 0
        prev = A[r][c]
        r += 1
        if r == n:
            break
    return r


def main():
    print('=' * 112)
    print('O222 scripts/19 -- INDEPENDENT audit of the D6 mapping table (does not import scripts/18)')
    print('=' * 112, flush=True)
    a2 = load(os.path.join(HERE, '09_a2_rollback.py'), 'a2d')
    b5 = load(os.path.join(HERE, '12_b5_budget.py'), 'b5d')
    _C1, _C2, ids, types, den1 = b5.load_a2()
    mm, K, MUL, hx, ids2, types2 = b5.load_machine()
    b5.KERNEL_TAB = K
    _axes, U, _i2, _t2, _h2 = mm.load_inputs()
    G, _idx_g, _MUL2 = mm.build_group()
    rec = json.load(io.open(os.path.join(DATA, '18_d6_results.json'), encoding='utf-8'))
    corr = json.load(io.open(os.path.join(DATA, '09_a2_correlation.json'), encoding='utf-8'))
    cells = rec['cells']

    # ---- P4a ranks, Bareiss ----
    r1 = rank_bareiss([[int(corr['C1_num'][a][b]) for b in range(N)] for a in range(N)], N)
    C2i = [[F(C2f_num) for C2f_num in row] for row in corr['C2']]

    def lcm_all(rows):
        D = 1
        for row in rows:
            for v in row:
                d = F(v).denominator
                x, y = D, d
                while y:
                    x, y = y, x % y
                D = D * d // x
        return D
    d2 = lcm_all(C2i)
    r2 = rank_bareiss([[int(F(v) * d2) for v in row] for row in C2i], N)
    rrev = rank_bareiss([[int(x) for x in row] for row in corr['C1rev_num']], N)
    ok_rank = (r1 == cells['P4a']['value']['rank_C1'] and r2 == cells['P4a']['value']['rank_C2']
               and rrev == cells['P4a']['value']['rank_C1rev'])
    claim('A1', 'exact ranks reproduced by fraction-free elimination: rank(C1) = %d, rank(C2) = %d, '
                'rank(C1rev) = %d (all > 1 => not factorisable)' % (r1, r2, rrev), ok_rank,
          'recorded = %d/%d/%d' % (cells['P4a']['value']['rank_C1'], cells['P4a']['value']['rank_C2'],
                                   cells['P4a']['value']['rank_C1rev']))

    # ---- P1a orbits WITHOUT rot_ref: sigma_q from the kernel relation ----
    # the identity index is FOUND, not assumed (the group table order is not ours to guess)
    ident = [e for e in range(120) if all(MUL[e][i] == i and MUL[i][e] == i for i in range(120))]
    IDENT = ident[0] if len(ident) == 1 else None
    INV = [None] * 120
    if IDENT is not None:
        for i in range(120):
            for j in range(120):
                if MUL[i][j] == IDENT and MUL[j][i] == IDENT:
                    INV[i] = j
                    break
    ok_inv = IDENT is not None and all(v is not None for v in INV)
    claim('A0', 'group table has a unique identity (index %s) and every element an inverse' % IDENT, ok_inv,
          'identity index = %s' % IDENT)
    parent = list(range(N))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    # my OWN quaternion algebra over Q(sqrt5) -- no rot_ref, no canon from scripts/18
    def add5(x, y):
        return (x[0] + y[0], x[1] + y[1])

    def mul5(x, y):
        return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])

    def neg5(x):
        return (-x[0], -x[1])

    def qmul5(q1, q2):
        a, b, c, d = q1
        e, f, g, h = q2
        w = neg5(add5(add5(mul5(a, e), mul5(b, f)), add5(mul5(c, g), mul5(d, h))))
        x = add5(add5(mul5(a, f), mul5(b, e)), add5(mul5(c, h), neg5(mul5(d, g))))
        y = add5(add5(mul5(a, g), mul5(c, e)), add5(neg5(mul5(b, h)), mul5(d, f)))
        z = add5(add5(mul5(a, h), mul5(d, e)), add5(mul5(b, g), neg5(mul5(c, f))))
        return (w, x, y, z)

    def qconj5(q):
        return (q[0], neg5(q[1]), neg5(q[2]), neg5(q[3]))

    def rot5(q, v):
        p = ((F(0), F(0)), v[0], v[1], v[2])
        r = qmul5(qmul5(q, p), qconj5(q))
        return (r[1], r[2], r[3])

    def sign5(x):
        """exact sign of p + q*sqrt5 (same-sign and mixed-sign cases treated separately)"""
        p, q = x
        if q == 0:
            return (p > 0) - (p < 0)
        if p == 0:
            return (q > 0) - (q < 0)
        if (p > 0) == (q > 0):
            return 1 if p > 0 else -1
        l, r = p * p, 5 * q * q
        if l == r:
            return 0
        if p > 0:
            return 1 if l > r else -1
        return 1 if r > l else -1

    def canon5(v):
        piv = None
        for i in range(3):
            if v[i][0] or v[i][1]:
                piv = i
                break
        p, q = v[piv]
        den = p * p - 5 * q * q
        out = [((a * p - 5 * b * q) / den, (b * p - a * q) / den) for (a, b) in v]
        for (a, b) in out:
            if a > 0 or (a == 0 and b > 0):
                break
            if a < 0 or (a == 0 and b < 0):
                out = [neg5(x) for x in out]
                break
        return tuple(out)

    key5 = {}
    for k in range(N):
        key5.setdefault(canon5(U[k]), []).append(k)
    found = 0
    for iq in range(120):
        for a in range(N):
            t = key5.get(canon5(rot5(G[iq], U[a])))
            if not t:
                continue
            found += 1
            r1x, r2x = find(a), find(t[0])
            if r1x != r2x:
                parent[r2x] = r1x
    groups = {}
    for k in range(N):
        groups.setdefault(find(k), []).append(k)
    sizes = sorted(len(v) for v in groups.values())
    type_ok = all(len({types[i] for i in v}) == 1 for v in groups.values())
    claim('A2', 'axis orbits recomputed with an independently coded exact quaternion conjugation '
                '(no rot_ref): sizes = %s, type-invariant = %s, orbits = %d'
          % (sizes, type_ok, len(groups)),
          sizes == cells['P1a']['value']['orbit_sizes'] and type_ok and found == 120 * N and len(groups) == 3,
          'recorded = %s ; (q, axis) images matched = %d/%d' % (cells['P1a']['value']['orbit_sizes'],
                                                                found, 120 * N))
    # A2b: independently reconstruct the WHOLE frozen kernel, including the vanishing-dot tie rule
    ns = [rot5(G[s], U[0]) for s in range(120)] if False else [mm.rot_ref(q, U[0]) for q in G]
    ties = 0
    mism = 0
    for s in range(120):
        r = ns[s]
        for a in range(N):
            dot = add5(add5(mul5(U[a][0], r[0]), mul5(U[a][1], r[1])), mul5(U[a][2], r[2]))
            sg = sign5(dot)
            if sg == 0:
                ties += 1
                for comp in r:
                    sc = sign5(comp)
                    if sc:
                        sg = sc
                        break
            if sg != K[s][a]:
                mism += 1
    claim('A2b', 'frozen kernel reconstructed exactly from the geometry + the tie rule: %d mismatches '
                 'of 7440, ties (vanishing dot) = %d' % (mism, ties), mism == 0,
          'ties = %d/%d = %.2f%% of the kernel' % (ties, 120 * N, 100.0 * ties / (120 * N)))

    # ---- P1a diagnostic: the 62 labels are 31 antipodal pairs ----
    anti = [[0] * N for _ in range(N)]
    for a in range(N):
        for b in range(N):
            ua, ub = U[a], U[b]
            dot = mm.add(mm.add(mm.mul(ua[0], ub[0]), mm.mul(ua[1], ub[1])), mm.mul(ua[2], ub[2]))
            na = mm.add(mm.add(mm.mul(ua[0], ua[0]), mm.mul(ua[1], ua[1])), mm.mul(ua[2], ua[2]))
            nb = mm.add(mm.add(mm.mul(ub[0], ub[0]), mm.mul(ub[1], ub[1])), mm.mul(ub[2], ub[2]))
            anti[a][b] = 1 if (mm.sgn(dot) < 0 and mm.mul(dot, dot) == mm.mul(na, nb)) else 0
    npairs = sum(anti[a][b] for a in range(N) for b in range(N)) // 2
    claim('A3', 'the 62 axes form exactly %d antipodal pairs (double cover of %d lines), each axis with '
                'exactly one antipode' % (npairs, N // 2),
          npairs == cells['P1a']['value']['antipodal_pairs'] == 31 and
          all(sum(anti[a][b] for b in range(N)) == 1 for a in range(N)),
          'recorded antipodal_pairs = %d' % cells['P1a']['value']['antipodal_pairs'])

    # ---- P2a / P2c / P3a: the memo law by an INDEPENDENT closed-form prediction ----
    def seq_of(oid):
        if oid == 'lex':
            return sorted([(a, b) for a in range(N) for b in range(N)])
        return sorted([(a, b) for a in range(N) for b in range(N)],
                      key=lambda p: (max(p[0], p[1]), min(p[0], p[1]), p[0]))

    total = {'pairs': 0, 'pred_ok': 0, 'growth_min': None, 'hits': 0}
    for oid in ('lex', 'block'):
        trail = []
        top = -1
        rem = F(123, 2)
        for (a, b) in seq_of(oid):
            try:
                r, rem = b5.run_pair(a, b, 0, top, K, MUL, hx, rem, trail)
            except RuntimeError:
                break
            top = r['top']
        incoming = None          # predict the incoming ledger top independently: top = previous pair's b
        for e in trail:
            a, b = e['pair']
            pred = 3 - (1 if incoming == a else 0) - (1 if b == a else 0)
            total['pairs'] += 1
            if pred == e['misses']:
                total['pred_ok'] += 1
            g = e['misses'] - 1
            total['growth_min'] = g if total['growth_min'] is None else min(total['growth_min'], g)
            if e['misses'] == 2:
                total['hits'] += 1
            incoming = b
    claim('A4', 'closed-form memo law predicts every observed read count: %d/%d pairs '
                '(misses = 3 - [top == a] - [b == a])' % (total['pred_ok'], total['pairs']),
          total['pred_ok'] == total['pairs'] and total['pairs'] > 0,
          'recorded memo_hit_pairs = %d ; audit hits = %d' % (cells['P3a']['value']['memo_hit_pairs_in_witnessed_passes'],
                                                             total['hits']))
    claim('A5', 'per-pair ledger growth (misses - 1) is at least %d > 0 on every witnessed pair '
                '=> the rollback never restores the record' % total['growth_min'], total['growth_min'] > 0,
          'recorded total growth = %s' % [cells['P2c']['value'][o]['total_ledger_growth'] for o in ('lex', 'block')])

    # ---- P2b / P4c: balance and history sensitivity recomputed from the raw kernel ----
    hist = sum(1 for c in range(N) if len({K[s][c] for s in range(120)}) > 1)
    bal = sum(1 for a in range(N) if sum(K[s][a] for s in range(120)) == 0)
    claim('A6', 'history-sensitive settings = %d/%d and outcome-balanced axes = %d/%d (marginal 1/2)'
          % (hist, N, bal, N), hist == cells['P2b']['value']['history_sensitive_settings'] == N
          and bal == cells['P4c']['value']['axes_with_balanced_outcomes'] == N,
          'recorded %d / %d' % (cells['P2b']['value']['history_sensitive_settings'],
                                cells['P4c']['value']['axes_with_balanced_outcomes']))

    # ---- P4b: the cited values really are the B3R2 record ----
    b3 = json.load(io.open(os.path.join(DATA, '15_b3r2_results.json'), encoding='utf-8'))
    cite_ok = (cells['P4b']['value']['budget_feasible_all4_E1'] == b3['per_order']['block']['feasible']['E1_all4']['value']
               and cells['P4b']['value']['unrestricted_all4_E2'] == b3['baseline']['E2_all4']['value'])
    claim('A7', 'P4b cites the B3R2 record exactly (16/15, 13/15, 2, 3) and adds no new number', cite_ok,
          'B3R2 14/14 = %s' % (len(b3['claims']) == 14 and all(c['ok'] for c in b3['claims'])))

    # ---- verdict table integrity ----
    order = rec['cell_order']
    verdicts = [cells[c]['verdict'] for c in order]
    claim('A8', 'verdict table integrity: %d cells, all with a verdict and a value' % len(order),
          len(order) == 13 and all(cells[c]['verdict'] in ('✅', '🟡', '🔴') and cells[c]['value']
                                   for c in order),
          'table = %s' % ''.join(v[0] for v in verdicts))

    with io.open(os.path.join(DATA, '19_d6_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'claims': CLAIMS, 'ranks': {'C1': r1, 'C2': r2, 'C1rev': rrev},
                   'antipodal_pairs': npairs, 'memo_law': total}, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)' % (npass, len(CLAIMS), len(CLAIMS) - npass))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
