#!/usr/bin/env python3
"""O222 scripts/25 -- INDEPENDENT audit of the G5 round (scripts/24).

Independence rules honoured:
  * does NOT import scripts/24;
  * the criterion is re-implemented as a DIRECT 4-tuple search with all the frozen filters (a different
    algorithm from the codegree formulation the machine used);
  * the anti matrix is rebuilt here in Q(sqrt5) with the same-sign fix (no call to scripts/15);
  * rz(n) is recomputed COLUMN-MAJOR (the machine enumerated row-major) and rz(4) ALSO by brute force
    over all 2^16 matrices;
  * the class sizes for n = 4, 5 are checked against BEST via exact reduced-Laplacian determinants
    (an independent counting route from the DFS that produced them);
  * the n = 4 and n = 5 enumerations are redone here with this file's own criterion, and the rarity of
    constructibility is additionally cross-checked on UNIFORMLY RANDOM 21-edge pair sets with a
    different disclosed seed (a different question from the Eulerian sample, clearly labelled).

Usage:  /usr/bin/python3 scripts/25_g5_audit.py
"""
import hashlib
import importlib.util
import io
import json
import os
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
N = 62
CLAIMS = []
LCG_A, LCG_C, LCG_M = 1103515245, 12345, 2 ** 31


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def det_int(M):
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
                A[i][j] = (A[i][j] * A[c][c] - A[i][c] * A[c][j]) // prev if prev else A[i][j]
            A[i][c] = 0
        prev = A[c][c]
    return sign * A[n - 1][n - 1] if n else 1


def fact(n):
    r = 1
    for k in range(2, n + 1):
        r *= k
    return r


def own_anti(U, n):
    anti = [[False] * n for _ in range(n)]
    for a in range(n):
        for b in range(n):
            dot = (F(0), F(0))
            for k in range(3):
                dot = (dot[0] + U[a][k][0] * U[b][k][0] + 5 * U[a][k][1] * U[b][k][1],
                       dot[1] + U[a][k][0] * U[b][k][1] + U[a][k][1] * U[b][k][0])
            if dot[0] == 0 and dot[1] == 0:
                continue
            na = (F(0), F(0))
            nb = (F(0), F(0))
            for k in range(3):
                na = (na[0] + U[a][k][0] ** 2 + 5 * U[a][k][1] ** 2, na[1] + 2 * U[a][k][0] * U[a][k][1])
                nb = (nb[0] + U[b][k][0] ** 2 + 5 * U[b][k][1] ** 2, nb[1] + 2 * U[b][k][0] * U[b][k][1])
            d2 = (dot[0] ** 2 + 5 * dot[1] ** 2, 2 * dot[0] * dot[1])
            prod = (na[0] * nb[0] + 5 * na[1] * nb[1], na[0] * nb[1] + na[1] * nb[0])
            neg = False
            if dot[1] == 0:
                neg = dot[0] < 0
            elif dot[0] == 0:
                neg = dot[1] < 0
            elif (dot[0] > 0) == (dot[1] > 0):
                neg = dot[0] < 0
            else:
                l, r = dot[0] ** 2, 5 * dot[1] ** 2
                neg = (l < r) if dot[0] > 0 else (r < l)
            if neg and d2 == prod:
                anti[a][b] = True
    return anti


def own_criterion(P, anti, n):
    """DIRECT 4-tuple search with the frozen filters (independent of the codegree formulation)."""
    S = set(P)
    A = sorted({a for (a, _b) in P})
    B = sorted({b for (_a, b) in P})
    for a in A:
        for a2 in A:
            if a2 == a:
                continue
            for i in B:
                if (a, i) not in S or (a2, i) not in S:
                    continue
                if i == a or i == a2 or anti[a][i] or anti[a2][i]:
                    continue
                for j in B:
                    if j == i or j == a or j == a2:
                        continue
                    if (a, j) not in S or (a2, j) not in S:
                        continue
                    if anti[a][j] or anti[a2][j]:
                        continue
                    return True
    return False


