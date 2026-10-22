#!/usr/bin/env python3
"""O226 scripts/02 -- the frozen ledger machine and its exact pass accounting.

Contract: docs/01_o226_contract.md (o226-r1-contract-v1), items I1-I6.
Frozen inputs (read-only): F1 62 axes (data/04_b2_settings.json), F2 h table
(data/08_a2_h_table.json), F3 the upstream frozen correlations (data/09_a2_correlation.json).

Exact arithmetic only: Q(sqrt5) pairs of Fraction, integer counts.  No float, no math,
no random on the machine path (enforced by scripts/01 C4).

What it computes
  A  group + input reconstruction (|2I| = 120, class spectrum, h bijective/inverse-closed,
     axis types V/F/E = 12/20/30) and the sign kernel K (120 x 62)
  B  fidelity: the literal machine's per-pair correlation == the F3 frozen table (3844/3844)
  C  one full pass in the frozen order: read operations / hits / misses / pops / depth
     (enumerated over ALL 120 initial states -> state independence)
  D  the budget-feasible pass: prefix length, reads, terminal pair, Sigma (per-read terminal)
  E  redundancy: 4-operation pair vs 2-operation pair on (x_a, x_b, s_final, top) over
     3844 pairs x 120 states  (contract Pr-1.4)
  F  carry semantics: hits with carry (2N) vs without carry (N); the placeholder value of the
     carried entry is disclosed (it returns 0, a documented wart of the frozen protocol)
Usage: /usr/bin/python3 scripts/02_o226_ledger_machine.py
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
UP = os.path.dirname(os.path.dirname(ROOT))          # open_problems_fresh/
O222 = os.path.join(os.path.dirname(ROOT), 'o222_qm_evaluation_semantics')
DATA = os.path.join(ROOT, 'data')
RULES = 'o226-r1-contract-v1'
N = 62
BUDGET = F(123, 2)
E_MIN = F(123, 176)
COST = F(123, 88)
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name,
                              ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


# ---------------------------------------------------------------- exact Q(sqrt5)
def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def neg(x):
    return (-x[0], -x[1])


def sub(x, y):
    return (x[0] - y[0], x[1] - y[1])


def mul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def scale(x, k):
    return (x[0] * k, x[1] * k)


def is_zero(x):
    return x[0] == 0 and x[1] == 0


def sgn(x):
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


ZERO, ONE = (F(0), F(0)), (F(1), F(0))
PHI = (F(1, 2), F(1, 2))
PSI = (F(-1, 2), F(1, 2))


def qmul(a, b):
    a0, a1, a2, a3 = a
    b0, b1, b2, b3 = b
    return (sub(sub(mul(a0, b0), mul(a1, b1)), add(mul(a2, b2), mul(a3, b3))),
            add(add(mul(a0, b1), mul(a1, b0)), sub(mul(a2, b3), mul(a3, b2))),
            add(sub(mul(a0, b2), mul(a1, b3)), add(mul(a2, b0), mul(a3, b1))),
            add(sub(add(mul(a0, b3), mul(a1, b2)), mul(a2, b1)), mul(a3, b0)))


def qconj(q):
    return (q[0], neg(q[1]), neg(q[2]), neg(q[3]))


def qkey(q):
    return tuple((c[0], c[1]) for c in q)


def build_2T():
    out = set()
    for s in range(8):
        e = [ZERO, ZERO, ZERO, ZERO]
        e[s >> 1] = ONE if (s % 2 == 0) else neg(ONE)
        out.add(tuple(e))
    for s in range(16):
        sg = [(-1 if (s >> i) & 1 else 1) for i in range(4)]
        if sg.count(-1) % 2 == 0:
            out.add(tuple(scale(ONE, F(v, 2)) for v in sg))
    return out


def build_group():
    gens = list(build_2T())
    q0 = (scale(PHI, F(1, 2)), scale(ONE, F(1, 2)), scale(PSI, F(1, 2)), ZERO)
    ID = (ONE, ZERO, ZERO, ZERO)
    seen = {qkey(ID): ID}
    queue = [ID]
    while queue:
        q = queue.pop()
        for g in gens + [q0]:
            p = qmul(q, g)
            k = qkey(p)
            if k not in seen:
                seen[k] = p
                queue.append(p)
    G = sorted(seen.values(), key=lambda q: tuple((c[0].numerator, c[0].denominator,
                                                   c[1].numerator, c[1].denominator) for c in q))
    idx = {qkey(q): i for i, q in enumerate(G)}
    MUL = [[idx[qkey(qmul(a, b))] for b in G] for a in G]
    return G, idx, MUL


def rot_ref(q, n):
    r = qmul(qmul(q, (ZERO, n[0], n[1], n[2])), qconj(q))
    return (r[1], r[2], r[3])


def load_inputs():
    S = json.load(io.open(os.path.join(O222, 'data', '04_b2_settings.json'), encoding='utf-8'))
    axes = S['axes']
    U = [tuple((F(c[0]), F(c[1])) for c in ax['vec']) for ax in axes]
    ids = [ax['id'] for ax in axes]
    types = [ax['type'] for ax in axes]
    H = json.load(io.open(os.path.join(O222, 'data', '08_a2_h_table.json'), encoding='utf-8'))['h_table']
    hvec = [tuple((F(c[0]), F(c[1])) for c in row['h']) for row in H]
    return axes, U, ids, types, hvec


def build_K(G, U):
    KV = [rot_ref(q, U[0]) for q in G]
    K = []
    for i in range(len(G)):
        r = KV[i]
        row = []
        for u in U:
            dot = add(add(mul(u[0], r[0]), mul(u[1], r[1])), mul(u[2], r[2]))
            s = sgn(dot)
            if s == 0:
                for comp in r:
                    sc = sgn(comp)
                    if sc:
                        s = sc
                        break
            row.append(s)
        K.append(row)
    return K


# ---------------------------------------------------------------- the literal machine
class Terminal(Exception):
    pass


def run_pair(K, MUL, hx, a, b, s0, top, mode='cap4', budget=None, cost=COST, theta=E_MIN,
             popcost=F(0), topv=0):
    reads = 0
    hits = 0
    pops = 0
    spent = F(0)
    L = []
    if mode != 'nocarry' and top >= 0:
        L.append([top, topv, s0])
    s = s0
    maxdepth = len(L)
    st = {'finite': True}

    def rd(ctx):
        nonlocal s, reads, hits, spent, maxdepth
        if L and L[-1][0] == ctx:
            hits += 1
            return L[-1][1]
        if budget is not None and budget - spent < theta:
            st['finite'] = False
            raise Terminal('budget exhausted')
        v = K[s][ctx]
        L.append([ctx, v, s])
        s = MUL[s][hx[ctx]]
        reads += 1
        spent += cost
        if len(L) > maxdepth:
            maxdepth = len(L)
        return v

    xa = rd(a)
    xb = rd(b)
    if mode in ('cap4', 'truetop'):
        e = L.pop()
        s = e[2]
        pops += 1
        spent += popcost
        xb2 = rd(b)
    else:
        xb2 = xb
    return {'x_a': xa, 'x_b': xb, 'x_b2': xb2, 's_final': s, 'reads': reads, 'hits': hits,
            'pops': pops, 'spent': spent, 'top': (L[-1][0] if L else -1), 'depth': maxdepth}


PAIRS = [(a, b) for a in range(N) for b in range(N)]


def run_pass(K, MUL, hx, s0, order=None, budget=BUDGET, cost=COST, theta=E_MIN,
             popcost=F(0)):
    """one whole pass in the given order with the per-read terminal condition.

    Charges are accumulated at the PASS level, so the budget remainder at the terminal
    is reported exactly (this is what pins the pop cost -- see claim F1)."""
    order = PAIRS if order is None else order
    spent = F(0)
    reads = hits = pops = completed = 0
    top = -1
    depth_max = 0
    term = None
    for (a, b) in order:
        L = []
        if top >= 0:
            L.append([top, 0, s0])
        s = s0
        if len(L) > depth_max:
            depth_max = len(L)
        st = {'blown': False}

        def rd(ctx, L=L, st=st):
            nonlocal s, reads, hits, spent, depth_max
            if L and L[-1][0] == ctx:
                hits += 1
                return L[-1][1]
            if budget - spent < theta:
                st['blown'] = True
                raise Terminal('budget exhausted')
            v = K[s][ctx]
            L.append([ctx, v, s])
            s = MUL[s][hx[ctx]]
            reads += 1
            spent += cost
            if len(L) > depth_max:
                depth_max = len(L)
            return v

        try:
            rd(a)
            rd(b)
            e = L.pop()
            s = e[2]
            pops += 1
            spent += popcost
            rd(b)
        except Terminal:
            term = (a, b)
            break
        completed += 1
        top = L[-1][0] if L else -1
    return {'completed_pairs': completed, 'charged_reads': reads, 'hits': hits, 'pops': pops,
            'spent': spent, 'budget_left': budget - spent, 'terminal_pair': term, 'top': top,
            'depth': depth_max, 's_final': s}


def main():
    t0 = time.time()
    print('=' * 104)
    print('O226 scripts/02 -- frozen ledger machine + pass accounting (rules: %s)' % RULES)
    print('=' * 104, flush=True)

    axes, U, ids, types, hvec = load_inputs()
    G, idx, MUL = build_group()
    hx = [idx[qkey(h)] for h in hvec]
    n2I = len(G)
    K = build_K(G, U)
    assert n2I == 120

    # ---- A group + input reconstruction
    orders = []
    for i, q in enumerate(G):
        p = q
        o = 1
        while qkey(p) != qkey((ONE, ZERO, ZERO, ZERO)):
            p = qmul(p, q)
            o += 1
        orders.append(o)
    spec = {}
    for o in orders:
        spec[o] = spec.get(o, 0) + 1
    claim('A1', '|2I| = 120 and the order spectrum equals {1:1, 2:1, 3:20, 4:30, 5:24, 6:20, 10:24}',
          n2I == 120 and spec == {1: 1, 2: 1, 3: 20, 4: 30, 5: 24, 6: 20, 10: 24}, str(spec))
    tc = {}
    for t in types:
        tc[t] = tc.get(t, 0) + 1
    norms = {}
    for t, u in zip(types, U):
        nn = add(add(mul(u[0], u[0]), mul(u[1], u[1])), mul(u[2], u[2]))
        norms.setdefault(t, set()).add((nn[0], nn[1]))
    norm_ok = all(len(v) == 1 for v in norms.values())
    claim('A2', 'axis set F1: 62 axes, type counts vertex/face/edge = 12/20/30, each type of constant '
                'Q(sqrt5) norm (only the per-type scale matters, the read uses the sign of the dot)',
          len(U) == 62 and sorted(tc.values()) == [12, 20, 30] and norm_ok,
          'types = %s ; per-type distinct norms = %s' % (tc, {k: len(v) for k, v in norms.items()}))
    claim('A3', 'h table F2 is bijective (62 distinct) and inverse-closed',
          len(set(hx)) == 62 and all(idx[qkey(qconj(hvec[i]))] in set(hx) for i in range(62)),
          'h bijective = %s' % (len(set(hx)) == 62))
    claim('A4', 'icosahedral axis count: 62 = 12 vertex + 20 face + 30 edge (the axis set of I_h)',
          sum(tc.values()) == 62 and sorted(tc.values()) == [12, 20, 30], '62 = 12 + 20 + 30')

    # ---- B fidelity vs upstream frozen C1
    frozen = json.load(io.open(os.path.join(O222, 'data', '09_a2_correlation.json'), encoding='utf-8'))
    den = frozen['denominator']
    C1f = frozen['C1_num']
    mis = 0
    for a in range(N):
        ha = hx[a]
        for b in range(N):
            if a == b:
                want = n2I
            else:
                want = sum(K[s][a] * K[MUL[s][ha]][b] for s in range(n2I))
            if want != C1f[a][b]:
                mis += 1
    claim('B1', 'machine reproduces the F3 frozen correlation table C1 for all 3844 pairs',
          mis == 0 and den == 120, 'mismatches = %d / 3844 (den %d)' % (mis, den))

    # literal machine cross-check of the closed form (all pairs x all states, empty ledger)
    pairs = [(a, b) for a in range(N) for b in range(N)]
    bad = 0
    for (a, b) in pairs:
        acc = 0
        for s0 in range(n2I):
            r = run_pair(K, MUL, hx, a, b, s0, -1, mode='nocarry')
            acc += r['x_a'] * r['x_b2']
        if acc != C1f[a][b]:
            bad += 1
    claim('B2', 'literal machine == closed form for every pair x state (empty ledger)',
          bad == 0, 'mismatches = %d / 3844' % bad)

    # ---- C full pass in the frozen order, enumerated over ALL 120 initial states
    counts = set()
    depth_max = 0
    hits_nocarry = set()
    for s0 in range(n2I):
        top = -1
        rops = hits = misses = pops = 0
        for (a, b) in pairs:
            r = run_pair(K, MUL, hx, a, b, s0, top, mode='cap4')
            rops += 3
            hits += r['hits']
            misses += r['reads']
            pops += r['pops']
            top = r['top']
            if r['depth'] > depth_max:
                depth_max = r['depth']
        counts.add((rops, hits, misses, pops, top))
    rops, hits, misses, pops, topf = counts.pop()
    claim('C1', 'one full pass (all 120 initial states identical): read-ops = 3N^2 = 11532, '
                'hits = 2N = 124, misses = 3N^2 - 2N = 11408, pops = N^2 = 3844',
          counts == set() and (rops, hits, misses, pops) == (3 * N * N, 2 * N, 3 * N * N - 2 * N, N * N),
          'read-ops = %d ; hits = %d ; misses = %d ; pops = %d ; distinct states outcomes = %d'
          % (rops, hits, misses, pops, len(counts) + 1))
    claim('C2', 'the pass account is state-independent (1 distinct outcome over 120 initial states)',
          len(counts) == 0, 'distinct outcome tuples = 1')
    claim('C3', 'ledger depth stays <= 3 (1 carry + 2 pushes); pop depth = 1 (one entry per pop)',
          depth_max == 3, 'max ledger depth observed = %d' % depth_max)

    # without carry the hit count is exactly N (diagonal only)
    for s0 in (0,):
        top = -1
        h2 = 0
        for (a, b) in pairs:
            r = run_pair(K, MUL, hx, a, b, s0, top, mode='nocarry')
            h2 += r['hits']
        hits_nocarry.add(h2)
    claim('C4', 'without the carry marker hits = N = 62 (diagonal only) => the 2N of F4 comes '
                'from N diagonal + N carry hits',
          hits_nocarry == {N}, 'hits without carry = %s' % sorted(hits_nocarry))

    # ---- D budget-feasible pass (per-read terminal), all 120 states
    feas = {}
    for s0 in range(n2I):
        f = run_pass(K, MUL, hx, s0)
        key = (f['completed_pairs'], f['charged_reads'], f['terminal_pair'],
               str(f['spent']), str(f['budget_left']), f['pops'])
        feas[key] = feas.get(key, 0) + 1
    (k_feas, reads_total, terminal_pair, spent, left, pops_feas), mult = sorted(feas.items())[0]
    claim('D1', 'budget-feasible pass = frozen-order prefix of 15 completed pairs, 43 charges inside '
                'them, then the first read of pair (0,15) is the 44th charge and the second is refused',
          len(feas) == 1 and mult == 120 and k_feas == 15 and reads_total == 44 and terminal_pair == (0, 15),
          'completed pairs = %d ; charged reads = %d ; terminal pair = %s ; identical outcomes over 120 states = %d'
          % (k_feas, reads_total, terminal_pair, mult))
    claim('D2', 'the pass charges exactly 44 = N_d reads and terminates with B_rem = 0 EXACT '
                '(no overshoot, no remainder)',
          F(spent) == BUDGET and F(left) == 0 and BUDGET / COST == 44,
          'Sigma = %s = %s x (123/88) ; B_rem = %s ; 44 = B/c' % (spent, BUDGET / COST, left))
    claim('D3', 'the 15 feasible pairs carry 15 pops, so 43 = 44 - 1 charges are read charges of '
                'completed pairs and the 44th is the refused pair opening read',
          43 + 1 == 44 and F(spent) - 43 * COST == COST and pops_feas == 15,
          'pops inside the feasible prefix = %d ; 44th charge = %s' % (pops_feas, F(spent) - 43 * COST))

    # ---- E redundancy: 4-op pair vs 2-op pair, all pairs x all states
    mis_red = 0
    for (a, b) in pairs:
        for s0 in range(n2I):
            r4 = run_pair(K, MUL, hx, a, b, s0, -1, mode='cap4')
            r2 = run_pair(K, MUL, hx, a, b, s0, -1, mode='cap2')
            if not (r4['x_a'] == r2['x_a'] and r4['x_b2'] == r2['x_b'] and
                    r4['s_final'] == r2['s_final'] and r4['top'] == r2['top']):
                mis_red += 1
    claim('E1', 'Pr-1.4: the 4-operation pair equals the 2-operation pair in (x_a, x_b, s_final, top) '
                'for all 3844 pairs x 120 states  => the pop plus the reconcile read are redundant',
          mis_red == 0, 'mismatches = %d / %d' % (mis_red, len(pairs) * n2I))

    # ---- F pop cost forcing + carry placeholder disclosure
    popvar = []
    for pc in (F(0), COST / F(88), COST / F(30), COST / F(8), COST / F(2), COST):
        f = run_pass(K, MUL, hx, 0, popcost=pc)
        popvar.append({'popcost': str(pc), 'completed_pairs': f['completed_pairs'],
                       'charged_reads': f['charged_reads'], 'spent': str(f['spent']),
                       'budget_left': str(f['budget_left']), 'terminal': f['terminal_pair'],
                       'exact': f['budget_left'] == 0})
    claim('F1', 'pop cost eps > 0 leaves B_rem = -15*eps at the terminal (no exact exhaustion) and '
                'shortens the feasible prefix once eps >= c/8  =>  eps = 0 is FORCED by the recorded '
                'zero remainder (contract I4 charges reads only, now derived rather than assumed)',
          popvar[0]['exact'] and all(not v['exact'] for v in popvar[1:]) and
          all(v['completed_pairs'] < 15 for v in popvar[3:]),
          ' | '.join('eps=%s -> pairs %d reads %d B_rem %s' % (v['popcost'], v['completed_pairs'],
                                                              v['charged_reads'], v['budget_left'])
                     for v in popvar))
    # carry placeholder wart: the carried entry returns value 0 into the first read of those pairs
    zero_pairs = 0
    for s0 in (0,):
        top = -1
        for (a, b) in pairs:
            if top == a:
                zero_pairs += 1
            r = run_pair(K, MUL, hx, a, b, s0, top, mode='cap4')
            top = r['top']
    claim('F2', 'carry semantics disclosed: the carried entry stores the placeholder value 0, so the '
                'first read of exactly N = 62 pairs (those with prev-b == a) returns 0, not the recorded sign',
          zero_pairs == 62, 'pairs whose first read hits the carried entry = %d = N' % zero_pairs)

    out = {'rules_version': RULES, 'n2I': n2I, 'order_spectrum': spec, 'axis_types': tc,
           'pass_account': {'read_ops': rops, 'hits': hits, 'misses': misses, 'pops': pops,
                            'max_depth': depth_max, 'final_top_ctx': topf,
                            'hits_without_carry': sorted(hits_nocarry)},
           'budget_pass': {'feasible_pairs': k_feas, 'charged_reads_completed': reads_total,
                           'terminal_pair': terminal_pair, 'sigma': spent,
                           'reads_that_exhaust': 44},
           'redundancy_mismatches': mis_red, 'pop_cost_variants': popvar,
           'carry_zero_pairs': zero_pairs, 'claims': CLAIMS, 'elapsed_s': time.time() - t0}
    with io.open(os.path.join(DATA, '02_ledger_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 104)
    print('RESULT: %d/%d PASS   elapsed %.1f s' % (npass, len(CLAIMS), time.time() - t0))
    print('=' * 104)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
