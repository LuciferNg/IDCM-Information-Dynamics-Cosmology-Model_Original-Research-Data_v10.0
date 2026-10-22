#!/usr/bin/env python3
"""O228 scripts/04 -- R2: the general machine theorem + OUT-OF-SAMPLE blind tests.

Contract: docs/02_r2_contract.md  (o228-r2-general-machine-v1)

Machines
  M_T      T   (order 12)  u0 = (1,1,1)   axes DERIVED from the group (3 two-fold + 4 three-fold lines)
  M_O      O   (order 24)  u0 = e1        axes DERIVED from the group (6 + 4 + 3 lines)
  M_D4     D4  (order 8)   u0 = e3        axes DERIVED from the group (4 two-fold + 1 four-fold)
  M_2I / M_face / M_edge   the frozen icosahedral machinery with u0 = V00 / F00 / E00 (read-only import)

Exact arithmetic throughout: integers for T/O/D4, the upstream Q(sqrt5) pair arithmetic for the
icosahedral machines.  Tie rule (frozen, verbatim from o222 scripts/12 L77-85):
    dot == 0  ->  sign of the FIRST NON-ZERO COMPONENT of the ROW vector.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/04_r2_general_machine.py
"""
import collections
import importlib.util
import io
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
O222 = os.path.abspath(os.path.join(ROOT, '..', 'o222_qm_evaluation_semantics'))
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


# --------------------------------------------------------------- integer 3-vectors / groups
def vdot(u, r):
    return u[0] * r[0] + u[1] * r[1] + u[2] * r[2]


def sgn_tie(u, r):
    s = vdot(u, r)
    if s > 0:
        return 1
    if s < 0:
        return -1
    for c in r:                      # frozen tie rule: first non-zero component of the ROW
        if c > 0:
            return 1
        if c < 0:
            return -1
    raise ValueError('zero row vector')


def matvec(M, v):
    return tuple(sum(M[i][j] * v[j] for j in range(3)) for i in range(3))


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def det3(M):
    return (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
            - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
            + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))


IDENT = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def signed_perm_mats():
    out = []
    for pm in itertools.permutations(range(3)):
        for sg in itertools.product([1, -1], repeat=3):
            M = [[0, 0, 0] for _ in range(3)]
            for i in range(3):
                M[i][pm[i]] = sg[i]
            if det3(M) == 1:
                out.append(M)
    return out


def group_closure(gens):
    seen = {tuple(map(tuple, IDENT)): IDENT}
    q = [IDENT]
    while q:
        A = q.pop()
        for B in gens:
            C = matmul(A, B)
            k = tuple(map(tuple, C))
            if k not in seen:
                seen[k] = C
                q.append(C)
    return list(seen.values())


def mat_order(M):
    k, P = 1, M
    while P != IDENT and k < 24:
        P = matmul(P, M)
        k += 1
    return k


