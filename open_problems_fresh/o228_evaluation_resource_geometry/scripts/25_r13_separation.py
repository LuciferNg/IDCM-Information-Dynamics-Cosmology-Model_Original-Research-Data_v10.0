#!/usr/bin/env python3
"""O228 scripts/25 -- R13: certificate completion (persist x/y) + census-informed separation test.

Contract: docs/22_r13_contract.md   (o228-r13-separation-and-certificate-v1)

Part 1  persist the root-LP certificates for the six machines (x over columns, y over row pairs) and
        re-verify BOTH sides by hand (closes closeout finding docs/21 sec 5.1).
Part 2  M := min sum_C mu_C  s.t.  sum_{C ni a} mu_C >= 1  for every support column a of the root LP,
        summed over the 8584 minimal 7-frames of M_edge (R11 census, re-enumerated here).
        The dual solution c (10 coefficients) IS the non-negative coefficient separating cut
        sum_{a in S} c_a x_a >= 1 ; its violation at x* = 1/2 * 1_S is M/2 - 1.

Solver reuse: scripts/10 (exact rational simplex, verified in R6 and re-verified here by certificate).
Read-only w.r.t. every other artifact.  Exact Fractions only, no thresholds, no new parameters.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/25_r13_separation.py
"""
import collections
import hashlib
import importlib.util
import itertools
import json
import math
import os
import random
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
O222 = os.path.abspath(os.path.join(ROOT, '..', 'o222_qm_evaluation_semantics'))
OUT = os.path.join(DATA, '25_r13_separation.json')
WALL_FRAMES = float(os.environ.get('WALL_FRAMES', '240'))
T0 = time.time()
CLAIMS = []
RES = {'o': 'O228', 'script': '25_r13_separation.py', 'contract': 'o228-r13-separation-and-certificate-v1',
       'started': time.strftime('%Y-%m-%d %H:%M:%S')}


