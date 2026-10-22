#!/usr/bin/env python3
"""O228 scripts/24 -- CLOSEOUT AUDIT (independent, read-only w.r.t. every other artifact).

Sections
  A frozen      : the 4 o222 frozen inputs (sha256 vs the R1 literals) + o222 window write scan
  B k_props     : K properties recomputed from scratch (shape / values / distinct cols / rank_Q)
  C edge        : M_edge rebuilt from the frozen o222 arithmetic; F_6, F_7 counted by an
                  INDEPENDENT DFS (suffix-union pruning); explicit 7-cover re-verified; LP primal
                  certificate re-verified; R12 support redundancy re-verified
  D machines    : M_2I / M_face / M_T / M_O / M_D4 counted independently, compared with data/04
  E r11         : per-column degrees / inclusion-minimality / pairwise mutual exclusion from the
                  INDEPENDENTLY counted frame list (complete only if the F_7 count finished)
  F manifest    : disk <-> MANIFEST.json both-sided (audit's own outputs excluded on BOTH sides)
  G register    : O228 events per pid, ref existence, R1..R12 verdict coverage (bidirectional)
  H hygiene     : /tmp write patterns in our scripts; o222 write scan; scratch files in workspace
  I docs        : contract<->results pairing; headline-number coverage in docs

Nothing here writes outside this O directory.  Exact arithmetic only; no random.
"""
import collections, hashlib, importlib.util, itertools, json, math, os, subprocess, sys, time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
DOCS = os.path.join(ROOT, 'docs')
LOGS = os.path.join(ROOT, 'logs')
REPO = os.path.abspath(os.path.join(ROOT, '..', '..'))
O222 = os.path.abspath(os.path.join(ROOT, '..', 'o222_qm_evaluation_semantics'))
OUT = os.path.join(DATA, '24_closeout_audit.json')
WALL = float(os.environ.get('WALL', '420'))
T0 = time.time()
RES = {'o': 'O228', 'script': '24_closeout_audit.py', 'started': time.strftime('%Y-%m-%d %H:%M:%S'),
       'claims': [], 'sections': {}}


def claim(tag, name, ok, detail=''):
    RES['claims'].append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


def save():
    json.dump(RES, open(OUT, 'w'), indent=1, ensure_ascii=False)
    return 0


def sec(name, **kw):
    RES['sections'][name] = kw
    kw['seconds'] = round(time.time() - T0, 1)
    save()


# ------------------------------------------------------------------ A frozen
EXPECT = {
    'scripts/12_b5_budget.py': 'f2cb54fa5df094a1e2f7b4910a4c16726a37160f39b194f0157988823aeb1e7a',
    'scripts/09_a2_rollback.py': 'd8037bb16f690a2935c7028b3680d48df6540e01c938ade1d3b5858aed594ace',
    'data/04_b2_settings.json': '2357006c68e0165dc9fd7d8d73524593a776e1bf6a8b62ddbc8dc2c1a8af20ee',
    'data/08_a2_h_table.json': 'adeaf8a7fb5495ea57be194c1a704c973a9208026cdd10ef615cd59c58005b66',
}
got = {}
for rel, h in EXPECT.items():
    p = os.path.join(O222, rel)
    got[rel] = hashlib.sha256(open(p, 'rb').read()).hexdigest()
ok = all(got[k] == EXPECT[k] for k in EXPECT)
claim('A1', 'o222 four frozen inputs: sha256 identical to the R1 literals', ok,
      '%d/%d match' % (sum(got[k] == EXPECT[k] for k in EXPECT), len(EXPECT)))
scan = subprocess.run(['bash', '-lc', "find %s -type f -newermt '2026-10-02 00:00' | wc -l" % O222],
                      capture_output=True, text=True).stdout.strip()
claim('A2', 'o222 untouched today (find -newermt count)', scan == '0', 'count=%s' % scan)
sec('frozen', sha256=got, o222_writes_today=scan)

# ------------------------------------------------------------------ load frozen machinery (INPUT)
spc = importlib.util.spec_from_file_location('mX', os.path.join(O222, 'scripts', '12_b5_budget.py'))
mX = importlib.util.module_from_spec(spc)
spc.loader.exec_module(mX)
m, K, MUL, hx, ids, types = mX.load_machine()
axes, U, ids_u, types_u, hvec = m.load_inputs()
Gf, idx, MULg = m.build_group()


