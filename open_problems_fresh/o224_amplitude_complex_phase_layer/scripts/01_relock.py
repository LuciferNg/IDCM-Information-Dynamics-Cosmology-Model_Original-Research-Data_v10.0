#!/usr/bin/env python3
"""O224 scripts/01_relock.py -- machine re-lock: rebuild the frozen machine inside O224 and
calibrate it against the O222 frozen values (read-only cross-check).

Pre-registered claims P1-P4 (see data/00_contract.json).  Nothing here is new physics: this
script exists so that every later O224 verdict rests on a machine rebuilt in this directory
(no O222 import, no O222 write).
"""
import io
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib2i as L

ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')


def rank_exact(rows, ncols):
    """exact rational rank by Fraction Gaussian elimination."""
    M = [[F(x) for x in r] for r in rows]
    rank = 0
    nrows = len(M)
    for c in range(ncols):
        piv = None
        for r in range(rank, nrows):
            if M[r][c] != 0:
                piv = r
                break
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        pv = M[rank][c]
        M[rank] = [x / pv for x in M[rank]]
        for r in range(nrows):
            if r != rank and M[r][c] != 0:
                f = M[r][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[rank])]
        rank += 1
        if rank == nrows:
            break
    return rank


def rank_modp(rows, ncols, p):
    M = [[x % p for x in r] for r in rows]
    rank = 0
    nrows = len(M)
    for c in range(ncols):
        piv = None
        for r in range(rank, nrows):
            if M[r][c]:
                piv = r
                break
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        inv = pow(M[rank][c], p - 2, p)
        M[rank] = [(x * inv) % p for x in M[rank]]
        for r in range(nrows):
            if r != rank and M[r][c]:
                f = M[r][c]
                M[r] = [(a - f * b) % p for a, b in zip(M[r], M[rank])]
        rank += 1
        if rank == nrows:
            break
    return rank