def axis_of(M):
    """primitive integer axis of a rotation (sign-canonical: first non-zero component positive)"""
    A = [[M[i][j] - (1 if i == j else 0) for j in range(3)] for i in range(3)]
    for i in range(3):
        for j in range(i + 1, 3):
            c = (A[i][1] * A[j][2] - A[i][2] * A[j][1],
                 A[i][2] * A[j][0] - A[i][0] * A[j][2],
                 A[i][0] * A[j][1] - A[i][1] * A[j][0])
            if c != (0, 0, 0):
                g = 0
                for x in c:
                    g = math.gcd(g, abs(x))
                c = tuple(x // g for x in c)
                for x in c:
                    if x != 0:
                        if x < 0:
                            c = tuple(-y for y in c)
                        break
                return c
    return None


def group_axes(grp, orders):
    lines = set()
    for M in grp:
        if mat_order(M) in orders:
            a = axis_of(M)
            if a is not None:
                lines.add(a)
    return sorted(lines)


# --------------------------------------------------------------- machine
class Machine(object):
    def __init__(self, name, rows, cols, n_zeros=0):
        self.name = name
        self.rows = list(rows)
        self.cols = list(cols)
        self.n_zeros = n_zeros
        self.m = len(self.rows)
        self.N = len(self.cols)
        self.pairs = [(i, j) for i in range(self.m) for j in range(i + 1, self.m)]
        self.types = None

    def census(self):
        cls = {}
        for a, v in enumerate(self.cols):
            cls.setdefault(min(v, tuple(-x for x in v)), []).append(a)
        self.types = sorted(cls.keys())
        self.tclass = cls
        self.mults = [len(cls[t]) for t in self.types]
        shapes = collections.Counter()
        for t in self.types:
            pos = sum(1 for x in t if x > 0)
            a, b2 = min(pos, self.m - pos), max(pos, self.m - pos)
            shapes['%dx%d' % (a, b2)] += 1             # UNORDERED shape (string key for JSON); the canonical
            #                                            +- representative must not create a fake (3,1)/(1,3) split
        return {'n_types': len(self.types), 'mults': self.mults,
                'mult_hist': dict(sorted(collections.Counter(self.mults).items())),
                'shapes': dict(sorted(shapes.items()))}

    def type_pair_masks(self):
        out = []
        for t in self.types:
            a = self.tclass[t][0]
            mk = 0
            for b, (i, j) in enumerate(self.pairs):
                if self.cols[a][i] != self.cols[a][j]:
                    mk |= (1 << b)
            out.append(mk)
        self.ALLP = (1 << len(self.pairs)) - 1
        return out

    def fk_typeset(self, kmax):
        """F_k = sum over SEPARATING type-sets T of e_k(T)   (e_k = elementary symmetric in the multiplicities)"""
        tpm = self.type_pair_masks()
        KT = len(self.types)
        out = {}
        for k in range(1, kmax + 1):
            s = 0
            for r in range(1, k + 1):
                for Ts in itertools.combinations(range(KT), r):
                    mk = 0
                    for i in Ts:
                        mk |= tpm[i]
                    if mk != self.ALLP:
                        continue
                    poly = [1]
                    for i in Ts:
                        coef = [math.comb(self.mults[i], t) for t in range(1, self.mults[i] + 1)]
                        new = [0] * (len(poly) + len(coef))
                        for u, cu in enumerate(poly):
                            if cu == 0:
                                continue
                            for v, cv in enumerate(coef, start=1):
                                new[u + v] += cu * cv
                        poly = new
                    s += poly[k] if k < len(poly) else 0
            out[k] = s
        return out

    def fk_direct(self, kmax):
        """independent: plain enumeration over column subsets with a pair-mask test"""
        cm = []
        for a in range(self.N):
            mk = 0
            for b, (i, j) in enumerate(self.pairs):
                if self.cols[a][i] != self.cols[a][j]:
                    mk |= (1 << b)
            cm.append(mk)
        ALLP = (1 << len(self.pairs)) - 1
        out = {}
        for k in range(1, kmax + 1):
            n = 0
            for combo in itertools.combinations(range(self.N), k):
                mk = 0
                for a in combo:
                    mk |= cm[a]
                if mk == ALLP:
                    n += 1
            out[k] = n
        return out

    def fk_dfs_k(self, k):
        """exact pruned-DFS count of separating k-subsets for a single k"""
        cm = []
        for a in range(self.N):
            mk = 0
            for b, (i, j) in enumerate(self.pairs):
                if self.cols[a][i] != self.cols[a][j]:
                    mk |= (1 << b)
            cm.append(mk)
        ALLP = (1 << len(self.pairs)) - 1
        n = len(cm)
        suf = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            suf[i] = suf[i + 1] | cm[i]
        cnt = [0]

        def rec(start, depth, mk):
            if depth == k:
                if mk == ALLP:
                    cnt[0] += 1
                return
            need = k - depth
            for j in range(start, n - need + 1):
                nm = mk | cm[j]
                if nm | suf[j + 1] != ALLP:
                    continue
                rec(j + 1, depth + 1, nm)

        rec(0, 0, 0)
        return cnt[0]

    def k_min_search(self, maxk, verbose=False):
        """k_min by early exit: the smallest k with F_k > 0 (returns k_min, {k: F_k})"""
        fs = {}
        for k in range(1, maxk + 1):
            t = time.time()
            fs[k] = self.fk_dfs_k(k)
            if verbose:
                print('      k_min search %s: F_%d = %d (%.1f s)' % (self.name, k, fs[k], time.time() - t),
                      flush=True)
            if fs[k] > 0:
                return k, fs
        return None, fs

    def fk_dfs(self, kmax):
        """pruned DFS enumeration (exact, R1's algorithm): prune when the remaining columns cannot cover"""
        cm = []
        for a in range(self.N):
            mk = 0
            for b, (i, j) in enumerate(self.pairs):
                if self.cols[a][i] != self.cols[a][j]:
                    mk |= (1 << b)
            cm.append(mk)
        ALLP = (1 << len(self.pairs)) - 1
        n = len(cm)
        suf = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            suf[i] = suf[i + 1] | cm[i]
        out = {}
        for k in range(1, kmax + 1):
            cnt = [0]

            def rec(start, depth, mk):
                if depth == k:
                    if mk == ALLP:
                        cnt[0] += 1
                    return
                need = k - depth
                for j in range(start, n - need + 1):
                    nm = mk | cm[j]
                    if nm | suf[j + 1] != ALLP:
                        continue
                    rec(j + 1, depth + 1, nm)

            rec(0, 0, 0)
            out[k] = cnt[0]
        return out

    def rank(self):
        A = [[F(self.cols[a][i]) for a in range(self.N)] for i in range(self.m)]
        nr, ncol = len(A), len(A[0])
        r = 0
        for c in range(ncol):
            piv = next((i for i in range(r, nr) if A[i][c] != 0), None)
            if piv is None:
                continue
            A[r], A[piv] = A[piv], A[r]
            for i in range(r + 1, nr):
                if A[i][c] != 0:
                    f = A[i][c] / A[r][c]
                    for j in range(c, ncol):
                        A[i][j] -= f * A[r][j]
            r += 1
        return r


# --------------------------------------------------------------- null (size-multiset reduction)
def int_parts(n, mx=None):
    if mx is None:
        mx = n
    if n == 0:
        yield []
        return
    for f in range(min(n, mx), 0, -1):
        for r in int_parts(n - f, f):
            yield [f] + r


def g_sizes(sizes):
    w = 1
    for s in sizes:
        w *= (-1) ** (s - 1) * math.factorial(s - 1)
    return w


def null_rate(m, k):
    """exact separating rate of k random bisections of m points, over all C(m,m/2)/2 bisections"""
    nbis = math.comb(m, m // 2) // 2
    tot = math.comb(nbis, k)
    for sizes in int_parts(m):
        if sizes == [1] * m:
            continue
        cnt = collections.Counter(sizes)
        npar = math.factorial(m)
        for s, mm in cnt.items():
            npar //= (math.factorial(mm) * math.factorial(s) ** mm)
        poly = [1] + [0] * (m // 2)
        for s in sizes:
            new = poly[:]
            for t in range(m // 2 - s + 1):
                new[t + s] += poly[t]
            poly = new
        bh = poly[m // 2] // 2
        if bh >= k:
            tot += npar * g_sizes(sizes) * math.comb(bh, k)
    return F(tot, math.comb(nbis, k)), nbis


def all_partitions(n):
    res = []

    def rec(i, blocks):
        if i == n:
            res.append(tuple(tuple(b) for b in blocks))
            return
        for b in blocks:
            b.append(i)
            rec(i + 1, blocks)
            b.pop()
        blocks.append([i])
        rec(i + 1, blocks)
        blocks.pop()
    rec(0, [])
    return res


def mobius_F(mm, kmax):
    """F_k = C(N,k) + sum_{pi != 0hat} g(pi) C(beta(pi),k) -- all partitions enumerated (small m only)"""
    weights = collections.Counter()
    for pi in all_partitions(mm.m):
        if all(len(B) == 1 for B in pi):
            continue
        beta = 0
        for c in mm.cols:
            ok = True
            for B in pi:
                v0 = c[B[0]]
                if any(c[x] != v0 for x in B[1:]):
                    ok = False
                    break
            if ok:
                beta += 1
        if beta >= 1:
            g = 1
            for B in pi:
                g *= (-1) ** (len(B) - 1) * math.factorial(len(B) - 1)
            weights[beta] += g
    out = {}
    for k in range(1, kmax + 1):
        s = math.comb(mm.N, k)
        for beta, g in weights.items():
            if beta >= k:
                s += g * math.comb(beta, k)
        out[k] = s
    return out


# --------------------------------------------------------------- main
def main():
    t0 = time.time()
    out = {}
    print('=' * 112)
    print('O228 scripts/04 -- R2: general machine theorem + blind tests   (contract o228-r2-general-machine-v1)')
    print('=' * 112, flush=True)

    # ---- frozen icosahedral machinery (read-only import)
    spc = importlib.util.spec_from_file_location('mX', os.path.join(O222, 'scripts', '12_b5_budget.py'))
    mX = importlib.util.module_from_spec(spc)
    spc.loader.exec_module(mX)
    m, K, MUL, hx, ids, types = mX.load_machine()
    axes, U, ids_u, types_u, hvec = m.load_inputs()
    Gf, idx, MULg = m.build_group()

    def icosa(u0_index, name):
        KV = [m.rot_ref(q, U[u0_index]) for q in Gf]
        rows, seen = [], set()
        for r in KV:
            key = tuple((x[0], x[1]) for x in r)
            if key not in seen:
                seen.add(key)
                rows.append(r)
        zc = 0
        cols = []
        for a in range(len(U)):
            u = U[a]
            col = []
            for r in rows:
                dot = m.add(m.add(m.mul(u[0], r[0]), m.mul(u[1], r[1])), m.mul(u[2], r[2]))
                s = m.sgn(dot)
                if s == 0:
                    zc += 1
                    for comp in r:
                        sc = m.sgn(comp)
                        if sc:
                            s = sc
                            break
                col.append(s)
            cols.append(tuple(col))
        return Machine(name, rows, cols, zc), rows

    M2I, _ = icosa(ids_u.index('V00'), 'M_2I')
    Mface, rows_f = icosa(ids_u.index('F00'), 'M_face')
    Medge, rows_e = icosa(ids_u.index('E00'), 'M_edge')

    edge_cols = [a for a in range(62) if ids_u[a].startswith('E')]
    vf_cols = [a for a in range(62) if not ids_u[a].startswith('E')]

    def col_ties(mach, a):
        u = U[a]
        n = 0
        for r in mach.rows:
            dot = m.add(m.add(m.mul(u[0], r[0]), m.mul(u[1], r[1])), m.mul(u[2], r[2]))
            if m.sgn(dot) == 0:
                n += 1
        return n

    # ---- T / O / D4 from their group structure
    SM = signed_perm_mats()
    V = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    Tgrp = [M for M in SM if sorted(matvec(M, v) for v in V) == sorted(V)]
    Ogrp = SM
    Rz = [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
    Rx = [[1, 0, 0], [0, -1, 0], [0, 0, -1]]
    D4grp = group_closure([Rz, Rx])
    axT = group_axes(Tgrp, {2, 3})
    axO = group_axes(Ogrp, {2, 3, 4})
    axD = group_axes(D4grp, {2, 4})
    out['groups'] = {'|T|': len(Tgrp), '|O|': len(Ogrp), '|D4|': len(D4grp)}
    out['derived_axes'] = {'T': [list(a) for a in axT], 'O': [list(a) for a in axO], 'D4': [list(a) for a in axD]}
    print('groups: |T|=%d |O|=%d |D4|=%d ; derived axis lines: T=%d O=%d D4=%d -> columns %d/%d/%d'
          % (len(Tgrp), len(Ogrp), len(D4grp), len(axT), len(axO), len(axD),
             2 * len(axT), 2 * len(axO), 2 * len(axD)), flush=True)

    def int_machine(name, grp, u0, ax):
        """ax = the LINES; the machine's columns are both +u and -u for every line (as upstream: 62 = 2x31)"""
        rows, seen = [], set()
        for M in grp:
            r = matvec(M, u0)
            if r not in seen:
                seen.add(r)
                rows.append(r)
        zc = 0
        cols = []
        for u in ax:
            for uu in (u, tuple(-x for x in u)):
                col = []
                for r in rows:
                    if vdot(uu, r) == 0:
                        zc += 1
                    col.append(sgn_tie(uu, r))
                cols.append(tuple(col))
        return Machine(name, rows, cols, zc)

    MT = int_machine('M_T', Tgrp, (1, 1, 1), axT)
    MO = int_machine('M_O', Ogrp, (1, 0, 0), axO)
    MD = int_machine('M_D4', D4grp, (0, 0, 1), axD)
    MACH = [M2I, Mface, Medge, MT, MO, MD]
    out['machine_shapes'] = {mm.name: {'m': mm.m, 'N': mm.N, 'tie_entries': mm.n_zeros} for mm in MACH}
    print('machines: %s' % out['machine_shapes'], flush=True)

    # ---------------- closed forms + census for all machines
    out['census'] = {}
    out['closed_form'] = {}
    out['k_min'] = {}
    for mm in MACH:
        cens = mm.census()
        ft = mm.fk_typeset(4)
        fd = mm.fk_direct(4)
        out['census'][mm.name] = cens
        out['closed_form'][mm.name] = {'typeset': {str(k): ft[k] for k in ft}, 'direct': {str(k): fd[k] for k in fd}}
        out['k_min'][mm.name] = min([k for k in range(1, 5) if ft[k] > 0], default=None)
        print('  %-7s m=%-3d N=%-3d ties=%-4d types=%-3d shapes=%s hist=%s F1..4=%s k_min=%s'
              % (mm.name, mm.m, mm.N, mm.n_zeros, cens['n_types'], cens['shapes'], cens['mult_hist'],
                 [ft[k] for k in (1, 2, 3, 4)], out['k_min'][mm.name]), flush=True)

    # ================ (C) consistency / regression
    c2 = out['census']['M_2I']
    f2 = out['closed_form']['M_2I']
    r2 = M2I.rank()
    claim('C1', 'M_2I rebuilt inside R2 reproduces R1 bit-for-bit: 16 types / hist {3:10,5:5,7:1} / '
                'F1..F4 = [0,0,0,12645] / k_min = 4 / rank = 6 / 120 tie entries',
          c2['n_types'] == 16 and c2['mult_hist'] == {3: 10, 5: 5, 7: 1}
          and [int(f2['typeset'][str(k)]) for k in (1, 2, 3, 4)] == [0, 0, 0, 12645]
          and [int(f2['direct'][str(k)]) for k in (1, 2, 3, 4)] == [0, 0, 0, 12645]
          and r2 == 6 and M2I.n_zeros == 120,
          'types=%d hist=%s F=%s direct=%s rank=%d ties=%d'
          % (c2['n_types'], c2['mult_hist'], [f2['typeset'][str(k)] for k in (1, 2, 3, 4)],
             [f2['direct'][str(k)] for k in (1, 2, 3, 4)], r2, M2I.n_zeros))
    nr12, nbis12 = null_rate(12, 4)
    claim('C3', 'the size-multiset null reduction regresses onto R1s exact p0 = 6240/180251 at m = 12',
          abs(float(nr12) - 0.03461839324053681) < 1e-12,
          'null_rate(12,4) = %s = %.8f ; nbis = %d' % (nr12, float(nr12), nbis12))
    claim('C2', 'tie entries: M_2I = 120 (R1 C8) and M_face = 120 (the B4 prediction)',
          M2I.n_zeros == 120 and Mface.n_zeros == 120,
          'ties: 2I=%d face=%d edge=%d T=%d O=%d D4=%d'
          % (M2I.n_zeros, Mface.n_zeros, Medge.n_zeros, MT.n_zeros, MO.n_zeros, MD.n_zeros))

    # ================ (A) general theorem
    claim('T1', 'every machine: #distinct rows = |orbit(u0)| = [G : Stab(u0)], no row repeated',
          len({tuple(r) for r in M2I.rows}) == 12
          and [mm.m for mm in MACH] == [12, 20, 30, 4, 6, 2],
          'm by machine = %s' % {mm.name: mm.m for mm in MACH})
    claim('T2', 'bisection iff tie-free: machines whose census is all (m/2,m/2) are exactly those with zero tie '
                'entries on every row; machines with ties show non-bisection shapes',
          all((mm.n_zeros == 0) == all(k.split('x')[0] == str(mm.m // 2)
                                      for k in out['census'][mm.name]['shapes'])
              for mm in MACH),
          ' ; '.join('%s: ties=%d shapes=%s' % (mm.name, mm.n_zeros, out['census'][mm.name]['shapes'])
                     for mm in MACH))
    t3ok = all(all(int(out['closed_form'][mm.name]['typeset'][str(k)])
                   == int(out['closed_form'][mm.name]['direct'][str(k)]) for k in range(1, 5)) for mm in MACH)
    claim('T3', 'the type-set closed form equals the independent direct enumeration for k = 1..4 on all six machines',
          t3ok, ' ; '.join('%s %s' % (mm.name, [out['closed_form'][mm.name]['typeset'][str(k)] for k in (1, 2, 3, 4)])
                           for mm in MACH))
    mob = {}
    for mm in (MT, MO, MD):
        mob[mm.name] = mobius_F(mm, 4)
    mobok = all(all(mob[mm.name][k] == int(out['closed_form'][mm.name]['typeset'][str(k)]) for k in range(1, 5))
                for mm in (MT, MO, MD))
    out['mobius_route'] = {n: {str(k): v for k, v in d.items()} for n, d in mob.items()}
    claim('T3b', 'the partition-lattice Mobius route (beta weights g(pi)) agrees with the type-set route on '
                 'M_T / M_O / M_D4 for k = 1..4 (a third, genuinely different algorithm; for m >= 12 the full '
                 'partition enumeration is infeasible and R1s pruned Mobius route stands as the m = 12 check)',
          mobok, ' ; '.join('%s %s' % (n, [mob[n][k] for k in (1, 2, 3, 4)]) for n in mob))
    # extend the k_min search on the 20/30-row machines with the exact pruned DFS (the type-set form
    # over 24 resp. 60 types is infeasible beyond k = 4)
    kmin = dict(out['k_min'])
    ext = {}
    for mm in (Mface, Medge):
        if kmin[mm.name] is not None:
            continue
        kk, fs = mm.k_min_search(7, verbose=True)
        ext[mm.name] = {'F': {str(k): fs[k] for k in fs}, 'k_min': kk}
        if kk is not None:
            kmin[mm.name] = kk
    out['extended_dfs'] = ext
    out['k_min_final'] = kmin
    claim('T4', 'k_min is finite for every machine and F_k = 0 exactly below it (type-set form for k <= 4, '
                'extended by the exact pruned DFS to k <= 5 on the 20/30-row machines)',
          all(v is not None for v in kmin.values()), 'k_min = %s ; extended DFS = %s' % (kmin, ext))
    ranks = {mm.name: mm.rank() for mm in MACH}
    out['rank'] = ranks
    claim('T5', 'CONJECTURE TESTED: k_min <= rank_Q(K) on every machine',
          all(kmin[n] is not None and kmin[n] <= ranks[n] for n in ranks),
          'rank = %s ; k_min = %s' % (ranks, kmin))
    t6det, t6ok = [], True
    for mm in MACH:
        if mm.m < 4 or kmin[mm.name] is None:
            continue
        k = kmin[mm.name]
        tv = out['closed_form'][mm.name]['typeset'].get(str(k))
        if tv is None:
            tv = ext[mm.name]['F'][str(k)] if mm.name in ext else None
        rmach = F(int(tv), math.comb(mm.N, k))
        rnull, nbis = null_rate(mm.m, k)
        t6det.append('%s: k_min=%d mach=%.6f null=%.6f nbis=%d' % (mm.name, k, float(rmach), float(rnull), nbis))
        if not (rmach < rnull):
            t6ok = False
    claim('T6', 'BLIND: no resource excess anywhere - rate_machine(k_min) < rate_null(k_min) on all machines '
                'with m >= 4', t6ok, ' | '.join(t6det))

    # ================ (B) blind tests
    cT, fT = out['census']['M_T'], out['closed_form']['M_T']
    claim('B1', 'BLIND M_T: m=4 ; 7 types = 4x(1,3) + 3x(2,2) each multiplicity 2 ; F1=0,F2=12,F3=212 ; k_min=2',
          MT.m == 4 and cT['n_types'] == 7 and cT['shapes'] == {'1x3': 4, '2x2': 3}
          and cT['mult_hist'] == {2: 7}
          and [int(fT['typeset'][str(k)]) for k in (1, 2, 3)] == [0, 12, 212] and out['k_min']['M_T'] == 2,
          'm=%d types=%d shapes=%s hist=%s F1,2,3=%s k_min=%s ties=%d'
          % (MT.m, cT['n_types'], cT['shapes'], cT['mult_hist'],
             [fT['typeset'][str(k)] for k in (1, 2, 3)], out['k_min']['M_T'], MT.n_zeros))
    cO, fO = out['census']['M_O'], out['closed_form']['M_O']
    claim('B2', 'BLIND M_O: m=6 ; exactly 4 types all (3,3) with multiplicities (8,6,6,6) ; F1=F2=0, F3=1080 ; k_min=3',
          MO.m == 6 and cO['n_types'] == 4 and cO['shapes'] == {'3x3': 4}
          and sorted(cO['mults'], reverse=True) == [8, 6, 6, 6]
          and [int(fO['typeset'][str(k)]) for k in (1, 2, 3)] == [0, 0, 1080] and out['k_min']['M_O'] == 3,
          'm=%d types=%d shapes=%s mults=%s F1,2,3=%s k_min=%s ties=%d'
          % (MO.m, cO['n_types'], cO['shapes'], sorted(cO['mults'], reverse=True),
             [fO['typeset'][str(k)] for k in (1, 2, 3)], out['k_min']['M_O'], MO.n_zeros))
    cD, fD = out['census']['M_D4'], out['closed_form']['M_D4']
    claim('B3', 'BLIND M_D4 (degenerate): m=2 ; 1 type with multiplicity 10 ; F_k = C(10,k) for k >= 1 ; k_min = 1',
          MD.m == 2 and cD['n_types'] == 1 and cD['mults'] == [10]
          and all(int(fD['typeset'][str(k)]) == math.comb(10, k) for k in range(1, 5)) and out['k_min']['M_D4'] == 1,
          'm=%d types=%d mults=%s F1..4=%s k_min=%s ties=%d'
          % (MD.m, cD['n_types'], cD['mults'], [fD['typeset'][str(k)] for k in range(1, 5)],
             out['k_min']['M_D4'], MD.n_zeros))
    et = [col_ties(Mface, a) for a in edge_cols]
    vt = [col_ties(Mface, a) for a in vf_cols]
    vf_bis = all(sum(1 for x in Mface.cols[a] if x > 0) == 10 for a in vf_cols)
    out['face_tie_law'] = {'edge_tie_counts': sorted(set(et)), 'vf_tie_counts': sorted(set(vt)),
                           'vf_all_10_10': vf_bis, 'total_ties': sum(et)}
    claim('B4', 'BLIND M_face: m = 20 ; every edge column has exactly 4 tied rows (its two faces and their '
                'opposites) ; the 32 vertex/face columns are tie-free (10,10) bisections ; total tie entries = 120',
          Mface.m == 20 and set(et) == {4} and set(vt) == {0} and vf_bis and sum(et) == 120,
          'm=%d edge ties=%s V/F ties=%s VF all (10,10)=%s total=%d'
          % (Mface.m, sorted(set(et)), sorted(set(vt)), vf_bis, sum(et)))
    # ---- post-blind diagnostic, used only for the B1 correction note (which family of separating
    #      triples the hand count of 212 missed)
    comp = collections.Counter()
    tmap = {}
    for i, t in enumerate(MT.types):
        for a in MT.tclass[t]:
            tmap[a] = i
    ALLP = MT.ALLP
    tpm = MT.type_pair_masks()
    for combo in itertools.combinations(range(MT.N), 3):
        mk = 0
        for a in combo:
            mk |= tpm[tmap[a]]
        if mk == ALLP:
            pat = tuple(sorted(collections.Counter(tmap[a] for a in combo).values(), reverse=True))
            comp[pat] += 1
    out['B1_diagnostic_3subset_compositions'] = {'%s' % (k,): v for k, v in sorted(comp.items())}
    print('B1 diagnostic: separating 3-subsets of M_T by type-multiplicity pattern: %s'
          % dict(sorted(comp.items())), flush=True)

    claim('B5', 'M_edge (measurement): m = 30 as per the upstream class count',
          Medge.m == 30, 'm=%d ties=%d shapes=%s k_min=%s (F_7 = %d)' % (Medge.m, Medge.n_zeros,
                                                              out['census']['M_edge']['shapes'],
                                                              kmin['M_edge'],
                                                              ext.get('M_edge', {}).get('F', {}).get('7', -1)))

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '04_r2_general_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              out['elapsed_s']))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