def rot_rows(u0_index):
    rows, seen = [], set()
    for q in Gf:
        r = m.rot_ref(q, U[u0_index])
        key = tuple((x[0], x[1]) for x in r)
        if key not in seen:
            seen.add(key)
            rows.append(r)
    return rows


def col_vec(u, rows):
    out = []
    for r in rows:
        d = m.add(m.add(m.mul(u[0], r[0]), m.mul(u[1], r[1])), m.mul(u[2], r[2]))
        s = m.sgn(d)
        if s == 0:
            for comp in r:
                sc = m.sgn(comp)
                if sc:
                    s = sc
                    break
        out.append(s)
    return out


def build_icosa(u0_id, name):
    rows = rot_rows(ids_u.index(u0_id))
    cols = [col_vec(U[a], rows) for a in range(len(U))]
    return name, rows, cols


def build_from(rows, axes_list, name, plusminus=True):
    cols = []
    for ax in axes_list:
        cols.append(col_vec(ax, rows))
        if plusminus:
            cols.append(col_vec(tuple(-x for x in ax), rows))
    return name, rows, cols


def masks_of(cols, mrows):
    ncol = len(cols)
    pairs = [(i, j) for i in range(mrows) for j in range(i + 1, mrows)]
    mk = []
    for a in range(ncol):
        v = 0
        for b, (i, j) in enumerate(pairs):
            if cols[a][i] != cols[a][j]:
                v |= (1 << b)
        mk.append(v)
    return mk, (1 << len(pairs)) - 1, len(pairs)


def count_frames(mk, k, wall):
    n = len(mk)
    ALLP = (1 << len(bin(max(mk))[2:])) if False else None
    SUF = [0] * (n + 1)
    for a in range(n - 1, -1, -1):
        SUF[a] = SUF[a + 1] | mk[a]
    ALL = SUF[0]
    nodes = [0]
    frames = []
    t0 = time.time()
    state = {'abort': False}

    def rec(i, chosen, cov):
        nodes[0] += 1
        if nodes[0] % 1000000 == 0:
            if time.time() - t0 > wall:
                state['abort'] = True
        if chosen.__len__() == k:
            if cov == ALL:
                frames.append(tuple(chosen))
            return
        if n - i < k - len(chosen):
            return
        if (cov | SUF[i]) != ALL:
            return
        chosen.append(i)
        nx = cov | mk[i]
        if not state['abort']:
            rec(i + 1, chosen, nx)
        chosen.pop()
        if not state['abort']:
            rec(i + 1, chosen, cov)

    rec(0, [], 0)
    return frames, nodes[0], state['abort'], time.time() - t0, ALL


def covers_all(mk_sel, ALL):
    c = 0
    for a in mk_sel:
        c |= a
    return c == ALL


# ------------------------------------------------------------------ B k_props
nrow = len(K)
ncol = len(K[0]) if nrow else 0
vals = set(x for r in K for x in r)
claim('B1', 'K shape = 120 x 62 and values in {+1,-1}', nrow == 120 and ncol == 62 and vals <= {1, -1},
      'shape=%dx%d values=%s' % (nrow, ncol, sorted(vals)))
dcols = len(set(tuple(K[i][a] for i in range(nrow)) for a in range(ncol)))
claim('B2', 'distinct full column vectors of K = 32 (R1 value)', dcols == 32, 'got %d' % dcols)
A = [[Fraction(K[i][a]) for a in range(ncol)] for i in range(nrow)]
r = 0
piv = []
for c in range(ncol):
    p = None
    for i in range(r, nrow):
        if A[i][c] != 0:
            p = i
            break
    if p is None:
        continue
    A[r], A[p] = A[p], A[r]
    pv = A[r][c]
    A[r] = [x / pv for x in A[r]]
    for i in range(nrow):
        if i != r and A[i][c] != 0:
            f = A[i][c]
            A[i] = [A[i][j] - f * A[r][j] for j in range(ncol)]
    piv.append(c)
    r += 1
    if r == nrow:
        break
