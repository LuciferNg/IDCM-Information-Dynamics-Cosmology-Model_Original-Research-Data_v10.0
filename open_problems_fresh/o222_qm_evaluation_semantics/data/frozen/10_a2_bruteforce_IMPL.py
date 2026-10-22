#!/usr/bin/env python3
"""O222 scripts/10 -- FULL-ENUMERATION brute-force audit of the A2 CHSH numbers.

NO optimisation of the enumeration domain: every ordered 4-tuple (a, a', b, b') in 62^4 =
14,776,336 is visited for every statistic variant, with exact arithmetic.  There is no P/Q
decomposition and no early exit; the only representation choice is converting the exact rational
tables of scripts/09 into exact integer numerators over their common denominator (a bijection
between rationals and integer pairs over a fixed D -- and one tuple per variant is recomputed in
raw Fraction arithmetic to prove that equivalence empirically).

Purpose: the authoritative CHSH values for the A2 layer must come from the full sweep, not from
the accelerated maximiser used inside scripts/09 for the nulls.

Usage:
    /usr/bin/python3 scripts/10_a2_bruteforce.py                 # E1 and E2, 4 variants each
    /usr/bin/python3 scripts/10_a2_bruteforce.py --nulls 3       # + full sweep on 3 null draws each
"""
import io
import json
import os
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
SEED = 222
MODES = ('raw', 'distinct', 'distinct_anti', 'all4')


def load():
    with io.open(os.path.join(DATA, '04_b2_settings.json'), encoding='utf-8') as fh:
        S = json.load(fh)
    U = [tuple((F(c[0]), F(c[1])) for c in ax['vec']) for ax in S['axes']]
    ids = [ax['id'] for ax in S['axes']]
    with io.open(os.path.join(DATA, '09_a2_correlation.json'), encoding='utf-8') as fh:
        C = json.load(fh)
    C1 = [[F(C['C1_num'][a][b], C['denominator']) for b in range(62)] for a in range(62)]
    C2 = [[F(x) for x in C['C2'][a]] for a in range(62)]
    with io.open(os.path.join(DATA, '08_a2_h_table.json'), encoding='utf-8') as fh:
        H = json.load(fh)['h_table']
    return U, ids, C1, C2, H


def lcm_den(T):
    D = 1
    for r in T:
        for v in r:
            d = v.denominator
            x, y = D, d
            while y:
                x, y = y, x % y
            D = D * d // x
    return D


def antipodal_table(U):
    anti = bytearray(62 * 62)
    def mulp(x, y):
        return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])
    def sg(x):
        if x[1] == 0:
            return (x[0] > 0) - (x[0] < 0)
        if x[0] == 0:
            return (x[1] > 0) - (x[1] < 0)
        if (x[0] > 0) == (x[1] > 0):
            return 1 if x[0] > 0 else -1
        l, r = x[0] * x[0], 5 * x[1] * x[1]
        if l == r:
            return 0
        return (1 if l > r else -1) * (1 if x[0] > 0 else -1)
    for a in range(62):
        ua = U[a]
        for b in range(62):
            ub = U[b]
            # exact componentwise Q(sqrt5) accumulation of u_a . u_b, |u_a|^2, |u_b|^2
            d0 = (F(0), F(0))
            for k in range(3):
                p, q = ua[k]
                p2, q2 = ub[k]
                d0 = (d0[0] + p * p2 + 5 * q * q2, d0[1] + p * q2 + q * p2)
            na = (F(0), F(0))
            nb = (F(0), F(0))
            for k in range(3):
                p, q = ua[k]
                na = (na[0] + p * p + 5 * q * q, na[1] + 2 * p * q)
                p, q = ub[k]
                nb = (nb[0] + p * p + 5 * q * q, nb[1] + 2 * p * q)
            if sg(d0) < 0:
                if mulp(d0, d0) == mulp(na, nb):
                    anti[a * 62 + b] = 1
    return anti


def brute(N, den, anti, mode):
    """full 62^4 sweep, no pruning of the domain"""
    best = 0
    barg = None
    rng = range(62)
    for a in rng:
        Na = N[a]
        for a2 in rng:
            if mode != 'raw' and a2 == a:
                continue
            Na2 = N[a2]
            base_a = a * 62
            base_a2 = a2 * 62
            for i in rng:
                if mode == 'all4' and (i == a or i == a2):
                    continue
                if mode in ('distinct_anti', 'all4'):
                    if anti[base_a + i] or anti[base_a2 + i]:
                        continue
                pi = Na[i] + Na2[i]
                for j in rng:
                    if mode != 'raw' and j == i:
                        continue
                    if mode == 'all4' and (j == a or j == a2):
                        continue
                    if mode in ('distinct_anti', 'all4'):
                        if anti[base_a + j] or anti[base_a2 + j]:
                            continue
                    S = pi - Na[j] + Na2[j]
                    if S < 0:
                        S = -S
                    if S > best:
                        best = S
                        barg = (a, a2, i, j)
    return best, barg, den