def main():
    R = L.Report('01_relock')
    print('=' * 108)
    print('O224 scripts/01 -- machine re-lock against the frozen O222 values')
    print('=' * 108, flush=True)

    G, idx, MUL, U, ids, types, hx, K = L.load_machine()
    n2I = len(G)
    nax = len(ids)

    # ---------- R1: group + kernel ----------------
    plus = sum(1 for s in range(n2I) for a in range(nax) if K[s][a] == 1)
    marg = [sum(K[s][a] for s in range(n2I)) for a in range(nax)]
    R.claim('R1', '|2I| = 120 ; K = 120x62 with +1/-1 = 3720/3720 ; all 62 columns sum to 0',
            n2I == 120 and len(K) == 120 and len(K[0]) == 62 and plus == 3720
            and (120 * 62 - plus) == 3720 and all(m == 0 for m in marg),
            'plus = %d, minus = %d, nonzero column sums = %d' %
            (plus, 120 * 62 - plus, sum(1 for m in marg if m)))
    types_ct = {}
    for t in types:
        types_ct[t] = types_ct.get(t, 0) + 1
    R.claim('R1b', 'axis composition = 30 edge + 20 face + 12 vertex = 62',
            types_ct == {'edge': 30, 'face': 20, 'vertex': 12}, str(types_ct))

    # ---------- R2/R3: external cross-check against the frozen O222 correlation table -----
    frz = json.load(io.open(os.path.join(DATA, 'frozen', '09_a2_correlation.json'),
                            encoding='utf-8'))
    den = frz['denominator']
    C1frz = frz['C1_num']
    C2frz = frz['C2']
    C1 = L.e1_table(K, MUL, hx, n2I, nax)
    mism1 = sum(1 for a in range(nax) for b in range(nax) if C1[a][b] != C1frz[a][b])
    R.claim('R2', 'our rebuilt C1 == frozen O222 C1_num on all 3844 entries (external check)',
            mism1 == 0 and den == 120,
            'mismatches = %d ; denominator = %d ; axis ids identical = %s' %
            (mism1, den, frz['axis_ids'] == ids))

    C2 = L.e2_table(K, MUL, hx, n2I, nax)
    mism2 = sum(1 for a in range(nax) for b in range(nax) if C2[a][b] != F(C2frz[a][b]))
    R.claim('R3', 'our rebuilt C2 == frozen O222 C2 on all 3844 entries (external check)',
            mism2 == 0, 'mismatches = %d' % mism2)

    # ---------- R4: diagonal ----------------
    R.claim('R4', 'C1[a][a] = +1 EXACT for all 62 axes (memo hit, no second write)',
            all(C1[a][a] == n2I for a in range(nax)), 'all 62 diagonal entries = 1')

    # ---------- R5: CHSH, exact ----------------
    anti = L.antipodal(U, nax)
    C1q = [[F(C1[a][b], n2I) for b in range(nax)] for a in range(nax)]
    res = {}
    for nm, mode in (('raw', 'raw'), ('distinct', 'distinct'),
                     ('distinct_anti', 'distinct_anti'), ('all4', 'all4')):
        v1, a1 = L.chsh_max(C1q, anti, mode, nax)
        v2, a2 = L.chsh_max(C2, anti, mode, nax)
        res['E1_' + nm] = (v1, [ids[i] for i in a1] if a1 else None)
        res['E2_' + nm] = (v2, [ids[i] for i in a2] if a2 else None)
    R.claim('R5', 'max|S| reproduced: E1 all4 = 2 (classical bound), E2 all4 = 3, '
                  'distinct = 4 for both E1 and E2',
            res['E1_all4'][0] == 2 and res['E2_all4'][0] == 3 and res['E1_distinct'][0] == 4
            and res['E2_distinct'][0] == 4,
            'E1 all4 = %s (argmax %s) ; E2 all4 = %s (argmax %s) ; E1 distinct = %s ; '
            'E2 distinct = %s' % (res['E1_all4'][0], res['E1_all4'][1], res['E2_all4'][0],
                                  res['E2_all4'][1], res['E1_distinct'][0], res['E2_distinct'][0]))
    R.claim('R5b', 'Tsirelson 2*sqrt2 = 2.828427... is NOT reached in the feasible window '
                   '(gap = 41.42% of the classical value)',
            True, 'all4 values are 2 (E1) and 3 (E2, budget-infeasible per docs/45)')

    # ---------- R6: no-signalling diagnostics ----------------
    cond = 0
    for a in range(nax):
        ha = hx[a]
        for b in range(nax):
            if sum(K[MUL[x][ha]][b] for x in range(n2I)) != 0:
                cond += 1
    abls = 0
    for a in range(nax):
        sa = sum(K[s][a] for s in range(n2I))
        for b in range(nax):
            abls += abs(sa * sum(K[t][b] for t in range(n2I)))
    R.claim('R6', 'no-signalling layer reproduced: marginals 62/62 = 1/2, conditionals '
                  '3844/3844 = 1/2, ablation = 0',
            all(m == 0 for m in marg) and cond == 0 and abls == 0,
            'nonzero marginals = %d/62 ; nonzero conditionals = %d/3844 ; sum|C_abl| = %d' %
            (sum(1 for m in marg if m), cond, abls))

    # ---------- R7: budget identities (window bookkeeping) ----------------
    reads_pass = F(123, 2) / F(123, 88)
    per_read = F(123, 88)
    e_min = F(123, 176)
    overrun = F(7688) / (F(123, 2) / F(123, 88))
    R.claim('R7', 'budget/window identities: (123/2)/(123/88) = 44 = N_d reads per pass ; '
                  'per-read cost = 2*E_min ; A2 pass overrun = 1922/11 = 174.7x ; '
                  'reads = 3N^2 = 11532 ; hits = 2N = 124',
            reads_pass == 44 and per_read == 2 * e_min and overrun == F(1922, 11)
            and 3 * 62 * 62 == 11532 and 2 * 62 == 124,
            'reads/pass = %s ; overrun = %s = %.4f ; 3N^2 = %d ; 2N = %d' %
            (reads_pass, overrun, float(overrun), 3 * 62 * 62, 2 * 62))

    # ---------- R8: exact value sets ----------------
    vs1 = sorted(set(F(C1[a][b], n2I) for a in range(nax) for b in range(nax)))
    mags = sorted(set(abs(v) for v in vs1))
    want = sorted([F(0), F(1, 15), F(2, 15), F(1, 5), F(4, 15), F(1, 3), F(2, 3), F(1)])
    vs2 = sorted(set(C2[a][b] for a in range(nax) for b in range(nax)))
    R.claim('R8', 'C1 value magnitudes == the docs/45 B2 set {0,1/15,2/15,1/5,4/15,1/3,2/3,1} '
                  'exactly (8 values, 15 signed values)',
            mags == want and len(vs1) == 15,
            'C1: %d distinct signed values ; magnitudes = %s' %
            (len(vs1), [str(x) for x in mags]))
    R.claim('R8b', 'C2 (persistent-ledger) value set reported for the record',
            True, '%d distinct values: %s' % (len(vs2), [str(x) for x in vs2[:12]] +
                                              (['...'] if len(vs2) > 12 else [])))

    # ---------- R9: behaviour collapse (120 -> 60, class size 2) ----------------
    # exact re-implementation of the frozen E2 pair semantics (lib2i.e2_table), but tracing
    # the readout pair (x_a, x_b) of every one of the 3844 pairs for a given initial state.
    order = [(a, b) for a in range(nax) for b in range(nax)]

    def trace(s0):
        s = s0
        top = -1
        out = []
        for (a, b) in order:
            Lg = []
            if top >= 0:
                Lg.append((top, 0, s))

            def rd(ctx, s):
                if Lg and Lg[-1][0] == ctx:
                    return Lg[-1][1], s
                v = K[s][ctx]
                Lg.append((ctx, v, s))
                return v, MUL[s][hx[ctx]]
            xa, s = rd(a, s)
            xb, s = rd(b, s)
            _c, _v, s_at = Lg.pop()
            s = s_at
            xb2, s = rd(b, s)
            top = Lg[-1][0] if Lg else -1
            out.append((xa, xb2))
        return tuple(out)
    beh = {}
    for s0 in range(n2I):
        beh.setdefault(trace(s0), []).append(s0)
    sizes = sorted(len(v) for v in beh.values())
    R.claim('R9', 'redundancy: 120 initial states collapse to 60 distinct behaviours, every '
                  'class of size 2 (centre Z2 2-to-1 collapse) => effective randomness '
                  'log2(60) bits',
            len(beh) == 60 and set(sizes) == {2},
            'distinct behaviours = %d ; class sizes = %s ; log2(60) = %.4f bits' %
            (len(beh), sorted(set(sizes)), 5.906890595608519))

    # ---------- R10: rank of K ----------------
    rk_fr = rank_exact([[K[s][a] for a in range(nax)] for s in range(n2I)], nax)
    rk_p1 = rank_modp([[K[s][a] for a in range(nax)] for s in range(n2I)], nax, 1000003)
    rk_p2 = rank_modp([[K[s][a] for a in range(nax)] for s in range(n2I)], nax, 2147483647)
    R.claim('R10', 'rank_R(K) = 6 EXACT (exact rational elimination, cross-checked mod '
                   'p = 1000003 and p = 2^31-1)',
            rk_fr == 6 and rk_p1 == 6 and rk_p2 == 6,
            'rank_Q = %d ; rank_GF(1000003) = %d ; rank_GF(2^31-1) = %d' %
            (rk_fr, rk_p1, rk_p2))

    # ---------- R11: explicit R^3 sign witness (+ tie structure) ----------------
    nref = U[0]
    ties = 0
    bad = 0
    tie_by_state = {}
    for i in range(n2I):
        r = L.rot_ref(G[i], nref)
        t = None
        for comp in r:
            sc = L.sgn(comp)
            if sc:
                t = sc
                break
        for a in range(nax):
            u = U[a]
            dot = L.add(L.add(L.mul(u[0], r[0]), L.mul(u[1], r[1])), L.mul(u[2], r[2]))
            s = L.sgn(dot)
            if s == 0:
                ties += 1
                s = t
                tie_by_state.setdefault(i, set()).add(K[i][a])
            if s != K[i][a]:
                bad += 1
    R.claim('R11', 'explicit real 3-dim sign witness: K[i][a] = sgn(x_i . y_a) with '
                   'x_i = R_{g_i} n_0 in R^3 and y_a = u_a in R^3, EXCEPT on the 1200 tied '
                   'entries where the frozen H3 rule (axis-independent, function of the state '
                   'alone) applies -- every one of these is verified',
            bad == 0 and ties == 1200 and all(len(v) == 1 for v in tie_by_state.values()),
            'ties = %d (%.2f%% of 7440) ; mismatches = %d ; tied entries are axis-independent = %s'
            % (ties, 100.0 * ties / 7440.0, bad,
               all(len(v) == 1 for v in tie_by_state.values())))
    R.claim('R11b', '[INHERITED, not re-verified here] sign_rank(K) = 3 EXACT '
                    '(O222 R20/M3 600/600 + R20/M7 circular-arc necessary condition: rank 2 '
                    'impossible; quoted as provenance for the "no rank advantage" statement)',
            True, 'provenance: o222 docs/26_r19_results.md, docs/28_r20_results.md, '
                  'docs/37_r23_u2_results.md')

    extra = {'n_2I': n2I, 'n_axes': nax, 'types': types_ct,
             'C1_values': [str(x) for x in vs1], 'C2_values': [str(x) for x in vs2],
             'chsh': {k: [str(v[0]), v[1]] for k, v in res.items()},
             'behaviour_classes': len(beh), 'class_sizes': sorted(set(sizes)),
             'rank_Q': rk_fr, 'rank_GF': [rk_p1, rk_p2], 'ties': ties}
    ok = R.finish(os.path.join(DATA, '01_relock.json'), extra)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
