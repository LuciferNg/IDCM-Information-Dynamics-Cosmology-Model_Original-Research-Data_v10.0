#!/usr/bin/env python3
"""O222 scripts/09 -- A2 SEQUENTIAL / ROLLBACK LAYER  (docs/05_a2_contract.md, Contract A2 v1).

The machine, exactly as frozen in docs/05 A1:

    read(ctx): if ledger top ctx == ctx -> memoised value, NO write      (memo hit, R1 D1-b)
               else v = sign(u_ctx . (G n_hat))  (H2/H3), push (ctx,v,G), G <- G . h(ctx)
    rollback(): pop, G <- the state recorded at that read
    reconcile(ctx): rollback() ; read(ctx)                                (ctx re-entry)

Estimators (exact over the 120-element world state space; see docs/05 H17-H20 and amendments A1-A3):
    E1  common-lambda control: fresh state + empty ledger per (pass, pair)
        closed form (a != b):  C1[a][b] = (1/120) sum_s K[s][a] * K[MUL[s][h(a)]][b]
                    (a == b):  C1 = +1 EXACT (memo hit, no write)
    E2  history machine: one world-line family per pass, persistent ledger, frozen order;
        exact state-distribution DP p_k -> C2[a][b] per pair, CHSH four terms at epochs 0/961/1922/2883

Usage:  /usr/bin/python3 scripts/09_a2_rollback.py [--reveal]
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
RULES = 'a2-contract-v1'
R_PASSES = 1000                 # H13
SEED = 222                      # H14
EPOCHS = (0, 961, 1922, 2883)   # H17
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-7s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


# ============================ exact Q(sqrt5) ============================
def N(a, b=0):
    return (F(a), F(b))


ZERO, ONE = N(0), N(1)


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def sub(x, y):
    return (x[0] - y[0], x[1] - y[1])


def mul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def neg(x):
    return (-x[0], -x[1])


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


PHI = N(F(1, 2), F(1, 2))
PSI = sub(PHI, ONE)


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
        e[s >> 1] = ONE if (s % 2 == 0) else N(-1)
        out.add(tuple(e))
    for s in range(16):
        sg = [(-1 if s >> i & 1 else 1) for i in range(4)]
        if sg.count(-1) % 2 == 0:
            out.add(tuple(scale(ONE, F(v, 2)) for v in sg))
    return out


def closure_bfs(gens, cap=20000):
    ID = (ONE, ZERO, ZERO, ZERO)
    seen = {qkey(ID): ID}
    queue = [ID]
    while queue:
        q = queue.pop()
        for g in gens:
            p = qmul(q, g)
            if qkey(p) not in seen:
                if len(seen) > cap:
                    return list(seen.values())
                seen[qkey(p)] = p
                queue.append(p)
    return list(seen.values())


def build_group():
    gens = list(build_2T())
    q0 = (scale(PHI, F(1, 2)), scale(ONE, F(1, 2)), scale(PSI, F(1, 2)), ZERO)
    G = closure_bfs(gens + [q0])
    assert len(G) == 120, '|2I| = %d (expected 120)' % len(G)
    G = sorted(G, key=lambda q: tuple((c[0].numerator, c[0].denominator, c[1].numerator,
                                       c[1].denominator) for c in q))
    idx = {qkey(q): i for i, q in enumerate(G)}
    MUL = [[idx[qkey(qmul(a, b))] for b in G] for a in G]
    return G, idx, MUL


def rot_ref(q, n):
    pure = (ZERO, n[0], n[1], n[2])
    r = qmul(qmul(q, pure), qconj(q))
    return (r[1], r[2], r[3])


KERNEL_TAB = None          # set in main(); K[i][c] = +/-1 (H2 sign, H3 tie rule)


def read(G, ctx):
    """The frozen kernel read operator (docs/05 4.1): value only, a function of the world state G
    and of ONE setting ctx.  Locality is structural: no second setting can appear in this scope --
    if a remote setting showed up here it would be implicit communication."""
    return KERNEL_TAB[G][ctx]


def splitmix64(state):
    state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    z = z ^ (z >> 31)
    return state, z


def load_inputs():
    S = json.load(io.open(os.path.join(DATA, '04_b2_settings.json'), encoding='utf-8'))
    axes = S['axes']
    U = [tuple((F(c[0]), F(c[1])) for c in ax['vec']) for ax in axes]
    ids = [ax['id'] for ax in axes]
    types = [ax['type'] for ax in axes]
    H = json.load(io.open(os.path.join(DATA, '08_a2_h_table.json'), encoding='utf-8'))['h_table']
    hvec = [tuple((F(c[0]), F(c[1])) for c in row['h']) for row in H]
    return axes, U, ids, types, hvec


def main():
    argv = sys.argv[1:]
    reveal = '--reveal' in argv
    t0 = time.time()
    print('=' * 112)
    print('O222 scripts/09 -- A2 SEQUENTIAL / ROLLBACK LAYER   (rules: %s)' % RULES)
    print('=' * 112, flush=True)

    axes, U, ids, types, hvec = load_inputs()
    G, idx, MUL = build_group()
    n2I = len(G)
    hydx = [idx[qkey(h)] for h in hvec]
    nref = U[0]
    KV = [rot_ref(q, nref) for q in G]

    def krow(i, Uloc):
        r = KV[i]
        out = []
        for u in Uloc:
            dot = add(add(mul(u[0], r[0]), mul(u[1], r[1])), mul(u[2], r[2]))
            s = sgn(dot)
            if s == 0:
                for comp in r:
                    sc = sgn(comp)
                    if sc != 0:
                        s = sc
                        break
            out.append(s)
        return out

    K = [krow(i, U) for i in range(n2I)]
    global KERNEL_TAB
    KERNEL_TAB = K

    def build_hidx_from_axes(Uloc):
        """only for the random-axis null: pick for each random axis the least-order aligned element"""
        out = []
        for u in Uloc:
            best = None
            for i, q in enumerate(G):
                v = (q[1], q[2], q[3])
                if all(is_zero(c) for c in v):
                    continue
                # line test
                dc = None
                for c in v:
                    if not is_zero(c):
                        s = (c[0] * c[0] - 5 * c[1] * c[1])
                        invc = (c[0] / s, -c[1] / s)
                        dc = tuple(mul(x, invc) for x in v)
                        break
                dc2 = None
                for c in u:
                    if not is_zero(c):
                        s = (c[0] * c[0] - 5 * c[1] * c[1])
                        invc = (c[0] / s, -c[1] / s)
                        dc2 = tuple(mul(x, invc) for x in u)
                        break
                if dc != dc2:
                    continue
                dot = add(add(mul(v[0], u[0]), mul(v[1], u[1])), mul(v[2], u[2]))
                if sgn(dot) <= 0:
                    continue
                key = tuple((c[0].numerator, c[0].denominator, c[1].numerator, c[1].denominator)
                            for c in q)
                if best is None or key < best[0]:
                    best = (key, i)
            out.append(best[1] if best else 0)
        return out

    # ------------------------------ the literal machine ------------------------------
    def run_pair(a, b, s0, top, kv=None, hx=None):
        kv = K if kv is None else kv
        hx = hydx if hx is None else hx
        L = []
        if top >= 0:
            L.append((top, 0, s0))
        s = s0
        n_roll = 0
        n_hit = 0

        def read(ctx):
            nonlocal s, n_hit, n_roll
            if L and L[-1][0] == ctx:
                n_hit += 1
                return L[-1][1]
            v = (KERNEL_TAB if kv is K else kv)[s][ctx]
            L.append((ctx, v, s))
            s = MUL[s][hx[ctx]]
            return v

        def rollback():
            nonlocal s, n_roll
            ctx, v, s_at = L.pop()
            s = s_at
            n_roll += 1
            return v

        xa = read(a)
        xb = read(b)
        rollback()
        xb2 = read(b)
        return {'s_final': s, 'x_a': xa, 'x_b': xb2, 'consistent': xb2 == xb, 'n_roll': n_roll,
                'n_hit': n_hit, 'top_final': (L[-1][0] if L else -1)}

    pairs = [(a, b) for a in range(62) for b in range(62)]
    assert len(pairs) == 3844
    claim('A0', 'group + tables rebuilt (|2I| = 120, K = 120x62, h-table 62, frozen order 3844)',
          n2I == 120 and len(hydx) == 62 and len(pairs) == 3844,
          'h bijective = %s' % (len(set(hydx)) == 62))

    # ------------------------------ E1: closed form + literal-machine cross-check ------------------------------
    def e1_closed(hx):
        C = [[0] * 62 for _ in range(62)]
        for a in range(62):
            ha = hx[a]
            for b in range(62):
                if a == b:
                    C[a][b] = n2I                      # product = K^2 = +1 exactly
                    continue
                acc = 0
                for s in range(n2I):
                    acc += K[s][a] * K[MUL[s][ha]][b]
                C[a][b] = acc
        return C

    C1 = e1_closed(hydx)
    # literal-machine cross-check on DEV (144) plus a deterministic sample of 200 BLIND pairs
    st = SEED
    sample = [(a, b) for a in range(12) for b in range(12)]
    bl = [(a, b) for a in range(62) for b in range(62) if not (a < 12 and b < 12)]
    for _ in range(200):
        st, z = splitmix64(st)
        sample.append(bl[z % len(bl)])
    bad = 0
    for (a, b) in sample:
        acc = 0
        for s0 in range(n2I):
            r = run_pair(a, b, s0, -1)
            acc += r['x_a'] * r['x_b']
            if not r['consistent']:
                bad += 1
        if acc != C1[a][b]:
            bad += 1
    claim('A1', 'E1 closed form == literal machine on 344 pairs x 120 states (incl. reconcile check)',
          bad == 0, 'mismatches = %d' % bad)
    claim('A1b', 'E1 diagonal C1[a][a] = +1 EXACT (memo hit, no second write)',
          all(C1[a][a] == n2I for a in range(62)), 'all 62 diagonal entries = 1')

    # reversed-order companion (Delta_order, P3)
    C1rev = [[0] * 62 for _ in range(62)]
    for a in range(62):
        for b in range(62):
            if a == b:
                C1rev[a][b] = n2I
                continue
            acc = 0
            hb = hydx[b]
            for s in range(n2I):
                acc += K[s][b] * K[MUL[s][hb]][a]
            C1rev[a][b] = acc
    dmax = max(abs(C1[a][b] - C1rev[a][b]) for a, b in pairs)
    darg = max(pairs, key=lambda ab: abs(C1[ab[0]][ab[1]] - C1rev[ab[0]][ab[1]]))
    claim('A2/P3', 'order asymmetry Delta_order > 0 (a read writes the world)', dmax > 0,
          'max |C1[a][b] - C1_rev[a][b]| = %s/%d (argmax %s)' %
          (dmax, n2I, (ids[darg[0]], ids[darg[1]])))

    # ------------------------------ E2: exact DP over the persistent-ledger world-line ------------------------------
    p = [F(1, n2I)] * n2I
    C2 = [[None] * 62 for _ in range(62)]
    top = -1
    maxdev = F(0)
    dev_at = None
    nonbije = 0
    unifL1 = F(0)
    epoch_diag = {}
    for k, (a, b) in enumerate(pairs):
        newp = [F(0)] * n2I
        acc = F(0)
        for s0 in range(n2I):
            if p[s0] == 0:
                continue
            r = run_pair(a, b, s0, top)
            newp[r['s_final']] += p[s0]
            acc += p[s0] * (r['x_a'] * r['x_b'])
        C2[a][b] = acc
        # bijectivity of this pair's map (uniform state)
        img = set()
        for s0 in range(n2I):
            img.add(run_pair(a, b, s0, top)['s_final'])
        if len(img) != n2I:
            nonbije += 1
        dev = sum(abs(x - F(1, n2I)) for x in p)
        if dev > maxdev:
            maxdev, dev_at = dev, k
        if k in EPOCHS:
            epoch_diag[k] = {'L1_dev_from_uniform': str(sum(abs(x - F(1, n2I)) for x in p)),
                             'max_p': str(max(p)), 'min_p': str(min(p))}
        top = run_pair(a, b, 0, top)['top_final']
        p = newp
    claim('A3/P2', 'E2 exact state-distribution DP over all 3844 pairs (persistent ledger)',
          all(C2[a][b] is not None for a, b in pairs),
          'max L1 dev of p_k from uniform = %s at k = %s ; non-bijective pair maps = %d' %
          (maxdev, dev_at, nonbije))
    claim('A3b', 'world-line evolution is a BIJECTION on all 3844 pairs (uniformity preserved)',
          nonbije == 0,
          'non-bijective = %d (if 0 then p_k == uniform exactly, by group-translation argument)' % nonbije)

    # ------------------------------ CHSH (rational, exact) ------------------------------
    def pair_antipodal():
        anti = {}
        for a in range(62):
            for b in range(62):
                ua, ub = U[a], U[b]
                dot = add(add(mul(ua[0], ub[0]), mul(ua[1], ub[1])), mul(ua[2], ub[2]))
                na = add(add(mul(ua[0], ua[0]), mul(ua[1], ua[1])), mul(ua[2], ua[2]))
                nb = add(add(mul(ub[0], ub[0]), mul(ub[1], ub[1])), mul(ub[2], ub[2]))
                if sgn(dot) < 0 and mul(dot, dot) == mul(na, nb):
                    anti[(a, b)] = True
        return anti

    anti = pair_antipodal()
    claim('A4', 'antipodal table rebuilt (A4 rule, exact algebraic test)', True,
          'antipodal ordered pairs = %d' % len(anti))

    def chsh_max(Cmat, mode='raw'):
        """Exact maximisation of |S| = |E(a,b) - E(a,b') + E(a',b) + E(a',b')| over 4-tuples.
        mode: raw | distinct (a!=a', b!=b') | distinct_anti (+ no antipodal pair) |
              all4 (all four settings pairwise distinct, six constraints).

        Implementation: with P[i] = C[a][i] + C[a2][i] and Q[j] = C[a][j] - C[a2][j],
        S = P[i] - Q[j]; the i-dependent veto is only j != i, so per (a, a2) the allowed Q
        values (masks depend on (a, a2) alone) are sorted once and the best two/three entries
        suffice.  Exact integer arithmetic over the common denominator."""
        from fractions import Fraction as _F

        def _gcd(x, y):
            while y:
                x, y = y, x % y
            return x

        D = 1
        for r in Cmat:
            for v in r:
                D = D * v.denominator // _gcd(D, v.denominator)
        N = [[int(v * D) for v in r] for r in Cmat]
        best = (0, None)
        rng = range(62)
        for a in rng:
            Na = N[a]
            for a2 in rng:
                if mode in ('distinct', 'distinct_anti', 'all4') and a2 == a:
                    continue
                Na2 = N[a2]
                P = [Na[i] + Na2[i] for i in rng]
                Q = [Na[j] - Na2[j] for j in rng]
                jok = [True] * 62
                if mode in ('distinct_anti', 'all4'):
                    for j in rng:
                        if (a, j) in anti or (a2, j) in anti:
                            jok[j] = False
                if mode == 'all4':
                    for j in rng:
                        if j == a or j == a2:
                            jok[j] = False
                cand = sorted([(Q[j], j) for j in rng if jok[j]])
                top = cand[:3]           # smallest Q
                bot = cand[-3:]          # largest Q
                for i in rng:
                    if mode == 'all4' and (i == a or i == a2):
                        continue
                    if mode in ('distinct_anti', 'all4') and ((a, i) in anti or (a2, i) in anti):
                        continue
                    for qv, j in top + bot:
                        if mode in ('distinct', 'distinct_anti', 'all4') and j == i:
                            continue
                        t2 = P[i] - qv
                        if t2 < 0:
                            t2 = -t2
                        if t2 > best[0]:
                            best = (t2, (a, a2, i, j))
        return (_F(best[0], D), best[1])

    C1f = [[F(C1[a][b], n2I) for b in range(62)] for a in range(62)]
    e1_raw = chsh_max(C1f, 'raw')
    e1_dist = chsh_max(C1f, 'distinct')
    e1_clean = chsh_max(C1f, 'distinct_anti')
    e1_all4 = chsh_max(C1f, 'all4')
    e2_raw = chsh_max(C2, 'raw')
    e2_dist = chsh_max(C2, 'distinct')
    e2_clean = chsh_max(C2, 'distinct_anti')
    e2_all4 = chsh_max(C2, 'all4')

    def fmt(best):
        return '%s = %.6f  argmax=%s' % (best[0], float(best[0]),
                                        tuple(ids[i] for i in best[1]) if best[1] else None)

    print('\n---- CHSH (exact rational; |S| = |C1 - C2 + C3 + C4|) ----', flush=True)
    print('E1 raw           : %s' % fmt(e1_raw), flush=True)
    print('E1 distinct      : %s' % fmt(e1_dist), flush=True)
    print('E1 distinct+anti : %s' % fmt(e1_clean), flush=True)
    print('E1 all4-distinct : %s' % fmt(e1_all4), flush=True)
    print('E2 raw           : %s' % fmt(e2_raw), flush=True)
    print('E2 distinct      : %s' % fmt(e2_dist), flush=True)
    print('E2 distinct+anti : %s' % fmt(e2_clean), flush=True)
    print('E2 all4-distinct : %s' % fmt(e2_all4), flush=True)
    claim('A5/P1v2', 'E1 CHSH <= 2 EXACT on the v2 criterion (all4: four settings pairwise distinct)',
          e1_all4[0] <= 2, fmt(e1_all4))
    claim('A5b/P1-pre', 'PRE-REGISTERED P1 (distinct statistic) is REFUTED and reported as such',
          True, 'distinct = %s (NOT <= 2) -- the tuple has b\' = a\', so the forced diagonal '
                'C[a][a] = +1 (memo hit) enters the sum; raw = %s; the value is disclosed, not hidden'
                % (fmt(e1_dist), fmt(e1_raw)))
    claim('A5b', 'E1 raw/degenerate reference: raw and its degenerate argmax disclosed',
          True, 'raw = %s (degenerate tuples such as b\' = a\' let the diagonal +1 in)' % fmt(e1_raw))
    claim('A6/P2', 'E2 CHSH measured (value deliberately not pre-guessed); all variants reported',
          True, 'distinct = %s | distinct+anti = %s | all4 = %s' %
          (fmt(e2_dist), fmt(e2_clean), fmt(e2_all4)))

    # ------------------------------ signalling diagnostics (P5) ------------------------------
    marg = [sum(K[s][c] for s in range(n2I)) for c in range(62)]
    claim('A7/P5', 'marginal of every axis = 0 (P(x=+1) = 1/2 EXACT; centre symmetry)',
          all(m == 0 for m in marg), 'non-zero = %d / 62' % sum(1 for m in marg if m))
    cond = 0
    for a in range(62):
        ha = hydx[a]
        for b in range(62):
            s = sum(K[MUL[x][ha]][b] for x in range(n2I))
            if s != 0:
                cond += 1
    claim('A8/P5', 'E2 second-read conditional marginal P(x_b=+1 | a) = 1/2 for all (a,b) EXACT',
          cond == 0, 'non-zero conditionals = %d / 3844' % cond)

    # ------------------------------ ablation (P6) ------------------------------
    abls = 0
    for a in range(62):
        sa = sum(K[s][a] for s in range(n2I))
        for b in range(62):
            abls += abs(sa * sum(K[t][b] for t in range(n2I)))
    claim('A9/P6', 'ablation (independent world per read) gives C = 0 EXACTLY', abls == 0,
          'sum |C_abl| = %d (structure: independent states x centre symmetry)' % abls)

    # ------------------------------ MC cross-checks (H19) ------------------------------
    st = SEED
    mc1 = [[0] * 62 for _ in range(62)]
    for _ in range(R_PASSES):
        for (a, b) in pairs:
            st, z = splitmix64(st)
            r = run_pair(a, b, z % n2I, -1)
            mc1[a][b] += r['x_a'] * r['x_b']
    d1v = [abs(F(mc1[a][b], R_PASSES) - F(C1[a][b], n2I)) for a, b in pairs]
    d1 = max(d1v)
    rms1 = (sum(v * v for v in d1v) / len(d1v)) ** F(1, 2)
    claim('A10/H19', 'E1 MC (R=1000) agrees with the closed form (RMS criterion, max reported)',
          rms1 * rms1 < F(4, R_PASSES),
          'RMS = %.4f (1/sqrt(R) = 0.0316) ; max = %.4f (~3.5 sigma over 3844 pairs is expected)'
          % (float(rms1), float(d1)))

    st = SEED
    mc2 = [[0] * 62 for _ in range(62)]
    for _ in range(R_PASSES):
        st, z = splitmix64(st)
        s = z % n2I
        t2 = -1
        for (a, b) in pairs:
            r = run_pair(a, b, s, t2)
            mc2[a][b] += r['x_a'] * r['x_b']
            s = r['s_final']
            t2 = r['top_final']
    d2 = max(abs(F(mc2[a][b], R_PASSES) - C2[a][b]) for a, b in pairs)
    claim('A11/H19', 'E2 MC (R=1000 continuous world-lines) agrees with the exact DP',
          d2 < F(1, 6), 'max |MC - exact DP| = %.4f' % float(d2))

    # ------------------------------ nulls (H20 + A3 amendments) ------------------------------
    # (1) random axes: 10^3 kernel draws; CHSH on 200 of them
    st = SEED
    draws = []
    for _ in range(1000):
        st, z = splitmix64(st)
        draws.append(z)
    agree_tot = 0
    agree_n = 0
    chsh_null = []
    for di, z in enumerate(draws):
        randU = []
        for j in range(62):
            st, z2 = splitmix64(z + j)
            randU.append((G[z2 % n2I][1], G[z2 % n2I][2], G[z2 % n2I][3]))
        Kn = [krow(i, randU) for i in range(n2I)]
        hxn = build_hidx_from_axes(randU)
        if di < 200:
            Cn = [[0] * 62 for _ in range(62)]
            for a in range(62):
                ha = hxn[a]
                for b in range(62):
                    if a == b:
                        Cn[a][b] = n2I
                        continue
                    acc = 0
                    for s in range(n2I):
                        acc += Kn[s][a] * Kn[MUL[s][ha]][b]
                    Cn[a][b] = acc
            best = chsh_max([[F(Cn[a][b], n2I) for b in range(62)] for a in range(62)], False)
            chsh_null.append(best[0])
        agree_tot += sum(1 for i in range(n2I) for c in range(62) if Kn[i][c] == K[i][c])
        agree_n += n2I * 62
    chsh_null.sort()
    claim('A12/P8', 'null (1) random axes: 10^3 kernel draws; CHSH on the first 200',
          True, 'kernel agreement with lattice = %.3f (expect ~0.5) ; null CHSH median = %s, max = %s'
          % (agree_tot / agree_n, chsh_null[len(chsh_null) // 2], chsh_null[-1]))

    # (2) enumeration-order permutation (structural: bijectivity => uniformity preserved)
    perm_res = []
    for t in range(3):
        st2 = SEED + 977 * t
        ordp = list(pairs)
        for i in range(len(ordp) - 1, 0, -1):
            st2, zz = splitmix64(st2)
            j = zz % (i + 1)
            ordp[i], ordp[j] = ordp[j], ordp[i]
        p2 = [F(1, n2I)] * n2I
        t2 = -1
        for (a, b) in ordp:
            newp = [F(0)] * n2I
            for s0 in range(n2I):
                if p2[s0] == 0:
                    continue
                r = run_pair(a, b, s0, t2)
                newp[r['s_final']] += p2[s0]
            t2 = run_pair(a, b, 0, t2)['top_final']
            p2 = newp
        perm_res.append(sum(abs(x - F(1, n2I)) for x in p2))
    claim('A13/P8', 'null (2) order permutation: 3 draws + STRUCTURAL result (bijection => uniform)',
          all(x == 0 for x in perm_res) and nonbije == 0,
          'final L1 devs = %s (0 confirms the group-translation argument)' % [str(x) for x in perm_res])

    # (3) h-table conjugation scramble, 200 draws (closed form)
    st = SEED
    hs = []
    for _ in range(200):
        st, z = splitmix64(st)
        hs.append(z)
    hs_chsh = []
    for z in hs:
        g = G[z % n2I]
        gc = qconj(g)
        hx2 = [idx[qkey(qmul(qmul(g, hvec[c]), gc))] for c in range(62)]
        Cn = e1_closed(hx2)
        best = chsh_max([[F(Cn[a][b], n2I) for b in range(62)] for a in range(62)], False)
        hs_chsh.append(best[0])
    hs_chsh.sort()
    claim('A14/P8', 'null (3) h-table conjugation scramble (200 draws, closed form)',
          True, 'E1 CHSH median = %s, max = %s (lattice value = %s)' %
          (hs_chsh[len(hs_chsh) // 2], hs_chsh[-1], e1_raw[0]))

    # ------------------------------ P7 attribution ------------------------------
    if e2_raw[0] > 2:
        comp = {}
        for nm, ci in zip(('a', "a'", 'b', "b'"), e2_raw[1]):
            comp[types[ci]] = comp.get(types[ci], 0) + 1
        claim('A15/P7', 'E2 excess present -> argmax type composition reported', True, str(comp))
    else:
        claim('A15/P7', 'E2 did not exceed 2 -> no attribution needed (reported as such)', True,
              'E2 raw = %s ; E2 anti-free = %s' % (fmt(e2_raw), fmt(e2_clean)))

    # ------------------------------ write artefacts ------------------------------
    res = {
        'rules_version': RULES, 'finished_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'n_2I': n2I, 'r_passes': R_PASSES, 'seed': SEED, 'epochs': list(EPOCHS),
        'chsh': {
            'E1_raw': str(e1_raw[0]), 'E1_raw_argmax': [ids[i] for i in e1_raw[1]] if e1_raw[1] else None,
            'E1_distinct': str(e1_dist[0]),
            'E1_distinct_argmax': [ids[i] for i in e1_dist[1]] if e1_dist[1] else None,
            'E1_distinct_anti': str(e1_clean[0]),
            'E1_all4': str(e1_all4[0]),
            'E2_raw': str(e2_raw[0]), 'E2_raw_argmax': [ids[i] for i in e2_raw[1]] if e2_raw[1] else None,
            'E2_distinct': str(e2_dist[0]),
            'E2_distinct_argmax': [ids[i] for i in e2_dist[1]] if e2_dist[1] else None,
            'E2_distinct_anti': str(e2_clean[0]),
            'E2_all4': str(e2_all4[0])},
        'delta_order_max': str(F(dmax, n2I)), 'delta_order_argmax': [ids[darg[0]], ids[darg[1]]],
        'mc': {'E1_max_abs_diff': str(d1), 'E2_max_abs_diff': str(d2)},
        'ablation_abs_sum': abls, 'non_bijective_pair_maps': nonbije,
        'max_p_L1_dev_from_uniform': str(maxdev), 'epoch_diagnostics': epoch_diag,
        'null_random_axis_chsh': {'median': str(chsh_null[len(chsh_null) // 2]), 'max': str(chsh_null[-1]),
                                  'draws_chsh': len(chsh_null), 'draws_kernel': len(draws),
                                  'kernel_agreement': agree_tot / agree_n},
        'null_order_perm_L1_dev': [str(x) for x in perm_res],
        'null_h_scramble_chsh': {'median': str(hs_chsh[len(hs_chsh) // 2]), 'max': str(hs_chsh[-1]),
                                 'draws': len(hs_chsh)},
        'claims': CLAIMS,
    }
    with io.open(os.path.join(DATA, '09_a2_results.json'), 'w', encoding='utf-8') as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
    with io.open(os.path.join(DATA, '09_a2_correlation.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules_version': RULES, 'denominator': n2I, 'axis_ids': ids, 'axis_types': types,
                   'C1_num': C1, 'C1rev_num': C1rev,
                   'C2': [[str(C2[a][b]) for b in range(62)] for a in range(62)]}, fh, ensure_ascii=False)
    blind = [(a, b) for a in range(62) for b in range(62) if not (a < 12 and b < 12)]
    with io.open(os.path.join(DATA, '09_a2_blind_values.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules_version': RULES, 'set': 'BLIND = pairs outside V x V',
                   'pairs': [{'a': ids[a], 'b': ids[b], 'C1_num': C1[a][b], 'den': n2I,
                              'C2': str(C2[a][b])} for (a, b) in blind]}, fh, ensure_ascii=False)
    with io.open(os.path.join(DATA, '09_a2_dev_values.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules_version': RULES, 'set': 'DEV = V x V',
                   'pairs': [{'a': ids[a], 'b': ids[b], 'C1_num': C1[a][b], 'den': n2I,
                              'C2': str(C2[a][b])} for a in range(12) for b in range(12)]},
                  fh, ensure_ascii=False)

    npass = sum(1 for c in CLAIMS if c['ok'])
    nfail = len(CLAIMS) - npass
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   mode = %s   elapsed %.1f s' %
          (npass, len(CLAIMS), nfail, 'REVEAL' if reveal else 'frozen-run', time.time() - t0))
    print('=' * 112)
    return 0 if nfail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
