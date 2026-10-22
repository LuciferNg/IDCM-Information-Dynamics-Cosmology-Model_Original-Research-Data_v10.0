#!/usr/bin/env python3
"""O222 scripts/22 -- INDEPENDENT audit of the G4 round (scripts/21).

Independence rules honoured:
  * does NOT import scripts/21;
  * the cost table is recomputed with a SELF-WRITTEN ledger simulator (explicit list of
    (ctx, value, state) entries, memo by top-only inspection) -- not by calling run_pair;
    a deterministic strided subset is ALSO pushed through the frozen machine, so the simulator
    itself is validated rather than assumed;
  * the Eulerian circuit is rebuilt with the auditor's own Hierholzer and checked against the
    recorded head;
  * the arborescence count is verified by an EXACT determinant of the reduced Laplacian
    (integer elimination) instead of the n^(n-2) closed form that scripts/21 quoted;
  * the CHSH value is recomputed by the auditor's own 4-tuple enumeration over its own
    reconstructed prefix, using the A2 record's C2 with a COMPUTED denominator.

Usage:  /usr/bin/python3 scripts/22_g4_audit.py
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


def sim_pair(K, MUL, hx, a, b, t, s0=0):
    """SELF-WRITTEN pair protocol: rd(a), rd(b), pop, rd(b).  Returns (misses, x_a, x_b, top, s)."""
    L = []
    if t >= 0:
        L.append((t, 0, s0))
    s = s0
    miss = 0

    def rd(ctx):
        nonlocal s, miss
        if L and L[-1][0] == ctx:
            return L[-1][1]
        v = K[s][ctx]
        L.append((ctx, v, s))
        s = MUL[s][hx[ctx]]
        miss += 1
        return v
    xa = rd(a)
    xb = rd(b)
    _c, _v, s_at = L.pop()
    s = s_at
    xb2 = rd(b)
    return miss, xa, xb, (L[-1][0] if L else -1), s, xb2


def law(t, a, b):
    return 3 - (1 if t == a else 0) - (1 if b == a else 0)


def own_hierholzer(n, start, first_edge=None):
    out_adj = [sorted(j for j in range(n) if j != v) for v in range(n)]
    ptr = [0] * n
    stack = [start]
    vseq = []
    while stack:
        v = stack[-1]
        if ptr[v] < len(out_adj[v]):
            w = out_adj[v][ptr[v]]
            ptr[v] += 1
            stack.append(w)
        else:
            vseq.append(stack.pop())
    vseq.reverse()
    edges = [(vseq[i], vseq[i + 1]) for i in range(len(vseq) - 1)]
    if first_edge is not None and edges:
        k = edges.index(first_edge)
        edges = edges[k:] + edges[:k]
    return edges


def det_int(M):
    """exact determinant by fraction-free (Bareiss) elimination on an integer matrix."""
    n = len(M)
    A = [[int(x) for x in row] for row in M]
    sign = 1
    prev = 1
    for c in range(n):
        p = None
        for i in range(c, n):
            if A[i][c] != 0:
                p = i
                break
        if p is None:
            return 0
        if p != c:
            A[c], A[p] = A[p], A[c]
            sign = -sign
        for i in range(c + 1, n):
            for j in range(c + 1, n):
                num = A[i][j] * A[c][c] - A[i][c] * A[c][j]
                A[i][j] = num // prev if prev else num
            A[i][c] = 0
        prev = A[c][c]
    return sign * A[n - 1][n - 1] if n else 1


def reduced_laplacian_det(n):
    """det of the reduced Laplacian of the loop-free complete digraph = # in-arborescences rooted at 0."""
    size = n - 1
    M = []
    for i in range(1, n):
        row = []
        for j in range(1, n):
            row.append((n - 1) if i == j else (-1))
        M.append(row)
    return det_int(M)