claim('B3', 'rank_Q(K) = 6 (independent rational RREF)', r == 6, 'rank=%d pivots=%d' % (r, len(piv)))
sec('k_props', shape=[nrow, ncol], values=sorted(vals), distinct_full_cols=dcols, rank=r)

# ------------------------------------------------------------------ C edge machine
name_e, rows_e, cols_e = build_icosa('E00', 'M_edge')
mk_e, ALL_e, npairs_e = masks_of(cols_e, len(rows_e))
claim('C1', 'M_edge rebuilt: rows=30 cols=62 pairs=435; every pair separated by >=1 column',
      len(rows_e) == 30 and len(cols_e) == 62 and npairs_e == 435 and covers_all(mk_e, ALL_e),
      'rows=%d cols=%d pairs=%d' % (len(rows_e), len(cols_e), npairs_e))
mcols = [tuple(cols_e[a][i] for i in range(len(rows_e))) for a in range(62)]
rawd = len(set(mcols))
pmd = len(set(min(v, tuple(-x for x in v)) for v in mcols))
claim('C1b', 'M_edge machine: 60 distinct column vectors (R11 value), 62 columns', rawd == 60,
      'raw_distinct=%d pm_classes=%d' % (rawd, pmd))
cover = [0, 1, 4, 9, 10, 15, 23]
claim('C2', 'R10 explicit 7-cover [0,1,4,9,10,15,23] separates all 435 pairs (independent)',
      covers_all([mk_e[a] for a in cover], ALL_e))
# per-pair candidate sets: S[p] = columns separating pair p
S = [[] for _ in range(npairs_e)]
for a in range(62):
    v = mk_e[a]
    b = 0
    while v:
        if v & 1:
            S[b].append(a)
        v >>= 1
        b += 1
Ssize = collections.Counter(len(s) for s in S)
d10 = json.load(open(os.path.join(DATA, '10_r6_lp_certificate.json')))['machines']['M_edge']
sup = d10['support']
claim('C3', 'root-LP support from data/10 = 10 columns; x* = 1/2 on it is a fractional cover (LP* >= 5)',
      len(sup) == 10 and all(sum(Fraction(1, 2) for a in S[p] if a in set(sup)) >= 1 for p in range(npairs_e)),
      'support=%s sum=%s' % (sup, d10['certificate'].get('sum_x')))
red = [a for a in sup if covers_all([mk_e[b] for b in sup if b != a], ALL_e)]
claim('C4', 'R12 support S is 9-redundant: S minus ANY one column still covers all 435 pairs',
      len(red) == len(sup), '%d/%d' % (len(red), len(sup)))
f6, n6, ab6, s6, _ = count_frames(mk_e, 6, min(WALL * 0.35, 150))
claim('C5', 'F_6(M_edge) = 0 by independent DFS (=> k_min >= 7)', (not ab6) and len(f6) == 0,
      'frames=%d nodes=%d abort=%s %.1fs' % (len(f6), n6, ab6, s6))
f7, n7, ab7, s7, _ = count_frames(mk_e, 7, min(WALL * 0.55, 300))
claim('C6', 'F_7(M_edge) = 8584 by independent DFS (=> k_min = 7)', (not ab7) and len(f7) == 8584,
      'frames=%d nodes=%d abort=%s %.1fs' % (len(f7), n7, ab7, s7))
sec('edge', pairs=npairs_e, Ssize=sorted(Ssize.items()), support=sup, redundant=len(red),
    F6={'frames': len(f6), 'nodes': n6, 'abort': ab6}, F7={'frames': len(f7), 'nodes': n7, 'abort': ab7})

