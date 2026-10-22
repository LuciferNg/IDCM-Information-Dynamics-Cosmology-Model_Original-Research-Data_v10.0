#!/usr/bin/env python3
"""O226 scripts/07 -- INDEPENDENT audit.  Contract docs/01_o226_contract.md §6 item 1.

This script re-derives the headline numbers of scripts/02-06 from the frozen inputs with
INDEPENDENT code: it does not import, exec or copy any of scripts/02-06 (contract C5 spirit).
It is allowed to read the frozen upstream JSON (F1/F2/F3) and this round's data/*.json, but
every number below is recomputed, then compared.

Two deliberate methodological differences from the engines:
  * the budget is recomputed in INTEGER units of theta (B = 88, c = 2, theta = 1) -- the
    Fraction form is only used to display;
  * hits are counted by comparing the context with an explicit ledger stack (no reuse of the
    machine's closed form).
Exact arithmetic only (Fraction / int); no float, math, random, numpy.
"""
import hashlib
import io
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UP = os.path.dirname(os.path.dirname(ROOT))
O222 = os.path.join(os.path.dirname(ROOT), 'o222_qm_evaluation_semantics')
DATA = os.path.join(ROOT, 'data')
N = 62
THETA_UNITS = F(123, 176)          # 1 theta = E_min
B_UNITS = 88                       # B / theta  = (123/2)/(123/176) = 88
C_UNITS = 2                        # c / theta  = (123/88)/(123/176) = 2
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name,
                              ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


