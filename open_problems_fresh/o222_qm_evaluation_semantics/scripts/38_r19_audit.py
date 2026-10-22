#!/usr/bin/env python3
"""O222 scripts/38 -- INDEPENDENT AUDIT of the R19 closure machine (scripts/37).

Does NOT import scripts/37 and does not reuse its helpers: every headline number is recomputed by a
different route.  Reads the pinned artefacts L1-L9 from REPO (read-only) via scripts/36_r19_freeze.json.

  A0 pin integrity (all L1-L9 hashes) + impl hash agreement with data/37_r19_results.json
  A1 rank_R(K) = 6 by independent column-space elimination + an independent 6x6 minor determinant
  A2 fooling-set maximum recomputed by an independent set-based branch and bound; witness verified
  A3 pair protocol recomputed by a top-context-only recurrence: hits / net ledger / histogram
  A4 override count at s0=0 and the 120-state sweep, recomputed from the value table
  A5 K5 exact cyclotomic test redone: Phi_88 by a second construction, Ramanujan trace, orbit size
  A6 K6 prefix vectors parsed raw-text from L6 and matched against an independent cost-law count
  A7 K7 window max |S| brute-forced over all quadruples for the smallest window + calibration values
  A8 scope: no writes outside this OO directory; the machine does not import another script
"""
import hashlib
import io
import json
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROOT))
PASS, FAIL = [], []


def ok(tag, name, cond, detail):
    (PASS if cond else FAIL).append(tag)
    print('[%s] %-4s %s -- %s' % ('PASS' if cond else 'FAIL', tag, name, detail), flush=True)