# ------------------------------------------------------------------ E r11 aggregates (independent census)
if not ab7 and len(f7):
    deg = collections.Counter()
    for fr in f7:
        for a in fr:
            deg[a] += 1
    dv = sorted(deg.values())
    claim('E1', 'per-column degrees: min 812 / max 1306, all 62 columns used', dv[0] == 812 and dv[-1] == 1306 and len(deg) == 62,
          'min=%d max=%d ncols=%d distinct=%d' % (dv[0], dv[-1], len(deg), len(set(dv))))
    nonmin = 0
    for fr in f7:
        for a in fr:
            if covers_all([mk_e[b] for b in fr if b != a], ALL_e):
                nonmin += 1
                break
    claim('E2', 'all 8584 frames inclusion-minimal', nonmin == 0, 'non-minimal=%d' % nonmin)
    d22 = json.load(open(os.path.join(DATA, '22_r11_opt_frame_census.json')))
    claim('E3', 'independently counted F_7 equals data/22 enumeration.frames',
          len(f7) == d22['enumeration']['frames'], '%d vs %d' % (len(f7), d22['enumeration']['frames']))
    masksets = [sum(1 << a for a in fr) for fr in f7]
    t1 = time.time()
    dis = 0
    if len(masksets) <= 9000:
        for i in range(len(masksets)):
            mi = masksets[i]
            for j in range(i + 1, len(masksets)):
                if mi & masksets[j] == 0:
                    dis += 1
    claim('E4', 'pairwise mutual-exclusion count = 17,659,238 (47.9%)',
          dis == d22['pairwise']['disjoint_pairs'], 'got %d vs %d (%.1fs)' % (dis, d22['pairwise']['disjoint_pairs'], time.time() - t1))
    cls = {}
    for a in range(62):
        v = tuple(cols_e[a][i] for i in range(len(rows_e)))
        cls[a] = min(v, tuple(-x for x in v))
    nclass = len(set(cls.values()))
    ntypes = len(set(frozenset(cls[a] for a in fr) for fr in f7))
    claim('E5', 'distinct frame types = 6960 (frames modulo +/- column classes)', ntypes == d22['type_spectrum']['n_distinct_frame_types'],
          'types=%d classes=%d vs %d' % (ntypes, nclass, d22['type_spectrum']['n_distinct_frame_types']))
    sec('r11', degrees=[dv[0], dv[-1]], non_minimal=nonmin, disjoint=dis, types=ntypes)
else:
    claim('E0', 'R11 aggregates recomputed independently', False, 'SKIPPED: F_7 count incomplete')
    sec('r11', skipped=True)

# ------------------------------------------------------------------ D other machines
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
    return name, rows, cols


V4 = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
SM = smats()
vs4 = sorted(V4)
Tgrp = [M for M in SM if sorted(mv(M, v) for v in V4) == vs4]
Ogrp = list(SM)
D4grp = closure([[[0, -1, 0], [1, 0, 0], [0, 0, 1]], [[1, 0, 0], [0, -1, 0], [0, 0, -1]]])
axT, axO, axD = axes_of(Tgrp, {2, 3}), axes_of(Ogrp, {2, 3, 4}), axes_of(D4grp, {2, 4})
claim('D0', 'T/O/D4 groups + axis lines rebuilt independently: |T|=12 |O|=24 |D4|=8; lines 7/13/5',
      len(Tgrp) == 12 and len(Ogrp) == 24 and len(D4grp) == 8 and (len(axT), len(axO), len(axD)) == (7, 13, 5),
      '|T|/|O|/|D4|=%s lines=%s' % ((len(Tgrp), len(Ogrp), len(D4grp)), (len(axT), len(axO), len(axD))))
MT = int_machine('M_T', Tgrp, (1, 1, 1), axT)
MO = int_machine('M_O', Ogrp, (1, 0, 0), axO)
MD = int_machine('M_D4', D4grp, (0, 0, 1), axD)
claim('D0b', 'machine shapes m/N match the record: 4/14, 6/26, 2/10',
      [(len(x[1]), len(x[2])) for x in (MT, MO, MD)] == [(4, 14), (6, 26), (2, 10)],
      '%s' % [(len(x[1]), len(x[2])) for x in (MT, MO, MD)])
