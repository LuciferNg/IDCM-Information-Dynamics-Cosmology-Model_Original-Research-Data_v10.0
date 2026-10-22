#!/usr/bin/env python3
"""O224 scripts/02_phase.py -- judgment item (a): can a non-trivial complex-phase (U(1))
factor group be generated from K_chain (x) K_tree inside the frozen inventory?

Pre-registered: P5, P6 (data/00_contract.json).  All arithmetic exact over Q(sqrt5).
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


def main():
    R = L.Report('02_phase')
    print('=' * 108)
    print('O224 scripts/02 -- (a) complex-phase layer inside the frozen inventory')
    print('=' * 108, flush=True)

    G, idx, MUL, U, ids, types, hx, K = L.load_machine()
    n = len(G)
    e = idx[L.qkey(L.ID_ELEM)]

    # ---------------- order distribution ----------------
    order = []
    for s in range(n):
        k = 1
        x = s
        while x != e:
            x = MUL[x][s]
            k += 1
        order.append(k)
    od = {}
    for k in order:
        od[k] = od.get(k, 0) + 1
    R.claim('A1', 'element-order distribution = {1:1, 2:1, 3:20, 4:30, 5:24, 6:20, 10:24} '
                  '(the 2I table) => group is 2I, not some other order-120 group',
            od == {1: 1, 2: 1, 3: 20, 4: 30, 5: 24, 6: 20, 10: 24},
            str(dict(sorted(od.items()))))

    # ---------------- conjugacy classes ----------------
    inv = [0] * n
    for s in range(n):
        x, k = s, 1
        while x != e:
            x = MUL[x][s]
            k += 1
        y = e
        for _ in range(k - 1):
            y = MUL[y][s]
        inv[s] = y
    assert all(MUL[s][inv[s]] == e for s in range(n))
    classes = []
    seen = [False] * n
    for s in range(n):
        if seen[s]:
            continue
        cl = set()
        for h in range(n):
            hi = inv[h]
            cl.add(MUL[MUL[h][s]][hi])
        for x in cl:
            seen[x] = True
        classes.append(sorted(cl))
    csize = sorted(len(c) for c in classes)
    R.claim('A2', 'conjugacy classes: exactly 9, sizes {1,1,12,12,12,12,20,20,30} '
                  '(2I table) => 9 irreps',
            len(classes) == 9 and csize == [1, 1, 12, 12, 12, 12, 20, 20, 30],
            'n classes = %d ; sizes = %s' % (len(classes), csize))

    # every class closed under inversion?
    cl_of = {}
    for i, c in enumerate(classes):
        for x in c:
            cl_of[x] = i
    bad_cl = [i for i, c in enumerate(classes) if cl_of[inv[c[0]]] != i]
    R.claim('A3', 'EVERY conjugacy class is closed under inversion (C^-1 = C) => every '
                  'irreducible character of 2I is REAL-valued => 2I has NO genuinely complex '
                  '(Frobenius-Schur indicator 0) irreducible representation',
            len(bad_cl) == 0,
            'classes not inversion-closed = %d ; equivalently: every g is conjugate to g^-1 '
            '(checked over all %d elements)' % (len(bad_cl), n))
    badinv = 0
    for s in range(n):
        if cl_of[inv[s]] != cl_of[s]:
            badinv += 1
    R.claim('A3b', 'element-wise version: g ~ g^-1 for all 120 elements', badinv == 0,
            'violations = %d' % badinv)

    # ---------------- commutator subgroup / abelianisation ----------------
    comms = set()
    for a in range(n):
        ai = inv[a]
        for b in range(n):
            comms.add(MUL[MUL[a][b]][MUL[ai][inv[b]]])
    # closure of the commutators
    sub = set([e])
    frontier = [e]
    cl = [c for c in comms]
    while frontier:
        nf = []
        for x in frontier:
            for g in cl:
                y = MUL[x][g]
                if y not in sub:
                    sub.add(y)
                    nf.append(y)
        frontier = nf
    R.claim('A4', '[2I,2I] = 2I (2I is a PERFECT group) => the abelianisation is trivial => '
                  'Hom(2I,U(1)) = {1}: NO non-trivial U(1)-valued phase CHARACTER exists',
            len(sub) == n,
            'distinct commutators = %d ; commutator subgroup order = %d (= |2I|) ; '
            'number of 1-dim irreps = |G/[G,G]| = 1' % (len(comms), len(sub)))

    # ---------------- Frobenius-Schur indicator of the faithful 2-dim rep ----------------
    # chi(g) = 2 * Re(scalar part of the quaternion g)  (the spin-1/2 character)
    # NOTE: the scalar part is a Q(sqrt5) PAIR, so it must be scaled component-wise (a bare
    # "2 * pair" would be Python tuple repetition).
    chi = [(2 * G[s][0][0], 2 * G[s][0][1]) for s in range(n)]
    sum_chi2 = L.ZERO
    for s in range(n):
        sum_chi2 = L.add(sum_chi2, L.mul(chi[s], chi[s]))
    sum_chi = L.ZERO
    for s in range(n):
        sum_chi = L.add(sum_chi, chi[s])
    nu = L.ZERO
    for s in range(n):
        g2 = MUL[s][s]
        nu = L.add(nu, chi[g2])
    nu = L.scale(nu, F(1, n))
    # independent cross-check of nu via the determinant identity tr(rho(g)^2) = chi^2 - 2
    nu2 = L.scale(L.sub(sum_chi2, L.N(2 * n)), F(1, n))
    R.claim('A5', 'the faithful 2-dim (spin-1/2) representation: sum_g |chi|^2 = 120 = |G| '
                  '(irreducible, re-verified); sum_g chi = 0 (no trivial component); '
                  'Frobenius-Schur indicator nu = (1/120) sum_g chi(g^2) = -1 '
                  '(cross-checked by the determinant identity nu = (sum chi^2 - 2|G|)/|G|)',
            sum_chi2 == L.N(120) and sum_chi == L.ZERO and nu == L.N(-1) and nu2 == L.N(-1),
            'sum|chi|^2 = %s ; sum chi = %s ; nu = %s ; nu(identity route) = %s  '
            '(nu = -1 => QUATERNIONIC / symplectic)' % (sum_chi2, sum_chi, nu, nu2))

    # ---------------- complex structure exists (order-4 elements) ----------------
    ord4 = [s for s in range(n) if order[s] == 4]
    minus1 = [s for s in range(n) if order[s] == 2][0]
    sq_ok = all(MUL[s][s] == minus1 for s in ord4)
    R.claim('A6', '30 elements of order 4 and for each g^2 = -1 (the central element) => a '
                  'complex structure J = rho(g) with J^2 = -I EXISTS inside 2I, but by A5 it is '
                  'the symplectic (quaternionic) J, NOT a U(1) structure',
            len(ord4) == 30 and sq_ok,
            'order-4 elements = %d ; all satisfy g^2 = -1 : %s ; -1 = element index %d'
            % (len(ord4), sq_ok, minus1))
    R.claim('A6b', 'the -1 element is central and gives the 2-to-1 spinor collapse '
                   '(2I -> A5), i.e. the "phase" that the group carries is a spinor sign, '
                   'not a U(1) angle',
            all(MUL[minus1][s] == MUL[s][minus1] for s in range(n)),
            'central = True ; 2I/{+-1} = A5 (order 60)')

    # ---------------- minimal-cost geometry of a phase extension ----------------
    R.claim('A7', 'MINIMAL COST (theorem, not a search over IDCM numbers): a finite group has a '
                  'genuinely complex irreducible character iff some element is NOT conjugate to '
                  'its inverse; every group of order <= 2 (=1 or Z2) has all characters real, '
                  'so the minimal finite carrier of a genuinely complex phase is Z3 (order 3, '
                  'character omega = exp(2 pi i/3)). For a CONTINUOUS U(1) phase one needs a '
                  'non-discrete sector. 2I satisfies neither: it is perfect (A4) with all-real '
                  'characters (A3)',
            True, 'minimal discrete carrier order = 3 (Z3) ; 2I has no element outside its '
                  'inverse class: verified on all 120 elements (A3b)')

    # ---------------- what the +-1 readout destroys ----------------
    nref = U[0]
    vals = set()
    for i in range(n):
        r = L.rot_ref(G[i], nref)
        for a in range(len(ids)):
            u = U[a]
            dot = L.add(L.add(L.mul(u[0], r[0]), L.mul(u[1], r[1])), L.mul(u[2], r[2]))
            vals.add(dot)
    R.claim('A8', 'the +-1 sign map destroys the exact structure: the un-binarised readout '
                  '<u_a, R_g n_0> takes far more than 2 values over the 7440 entries, while the '
                  'frozen readout keeps only 2',
            len(vals) > 2, 'distinct exact inner-product values (in Q(sqrt5)) = %d ; '
                           'frozen readout alphabet = {+1,-1}' % len(vals))

    # ---------------- the phase sector that DOES exist in IDCM (citation only) ----------------
    R.claim('A9', '[CITATION, no re-derivation] IDCM does possess an exact continuous U(1) phase '
                  'sector: the W-field Goldstone phase theta. O73 docs/15 §0/§1 '
                  '(o73_h0_first_principles/docs/15_c_first_principles.md): "light = the W-field '
                  'phase (Goldstone) mode"; the action S_theta = (1/2) W_0^2 int (d_mu theta)^2 '
                  'has NO potential => m_theta = 0. O144 docs/17 §1-§2 '
                  '(o144_boson_identity/docs/17_photon_phase_mode.md): the radial mode carries '
                  'm_rho^2 = mu^2 = 2 while the phase mode has m_theta^2 = 0, and the action is '
                  'EXACTLY U(1)-invariant ("U(1) 唔係貼上去")',
            True, 'VERDICT consequence: the complex-phase layer EXISTS in IDCM, but it lives in '
                  'the W-field sector and is invisible to the frozen +-1 real-sign readout; '
                  'a readout that could see it must be phase-sensitive (new object, F1(a))')

    extra = {'order_distribution': {str(k): v for k, v in sorted(od.items())},
             'n_classes': len(classes), 'class_sizes': csize,
             'commutator_subgroup_order': len(sub), 'n_distinct_commutators': len(comms),
             'sum_chi2': str(sum_chi2), 'sum_chi': str(sum_chi), 'fs_indicator': str(nu),
             'n_order4': len(ord4), 'minus_one_index': minus1,
             'distinct_inner_product_values': len(vals),
             'verdict_a': 'RED inside the frozen inventory (perfect group + all-real characters '
                          '+ real +-1 readout); the phase layer itself EXISTS in IDCM as the '
                          'W-field Goldstone theta (cited), i.e. the boundary is a boundary of '
                          'the PROTOCOL, not of IDCM'}
    ok = R.finish(os.path.join(DATA, '02_phase.json'), extra)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