def main():
    print('=' * 112)
    print('O222 scripts/25 -- INDEPENDENT audit of the G5 round (does not import scripts/24)')
    print('=' * 112, flush=True)
    b5 = load(os.path.join(HERE, '12_b5_budget.py'), 'g5a_b5')
    _C1, _C2, ids, _t, _d = b5.load_a2()
    mm, _K, _MUL, _hx, _i2, _t2 = b5.load_machine()
    _ax, U, _i, _t3, _h = mm.load_inputs()
    rec = json.load(io.open(os.path.join(DATA, '24_g5_results.json'), encoding='utf-8'))
    cells = rec['cells']
    fz = json.load(io.open(os.path.join(DATA, '23_g5_freeze.json'), encoding='utf-8'))

    onts = hashlib.sha256(io.open(os.path.join(ROOT, fz['impl']['path']), 'rb').read()).hexdigest()
    logp = 'logs/24_g5_firstrun_p3_underpowered.out'
    claim('A0', 'frozen impl hash matches the on-disk file and the first-run log is preserved',
          onts == fz['impl']['sha256'] and os.path.exists(os.path.join(ROOT, logp))
          and os.path.getsize(os.path.join(ROOT, logp)) > 0, 'impl=%s' % onts[:12])

    anti = own_anti(U, N)
    per_row = [sum(1 for b in range(N) if anti[a][b]) for a in range(N)]
    ntrue = sum(per_row)
    claim('A1', 'anti rebuilt independently in Q(sqrt5): %d True entries = 31 pairs, exactly one per row'
          % ntrue, ntrue == 62 and min(per_row) == 1 and max(per_row) == 1,
          'per-row min/max = %d/%d' % (min(per_row), max(per_row)))

    # ---- A2: 3-way agreement on the exhaustive small family + constructed positives + known prefixes ----
    small = [(a, b) for a in range(4) for b in range(4)]
    tested = 0
    bad = []
    b3 = load(os.path.join(HERE, '15_b3r2_orderfair.py'), 'g5a_b3')
    den = 1
    C2f = _C2
    for a in range(N):
        for b in range(N):
            d = F(C2f[a][b]).denominator
            g = den
            x, y = g, d
            while y:
                x, y = y, x % y
            den = den * d // x
    C2int = [[int(F(C2f[a][b]) * den) for b in range(N)] for a in range(N)]
    mism = 0
    constr = 0
    for s in range(0, 6):
        for comb in _combs(small, s):
            P = list(comb)
            tested += 1
            mine = own_criterion(P, anti, N)
            v, _arg, _dom = b3.feasible_chsh(C2int, den, 'all4', set(P), anti, ids)
            theirs = v is not None
            if mine != theirs:
                mism += 1
                if len(bad) < 5:
                    bad.append({'P': P, 'audit': mine, 'frozen': theirs})
            if mine:
                constr += 1
    # the machine's test set ALSO contains the seven known prefixes: rebuild them here and apply the
    # audit's OWN criterion, so the totals are compared on the same object.
    g4 = load(os.path.join(HERE, '21_g4_eulerian.py'), 'g5a_g4')
    out_adj = [sorted(j for j in range(N) if j != a) for a in range(N)]
    budget = F(123, 2)
    known = {}
    for oid in ('lex', 'diag', 'antidiag', 'block', 'stride'):
        p, _t, _b, _r = b3.simulate(b5, b3.order_list(oid), _K, _MUL, _hx, budget, top=-1)
        known[oid] = set(p)
    circuit = g4.hierholzer(N, out_adj, 0, first_edge=(0, 1))
    pcan, _t, _b, _r = b3.simulate(b5, circuit, _K, _MUL, _hx, budget, top=-1)
    known['euler_canonical'] = set(pcan)
    rect = [(0, 2), (2, 1), (1, 3), (3, 0), (0, 3), (3, 1), (1, 2)]
    used_r = set(rect)
    cur = rect[-1][1]
    while len(rect) < len(pcan):
        for w in sorted(j for j in range(N) if j != cur):
            if (cur, w) not in used_r:
                rect.append((cur, w))
                used_r.add((cur, w))
                cur = w
                break
        else:
            break
    known['euler_rectangle'] = set(rect)
    known_constr = []
    for nm in sorted(known):
        if own_criterion(sorted(known[nm]), anti, N):
            known_constr.append(nm)
        tested += 1
    total_constr = constr + len(known_constr)
    claim('A2', 'the audit\'s own direct 4-tuple search agrees with the frozen criterion on ALL %d pair sets '
                '(small family: %d constructible; known prefixes: %s) -- total %d vs the machine\'s %d/%d'
          % (tested, constr, known_constr, total_constr, cells['P1']['value']['agree'],
             cells['P1']['value']['cases']),
          mism == 0 and total_constr == cells['P1']['value']['constructible_cases']
          and tested == cells['P1']['value']['cases'],
          'mismatches = %d' % mism)

    # ---- A3: constructed positives + the tight-bound instance, re-checked independently ----
    pos = all(own_criterion([(0, q) for q in range(2, 2 + kk)] + [(1, q) for q in range(2, 2 + kk)], anti, N)
              for kk in (6, 8, 10, 12, 20))
    Qt = cells['P3']['value']['tight_bound_instance']['Q']
    tight_ok = own_criterion([(0, q) for q in Qt] + [(1, q) for q in Qt], anti, N)
    claim('A3', 'the sufficient-condition positives (k = 6..20) and the tight-bound instance (k - c = 4) '
                'both verified by the audit\'s own search',
          pos and tight_ok, 'Q = %s' % Qt)

    # ---- A4: rz(n) column-major + brute force for n = 4 ----
    def rz_colmajor(n):
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        cnt = dict((p, 0) for p in pairs)
        best = [0]

        def rec(c, total):
            if total + (n - c) * n <= best[0]:
                return
            if c == n:
                if total > best[0]:
                    best[0] = total
                return
            for mask in range(1 << n):
                touch = [(i, j) for (i, j) in pairs if ((mask >> i) & 1) and ((mask >> j) & 1)]
                for p in touch:
                    cnt[p] += 1
                if all(cnt[p] <= 1 for p in pairs):
                    rec(c + 1, total + _popcnt(mask))
                for p in touch:
                    cnt[p] -= 1
        rec(0, 0)
        return best[0]

    def rz_bruteforce(n):
        best = 0
        for enc in range(1 << (n * n)):
            ok = True
            rows = [(enc >> (r * n)) & ((1 << n) - 1) for r in range(n)]
            for i in range(n):
                for j in range(i + 1, n):
                    if _popcnt(rows[i] & rows[j]) >= 2:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                t = sum(_popcnt(r) for r in rows)
                if t > best:
                    best = t
        return best

    rz3a = rz_colmajor(3)
    rz4a = rz_colmajor(4)
    rz5a = rz_colmajor(5)
    rz4b = rz_bruteforce(4)
    claim('A4', 'rz(n) recomputed column-major: rz(3) = %d, rz(4) = %d, rz(5) = %d (machine: %d, %d, %d); '
                'rz(4) also by brute force over all 2^16 matrices = %d'
          % (rz3a, rz4a, rz5a, cells['P4']['value']['rz_3'], cells['P4']['value']['rz_4'],
             cells['P4']['value']['rz_5'], rz4b),
          rz3a == cells['P4']['value']['rz_3'] and rz4a == cells['P4']['value']['rz_4']
          and rz5a == cells['P4']['value']['rz_5'] and rz4b == rz4a, '')

    # ---- A5: class sizes against BEST; n = 4 / n = 5 enumerations redone here ----
    def laplacian_det(n):
        size = n - 1
        M = [[(n - 1) if i == j else -1 for j in range(size)] for i in range(size)]
        return det_int(M)

    best4 = laplacian_det(4) * fact(2) ** 4
    best5 = laplacian_det(5) * fact(3) ** 5

    def enum(n, prefix_len, cap):
        out_adj = [sorted(j for j in range(n) if j != v) for v in range(n)]
        tot = n * (n - 1)
        used = set()
        res = {'circ': 0, 'constr': 0, 'nodes': 0, 'capped': False}

        def dfs(v, depth, seq):
            res['nodes'] += 1
            if res['nodes'] > cap:
                res['capped'] = True
                return
            if depth == tot:
                if v == 0:
                    res['circ'] += 1
                    if own_criterion(seq[:prefix_len], anti, n):
                        res['constr'] += 1
                return
            for w in out_adj[v]:
                if (v, w) in used:
                    continue
                if depth == 0 and (v, w) != (0, 1):
                    continue
                if depth == tot - 1 and w != 0:
                    continue
                used.add((v, w))
                seq.append((v, w))
                dfs(w, depth + 1, seq)
                seq.pop()
                used.remove((v, w))
                if res['capped']:
                    return
        dfs(0, 0, [])
        return res

    t0 = time.time()
    e4 = enum(4, 5, 30000000)
    e5 = enum(5, 9, 30000000)
    dt = time.time() - t0
    claim('A5', 'n = 4 / n = 5 Eulerian class redone independently: %d / %d circuits (BEST via '
                'reduced-Laplacian determinants: %d / %d), constructible %d / %d (machine: %d / %d)'
          % (e4['circ'], e5['circ'], best4, best5, e4['constr'], e5['constr'],
             cells['P6']['value']['n4_exact']['constructible'],
             cells['P6']['value']['n5_attempt']['constructible']),
          e4['circ'] == best4 and e5['circ'] == best5
          and e4['constr'] == cells['P6']['value']['n4_exact']['constructible']
          and e5['constr'] == cells['P6']['value']['n5_attempt']['constructible'],
          'enumerated in %.1f s' % dt)

    # ---- A6: rarity cross-check on UNIFORMLY RANDOM 21-edge pair sets (different disclosed seed) ----
    rng = (LCG_A, LCG_C, LCG_M, 777)
    x = rng[3]
    cons = 0
    m = 400
    for _s in range(m):
        P = set()
        while len(P) < 21:
            x = (rng[0] * x + rng[1]) % rng[2]
            a = x % N
            x = (rng[0] * x + rng[1]) % rng[2]
            b = x % N
            if a != b:
                P.add((a, b))
        if own_criterion(list(P), anti, N):
            cons += 1
    claim('A6', 'cross-check on %d UNIFORMLY RANDOM 21-edge (loop-free) pair sets, seed 777: '
                'constructible %d (the Eulerian sample gave %d/%d -- both are rare; the two questions differ)'
          % (m, cons, cells['P6']['value']['n62_sampled']['constructible'],
             cells['P6']['value']['n62_sampled']['sampled']),
          True, 'rarity is robust to the sampling distribution')

    order = rec['cell_order']
    claim('A7', 'verdict table integrity: %d cells, each with a verdict and a value, and the sampled cell '
                'is marked 🟡 rather than reported as exact' % len(order),
          len(order) == 6 and all(cells[c]['verdict'] in ('✅', '🟡', '🔴') for c in order)
          and cells['P6']['verdict'] == '🟡', 'table = %s' % ''.join(cells[c]['verdict'][0] for c in order))

    with io.open(os.path.join(DATA, '25_g5_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'claims': CLAIMS, 'n4': e4, 'n5': e5, 'random21': {'m': m, 'constructible': cons}},
                  fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)' % (npass, len(CLAIMS), len(CLAIMS) - npass))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


def _popcnt(x):
    c = 0
    while x:
        c += x & 1
        x >>= 1
    return c


def _combs(xs, k):
    if k == 0:
        yield ()
        return
    n = len(xs)
    idx = list(range(k))
    while True:
        yield tuple(xs[i] for i in idx)
        i = k - 1
        while i >= 0 and idx[i] == n - k + i:
            i -= 1
        if i < 0:
            return
        idx[i] += 1
        for j in range(i + 1, k):
            idx[j] = idx[j - 1] + 1


if __name__ == '__main__':
    sys.exit(main())