d4 = json.load(open(os.path.join(DATA, '04_r2_general_machine.json')))
dout = {}
for (nm, rws, cxx), kmin in ((MT, 4), (MO, 4), (MD, 4)):
    mks, ALLX, npx = masks_of(cxx, len(rws))
    fk = {}
    abt_any = False
    for k in range(1, kmin + 1):
        fr, nd, abt, sc, _ = count_frames(mks, k, min(WALL * 0.1, 40))
        fk[k] = len(fr)
        abt_any = abt_any or abt
    rec = d4['closed_form'].get(nm, {}).get('typeset', {})
    recd = {int(k): v for k, v in rec.items()}
    agree = all(fk.get(k, 0) == recd[k] for k in recd if k in fk) and len(fk) == len(recd)
    dout[nm] = {'rows': len(rws), 'cols': len(cxx), 'pairs': npx, 'F': fk, 'recorded': recd, 'agree': agree, 'abort': abt_any}
    claim('D1', '%s F_k recomputed independently (k<=k_min) agrees with data/04' % nm, agree and not abt_any,
          'F=%s recorded=%s' % (fk, recd))
m2, ALL2, np2 = masks_of([col_vec(U[a], rot_rows(ids_u.index('V00'))) for a in range(62)], 12)
f4, n4, ab4, s4, _ = count_frames(m2, 4, min(WALL * 0.2, 90))
claim('D3', 'M_2I F_4 = 12645 (independent DFS)', (not ab4) and len(f4) == 12645, 'frames=%d nodes=%d %.1fs' % (len(f4), n4, s4))
nf, rf = build_icosa('F00', 'M_face')[1:], None
mkf, ALLf, npf = masks_of(nf[1], len(nf[0]))
f5, n5, ab5, s5, _ = count_frames(mkf, 5, min(WALL * 0.2, 90))
claim('D4', 'M_face F_5 = 320 (independent DFS)', (not ab5) and len(f5) == 320, 'frames=%d nodes=%d %.1fs' % (len(f5), n5, s5))
sec('machines', detail=dout, M2I_F4=len(f4), Mface_F5=len(f5))

# ------------------------------------------------------------------ F manifest
man = json.load(open(os.path.join(ROOT, 'MANIFEST.json')))
disk = []
for sub in ('docs', 'scripts', 'data', 'logs'):
    for fn in sorted(os.listdir(os.path.join(ROOT, sub))):
        p = os.path.join(ROOT, sub, fn)
        if os.path.isfile(p) and not fn.endswith('.pyc'):
            disk.append(sub + '/' + fn)
for fn in ('01_problem_record.md', 'SESSION_START.md', 'final_result.md'):
    if os.path.exists(os.path.join(ROOT, fn)):
        disk.append(fn)
SELF_PREFIX = ('logs/24_closeout', 'data/24_closeout')
SELF = {'data/00_o228_manifest.json', 'logs/08_manifest.out'}


def is_self(f):
    return f in SELF or f.startswith(SELF_PREFIX)
unc = [f for f in disk if f not in man['files'] and not is_self(f)]
stale = [f for f in man['files'] if f not in disk and not is_self(f)]
mism = []
for f, h in man['files'].items():
    p = os.path.join(ROOT, f)
    if os.path.exists(p) and hashlib.sha256(open(p, 'rb').read()).hexdigest() != h:
        mism.append(f)
claim('F1', 'MANIFEST covers the disk both ways (self-excluded on both sides)', not unc and not stale,
      'uncovered=%s stale=%s' % (unc, stale))
claim('F2', 'MANIFEST hashes match the disk (audit own outputs excluded)', not mism, 'mismatch=%s' % mism)
comp = 0
for fn in sorted(os.listdir(os.path.join(ROOT, 'scripts'))):
    if fn.endswith('.py'):
        txt = open(os.path.join(ROOT, 'scripts', fn), encoding='utf-8').read()
        if 'RESULT:' in txt or 'RESULT' in txt:
            comp += 1
claim('F3', 'script-chain symmetry: every docs/contract round has a results doc',
      all(os.path.exists(os.path.join(DOCS, t)) for t in
          ['00_r1_contract.md', '01_r1_results.md', '02_r2_contract.md', '02_r2_results.md', '03_r3_contract.md',
           '04_r3_results.md', '05_r5_contract.md', '06_r5_results.md', '07_r6_contract.md', '08_r6_results.md',
           '09_r7_contract.md', '10_r7_results.md', '11_r8_contract.md', '12_r8_results.md', '13_r9_contract.md',
           '14_r9_results.md', '15_r10_contract.md', '16_r10_results.md', '17_r11_contract.md', '18_r11_results.md',
           '19_r12_contract.md', '20_r12_results.md']))
