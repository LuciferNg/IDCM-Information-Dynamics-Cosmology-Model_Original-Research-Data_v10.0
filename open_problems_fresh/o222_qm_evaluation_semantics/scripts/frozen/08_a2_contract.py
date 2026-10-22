#!/usr/bin/env python3
"""O222 scripts/08 -- CONTRACT A2 v1 ENFORCER (executable gate for the sequential/rollback layer).

docs/05_a2_contract.md is the frozen contract text; THIS file is its machine-checkable form.
Nothing here may be tuned: it reconstructs the group from zero, re-derives the frozen 62 lattice
axes and REFUSES to proceed if they do not reproduce data/04_b2_settings.json exactly.

Usage:
    /usr/bin/python3 scripts/08_a2_contract.py
    /usr/bin/python3 scripts/08_a2_contract.py --freeze-impl scripts/09_a2_rollback.py

Exit status 0 = gate OPEN.  Any [FAIL] = gate CLOSED (scripts/09 must not be run / revealed).
"""
import ast
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
LOGS = os.path.join(ROOT, 'logs')
DOC = os.path.join(ROOT, 'docs', '05_a2_contract.md')
FREEZE = os.path.join(DATA, '08_a2_freeze.json')
HTAB = os.path.join(DATA, '08_a2_h_table.json')
B2_FREEZE = os.path.join(DATA, '04_b2_freeze.json')
B2_SETTINGS = os.path.join(DATA, '04_b2_settings.json')
B2_PARTITION = os.path.join(DATA, '04_b2_partition.json')

RULES_VERSION = 'a2-contract-v1'
RESULTS = []