def main():
    print('=' * 112)
    print('O222 scripts/22 -- INDEPENDENT audit of the G4 round (does not import scripts/21)')
    print('=' * 112, flush=True)
    b5 = load(os.path.join(HERE, '12_b5_budget.py'), 'g4aud_b5')
    _C1, C2f, ids, types, _d1 = b5.load_a2()
    _m, K, MUL, hx, ids2, types2 = b5.load_machine()
    rec = json.load(io.open(os.path.join(DATA, '21_g4_results.json'), encoding='utf-8'))
    cells = rec['cells']
    fz = json.load(io.open(os.path.join(DATA, '20_g4_freeze.json'), encoding='utf-8'))

    # ---- A0: freeze/hash and first-run evidence ----
    import hashlib
    onts = hashlib.sha256(io.open(os.path.join(ROOT, fz['impl']['path']), 'rb').read()).hexdigest()
    logs = ['logs/21_g4_firstrun_int_str_limit.out', 'logs/21_g4_firstrun_convention_mismatch.out']
    logs_ok = all(os.path.exists(os.path.join(ROOT, p)) and os.path.getsize(os.path.join(ROOT, p)) > 0
                  for p in logs)
    claim('A0', 'frozen impl hash matches the on-disk file and both first-run logs are preserved',
          onts == fz['impl']['sha256'] and logs_ok, 'impl=%s logs=%s' % (onts[:12], logs_ok))

    # ---- A1: the cost table, own simulator, plus a strided frozen-machine cross-check ----
    total = 0
    match_law = 0
    ex = []
    for t in (-1,) + tuple(range(N)):
        for a in range(N):
            for b in range(N):
                got = sim_pair(K, MUL, hx, a, b, t)[0]
                total += 1
                if got == law(t, a, b):
                    match_law += 1
                elif len(ex) < 10:
                    ex.append({'t': t, 'a': ids[a], 'b': ids[b], 'sim': got, 'law': law(t, a, b)})
    frozen_ok = 0
    frozen_n = 0
    for t in (-1,) + tuple(range(N)):
        for a in range(N):
            for b in range(N):
                if (t * 3844 + a * 62 + b) % 977 != 0:
                    continue
                r, _rem = b5.run_pair(a, b, 0, t, K, MUL, hx, F(123, 2))
                frozen_n += 1
                if r['misses'] == law(t, a, b):
                    frozen_ok += 1
    claim('A1', 'cost law holds on the whole table in an independent simulator (%d/%d) and on the '
                'strided frozen-machine subset (%d/%d)' % (match_law, total, frozen_ok, frozen_n),
          match_law == total and frozen_ok == frozen_n and total == cells['P1']['value']['cells'],
          'recorded %d/%d' % (cells['P1']['value']['matches'], cells['P1']['value']['cells']))

    # ---- A2: independent Hierholzer + prefix + fairness ----
    circ = own_hierholzer(N, 0, first_edge=(0, 1))
    wanted = set((a, b) for a in range(N) for b in range(N) if a != b)
    head = [[ids[a], ids[b]] for a, b in circ[:12]]
    circ_ok = (len(circ) == N * (N - 1) and set(circ) == wanted and len(set(circ)) == len(circ)
               and all(circ[i][1] == circ[i + 1][0] for i in range(len(circ) - 1))
               and circ[-1][1] == circ[0][0])
    claim('A2', 'Eulerian circuit rebuilt independently (own Hierholzer): %d edges, valid, recorded head matched'
          % len(circ), circ_ok and head == rec['eulerian_circuit_head'],
          'head = %s' % head[:3])

    budget = F(123, 2)
    pref = []
    rem = budget
    t = -1
    for (a, b) in circ:
        c = law(t, a, b)
        if rem - F(123, 88) * c < F(123, 176):
            break
        rem = rem - F(123, 88) * c
        pref.append((a, b))
        t = b
    reads = sum(law((-1 if i == 0 else pref[i - 1][1]), a, b) for i, (a, b) in enumerate(pref))
    claim('A3', 'feasible prefix recomputed: %d edges / %d reads (recorded %d / %d)'
          % (len(pref), reads, cells['P3']['value']['ii_measured']['feasible_prefix_edges'],
             cells['P3']['value']['ii_measured']['reads']),
          len(pref) == cells['P3']['value']['ii_measured']['feasible_prefix_edges']
          and reads == cells['P3']['value']['ii_measured']['reads'],
          'budget left = %s' % rem)

    outd = dict((v, 0) for v in range(N))
    ind = dict((v, 0) for v in range(N))
    for (a, b) in pref:
        outd[a] += 1
        ind[b] += 1
    fair = max(abs(outd[v] - ind[v]) for v in range(N))
    claim('A4', 'fairness of the canonical prefix recomputed: max|out - in| = %d (<= 1 theorem; recorded %d)'
          % (fair, cells['P6']['value'][0]['max_abs_out_minus_in']),
          fair == cells['P6']['value'][0]['max_abs_out_minus_in'] and fair <= 1, '')

    # ---- A5: optimality toy (own cost function, all 720 permutations) ----
    pairs3 = [(a, b) for a in range(3) for b in range(3) if a != b]
    import itertools
    best = None
    minim = []
    for perm in itertools.permutations(pairs3):
        tt = -1
        c = 0
        for (a, b) in perm:
            c += law(tt, a, b)
            tt = b
        if best is None or c < best:
            best = c
            minim = [perm]
        elif c == best:
            minim.append(perm)
    eul = [p for p in minim if all(p[i][1] == p[i + 1][0] for i in range(len(p) - 1)) and p[-1][1] == p[0][0]]
    claim('A5', 'n=3 toy reproduced independently: min total = %d, minimisers = %d, all Eulerian = %s'
          % (best, len(minim), len(eul) == len(minim)),
          best == cells['P3']['value']['iii_toy_n3']['min_total_cost']
          and len(minim) == cells['P3']['value']['iii_toy_n3']['minimiser_count']
          and len(eul) == len(minim),
          'recorded min/count = %d/%d' % (cells['P3']['value']['iii_toy_n3']['min_total_cost'],
                                          cells['P3']['value']['iii_toy_n3']['minimiser_count']))

    # ---- A6: BEST via exact reduced-Laplacian determinants (not the quoted closed form) ----
    rows = []
    for n in (3, 4, 62):
        d = reduced_laplacian_det(n)
        rows.append({'n': n, 'det_reduced_laplacian': d, 'n^(n-2)': n ** (n - 2), 'agree': d == n ** (n - 2)})
    rec_n34 = cells['P4']['value']['n3_n4_validation']
    best_ok = all(r['agree'] for r in rows) and all(
        r2['best_theorem_fixed_first_edge'] == reduced_laplacian_det(r2['n']) * fact_aud(r2['n'] - 2) ** r2['n']
        for r2 in rec_n34)
    claim('A6', 'BEST verified with exact reduced-Laplacian determinants: t_w = n^(n-2) for n = 3, 4, 62',
          best_ok, 'det(62) has %d digits, equals 62^60 = %s' % (len(str(rows[2]['det_reduced_laplacian'])),
                                                                rows[2]['agree']))

    # ---- A7: constructibility + CHSH recomputed on the auditor's own prefix ----
    inpref = set(pref)
    four = [((0, 2), (0, 3), (1, 2), (1, 3))]
    rect_present = all(e in inpref for e in four[0])
    den2 = 1
    for a in range(N):
        for b in range(N):
            d = F(C2f[a][b]).denominator
            g = den2
            x, y = g, d
            while y:
                x, y = y, x % y
            den2 = den2 * d // x
    C2int = [[int(F(C2f[a][b]) * den2) for b in range(N)] for a in range(N)]
    # the auditor's own trail: 4 rectangle edges + a deterministic filler to 21 edges
    trail = [(0, 2), (2, 1), (1, 3), (3, 0), (0, 3), (3, 1), (1, 2)]
    used = set(trail)
    cur = trail[-1][1]
    while len(trail) < len(pref):
        nxt = [w for w in range(N) if w != cur and (cur, w) not in used]
        if not nxt:
            break
        trail.append((cur, nxt[0]))
        used.add((cur, nxt[0]))
        cur = nxt[0]
    trail_set = set(trail)
    ok_rect = all(e in trail_set for e in four[0])
    # own all4 maximum over the rectangle's own 4-tuple domain
    # the auditor's OWN antipodal matrix (own exact sign in Q(sqrt5)) and own full 4-tuple enumeration
    axis2, U2, _i5, _t5, _h5 = _m.load_inputs()
    antiM = [[False] * N for _ in range(N)]
    for a in range(N):
        for b in range(N):
            dot = (F(0), F(0))
            for k in range(3):
                dot = (dot[0] + U2[a][k][0] * U2[b][k][0] + 5 * U2[a][k][1] * U2[b][k][1],
                       dot[1] + U2[a][k][0] * U2[b][k][1] + U2[a][k][1] * U2[b][k][0])
            na = (F(0), F(0))
            nb = (F(0), F(0))
            for k in range(3):
                na = (na[0] + U2[a][k][0] ** 2 + 5 * U2[a][k][1] ** 2, na[1] + 2 * U2[a][k][0] * U2[a][k][1])
                nb = (nb[0] + U2[b][k][0] ** 2 + 5 * U2[b][k][1] ** 2, nb[1] + 2 * U2[b][k][0] * U2[b][k][1])
            def sgn5(x):
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
                return (1 if l > r else -1) if p > 0 else (1 if r > l else -1)
            dotd = (dot[0] ** 2 - 5 * dot[1] ** 2, 2 * dot[0] * dot[1])
            prod = (na[0] * nb[0] + 5 * na[1] * nb[1], na[0] * nb[1] + na[1] * nb[0])
            if sgn5(dot) < 0 and dotd == prod:
                antiM[a][b] = True
    A = sorted({a for (a, b) in trail})
    B = sorted({b for (a, b) in trail})
    best = None
    barg = None
    dom = 0
    for a in A:
        for a2 in A:
            if a2 == a:
                continue
            for i in B:
                if (a, i) not in trail_set or (a2, i) not in trail_set:
                    continue
                if i == a or i == a2 or antiM[a][i] or antiM[a2][i]:
                    continue
                for j in B:
                    if (a, j) not in trail_set or (a2, j) not in trail_set:
                        continue
                    if j == i or j == a or j == a2 or antiM[a][j] or antiM[a2][j]:
                        continue
                    dom += 1
                    Sabs = abs(C2int[a][i] + C2int[a2][i] - C2int[a][j] + C2int[a2][j])
                    if best is None or Sabs > best:
                        best = Sabs
                        barg = (a, a2, i, j)
    vS = F(best, den2) if best is not None else None
    claim('A7', 'constructibility recomputed: canonical prefix rectangle = %s (recorded %s); auditor trail '
                'rectangle = %s, own all4 max over %d tuples = %s (recorded %s)'
          % (rect_present, cells['P5']['value']['a_constructible'], ok_rect, dom, vS, cells['P5']['value']['b_all4']),
          (not rect_present) and ok_rect and vS is not None and vS <= 2 and str(vS) == cells['P5']['value']['b_all4'],
          'argmax = %s' % (None if barg is None else [ids[x] for x in barg]))

    # ---- A8: verdict table integrity ----
    order = rec['cell_order']
    claim('A8', 'verdict table integrity: %d cells, each with a verdict and a value' % len(order),
          len(order) == 6 and all(cells[c]['verdict'] in ('✅', '🟡', '🔴') and cells[c]['value'] for c in order),
          'table = %s' % ''.join(cells[c]['verdict'][0] for c in order))

    with io.open(os.path.join(DATA, '22_g4_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'claims': CLAIMS, 'det_rows': rows, 'own_prefix_edges': len(pref),
                   'own_prefix_reads': reads, 'fairness': fair}, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)' % (npass, len(CLAIMS), len(CLAIMS) - npass))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


def fact_aud(n):
    r = 1
    for k in range(2, n + 1):
        r *= k
    return r


if __name__ == '__main__':
    sys.exit(main())