sec('manifest', n_files=man['n_files'], disk_files=len(disk), uncovered=unc, stale=stale, mismatch=mism, scripts_with_RESULT=comp)

# ------------------------------------------------------------------ G register
reg = os.path.join(REPO, 'problem_register', 'register.jsonl')
ev = []
for line in open(reg, encoding='utf-8'):
    try:
        e = json.loads(line)
    except Exception:
        continue
    if str(e.get('pid', '')).startswith('O228'):
        ev.append(e)
kinds = collections.Counter(e.get('kind') for e in ev)
pids = collections.Counter(e.get('pid') for e in ev)
badref = []
for e in ev:
    rf = e.get('ref')
    if rf:
        p = rf.split(':')[0]
        if not os.path.exists(os.path.join(REPO, p)):
            badref.append(e.get('pid') + '->' + str(rf))
rounds = ['O228/R%d' % i for i in range(1, 13)]
missing = [r for r in rounds if r not in pids]
claim('G1', 'register: every R1..R12 has at least one event (bidirectional coverage)', not missing,
      'missing=%s kinds=%s' % (missing, dict(kinds)))
claim('G2', 'register: every ref path exists (no REF-MISSING drift)', not badref, 'bad=%s' % badref[:5])
claim('G3', 'register: no ghost entry outside R1..R12 (reverse coverage)',
      set(pids) == set(rounds + ['O228']), 'extra=%s' % sorted(set(pids) - set(rounds + ['O228'])))
sec('register', events=dict(kinds), by_pid=dict(pids), bad_refs=badref[:10])

# ------------------------------------------------------------------ H hygiene
hits = []
for fn in sorted(os.listdir(os.path.join(ROOT, 'scripts'))):
    if not fn.endswith('.py'):
        continue
    txt = open(os.path.join(ROOT, 'scripts', fn), encoding='utf-8').read()
    for ln, line in enumerate(txt.splitlines(), 1):
        if fn == os.path.basename(__file__):
            continue
        bad = ('/tm' + 'p/', '/va' + 'r/tmp/')
        if (bad[0] in line or bad[1] in line) and ('open(' in line or 'write' in line or 'dump' in line or 'savetxt' in line):
            hits.append('%s:%d' % (fn, ln))
claim('H1', 'no /tmp write patterns in scripts/', not hits, 'hits=%s' % hits)
WS = os.path.expanduser('~/.hermes/cache/scratch')
scr = sorted(f for f in os.listdir(WS) if f.startswith('o228_')) if os.path.isdir(WS) else []
sec('hygiene', tmp_hits=hits, scratch=scr)

# ------------------------------------------------------------------ I docs
tokens = ['8584', '152,157,793', '6960', '47.9', '23083292', '1051351', '12645', '[0, 1, 4, 9, 10, 15, 23]',
          '9085', '3554', '174.5', '0.03461839', '9,085']
files = [os.path.join(DOCS, f) for f in sorted(os.listdir(DOCS))] + \
        [os.path.join(ROOT, f) for f in ('final_result.md', 'SESSION_START.md', '01_problem_record.md')]
txt = '\n'.join(open(p, encoding='utf-8').read() for p in files if os.path.exists(p))
miss = [t for t in tokens if t not in txt]
claim('I1', 'headline numbers present in the doc set (coverage, not correctness)', not miss, 'missing=%s' % miss)
sec('docs', tokens_checked=len(tokens), missing=miss)

# ------------------------------------------------------------------ verdict
okn = sum(1 for c in RES['claims'] if c['ok'])
RES['verdict'] = '%d/%d PASS' % (okn, len(RES['claims']))
RES['total_seconds'] = round(time.time() - T0, 1)
save()
print('RESULT: %s  (%s)' % (RES['verdict'], RES['total_seconds']))
for c in RES['claims']:
    if not c['ok']:
        print('  FAIL %s %s' % (c['tag'], c['name']))
sys.exit(0 if okn == len(RES['claims']) else 1)