def main():
    argv = sys.argv[1:]
    n_null = int(argv[argv.index('--nulls') + 1]) if '--nulls' in argv else 0
    t0 = time.time()
    U, ids, C1, C2, H = load()
    anti = antipodal_table(U)
    print('=' * 112)
    print('O222 scripts/10 -- FULL 62^4 = 14,776,336 tuple sweep per variant (exact, no pruning)')
    print('=' * 112, flush=True)
    print('antipodal pairs = %d' % sum(anti), flush=True)
    out = {}
    for name, T in (('E1', C1), ('E2', C2)):
        D = lcm_den(T)
        N = [[int(v * D) for v in r] for r in T]
        for mode in MODES:
            ts = time.time()
            best, barg, den = brute(N, D, anti, mode)
            val = F(best, den)
            out['%s_%s' % (name, mode)] = {'num': best, 'den': den, 'value': str(val),
                                           'argmax': [ids[k] for k in barg] if barg else None,
                                           'secs': time.time() - ts}
            print('%s %-14s |S| = %-14s = %.9f  argmax=%s   (%.1f s)' %
                  (name, mode, '%d/%d' % (best, den), float(val),
                   [ids[k] for k in barg] if barg else None, time.time() - ts), flush=True)
    # Fraction cross-check: the exact rational table is *by construction* identical to int/D
    # (a bijection between rationals and integer pairs over the fixed denominator D).  To make that
    # empirical rather than asserted, recompute |S| in raw Fraction arithmetic on the argmax tuple
    # that the full integer sweep selected for each variant.
    for key in [k for k in out if k.startswith(('E1_', 'E2_'))]:
        name, mode = key.split('_', 1)
        T = C1 if name == 'E1' else C2
        a, a2, i, j = [ids.index(x) if isinstance(x, str) else x for x in out[key]['argmax']]
        S = T[a][i] - T[a][j] + T[a2][i] + T[a2][j]
        if S < 0:
            S = -S
        ok = (str(S) == out[key]['value'])
        out[key]['fraction_reat_argmax'] = {'value': str(S), 'identical': bool(ok)}
        print('Fraction recheck %-14s %s vs %s -> %s' %
              (key, S, out[key]['value'], 'IDENTICAL' if ok else 'MISMATCH'), flush=True)
    if n_null:
        print('\n-- FULL-ENUMERATION null: %d random-axis draws, h reassigned per draw --' % n_null,
              flush=True)
        import importlib.util
        spec = importlib.util.spec_from_file_location('a2', os.path.join(ROOT, 'scripts',
                                                                        '09_a2_rollback.py'))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        G, idx, MUL = m.build_group()
        n2I = len(G)
        KV = [m.rot_ref(q, U[0]) for q in G]

        def splitmix64(state):
            state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
            z = state
            z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
            z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
            return state, z ^ (z >> 31)

        def dotq(x, y):
            return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])

        def krow_for(randU, ri):
            r = KV[ri]
            row = []
            for u in randU:
                dot = (F(0), F(0))
                for k in range(3):
                    pu, qu = u[k]
                    pr, qr = r[k]
                    dot = (dot[0] + pu * pr + 5 * qu * qr, dot[1] + pu * qr + qu * pr)
                sg = m.sgn(dot)
                if sg == 0:
                    for comp in r:
                        sc = m.sgn(comp)
                        if sc:
                            sg = sc
                            break
                row.append(sg)
            return row

        def canon_line(v):
            for c in v:
                if not m.is_zero(c):
                    den = (c[0] * c[0] - 5 * c[1] * c[1])
                    ic = (c[0] / den, -c[1] / den)
                    return tuple(m.mul(x, ic) for x in v)
            return None

        def hidx_for(randU, u):
            du = canon_line(u)
            best = None
            for gi, qq in enumerate(G):
                v = (qq[1], qq[2], qq[3])
                dv = canon_line(v)
                if dv is None or dv != du:
                    continue
                dot = (F(0), F(0))
                for k in range(3):
                    pv, qv = v[k]
                    pu, qu = u[k]
                    dot = (dot[0] + pv * pu + 5 * qv * qu, dot[1] + pv * qu + qv * pu)
                if m.sgn(dot) <= 0:
                    continue
                key = tuple((c[0].numerator, c[0].denominator, c[1].numerator, c[1].denominator)
                            for c in qq)
                if best is None or key < best[0]:
                    best = (key, gi)
            return best[1] if best else 0

        pairs = [(a, b) for a in range(62) for b in range(62)]
        st = SEED
        null_records = []
        for d in range(n_null):
            st, z = splitmix64(st)
            randU = []
            for j in range(62):
                st, z2 = splitmix64(st)
                qq = G[z2 % n2I]
                randU.append((qq[1], qq[2], qq[3]))
            K = [krow_for(randU, i) for i in range(n2I)]
            hx = [hidx_for(randU, u) for u in randU]
            rec = {'draw': d, 'E1': {}, 'E2': {}}

            # ---- E1 (fresh ledger per pair) ----
            C1n = [[0] * 62 for _ in range(62)]
            for a in range(62):
                ha = hx[a]
                for b in range(62):
                    if a == b:
                        C1n[a][b] = n2I
                        continue
                    acc = 0
                    for s0 in range(n2I):
                        acc += K[s0][a] * K[MUL[s0][ha]][b]
                    C1n[a][b] = acc
            for mode in MODES:
                best, barg, den = brute(C1n, n2I, anti, mode)
                rec['E1'][mode] = [best, den, [ids[k] for k in barg] if barg else None]
            # ---- E2 (persistent ledger, exact DP) ----
            if d < n_null:
                def machine(a, b, s0, top):
                    L = []
                    if top >= 0:
                        L.append((top, 0, s0))
                    s = s0
                    n_hit = 0

                    def rd(ctx):
                        nonlocal s, n_hit
                        if L and L[-1][0] == ctx:
                            n_hit += 1
                            return L[-1][1]
                        v = K[s][ctx]
                        L.append((ctx, v, s))
                        s = MUL[s][hx[ctx]]
                        return v

                    xa = rd(a)
                    xb = rd(b)
                    _c, _v, s_at = L.pop()      # rollback: restore the state recorded at that read
                    s = s_at
                    xb2 = rd(b)
                    return {'s_final': s, 'x_a': xa, 'x_b': xb2,
                            'top': (L[-1][0] if L else -1)}

                pdist = [F(1, n2I)] * n2I
                top = -1
                C2n = [[F(0)] * 62 for _ in range(62)]
                for (a, b) in pairs:
                    newp = [F(0)] * n2I
                    acc = F(0)
                    for s0 in range(n2I):
                        if pdist[s0] == 0:
                            continue
                        rr = machine(a, b, s0, top)
                        newp[rr['s_final']] += pdist[s0]
                        acc += pdist[s0] * (rr['x_a'] * rr['x_b'])
                    C2n[a][b] = acc
                    top = machine(a, b, 0, top)['top']
                    pdist = newp
                Dn = lcm_den(C2n)
                Nn = [[int(v * Dn) for v in r] for r in C2n]
                for mode in MODES:
                    best, barg, den2 = brute(Nn, Dn, anti, mode)
                    rec['E2'][mode] = [best, den2, [ids[k] for k in barg] if barg else None]
            null_records.append(rec)
            print('draw %-3d E1 all4 = %d/%d  E2 all4 = %s   E1 raw = %d/%d' %
                  (d, rec['E1']['all4'][0], rec['E1']['all4'][1],
                   ('%d/%d' % (rec['E2']['all4'][0], rec['E2']['all4'][1])) if rec['E2'] else 'n/a',
                   rec['E1']['raw'][0], rec['E1']['raw'][1]), flush=True)
        out['nulls'] = null_records
        for mode in MODES:
            v1 = sorted(r['E1'][mode][0] / r['E1'][mode][1] for r in null_records)
            print('null E1 %-14s median = %.6f  max = %.6f  (min = %.6f)' %
                  (mode, v1[len(v1) // 2], v1[-1], v1[0]), flush=True)
        e2a = sorted(r['E2']['all4'][0] / r['E2']['all4'][1] for r in null_records if r['E2'])
        if e2a:
            print('null E2 all4 median = %.6f  max = %.6f' % (e2a[len(e2a) // 2], e2a[-1]), flush=True)
        print('lattice E1 all4 = 2.0   lattice E2 all4 = 3.0', flush=True)
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '10_a2_bruteforce.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print('wrote data/10_a2_bruteforce.json   elapsed %.1f s' % (time.time() - t0), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