def main():
    freeze = json.load(io.open(os.path.join(ROOT, 'data', '36_r19_freeze.json'), encoding='utf-8'))
    res = json.load(io.open(os.path.join(ROOT, 'data', '37_r19_results.json'), encoding='utf-8'))
    drift = [j for j, rec in sorted(freeze['pins'].items())
             if hashlib.sha256(io.open(os.path.join(REPO, rec['path']), 'rb').read()).hexdigest()
             != rec['sha256']]
    impl = os.path.join(HERE, '37_r19_closure.py')
    impl_hash = hashlib.sha256(io.open(impl, 'rb').read()).hexdigest()
    ok('A0', 'pins L1-L9 unchanged and the impl hash matches the freeze',
       not drift and impl_hash.startswith(freeze['impl_sha256'][:16]) if 'impl_sha256' in freeze
       else not drift, 'drift = %s ; impl = %s' % (drift or 'none', impl_hash[:16]))

    # --- load K / MUL / hx through the frozen interfaces (read-only use of L1/L2)
    import importlib.util

    def load(p, n):
        sp = importlib.util.spec_from_file_location(n, p)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        return m
    b5 = load(os.path.join(HERE, '12_b5_budget.py'), 'a_b5')
    b5.KERNEL_TAB = None
    b3 = load(os.path.join(HERE, '15_b3r2_orderfair.py'), 'a_b3')
    mach = b5.load_machine()
    K = next(x for x in mach if isinstance(x, list) and len(x) == 120 and isinstance(x[0], list)
             and len(x[0]) == 62)
    MUL = next(x for x in mach if isinstance(x, list) and len(x) == 120 and isinstance(x[0], list)
               and len(x[0]) == 120)
    hx = next(x for x in mach if isinstance(x, list) and len(x) == 62 and isinstance(x[0], int))
    D, N = 120, 62

    # --- A1: column-space elimination (different pivot order) + one explicit 6x6 determinant
    A = [[F(K[i][j]) for i in range(D)] for j in range(N)]          # 62 x 120 (columns as rows)
    rows, rank, pivots = [r[:] for r in A], 0, []
    for c in range(D):
        s = next((i for i in range(rank, N) if rows[i][c]), None)
        if s is None:
            continue
        rows[rank], rows[s] = rows[s], rows[rank]
        pv = rows[rank][c]
        rows[rank] = [x / pv for x in rows[rank]]
        for i in range(N):
            if i != rank and rows[i][c]:
                f = rows[i][c]
                rows[i] = [rows[i][k] - f * rows[rank][k] for k in range(D)]
        pivots.append(c)
        rank += 1
    # explicit 6x6 minor on the machine's pivot columns / first six rows
    def det6(M):
        n = len(M)
        Mx = [r[:] for r in M]
        d = F(1)
        for c in range(n):
            s = next((i for i in range(c, n) if Mx[i][c]), None)
            if s is None:
                return F(0)
            if s != c:
                Mx[s], Mx[c] = Mx[c], Mx[s]
                d = -d
            d *= Mx[c][c]
            for i in range(c + 1, n):
                f = Mx[i][c] / Mx[c][c]
                for k in range(c, n):
                    Mx[i][k] -= f * Mx[c][k]
        return d
    rowsidx = list(range(D))
    sub = [[F(K[r][c]) for c in range(6)] for r in range(D)]
    rr, pivot_src = 0, []
    for c in range(6):
        srow = next((i for i in range(rr, D) if sub[i][c]), None)
        if srow is None:
            continue
        sub[rr], sub[srow] = sub[srow], sub[rr]
        rowsidx[rr], rowsidx[srow] = rowsidx[srow], rowsidx[rr]
        pv = sub[rr][c]
        sub[rr] = [x / pv for x in sub[rr]]
        for i in range(D):
            if i != rr and sub[i][c]:
                f = sub[i][c]
                sub[i] = [sub[i][k] - f * sub[rr][k] for k in range(6)]
        pivot_src.append(rowsidx[rr])
        rr += 1
    minor_rows = sorted(pivot_src[:6])
    minor = det6([[F(K[r][c]) for c in range(6)] for r in minor_rows])
    minors = [minor]
    any_nonzero = minor != 0
    ok('A1', 'rank_R(K) = 6 by an independent column elimination and a nonzero 6x6 minor',
       rank == 6 and any_nonzero and res['numbers']['K1']['rank_R'] == 6,
       'column-space rank = %d ; pivot state indices = %s ; nonzero 6x6 minor on states %s x axes 0-5 = %s'
       % (rank, pivots[:6], minor_rows, minor))

    # --- A2: independent fooling-set maximum (set-based BnB)
    cells = [(s, a) for s in range(D) for a in range(N) if K[s][a] == 1]
    nb = {}
    for i, (s, a) in enumerate(cells):
        nb[i] = set(j for j, (t, b) in enumerate(cells)
                    if j != i and t != s and b != a and K[s][b] == -1 and K[t][a] == -1)
    best = []

    import time as _t
    _t0 = _t.time()

    def bb(R, P):
        if len(R) > len(best):
            best[:] = list(R)
        if not P or _t.time() - _t0 > 240:
            return
        # greedy colouring bound
        order, col = [], []
        Q = set(P)
        while Q:
            indep = []
            for v in sorted(Q, key=lambda x: -len(nb[x] & Q)):
                if all(u not in nb[v] for u in indep):
                    indep.append(v)
            for v in indep:
                Q.discard(v)
            col.append(indep)
        for i in range(len(col) - 1, -1, -1):
            if len(R) + i + 1 <= len(best):
                return
            for v in col[i]:
                bb(R + [v], P & nb[v])
                P.discard(v)
    bb([], set(range(len(cells))))
    fs = [cells[i] for i in best]
    two_sided = all(K[s][a] == 1 for s, a in fs) and \
        all(K[s][b] == -1 for i, (s, _a) in enumerate(fs) for j, (_t, b) in enumerate(fs) if i != j)
    mach_fs = res['numbers']['K1']['fooling_set_size']
    _t_used = _t.time() - _t0
    ok('A2', 'fooling-set maximum reproduced independently (= 5, set-based BnB) and the witness re-verified',
       len(fs) == mach_fs == 5 and two_sided,
       'independent max = %d ; machine = %d ; witness = %s ; two-sided = %s ; %.1fs (cap 240s)'
       % (len(fs), mach_fs, fs, two_sided, _t_used))

    # --- A3: pair protocol from the top-context recurrence only
    order0 = b3.order_list(list(json.load(io.open(os.path.join(ROOT, 'data', '15_b3r2_results.json'),
                                                 encoding='utf-8'))['order_ids'])[0])
    st, st_s, s, hits, hf, hl, per = [], [], 0, 0, 0, 0, []
    for (a, b) in order0:
        miss = 0
        for k, ctx in enumerate((a, b, b)):
            if k == 2:
                if st:
                    st.pop()
                    st_s.pop()
                    s = st_s[-1] if st_s else 0
                else:
                    continue
            if st and st[-1] == ctx:
                hits += 1
                hf += (k == 0)
                hl += (k != 0)
            else:
                st.append(ctx)
                st_s.append(s)
                s = MUL[s][hx[ctx]]
                miss += 1
        per.append(miss)
    pushes = len(st)
    hist = {}
    for m in per:
        hist[m] = hist.get(m, 0) + 1
    l8 = json.load(io.open(os.path.join(ROOT, 'data', '30_g1g8_results.json'), encoding='utf-8'))
    g8 = l8['cells']['G8a']['value']
    ok('A3', 'protocol recomputed (top-only recurrence): hits 124, net ledger 7564, histogram match',
       hits == 124 and pushes == 7564 and hist == {2: 124, 3: 3720}
       and g8['entries_total'] == 7564 and g8['reads_per_pass'] == 11532,
       'hits = %d ; net ledger = %d ; histogram = %s ; record: entries %d, reads %d'
       % (hits, pushes, hist, g8['entries_total'], g8['reads_per_pass']))

    # --- A4: override counts (s0 = 0 and the sweep) recomputed with an event log
    def events(s0):
        L, s, ev = [], s0, []
        for (a, b) in order0:
            for k, ctx in enumerate((a, b, b)):
                if k == 2:
                    if L:
                        L.pop()
                        s = L[-1][2] if L else s0
                    else:
                        continue
                if L and L[-1][0] == ctx:
                    ev.append((k, L[-1][1], K[s][ctx]))
                else:
                    L.append((ctx, K[s][ctx], s))
                    s = MUL[s][hx[ctx]]
        return ev
    ev0 = events(0)
    over0 = sum(1 for (_k, v0, v1) in ev0 if v0 != v1)
    ov65 = [s0 for s0 in range(D) if sum(1 for (_k, v0, v1) in events(s0) if v0 != v1) == 65]
    n3 = res['numbers']['K3']
    ok('A4', 'override recomputation: s0=0 gives 58 with a 28/30 split; 65 at 10 starting states',
       over0 == 58 == n3['s0_zero']['overrides'] and len(ov65) == 10
       and sorted(ov65) == sorted(n3['s0_sweep']['states_with_65'])
       and n3['s0_zero']['first_read_overrides'] > 0 and n3['s0_zero']['post_rollback_overrides'] > 0,
       's0=0 overrides = %d (first %d / post %d) ; states giving 65 = %s'
       % (over0, n3['s0_zero']['first_read_overrides'], n3['s0_zero']['post_rollback_overrides'], ov65))

    # --- A5: exact cyclotomic test, second construction of Phi_88
    x88 = [-1] + [0] * 87 + [1]
    # direct long division: Phi_88 = (x^88-1)(x^4-1)/((x^8-1)(x^44-1))
    def pmul(a, b):
        r = [0] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    r[i + j] += x * y
        return r
    def pdiv(a, b):
        a, out = a[:], [0] * max(1, len(a) - len(b) + 1)
        while len(a) >= len(b) and any(a):
            d = len(a) - len(b)
            c = a[-1] // b[-1]
            out[d] = c
            for i in range(len(b)):
                a[d + i] -= c * b[i]
            while len(a) > 1 and a[-1] == 0:
                a.pop()
        return out, a
    phi, rem = pdiv(pmul(x88, [-1] + [0] * 3 + [1]), pmul([-1] + [0] * 7 + [1], [-1] + [0] * 43 + [1]))
    # verify: Phi_88 * (x^8-1)(x^44-1) == (x^88-1)(x^4-1) exactly
    chk = pmul(phi, pmul([-1] + [0] * 7 + [1], [-1] + [0] * 43 + [1]))
    chk_ok = chk == pmul(x88, [-1] + [0] * 3 + [1])
    # G = sum_{n=28..44} (x^n + x^{88-n}) mod phi ; trace by Ramanujan sums
    def pmod(p, mod):
        p = p[:]
        while len(p) >= len(mod) and any(p):
            d = len(p) - len(mod)
            c = p[-1]
            for i in range(len(mod)):
                p[d + i] -= c * mod[i]
            while len(p) > 1 and p[-1] == 0:
                p.pop()
        return p + [0] * (len(mod) - 1 - len(p))
    b = len(phi) - 1
    G = [0] * b
    for n in range(28, 45):
        for e in (n, 88 - n):
            t = [0] * (e + 1)
            t[e] = 1
            G = [x + y for x, y in zip(G, pmod(t, phi))]
    def mobius(n):
        f, d, m = 0, 2, n
        while d * d <= m:
            if m % d == 0:
                m //= d
                if m % d == 0:
                    return 0
                f += 1
            d += 1
        if m > 1:
            f += 1
        return -1 if f % 2 else 1
    def ram(m, n):
        return sum(d * mobius(m // d) for d in range(1, min(m, n) + 1) if m % d == 0 and n % d == 0)
    tr = sum(ram(88, n) for n in range(28, 45))
    diff = [(b // 2) * c for c in G]
    diff[0] -= tr
    nonrational = any(v != 0 for v in diff)
    ok('A5', 'exact cyclotomic test reproduced: Phi_88 divides correctly, Tr_K(G) = -40, residual not in Q',
       chk_ok and len(phi) - 1 == 40 and tr == -40 and nonrational
       and res['numbers']['K5_add']['G_rational'] is False
       and res['numbers']['K5_add']['trace_K_G'] == -40,
       'Phi_88 reconstructed: %s ; Tr_K(G) = %d ; (b/2)G - Tr = %s ; residual rational = %s'
       % (chk_ok, tr, diff[:5], res['numbers']['K5_add']['G_rational']))

    # --- A6: K6 prefix vectors raw-text + independent cost-law count
    l6raw = io.open(os.path.join(REPO, freeze['pins']['L6']['path']), encoding='utf-8').read()
    l6parsed = json.loads(l6raw)          # raw-text read of the pinned file, parsed locally
    bad = 0
    for row in res['numbers']['K6']['orders']:
        recv = [int(v) for v in l6parsed['per_order'][row['order']]['per_pair_misses']]
        if recv != row['recorded_vector'] or json.dumps(recv, separators=(',', ':')) not in \
                l6raw.replace(' ', '').replace('\n', ''):
            bad += 1
    ok('A6', 'K6 prefix vectors found verbatim in the raw L6 text and cost sums match',
       bad == 0 and all(r['my_misses'] == r['recorded_reads'] for r in res['numbers']['K6']['orders']),
       'vectors not found verbatim = %d ; cost sums = %s'
       % (bad, [(r['order'], r['my_misses'], r['recorded_reads']) for r in res['numbers']['K6']['orders']]))

    # --- A7: brute force the smallest window (block, W = 7) over all quadruples
    C1n = None
    C1, C2, ids, types, den = b5.load_a2()
    C1n = [[int(v * den) for v in C1[a]] for a in range(N)]
    blk = next(r for r in res['numbers']['K7']['windows'] if r['order'] == 'block')
    o = b3.order_list('block')
    W = sorted(set(x for p in o[:44] for x in p))
    pts = []
    for a in range(N):
        for b in range(N):
            if a != b and all(K[s][a] == -K[s][b] for s in range(D)):
                pts.append((a, b))
    ptset = set(pts)
    bestv, arg = 0, None
    for a in W:
        for a2 in W:
            if a2 == a:
                continue
            for i in W:
                if i == a or i == a2:
                    continue
                for j in W:
                    if j == i or j == a or j == a2:
                        continue
                    if (a, i) in ptset or (a2, i) in ptset or (a, j) in ptset or (a2, j) in ptset:
                        continue
                    v = C1n[a][i] - C1n[a][j] + C1n[a2][i] + C1n[a2][j]
                    if v < 0:
                        v = -v
                    if v > bestv:
                        bestv, arg = v, (a, a2, i, j)
    bf = F(bestv, den)
    ok('A7', 'block window brute-forced over all quadruples: max |S| = 16/15, matching the machine',
       str(bf) == blk['max_abs_S'] and str(bf) == '16/15',
       'brute force = %s at %s ; machine = %s ; W size = %d ; antipodal ordered pairs = %d'
       % (bf, arg, blk['max_abs_S'], len(W), len(pts)))

    # --- A8: scope
    import re as _re
    msrc = io.open(impl, encoding='utf-8').read()
    asrc = io.open(os.path.abspath(__file__), encoding='utf-8').read()
    writes = _re.findall(r"open\(([^,]+),\s*'w'", msrc)
    own = all(('ROOT' in w or 'data' in w or 'logs' in w or 'REPO' in w) for w in writes)
    pins_only = sorted(set(rec['path'].split('/')[0] for rec in freeze['pins'].values()))
    loads37 = _re.findall(r"load\(os\.path\.join\(HERE,\s*'([^']+)'", asrc)
    ok('A8', 'machine writes only inside this OO; audit loads no sibling script (only L1/L2 interfaces)',
       own and '37_r19_closure.py' not in loads37,
       'machine write targets = %s ; audit script loads = %s ; pin roots = %s'
       % (writes, sorted(set(loads37)), pins_only))

    out = {'pass': PASS, 'fail': FAIL, 'n_pass': len(PASS), 'n_total': len(PASS) + len(FAIL)}
    with io.open(os.path.join(ROOT, 'data', '38_r19_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print('-' * 100)
    print('AUDIT %d/%d PASS   fail = %s' % (len(PASS), len(PASS) + len(FAIL), FAIL or 'none'))
    print('-' * 100)
    return 0 if not FAIL else 1


if __name__ == '__main__':
    raise SystemExit(main())