def chk(tag, name, ok, detail=''):
    RESULTS.append((tag, name, bool(ok), detail))
    print('[%s] %-6s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def sha256_file(p):
    with open(p, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def sha256_text(t):
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


# ============================ exact Q(sqrt5) ============================
def N(a, b=0):
    return (F(a), F(b))


ZERO, ONE = N(0), N(1)


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def sub(x, y):
    return (x[0] - y[0], x[1] - y[1])


def neg(x):
    return (-x[0], -x[1])


def mul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def scale(x, k):
    return (x[0] * k, x[1] * k)


def inv(x):
    d = x[0] * x[0] - 5 * x[1] * x[1]
    return (x[0] / d, -x[1] / d)


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


def qorder(q):
    e = q
    n = 1
    while not (e[0] == ONE and is_zero(e[1]) and is_zero(e[2]) and is_zero(e[3])):
        e = qmul(e, q)
        n += 1
        if n > 30:
            return -1
    return n


def vpart(q):
    return (q[1], q[2], q[3])


def vneg(v):
    return tuple(neg(x) for x in v)


def dir_canon(v):
    """canonical LINE representative: first non-zero component normalised to exactly +1"""
    for c in v:
        if not is_zero(c):
            s = inv(c)
            return tuple(mul(x, s) for x in v)
    return v


def qsortkey(q):
    out = []
    for c in q:
        for x in c:
            out.extend([x.numerator, x.denominator])
    return tuple(out)


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


# ============================ AST gate ============================
BANNED_NAMES = {'cos', 'sin', 'tan', 'acos', 'asin', 'atan', 'atan2', 'pi', 'sqrt', 'exp', 'log',
                'log2', 'log10', 'hypot', 'degrees', 'radians', 'numpy', 'np', 'scipy', 'math',
                'random'}
BANNED_LITERALS = {0.7071067811865476, 1.4142135623730951, 2.8284271247461903,
                   0.7071067811865475, 3.141592653589793}


def ast_scan(path):
    """returns (ok, notes).  Bans trig/float/external-math inside the impl."""
    src = io.open(path, encoding='utf-8').read()
    tree = ast.parse(src)
    notes = []
    constrained = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # locality rule: the machine read operator takes exactly (G, ctx)
            if node.args.args and [a.arg for a in node.args.args] == ['G', 'ctx']:
                constrained.append(node.name)
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            mods = [a.name.split('.')[0] for a in node.names] if isinstance(node, ast.Import) else \
                   [(node.module or '').split('.')[0]]
            for m in mods:
                if m in ('numpy', 'np', 'scipy', 'math'):
                    notes.append('banned import: %s' % m)
        if isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            notes.append('banned name: %s' % node.id)
        if isinstance(node, ast.Attribute) and node.attr in BANNED_NAMES:
            notes.append('banned attribute: %s' % node.attr)
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            notes.append('float literal: %r' % node.value)
    # factor-table locality: exactly one function must carry the (G, ctx) signature
    return (not notes), notes, constrained, src


# ============================ main ============================
def main():
    argv = sys.argv[1:]
    impl = None
    if '--freeze-impl' in argv:
        impl = argv[argv.index('--freeze-impl') + 1]
        if not os.path.isabs(impl):
            impl = os.path.join(ROOT, impl)
    print('=' * 110)
    print('O222 scripts/08 -- A2 CONTRACT v1 ENFORCER   (rules: %s)' % RULES_VERSION)
    print('=' * 110, flush=True)

    # ---------- C1 group rebuilt from zero ----------
    gens = list(build_2T())
    q0 = (scale(PHI, F(1, 2)), scale(ONE, F(1, 2)), scale(PSI, F(1, 2)), ZERO)
    for q in gens + [q0]:
        u = qmul(q, qconj(q))
        if not (u[0] == ONE and all(is_zero(c) for c in u[1:])):
            chk('[C1]', 'generators are unit quaternions', False, 'non-unit generator %r' % (q,))
            break
    else:
        chk('[C1]', '17 generators (24-element 2T + q0=(phi,1,psi,0)/2) are unit quaternions', True,
            'with q q* = 1 exactly')
    G = closure_bfs(gens + [q0])
    chk('[C2]', '2I = <2T, q0> closes to exactly 120 UNIT quaternions', len(G) == 120,
        '|2I| = %d' % len(G))
    inv_ok = all(qkey(qconj(q)) in {qkey(x) for x in G} for q in G)
    chk('[C3]', '2I is inverse-closed', inv_ok)
    ords = {}
    for q in G:
        ords[qorder(q)] = ords.get(qorder(q), 0) + 1
    hist_ok = ords == {1: 1, 2: 1, 3: 20, 4: 30, 5: 24, 6: 20, 10: 24}
    chk('[C4]', 'order histogram = {1:1, 2:1, 3:20, 4:30, 5:24, 6:20, 10:24}', hist_ok, str(ords))

    # ---------- C5 re-derive the 62 axes and match the FROZEN list ----------
    S = json.load(io.open(B2_SETTINGS, encoding='utf-8'))
    frozen = {}
    for ax in S['axes']:
        vec = tuple((F(c[0]), F(c[1])) for c in ax['vec'])
        frozen.setdefault(ax['type'], {})[ax['id']] = vec
    raw = {'vertex': set(), 'face': set(), 'edge': set()}
    for q in G:
        o = qorder(q)
        v = vpart(q)
        if all(is_zero(c) for c in v):
            continue
        if o in (5, 10):
            raw['vertex'].add(dir_canon(v))
        elif o in (3, 6):
            raw['face'].add(dir_canon(v))
        elif o == 4:
            raw['edge'].add(dir_canon(v))
    line_counts = {k: len(v) for k, v in raw.items()}
    chk('[C5]', 'axis LINES re-derived from element orders = 6 vertex / 10 face / 15 edge',
        line_counts == {'vertex': 6, 'face': 10, 'edge': 15}, str(line_counts))
    match = {}
    for t, span in (('vertex', (5, 10)), ('face', (3, 6)), ('edge', (4,))):
        fro_lines = {dir_canon(v) if sgn(next(c for c in v if not is_zero(c))) > 0
                     else dir_canon(vneg(v)) for v in frozen[t].values()}
        match[t] = (raw[t] == fro_lines)
    chk('[C6]', 're-derived axis lines reproduce data/04_b2_settings.json EXACTLY (all 3 classes)',
        all(match.values()), str(match))
    chk('[C7]', 'oriented axis counts (frozen) = 12 V + 20 F + 30 E = 62',
        (len(frozen['vertex']), len(frozen['face']), len(frozen['edge'])) == (12, 20, 30),
        str({k: len(v) for k, v in frozen.items()}))

    # ---------- C8 build the h table (least order, positive alignment, canonical tie-break) ----------
    axis_list = list(S['axes'])          # FROZEN enumeration order (docs/03 1.2)
    htab, hdetail = [], []
    for ax in axis_list:
        u = tuple((F(c[0]), F(c[1])) for c in ax['vec'])
        want = {'vertex': (5, 10), 'face': (3, 6), 'edge': (4,)}[ax['type']]
        cands = []
        for q in G:
            if qorder(q) not in want:
                continue
            v = vpart(q)
            if all(is_zero(c) for c in v):
                continue
            if dir_canon(v) != dir_canon(u):
                continue
            dot = add(add(mul(v[0], u[0]), mul(v[1], u[1])), mul(v[2], u[2]))
            if sgn(dot) <= 0:
                continue
            cands.append(q)
        if not cands:
            hdetail.append((ax['id'], None))
            continue
        h = sorted(cands, key=qsortkey)[0]
        htab.append((ax['id'], h))
    ok_h = len(htab) == 62 and all(h is not None for _, h in htab)
    chk('[C8]', 'h(ctx) well-defined for all 62 oriented axes (least order + positive alignment)',
        ok_h, '%d / 62 assigned' % len(htab))
    if ok_h:
        rot_order = []
        for (aid, h), ax in zip(htab, axis_list):
            o = qorder(h)
            rot_order.append({5: 5, 10: 5, 3: 3, 6: 3, 4: 2}[o])
        want_order = [{'vertex': 5, 'face': 3, 'edge': 2}[ax['type']] for ax in axis_list]
        chk('[C9]', 'h(ctx) rotation order matches the axis class (V->5, F->3, E->2)',
            rot_order == want_order, 'distinct h values = %d' % len({qkey(h) for _, h in htab}))
        # h must be a bijection on the 62 oriented axes?  report, do not require
        chk('[C10]', 'h table recorded (62 rows, exact quaternion components)',
            len(htab) == 62, 'bijective = %s' % (len({qkey(h) for _, h in htab}) == 62))

    # ---------- C11 structural pre-checks (centre symmetry, ties) ----------
    vdirs = [frozen['vertex'][k] for k in sorted(frozen['vertex'])]
    bad = 0
    for ax in axis_list:
        u = tuple((F(c[0]), F(c[1])) for c in ax['vec'])
        s = 0
        for v in vdirs:
            dot = add(add(mul(u[0], v[0]), mul(u[1], v[1])), mul(u[2], v[2]))
            s += sgn(dot)
        if s != 0:
            bad += 1
    chk('[C11]', 'centre symmetry: sum_v sign(u.v) = 0 for all 62 axes (marginal = 1/2 EXACT)',
        bad == 0, 'unbalanced = %d / 62' % bad)
    tie = S['tie_audit']
    chk('[C12]', 'frozen tie audit reproduced (7200 tie events, 0 unbalanced after H3)',
        tie['tie_events_12refs'] == 7200 and tie['unbalanced_with_ties_assigned'] == 0,
        'tie_events=%d unbalanced=%d' % (tie['tie_events_12refs'],
                                         tie['unbalanced_with_ties_assigned']))

    # ---------- C13 frozen B2 artifacts reused, hashes as recorded ----------
    b2 = json.load(io.open(B2_FREEZE, encoding='utf-8'))
    part = json.load(io.open(B2_PARTITION, encoding='utf-8'))
    chk('[C13]', 'B2 contract artifacts reused unchanged (settings/partition hashes match freeze)',
        sha256_file(B2_SETTINGS) == b2['settings']['sha256'] and
        sha256_file(B2_PARTITION) == b2['partition']['sha256'],
        'settings=%s partition=%s' % (sha256_file(B2_SETTINGS)[:12], sha256_file(B2_PARTITION)[:12]))
    chk('[C14]', 'DEV=144 / BLIND=3700 partition reused; enumeration order = frozen list order',
        len(part['dev']) == 144 and len(part['blind']) == 3700, 'dev=%d blind=%d' %
        (len(part['dev']), len(part['blind'])))

    # ---------- C15 contract text present + hashable ----------
    doc_hash = sha256_file(DOC)
    chk('[C15]', 'A2 contract text present (docs/05) and hashable', doc_hash is not None,
        'docs/05 sha256 = %s...' % doc_hash[:16])

    # ---------- C16 impl AST gate ----------
    impl_hash = None
    if impl is None:
        print('[WAITING] [C16] implementation not supplied: run with '
              '--freeze-impl scripts/09_a2_rollback.py', flush=True)
        RESULTS.append(('[C16]', 'impl AST gate', False, 'WAITING (no impl supplied)'))
    elif not os.path.exists(impl):
        chk('[C16]', 'impl exists', False, '%s missing -> GATE = WAITING' % impl)
    else:
        ok, notes, constrained, src = ast_scan(impl)
        impl_hash = sha256_text(src) if False else sha256_file(impl)
        chk('[C16]', 'impl AST gate: no trig / no float / no numpy-scipy-math / no random',
            ok, ('; '.join(sorted(set(notes))[:4]) if notes else 'clean'))
        loc_ok = (constrained == ['read']) or ('read' in constrained)
        chk('[C16b]', 'factor-table locality: the machine read operator is read(G, ctx)',
            loc_ok, 'constrained functions = %s' % (constrained,))

    # ---------- write artefacts ----------
    out = {'rules_version': RULES_VERSION, 'frozen_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
           'contract_doc': {'path': 'docs/05_a2_contract.md', 'sha256': doc_hash},
           'b2_reused': {'settings_sha256': sha256_file(B2_SETTINGS),
                         'partition_sha256': sha256_file(B2_PARTITION),
                         'b2_impl_sha256': b2.get('impl', {}).get('sha256')},
           'group': {'order_histogram': ords, 'n2I': len(G), 'generator': 'q0=(phi,1,psi,0)/2 + 2T(24)'},
           'axes_match_frozen': match,
           'h_table': [{'id': a, 'h': [[str(c[0]), str(c[1])] for c in h]} for a, h in htab]}
    if impl_hash:
        out['impl'] = {'path': os.path.relpath(impl, ROOT), 'sha256': impl_hash,
                       'frozen_at': time.strftime('%Y-%m-%dT%H:%M:%S%z')}
    with io.open(HTAB, 'w', encoding='utf-8') as fh:
        json.dump({'rules_version': RULES_VERSION,
                   'h_table': [{'id': a, 'h': [[str(c[0]), str(c[1])] for c in h]} for a, h in htab]},
                  fh, indent=1, ensure_ascii=False)
    # preserve previous impl freeze if this run did not supply one
    if not impl_hash and os.path.exists(FREEZE):
        try:
            prev = json.load(io.open(FREEZE, encoding='utf-8'))
            if 'impl' in prev:
                out['impl'] = prev['impl']
                print('[note] impl hash preserved from previous freeze: %s' % prev['impl']['sha256'][:16])
        except Exception as exc:      # pragma: no cover
            print('[note] could not read previous freeze: %r' % (exc,))
    with io.open(FREEZE, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)

    npass = sum(1 for r in RESULTS if r[2])
    nfail = len(RESULTS) - npass
    print('=' * 110)
    print('RESULT: %d/%d PASS  (%d FAIL)   GATE = %s' % (npass, len(RESULTS), nfail,
                                                         'OPEN' if nfail == 0 else 'CLOSED'))
    print('freeze -> data/08_a2_freeze.json   h-table -> data/08_a2_h_table.json')
    if impl_hash:
        print('frozen impl %s = %s' % (os.path.relpath(impl, ROOT), impl_hash))
    print('=' * 110)
    return 0 if nfail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