# ---------------- independent exact Q(sqrt5) and quaternion algebra
def q5_add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def q5_mul(a, b):
    # (x + y r)(u + v r) = xu + 5yv + (xv + yu) r
    return (a[0] * b[0] + 5 * a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def q5_sign(a):
    x, y = a
    if y == 0:
        return 1 if x > 0 else (-1 if x < 0 else 0)
    if x == 0:
        return 1 if y > 0 else -1
    if (x > 0) != (y > 0):
        # opposite signs: sign of x + y*sqrt5
        return (1 if x > 0 else -1) * (1 if x * x > 5 * y * y else -1)
    return 1 if x > 0 else -1


Z, O, H = (F(0), F(0)), (F(1), F(0)), (F(1, 2), F(1, 2))
PSI = (F(-1, 2), F(1, 2))


def h_mul(p, q):
    """Hamilton product written via the (1,i,j,k) = (a,b,c,d) basis, independent form."""
    a, b, c, d = p
    e, f, g, h = q
    return (q5_add(q5_add(q5_mul(a, e), (-1 * q5_mul(b, f)[0], -1 * q5_mul(b, f)[1])),
                   q5_add((-1 * q5_mul(c, g)[0], -1 * q5_mul(c, g)[1]),
                          (-1 * q5_mul(d, h)[0], -1 * q5_mul(d, h)[1]))),
            q5_add(q5_add(q5_mul(a, f), q5_mul(b, e)),
                   q5_add(q5_mul(c, h), (-1 * q5_mul(d, g)[0], -1 * q5_mul(d, g)[1]))),
            q5_add(q5_add(q5_mul(a, g), (-1 * q5_mul(b, h)[0], -1 * q5_mul(b, h)[1])),
                   q5_add(q5_mul(c, e), q5_mul(d, f))),
            q5_add(q5_add(q5_mul(a, h), q5_mul(b, g)),
                   q5_add((-1 * q5_mul(c, f)[0], -1 * q5_mul(c, f)[1]), q5_mul(d, e))))


def key(q):
    return tuple((c[0], c[1]) for c in q)


def build_group():
    units = set()
    for k in range(4):
        for sgn in (1, -1):
            e = [Z, Z, Z, Z]
            e[k] = (O[0] * sgn, O[1] * sgn)
            units.add(tuple(e))
    for m in range(16):
        sg = [(-1 if (m >> i) & 1 else 1) for i in range(4)]
        if sg.count(-1) % 2 == 0:
            units.add(tuple((F(v, 2), F(0)) for v in sg))
    gen = list(units)
    # the icosahedral generator PHI/2 + i/2 + PSI/2 (note the extra 1/2 on every component:
    # without it the element leaves 2I and the BFS closure never terminates)
    q0 = ((F(1, 4), F(1, 4)), (F(1, 2), F(0)), (F(-1, 4), F(1, 4)), (Z[0], Z[1]))
    ident = (O, Z, Z, Z)
    seen = {key(ident): ident}
    stack = [ident]
    while stack:
        p = stack.pop()
        for g in gen + [q0]:
            r = h_mul(p, g)
            k = key(r)
            if k not in seen:
                seen[k] = r
                stack.append(r)
        if len(seen) > 500:            # hard guard: a non-closing BFS must fail loudly, not hang
            print('!! BFS did not close: %d elements -- aborting the closure' % len(seen), flush=True)
            break
    G = sorted(seen.values(), key=lambda q: tuple((c[0].numerator, c[0].denominator,
                                                   c[1].numerator, c[1].denominator) for c in q))
    idx = {key(q): i for i, q in enumerate(G)}
    return G, idx


def main():
    print('=' * 104)
    print('O226 scripts/07 -- INDEPENDENT audit (recomputes 02-06 from the frozen inputs)')
    print('=' * 104, flush=True)
    ref = json.load(io.open(os.path.join(DATA, '02_ledger_machine.json'), encoding='utf-8'))
    S = json.load(io.open(os.path.join(O222, 'data', '04_b2_settings.json'), encoding='utf-8'))
    Htab = json.load(io.open(os.path.join(O222, 'data', '08_a2_h_table.json'), encoding='utf-8'))['h_table']
    corr = json.load(io.open(os.path.join(O222, 'data', '09_a2_correlation.json'), encoding='utf-8'))
    axes = S['axes']
    U = [tuple((F(c[0]), F(c[1])) for c in ax['vec']) for ax in axes]
    types = [ax['type'] for ax in axes]
    hv = [tuple((F(c[0]), F(c[1])) for c in row['h']) for row in Htab]

    G, idx = build_group()
    claim('A1', '|2I| = 120 rebuilt independently (Hurwitz units, BFS closure)',
          len(G) == 120, 'order = %d' % len(G))
    tc = {}
    for t in types:
        tc[t] = tc.get(t, 0) + 1
    claim('A2', 'F1 axes: 62 with type counts 12 vertex / 20 face / 30 edge',
          len(U) == 62 and sorted(tc.values()) == [12, 20, 30], 'types = %s' % tc)

    hk = [key(h) for h in hv]
    hset = set(hk)
    inv_closed = True
    for h in hv:
        cj = (h[0], (-h[1][0], -h[1][1]), (-h[2][0], -h[2][1]), (-h[3][0], -h[3][1]))
        if key(cj) not in hset:
            inv_closed = False
    claim('A3', 'F2 h table: 62 distinct entries, inverse-closed, all inside 2I',
          len(hset) == 62 and inv_closed and all(k in idx for k in hk),
          'distinct = %d ; inverse-closed = %s ; all in 2I = %s'
          % (len(hset), inv_closed, all(k in idx for k in hk)))

    # ---- independent rebuild of the read kernel (rotated reference axis against each axis)
    def rot3(q, v):
        # conjugation q (0,v) q^-1 for unit q: use the fused rotate-by-quaternion formula
        a, b, c, d = q
        conj = (a, (-b[0], -b[1]), (-c[0], -c[1]), (-d[0], -d[1]))
        r = h_mul(h_mul(q, (Z, v[0], v[1], v[2])), conj)
        return (r[1], r[2], r[3])

    ref_axis = U[0]
    K = []
    for q in G:
        r = rot3(q, ref_axis)
        row = []
        for u in U:
            dot = q5_add(q5_add(q5_mul(u[0], r[0]), q5_mul(u[1], r[1])), q5_mul(u[2], r[2]))
            s = q5_sign(dot)
            if s == 0:
                for comp in r:
                    sc = q5_sign(comp)
                    if sc:
                        s = sc
                        break
            row.append(s)
        K.append(row)
    hx = [idx[key(h)] for h in hv]
    MULT = [[idx[key(h_mul(a, b))] for b in G] for a in G]

    # fidelity: the rebuilt kernel must reproduce the frozen upstream integer correlation table
    # (F3: data/09_a2_correlation.json, denominator 120, numerators C1_num) for all 62 x 62 pairs
    # the correct fidelity object is the correlation of the PAIR OUTPUTS under the frozen read law:
    #   C1[a][b] = sum_s x_a(s) x_b(s.h(a)), with x_b = x_a when a == b (the second read is a memo hit)
    C1n = corr['C1_num']
    mm = 0
    for a in range(N):
        ha = hx[a]
        for b in range(N):
            acc = 0
            for s in range(120):
                xa = K[s][a]
                xb = xa if a == b else K[MULT[s][ha]][b]
                acc += xa * xb
            if acc != C1n[a][b]:
                mm += 1
    claim('A4', 'the independently rebuilt kernel reproduces the FROZEN upstream correlation table '
                '(F3 C1_num, denominator 120) under the read law: C1[a][b] = sum_s x_a(s).x_b(s.h(a)) '
                'with the a == b memo hit -> all 3844 pairs',
          mm == 0, 'mismatches = %d / 3844' % mm)

    # ---- independent full-pass accounting with an explicit ledger (hits by stack compare)
    accts = set()
    for s0 in range(120):
        top = -1
        reads = hits = pops = 0
        for a in range(N):
            for b in range(N):
                L = [[top, 0, s0]] if top >= 0 else []
                s = s0
                for ctx in (a, b):
                    if L and L[-1][0] == ctx:
                        hits += 1
                    else:
                        L.append([ctx, K[s][ctx], s])
                        s = MULT[s][hx[ctx]]
                        reads += 1
                e = L.pop()
                s = e[2]
                pops += 1
                ctx = b
                if L and L[-1][0] == ctx:
                    hits += 1
                else:
                    L.append([ctx, K[s][ctx], s])
                    s = MULT[s][hx[ctx]]
                    reads += 1
                top = L[-1][0] if L else -1
        accts.add((3 * N * N, reads, hits, pops))
    acc = sorted(accts)[0]
    claim('A5', 'independent full-pass account over all 120 states, as (read-ops, CHARGED reads = misses, '
                'hits, pops) = (3N^2, 3N^2 - 2N, 2N, N^2) = (11532, 11408, 124, 3844)',
          len(accts) == 1 and acc == (3 * N * N, 3 * N * N - 2 * N, 2 * N, N * N),
          'account = %s ; distinct accounts = %d ; engine read-ops %d misses %d hits %d pops %d'
          % (acc, len(accts), ref['pass_account']['read_ops'], ref['pass_account']['misses'],
             ref['pass_account']['hits'], ref['pass_account']['pops']))

    # ---- independent budget law in INTEGER theta units
    def mstar(B_u, c_u):
        return (B_u - 1) // c_u + 1

    rows = []
    for B_u, c_u in ((B_UNITS, C_UNITS), (176, 2), (44, 2), (B_UNITS, 3)):
        m = mstar(B_u, c_u)
        rows.append((B_u, c_u, m, m * c_u, m * c_u == B_u, m * c_u > B_u))
    claim('A6', 'budget law recomputed in integer theta units: m* = floor((B-1)/c) + 1 ; the four cases '
                'are (88,2)->44 exact, (176,2)->88 exact, (44,2)->22 exact, (88,3)->30 with Sigma = 90 '
                'theta > 88 theta (overshoot)',
          rows[0][2] == 44 and rows[0][4] and rows[1][2] == 88 and rows[1][4] and rows[2][2] == 22 and
          rows[2][4] and rows[3][2] == 30 and rows[3][5] and rows[3][3] == 90,
          ' | '.join('B=%d c=%d -> m*=%d Sigma=%d theta exact=%s' % (r[0], r[1], r[2], r[3], r[4])
                     for r in rows))
    claim('A7', 'the three pre-registered blind values are confirmed in the integer form: B\'=123 -> 88 '
                'reads / Sigma = 176 theta = 123 ; B\'\'=123/4 -> 22 / 44 theta = 123/4 ; c\'\'\'=3 theta -> '
                '30 / 90 theta = 5535/88 = 11070/176',
          THETA_UNITS * 176 == F(123) and THETA_UNITS * 44 == F(123, 4) and
          THETA_UNITS * 90 == F(5535, 88) and F(5535, 88) == F(11070, 176),
          '176 theta = %s ; 44 theta = %s ; 90 theta = %s' % (THETA_UNITS * 176, THETA_UNITS * 44,
                                                              THETA_UNITS * 90))

    # ---- independent kernel-class / staleness recomputation
    rws = [tuple(r) for r in K]
    cls = {}
    for s in range(120):
        cls.setdefault(rws[s], []).append(s)
    reps = [sorted(v)[0] for v in cls.values()]
    bal = sorted({sum(1 for s in range(120) if K[s][c] == 1) for c in range(N)})
    Dm = sorted({sum(1 for x in range(N) if K[reps[i]][x] != K[reps[j]][x])
                 for i in range(len(reps)) for j in range(len(reps))})
    ref6 = json.load(io.open(os.path.join(DATA, '06_staleness.json'), encoding='utf-8'))

    def order_of(i):
        p, o = G[i], 1
        while key(p) != key(G[idx[key((O, Z, Z, Z))]]):
            p = h_mul(p, G[i])
            o += 1
        return o
    stab = sorted(order_of(g) for g in range(120) if rws[MULT[reps[0]][g]] == rws[reps[0]])
    claim('A8', 'kernel structure recomputed independently: 12 classes of 10, per-setting balance 60/60, '
                'class-pair Hamming value set {0,22,24,38,40,62}, stabiliser orders {1,2,5x4,10x4}',
          len(cls) == 12 and sorted({len(v) for v in cls.values()}) == [10] and bal == [60] and
          Dm == [0, 22, 24, 38, 40, 62] and stab == [1, 2, 5, 5, 5, 5, 10, 10, 10, 10] and
          Dm == sorted(ref6['kernel_structure']['metric_value_set']),
          'classes = %d ; balance = %s ; value set = %s ; stabiliser = %s' % (len(cls), bal, Dm, stab))

    # ---- independent pop-redundancy check (4-op vs 2-op pair)
    bad = 0
    for s0 in range(120):
        top = -1
        for a in range(N):
            for b in range(N):
                # 2-op
                L1 = [[top, 0, s0]] if top >= 0 else []
                s1 = s0
                out1 = []
                for ctx in (a, b):
                    if L1 and L1[-1][0] == ctx:
                        out1.append(L1[-1][1])
                    else:
                        out1.append(K[s1][ctx])
                        L1.append([ctx, K[s1][ctx], s1])
                        s1 = MULT[s1][hx[ctx]]
                top1 = L1[-1][0] if L1 else -1
                # 4-op (pop then re-read)
                L2 = [[top, 0, s0]] if top >= 0 else []
                s2 = s0
                for ctx in (a, b):
                    if L2 and L2[-1][0] == ctx:
                        pass
                    else:
                        L2.append([ctx, K[s2][ctx], s2])
                        s2 = MULT[s2][hx[ctx]]
                e = L2.pop()
                s2 = e[2]
                # the reconciliation read of b (memo hit if the popped stack top is b)
                if L2 and L2[-1][0] == b:
                    v2 = L2[-1][1]
                else:
                    v2 = K[s2][b]
                    L2.append([b, v2, s2])
                    s2 = MULT[s2][hx[b]]
                top2 = L2[-1][0] if L2 else -1
                if (s1, top1) != (s2, top2) or v2 != out1[1]:
                    bad += 1
                top = top1
    claim('A9', 'pop redundancy rechecked independently: (s_final, ledger top, reconciled value) of the '
                '4-operation pair equals the 2-operation pair for all 3844 x 120 cases',
          bad == 0, 'mismatches = %d / %d' % (bad, 3844 * 120))

    # ---- the engine's own recorded account (cross-reference, not a re-derivation)
    pa = ref['pass_account']
    bp = ref['budget_pass']
    claim('A10', 'the engine JSON (scripts/02) records the same account and budget prefix as the audit: '
                 'read-ops 11532 / hits 124 / misses 11408 / pops 3844, prefix 15 pairs, terminal (0,15), '
                 'Sigma = 123/2, 44 charged reads',
          (pa['read_ops'], pa['hits'], pa['misses'], pa['pops']) == (11532, 124, 11408, 3844) and
          bp['feasible_pairs'] == 15 and bp['terminal_pair'] == [0, 15] and bp['sigma'] == '123/2' and
          bp['reads_that_exhaust'] == 44,
          'engine account = %s ; prefix = %s' % (pa, bp))

    digest = {}
    for nm in sorted(os.listdir(DATA)):
        if nm.endswith('.json'):
            with io.open(os.path.join(DATA, nm), 'rb') as fh:
                digest[nm] = hashlib.sha256(fh.read()).hexdigest()[:16]
    print('data/ digests:', json.dumps(digest, ensure_ascii=False))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 104)
    print('RESULT: %d/%d PASS (independent audit)' % (npass, len(CLAIMS)))
    print('=' * 104)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