def claim(tag, name, ok, detail='', na=False):
    st = 'N/A' if na else ('PASS' if ok else 'FAIL')
    CLAIMS.append({'tag': tag, 'name': name, 'ok': None if na else bool(ok), 'status': st, 'detail': detail})
    print('[%s] %-5s %s%s' % (st, tag, name, ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


def load(path, name):
    spc = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spc)
    spc.loader.exec_module(mod)
    return mod


S10 = load(os.path.join(HERE, '10_r6_lp_certificate.py'), 's10')
spc = importlib.util.spec_from_file_location('mX', os.path.join(O222, 'scripts', '12_b5_budget.py'))
mX = importlib.util.module_from_spec(spc)
spc.loader.exec_module(mX)
m, K, MUL, hx, ids, types = mX.load_machine()
axes, U, ids_u, types_u, hvec = m.load_inputs()
Gf, idx, MULg = m.build_group()


class Mch(object):
    def __init__(self, name, rows, cols):
        self.name = name
        self.rows = rows
        self.cols = cols
        self.m = len(rows)
        self.N = len(cols)
        self.pairs = [(i, j) for i in range(self.m) for j in range(i + 1, self.m)]


def icosa(u0_id, name):
    u0 = U[ids_u.index(u0_id)]
    rows, seen = [], set()
    for q in Gf:
        r = m.rot_ref(q, u0)
        key = tuple((x[0], x[1]) for x in r)
        if key not in seen:
            seen.add(key)
            rows.append(r)
    cols = []
    for a in range(len(U)):
        col = []
        for r in rows:
            d = m.add(m.add(m.mul(U[a][0], r[0]), m.mul(U[a][1], r[1])), m.mul(U[a][2], r[2]))
            s = m.sgn(d)
            if s == 0:
                for comp in r:
                    sc = m.sgn(comp)
                    if sc:
                        s = sc
                        break
            col.append(s)
        cols.append(tuple(col))
    return Mch(name, rows, cols)


# ---- integer machines T / O / D4 (own reconstruction, plain integer arithmetic)
def i_dot(u, r):
    return u[0] * r[0] + u[1] * r[1] + u[2] * r[2]


def i_sgn_tie(u, r):
    s = i_dot(u, r)
    if s:
        return 1 if s > 0 else -1
    for c in r:
        if c:
            return 1 if c > 0 else -1
    raise ValueError('zero row')


def m3(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def mv(M, v):
    return tuple(sum(M[i][j] * v[j] for j in range(3)) for i in range(3))


def mdet(M):
    return (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
            - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
            + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))


def morder(M):
    I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    P, o = M, 1
    while P != I and o < 25:
        P = m3(P, M)
        o += 1
    return o


def canon(v):
    g = 0
    for x in v:
        g = math.gcd(g, abs(x))
    if g == 0:
        return None
    v = tuple(x // g for x in v)
    for x in v:
        if x:
            return tuple(-y for y in v) if x < 0 else v
    return None


def axis_of(M):
    A = [[M[i][j] - (1 if i == j else 0) for j in range(3)] for i in range(3)]
    for i, j in ((0, 1), (0, 2), (1, 2)):
        c = (A[i][1] * A[j][2] - A[i][2] * A[j][1], A[i][2] * A[j][0] - A[i][0] * A[j][2],
             A[i][0] * A[j][1] - A[i][1] * A[j][0])
        if c != (0, 0, 0):
            return canon(c)
    return None


def smats():
    out = []
    for p in itertools.permutations(range(3)):
        for s in itertools.product((1, -1), repeat=3):
            M = [[0, 0, 0] for _ in range(3)]
            for i in range(3):
                M[i][p[i]] = s[i]
            if mdet(M) == 1:
                out.append(M)
    return out


def closure(gens):
    key = lambda M: tuple(tuple(r) for r in M)
    out, S, stack = [], set(), []
    for g in gens:
        out.append(g)
        S.add(key(g))
        stack.append(g)
    while stack:
        A = stack.pop()
        for B in out[:] + list(gens):
            C = m3(A, B)
            if key(C) not in S:
                S.add(key(C))
                out.append(C)
                stack.append(C)
    return out


def axes_of(grp, orders):
    s = set()
    for M in grp:
        if morder(M) in orders:
            a = axis_of(M)
            if a:
                s.add(a)
    return sorted(s)


def int_machine(name, grp, u0, ax):
    rows, seen = [], set()
    for M in grp:
        r = mv(M, u0)
        if r not in seen:
            seen.add(r)
            rows.append(r)
    cols = []
    for u in ax:
        for uu in (u, tuple(-x for x in u)):
            cols.append(tuple(i_sgn_tie(uu, r) for r in rows))
    return Mch(name, rows, cols)


V4 = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
SM = smats()
vs4 = sorted(V4)
Tgrp = [X for X in SM if sorted(mv(X, v) for v in V4) == vs4]
D4grp = closure([[[0, -1, 0], [1, 0, 0], [0, 0, 1]], [[1, 0, 0], [0, -1, 0], [0, 0, -1]]])
MACH = [icosa('V00', 'M_2I'), icosa('F00', 'M_face'), icosa('E00', 'M_edge'),
        int_machine('M_T', Tgrp, (1, 1, 1), axes_of(Tgrp, {2, 3})),
        int_machine('M_O', SM, (1, 0, 0), axes_of(SM, {2, 3, 4})),
        int_machine('M_D4', D4grp, (0, 0, 1), axes_of(D4grp, {2, 4}))]
claim('R13-0', 'machines rebuilt: shapes match the record (12/20/30/4/6/2 rows, N=62/62/62/14/26/10)',
      [(x.m, x.N) for x in MACH] == [(12, 62), (20, 62), (30, 62), (4, 14), (6, 26), (2, 10)],
      '%s' % [(x.m, x.N) for x in MACH])

# ---------------------------------------------------------- part 1: certificates persisted + re-verified
cert_out = {}
LP = {}
for mm in MACH:
    A, cm = S10.sep_matrix(mm)
    npairs = len(mm.pairs)
    res = S10.solve_packing_lp(A, npairs, mm.N)
    LP[mm.name] = res['opt']
    ok_own = {}
    if res.get('opt') is not None:
        x = res['x']
        y = res['y']
        pr_nonneg = all(v >= 0 for v in x) and all(v >= 0 for v in y)
        pr_cover = all(sum(x[a] for a in A[p]) >= 1 for p in range(npairs))
        du_pack = all(sum(y[p] for p in range(npairs) if a in A[p]) <= 1 for a in range(mm.N))
        eq = sum(x) == sum(y) == res['opt']
        ok_own = {'primal_nonneg': pr_nonneg, 'primal_covers': pr_cover, 'dual_nonneg': pr_nonneg,
                  'dual_packs': du_pack, 'sums_equal_objective': eq}
        cert_out[mm.name] = {
            'status': res['status'], 'pivots': res['pivots'], 'LP': str(res['opt']),
            'support': [a for a in range(mm.N) if x[a] > 0],
            'x': [str(v) for v in x], 'y': [str(v) for v in y],
            'sum_x': str(sum(x)), 'sum_y': str(sum(y)), 'n_pairs': npairs, 'n_cols': mm.N,
            'own_reverify': ok_own,
            'solver_flags': S10.verify_certificate(A, npairs, mm.N, res)}
    print('  %-7s LP* = %-8s pivots=%-4s  own-reverify=%s' % (mm.name, LP[mm.name], res['pivots'], ok_own), flush=True)

e = cert_out['M_edge']
claim('P12-1', 'certificates persisted for all six machines: x over columns + y over pairs, |x|=N, |y|=pairs',
      all(len(cert_out[k]['x']) == mm.N and len(cert_out[k]['y']) == len(mm.pairs)
          for k, mm in [(x.name, x) for x in MACH]),
      'M_edge: |x|=%d |y|=%d sum_x=%s sum_y=%s' % (len(e['x']), len(e['y']), e['sum_x'], e['sum_y']))
claim('P12-2', 'independent dual/complementary-side re-verification of the persisted vectors (all six)',
      all(all(v for v in cert_out[k]['own_reverify'].values()) for k in cert_out),
      'M_edge dual_packs=%s sum_y=%s' % (cert_out['M_edge']['own_reverify']['dual_packs'], e['sum_y']))
claim('P12-2b', 'M_edge LP* = 5 reproduced by this round (both certificate sides)',
      str(LP['M_edge']) == '5' and e['sum_x'] == '5' and e['sum_y'] == '5', 'LP*=%s' % LP['M_edge'])

# ---------------------------------------------------------- part 2: 8584 minimal 7-frames (own DFS)
mm = [x for x in MACH if x.name == 'M_edge'][0]
Ae, cme = S10.sep_matrix(mm)
ALLP = (1 << len(mm.pairs)) - 1
SUF = [0] * (mm.N + 1)
for a in range(mm.N - 1, -1, -1):
    SUF[a] = SUF[a + 1] | cme[a]
CACHE = os.path.join(DATA, '25_r13_frames.json')
nodes = [0]
frames = []
st = {'abort': False}
if os.path.exists(CACHE):
    cf = json.load(open(CACHE))
    if cf.get('n') == 8584 and len(cf.get('frames', [])) == 8584:
        frames = [tuple(x) for x in cf['frames']]
        st['abort'] = 'cached'
t0 = time.time()


def rec(i, chosen, cov):
    nodes[0] += 1
    if nodes[0] % 500000 == 0 and time.time() - t0 > WALL_FRAMES:
        st['abort'] = True
    if len(chosen) == 7:
        if cov == ALLP:
            frames.append(tuple(chosen))
        return
    if mm.N - i < 7 - len(chosen) or (cov | SUF[i]) != ALLP:
        return
    chosen.append(i)
    if not st['abort']:
        rec(i + 1, chosen, cov | cme[i])
    chosen.pop()
    if not st['abort']:
        rec(i + 1, chosen, cov)


if st['abort'] != 'cached':
    rec(0, [], 0)
    json.dump({'n': len(frames), 'frames': [list(x) for x in frames]}, open(CACHE, 'w'))
print('  census: frames=%d nodes=%d abort=%s %.1fs' % (len(frames), nodes[0], st['abort'], time.time() - t0), flush=True)
claim('R13-1', '8584 minimal 7-frames available (own DFS re-enumeration, cached copy declared)',
      len(frames) == 8584 and (st['abort'] in (False, 'cached')), 'frames=%d nodes=%d abort=%s' % (len(frames), nodes[0], st['abort']))

S = e['support']
idx = {a: i for i, a in enumerate(S)}
# M = min sum_C mu_C  s.t.  sum_{C ni a} mu_C >= 1 (a in S)  <=>  max sum_a y_a  s.t.  sum_{a in C∩S} y_a <= 1 (all C)
# The 10-variable dual is solved by an exact cutting-plane loop (tableau stays ~10 x (|subset|+10)); the
# separation oracle scans ALL 8584 frames, so at termination y is certified optimal for the FULL dual and
# the returned mu is a feasible primal of the same objective -> M is exact with BOTH sides certified.
subset = []
for a in S:
    for fr in frames:
        if a in fr:
            subset.append(fr)
            break
it = 0
hist = []
res2 = None
while True:
    it += 1
    A2 = [[] for _ in range(len(S))]
    for j, fr in enumerate(subset):
        for a in fr:
            if a in idx:
                A2[idx[a]].append(j)
    res2 = S10.solve_packing_lp(A2, len(S), len(subset))
    if res2.get('opt') is None:
        break
    y = res2['y']
    viol = []
    for fr in frames:
        val = sum(y[idx[a]] for a in fr if a in idx)
        if val > 1:
            viol.append((val, fr))
    hist.append({'iter': it, 'subset': len(subset), 'LP': str(res2['opt']), 'violations': len(viol)})
    if not viol or it >= 200:
        break
    viol.sort(key=lambda t: -t[0])
    for _, fr in viol[:5]:
        subset.append(fr)
M = res2.get('opt') if res2 else None
c = res2['y'] if res2 and res2.get('opt') is not None else None
mu = res2['x'] if res2 and res2.get('opt') is not None else None
print('  M = %s (cut-gen iters %d, subset %d, violations %s)' % (M, it, len(subset), hist[-1]['violations'] if hist else '-'), flush=True)
claim('P12-3', 'BLIND: M <= 2 (census-informed non-negative coefficient cut family also dies)',
      M is not None and M <= 2, 'M = %s ; violation at x* = M/2 - 1 = %s' % (M, (M / 2 - 1)))
cnonneg = all(v >= 0 for v in c)
valid = all(sum(c[idx[a]] for a in fr if a in idx) >= 1 for fr in frames)
claim('P12-4', 'cut c >= 0 and satisfies sum_{a in C ∩ S} c_a >= 1 for ALL 8584 frames', cnonneg and valid,
      'c = %s' % [str(v) for v in c])
claim('P12-4c', 'CORRECTED (P12-4-c): c >= 0 and sum_{a in C∩S} c_a <= 1 for ALL 8584 frames, with '
      'sum_a c_a x*_a = M/2 = 9/10 < 1 -> Farkas certificate that NO non-negative coefficient cut exists',
      all(v >= 0 for v in c) and all(sum(c[idx[a]] for a in fr if a in idx) <= 1 for fr in frames)
      and sum(c[idx[a]] * F(1, 2) for a in S) == M / 2 and M / 2 < 1,
      'max_C sum = %s ; sum c x* = %s' % (max(sum(c[idx[a]] for a in fr if a in idx) for fr in frames), sum(c[idx[a]] * F(1, 2) for a in S)))
cutok = False
if M is not None and M > 2:
    # the cut adds one row whose coefficient of column a is c_a (Fractions supported by the solver)
    A4 = [list(row) for row in Ae]
    A4.append([c[idx[a]] if a in idx else F(0) for a in range(mm.N)])
    res4 = S10.solve_packing_lp(A4, len(A4), mm.N)
    newopt = res4['opt']
    print('  cut-augmented LP = %s (was %s)' % (newopt, LP['M_edge']), flush=True)
    cutok = newopt is not None and newopt > F(5)
    claim('P12-5', 'M > 2 -> cut-augmented LP strictly above 5 (ladder rises)', cutok, 'new LP = %s' % newopt)
else:
    claim('P12-5', 'M > 2 -> ladder rises (conditional)', False, 'M = %s <= 2 : family dies, ladder stays at 5' % M, na=True)

# ---------------------------------------------------------- auxiliary: 8-cover validity probe (10^5 + hill-climb)
random.seed(20261002)


def coverage(C):
    cov = 0
    for a in C:
        cov |= cme[a]
    return cov


def minscore(C):
    return sum(1 for a in C if coverage([b for b in C if b != a]) == ALLP)


bad = 0
tested = 0
maxsum = F(0)
for _ in range(100000):
    fr = frames[random.randrange(len(frames))]
    extra = random.randrange(mm.N)
    C = list(fr) + ([extra] if extra not in fr else [])
    if len(C) != 8 or coverage(C) != ALLP:
        continue
    tested += 1
    s = sum(c[idx[a]] for a in C if a in idx)
    if s > maxsum:
        maxsum = s
    if s > 1:
        bad += 1
best = 8
wit = set()
t1 = time.time()
while time.time() - t1 < 20.0:
    fr = list(frames[random.randrange(len(frames))])
    extra = next((x for x in range(mm.N) if x not in fr), None)
    C = fr + [extra]
    if coverage(C) != ALLP:
        continue
    sc = minscore(C)
    for _ in range(60):
        i = random.randrange(8)
        b = random.randrange(mm.N)
        if b in C:
            continue
        C2 = [C[j] for j in range(8) if j != i] + [b]
        if coverage(C2) != ALLP:
            continue
        s2 = minscore(C2)
        if s2 < sc or (s2 == sc and random.random() < 0.3):
            C, sc = C2, s2
    if sc < best:
        best = sc
    if sc == 0:
        wit.add(tuple(sorted(C)))
claim('R13-2', 'probe of covers OUTSIDE the frame family: certificate bound holds on every sampled 8-cover '
      'and no inclusion-minimal 8-cover exists',
      bad == 0 and best >= 1 and maxsum <= 1,
      'sampled 8-covers=%d bound-violations=%d max sum_C c=%s ; best minimality score=%d (0 = inclusion-minimal 8-cover)'
      % (tested, bad, maxsum, best))
# ---- corrected twin: the finding is real and it STRENGTHENS the negative conclusion
wver = []
for W in sorted(wit)[:5]:
    covok = coverage(list(W)) == ALLP
    minok = all(coverage([b for b in W if b != a]) != ALLP for a in W)
    wver.append({'witness': list(W), 'size': len(W), 'covers': covok, 'inclusion_minimal': minok,
                 'cut_sum': str(sum(c[idx[a]] for a in W if a in idx))})
claim('R13-2c', 'CORRECTED (R13-2-c): inclusion-minimal covers outside the 8584 size-7 family EXIST '
      '(witness verified exactly: covers all 435 pairs AND every (n-1)-subset fails)',
      bool(wit) and all(v['covers'] and v['inclusion_minimal'] for v in wver),
      'witnesses found=%d ; first=%s' % (len(wit), wver[0]['witness'] if wver else None))
# ---- robustness: re-solve the packing dual with the witnesses ADDED as constraints (adding covers can only lower M)
sub2 = list(subset) + [W for W in sorted(wit)[:5]]
ALLCHK = list(frames) + [tuple(sorted(W)) for W in sorted(wit)[:5]]
it2 = 0
resw = None
while True:
    it2 += 1
    A5 = [[] for _ in range(len(S))]
    for j, fr in enumerate(sub2):
        for a in fr:
            if a in idx:
                A5[idx[a]].append(j)
    resw = S10.solve_packing_lp(A5, len(S), len(sub2))
    if resw.get('opt') is None:
        break
    y2 = resw['y']
    v2 = [fr for fr in ALLCHK if sum(y2[idx[a]] for a in fr if a in idx) > 1]
    if not v2 or it2 >= 200:
        break
    sub2.extend(v2[:5])
Mw = resw.get('opt') if resw else None
claim('P12-6', 'robustness: with the extra inclusion-minimal covers added as constraints, M_w <= M and still < 2 '
      '(the frame family is a RELAXATION, so the non-separation conclusion survives a fortiori)',
      Mw is not None and Mw <= M and Mw < 2, 'M_w = %s <= M = %s < 2 ; subset %d -> %d' % (Mw, M, len(subset), len(sub2)))
RES['witness_covers'] = {'n_found': len(wit), 'verified': wver,
                         'M_with_witnesses': str(Mw) if Mw is not None else None,
                         'cutgen_iters': it2, 'constraints': len(sub2)}

RES['machines'] = {k: {kk: vv for kk, vv in v.items()} for k, v in cert_out.items()}
RES['M'] = str(M) if M is not None else None
RES['M_cutgen'] = {'iterations': it, 'subset_size': len(subset), 'history': hist,
                   'mu_sum': str(sum(mu)) if mu else None,
                   'optimality': 'y feasible for ALL 8584 frames at termination (full separation scan)'}
RES['cut_c'] = [str(v) for v in c]
RES['S'] = S
RES['frames'] = {'n': len(frames), 'nodes': nodes[0], 'abort': st['abort']}
RES['aux8'] = {'sampled': tested, 'violations': bad, 'max_sum_c_on_sampled_8covers': str(maxsum),
               'best_minimality_score': best, 'normalisation':
               'score = number of columns whose removal still covers (0 = inclusion-minimal 8-cover)'}
RES['claims'] = CLAIMS
npass = sum(1 for x in CLAIMS if x['status'] == 'PASS')
njudged = sum(1 for x in CLAIMS if x['status'] != 'N/A')
RES['verdict'] = '%d/%d PASS (+%d N/A)' % (npass, njudged, len(CLAIMS) - njudged)
RES['elapsed_s'] = round(time.time() - T0, 1)
def js(o):
    if isinstance(o, F):
        return str(o)
    if isinstance(o, dict):
        return {k: js(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [js(v) for v in o]
    return o


json.dump(js(RES), open(OUT, 'w'), indent=1, ensure_ascii=False)
print('RESULT: %s  (%.1fs)' % (RES['verdict'], RES['elapsed_s']))
for x in CLAIMS:
    if x['status'] == 'FAIL':
        print('  FAIL %s %s' % (x['tag'], x['name']))
sys.exit(0 if npass == njudged else 1)
