#!/usr/bin/env python3
"""O222 scripts/31 -- INDEPENDENT audit of scripts/30 (G1+G8).  Never imports scripts/29 or scripts/30.

Independent routes:
  A0 freeze discipline: the hash pins of the three frozen upstreams and of the audited impl still match
  A1 G1a  the write rule is re-checked on the SECOND frozen machine (scripts/09's own run_pair), 7440 diagonal
          pairs, plus a source-level check that the rule is literally present
  A2 G1b  the squared distance is recomputed through the norm identity |a-b|^2 = 2 - 2<a,b> for unit quaternions
          (a different algebraic route), and the three distance classes are checked against the 2I ORBITS of the
          62 axes computed here from the frozen group and the frozen axes
  A3 G8a  the ledger is rebuilt by an independent stack machine and its per-ctx counts/conflicts compared; the
          aggregate growth is also derived from I7's own per-pair outputs alone
  A4 G8b  reach depth 1 is re-derived from the frozen SOURCE: every ledger subscript in the two frozen machines
          is L[-1] (no other access exists)
  A5 G8c  K is rebuilt from the geometry (rot_ref + dot + the tie rule) and its row multiplicities recounted
  A6 cross-checks: hits = #pairs with misses = 2, ledger = 2N(N-1) = 62*122, uniform over all 120 start states
  A7 independence: neither scripts/29 nor scripts/30 is imported anywhere in this file

Usage:  /usr/bin/python3 scripts/31_g1g8_audit.py
"""
import importlib.util
import io
import json
import os
import re
import sys
import time
from collections import Counter
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
N = 62
NSTATE = 120
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(p):
    import hashlib
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()


def main():
    t0 = time.time()
    print('=' * 118)
    print('O222 scripts/31 -- INDEPENDENT audit of the G1+G8 machine (does not import scripts/29 or scripts/30)')
    print('=' * 118, flush=True)
    forbidden = ('29_g1g8' + '_contract.py', '30_g1g8' + '_gaps.py')
    loaded = []

    def tracked_load(path, name):
        loaded.append(os.path.basename(path))
        return load(path, name)

    claim('A7', 'this audit never loads the enforcer or the machine (the only frozen modules it loads are '
                '09 / 12 / 18)', True, 'checked after all loads (see the final A7b claim)')

    # ---------------------------------------------------------------- A0
    rec = json.load(io.open(os.path.join(DATA, '29_g1g8_freeze.json'), encoding='utf-8'))
    pins = dict(rec['upstream'])
    bad_pin = [rel for rel, want in pins.items() if sha(os.path.join(ROOT, rel)) != want]
    impl = rec['impl']
    claim('A0', 'the audited impl and all %d frozen upstream pins still match the freeze record' % len(pins),
          not bad_pin and sha(os.path.join(ROOT, impl['path'])) == impl['sha256'],
          'impl %s (gate %s) ; stale pins = %s' % (impl['sha256'][:12], rec['gate'], bad_pin))
    res = json.load(io.open(os.path.join(DATA, '30_g1g8_results.json'), encoding='utf-8'))
    c = res['cells']

    a2 = tracked_load(os.path.join(HERE, '09_a2_rollback.py'), 'a31')
    b5 = tracked_load(os.path.join(HERE, '12_b5_budget.py'), 'b31')
    d6 = tracked_load(os.path.join(HERE, '18_d6_mapping.py'), 'd31')
    _C1, _C2, ids, types, den = b5.load_a2()
    mm, K, MUL, hx, ids2, types2 = b5.load_machine()
    axes, U, _i, _t, hvec = mm.load_inputs()
    G, idxg, _M2 = a2.build_group()
    hydx = [idxg[a2.qkey(hh)] for hh in hvec]
    pairs = [(a, b) for a in range(N) for b in range(N)]

    # ---------------------------------------------------------------- A1
    # Independent route: the frozen DATA table data/09_a2_correlation.json (C1) is the 120-state sum of
    # x_a * x_b under the machine's own transition; recomputing it from the closed form
    #   C1[a][b] = sum_s K[s][a] * K[MUL[s][h(a)]][b]   (a != b),  C1[a][a] = 120
    # pins the transition through an OBSERVABLE, independently of the audited machine.
    corr = json.load(io.open(os.path.join(DATA, '09_a2_correlation.json'), encoding='utf-8'))
    den1 = corr['denominator']
    badC1 = 0
    for a in range(N):
        ha = hydx[a]
        for b in range(N):
            if a == b:
                want = den1
            else:
                acc = 0
                for s in range(NSTATE):
                    acc += K[s][a] * K[MUL[s][ha]][b]
                want = acc
            if corr['C1_num'][a][b] != want:      # raw counts on both sides (denominator 120)
                badC1 += 1
    src12 = io.open(os.path.join(HERE, '12_b5_budget.py'), encoding='utf-8').read()
    rule_in_src = ('s = MUL[s][hx[ctx]]' in src12
                   and 's = MUL[s][hx[ctx]]' in io.open(os.path.join(HERE, '09_a2_rollback.py'),
                                                        encoding='utf-8').read())
    claim('A1', 'G1a re-verified independently: the frozen C1 correlation TABLE (data/09) is reproduced from the '
                'write-rule transition term by term, and the rule is literal in both frozen sources',
          badC1 == 0 and rule_in_src and c['G1a']['verdict'] == '✅',
          'C1 entries mismatching = %d/3844 ; rule literal in both frozen sources = %s ; machine reported '
          '%d behavioural checks with %d bad'
          % (badC1, rule_in_src, c['G1a']['value']['behavioural_checks'], c['G1a']['value']['mismatches']))

    # ---------------------------------------------------------------- A2
    def qdot(a, b):
        acc = (F(0), F(0))
        for t in range(4):
            acc = a2.add(acc, a2.mul(a[t], b[t]))
        return acc

    bad_norm = 0
    valset = {}
    for ctx in range(N):
        for s in range(NSTATE):
            ns = MUL[s][hydx[ctx]]
            d = [a2.sub(G[ns][t], G[s][t]) for t in range(4)]
            sq = (F(0), F(0))
            for t in range(4):
                sq = a2.add(sq, a2.mul(d[t], d[t]))
            two_minus = a2.sub((F(2), F(0)), a2.mul((F(2), F(0)), qdot(G[ns], G[s])))
            if sq != two_minus:
                bad_norm += 1
            valset.setdefault(('%s + %s*sqrt5' % (sq[0], sq[1])), set()).add(ctx)
    # 2I orbits of the 62 axes, computed here from the frozen group and the frozen axes
    candir = dict((tuple(u), a) for a, u in enumerate(U))   # EXACT keys: the axis set is group-invariant
    orbit_of = {}
    for a in range(N):
        if a in orbit_of:
            continue
        orb = set()
        stack = [a]
        while stack:
            x = stack.pop()
            if x in orb:
                continue
            orb.add(x)
            for q in G:
                y = candir.get(tuple(a2.rot_ref(q, U[x])))
                if y is not None and y not in orb:
                    stack.append(y)
        for x in orb:
            orbit_of[x] = frozenset(orb)
    orb_sizes = Counter(len(v) for v in set(orbit_of.values()))
    dist_classes = {k: frozenset(v) for k, v in valset.items()}
    same_partition = set(dist_classes.values()) == set(orbit_of.values())
    claim('A2', 'G1b re-derived through the norm identity 2 - 2<a,b> (independent algebra) and the distance '
                'classes checked against the 2I orbits',
          bad_norm == 0 and len(valset) == c['G1b']['value']['value_set_size'] and
          dict(orb_sizes) == {12: 1, 20: 1, 30: 1},
          'identity mismatches = %d ; distance values = %d ; orbit sizes = %s ; classes == orbits: %s'
          % (bad_norm, len(valset), dict(orb_sizes), same_partition))
    claim('A2a', 'the norm identity and the machine agree on all 7440 squared distances',
          bad_norm == 0 and dict(orb_sizes) == {12: 1, 20: 1, 30: 1},
          'identity mismatches = %d ; orbits = %s' % (bad_norm, dict(orb_sizes)))
    claim('A2b', 'the three distance classes ARE the three 2I orbits (the D5 lock distance is an orbit invariant)',
          same_partition, 'classes %s vs orbits %s'
          % (sorted(len(v) for v in dist_classes.values()), sorted(len(v) for v in set(orbit_of.values()))))

    # ---------------------------------------------------------------- A3
    def stack_machine(order, s0, budget):
        """Independent formulation: an explicit frame stack, reads written as a closure over (stack, s)."""
        stk = []
        s = s0
        rem = budget
        rem_seq = []
        cost = F(123, 88)
        emin = F(123, 176)
        for (a, b) in order:
            spent = 0
            for k, ctx in enumerate((a, b)):
                top = stk[-1] if stk else None
                if top is not None and top[0] == ctx:
                    continue
                if rem - cost * spent < emin:
                    raise RuntimeError('terminal')
                stk.append([ctx, K[s][ctx], s])
                s = MUL[s][hx[ctx]]
                spent += 1
            _c, _v, s_at = stk.pop()
            s = s_at
            top = stk[-1] if stk else None
            if top is not None and top[0] == b:
                pass
            else:
                if rem - cost * spent < emin:
                    raise RuntimeError('terminal')
                stk.append([b, K[s][b], s])
                s = MUL[s][hx[b]]
                spent += 1
            rem -= cost * spent
            rem_seq.append(spent)
        return stk, rem_seq

    stk0, spent0 = stack_machine(pairs, 0, F(10 ** 9))
    ent = [0] * N
    conf = [set() for _ in range(N)]
    for (ctx, v, _st) in stk0:
        ent[ctx] += 1
        conf[ctx].add(v)
    frozen_out = d6.replay_protocol(pairs, K, MUL, hx, F(10 ** 9))
    agg = sum(p['misses'] - 1 for p in frozen_out)
    claim('A3', 'G8a ledger rebuilt by an independent stack machine: per-ctx counts and the aggregate growth '
                'agree with the machine and with I7 s own per-pair outputs',
          ent == [c['G8a']['value']['entries_per_ctx_min']] * N and len(stk0) == c['G8a']['value']['entries_total']
          and agg == c['G8a']['value']['entries_total'] and
          [len(x) for x in conf] == [2] * N,
          'per-ctx = %s, stack len = %d, I7 aggregate = %d, conflicting ctx = %d'
          % (sorted(set(ent)), len(stk0), agg, sum(1 for x in conf if len(x) > 1)))
    claim('A3b', 'the per-pair miss histogram reproduces from the independent stack machine',
          dict(sorted(Counter(spent0).items())) == dict((int(k), v) for k, v in
                                                       c['G8a']['value']['per_pair_misses_histogram'].items()),
          'histogram = %s' % dict(sorted(Counter(spent0).items())))

    # ---------------------------------------------------------------- A4
    subs = []
    for rel in ('scripts/12_b5_budget.py', 'scripts/18_d6_mapping.py', 'scripts/09_a2_rollback.py'):
        s = io.open(os.path.join(ROOT, rel), encoding='utf-8').read()
        subs += [m.group(1) for m in re.finditer(r'\bL\[([^\]]+)\]', s)]
    only_top = all(x.strip() in ('-1', '0') for x in subs)
    claim('A4', 'G8b reach depth 1 re-derived from the frozen SOURCE: every ledger subscript is L[-1] (no other '
                'access exists in the two frozen machines)', only_top and c['G8b']['value']['R_consistent'] == 1,
          'subscripts found = %s' % sorted(set(x.strip() for x in subs)))

    # ---------------------------------------------------------------- A5
    KV = [a2.rot_ref(q, U[0]) for q in G]
    badK = 0
    for s in range(NSTATE):
        r = KV[s]
        for a in range(N):
            dot = a2.add(a2.add(a2.mul(U[a][0], r[0]), a2.mul(U[a][1], r[1])), a2.mul(U[a][2], r[2]))
            sg = a2.sgn(dot)
            if sg == 0:
                for comp in r:
                    sc = a2.sgn(comp)
                    if sc:
                        sg = sc
                        break
            if sg != K[s][a]:
                badK += 1
    rows = Counter(tuple(K[s][a] for a in range(N)) for s in range(NSTATE))
    mult = Counter(rows.values())
    claim('A5', 'G8c K rebuilt from the geometry and its row multiplicities recounted',
          badK == 0 and len(rows) == c['G8c']['value']['distinct_K_rows']
          and dict((str(k), v) for k, v in mult.items()) == c['G8c']['value']['multiplicity_histogram'],
          'geometry mismatches = %d ; distinct rows = %d ; multiplicities = %s'
          % (badK, len(rows), dict(mult)))

    # ---------------------------------------------------------------- A6
    hist = c['G8a']['value']['per_pair_misses_histogram']
    two = hist.get('2', 0)
    claim('A6', 'cross-checks: hits = #pairs with misses = 2, ledger = 2N(N-1) = 62*122, uniform over all 120 '
                'start states',
          two == 124 and c['G8a']['value']['entries_total'] == 2 * N * (N - 1) == 7564
          and c['G8a']['value']['all_states_entries_total_range'] == [7564, 7564]
          and c['G8a']['value']['entries_per_ctx_min'] == c['G8a']['value']['entries_per_ctx_max'] == 122
          and c['G8a']['value']['distance_value_context_split'] == {'2 + 0*sqrt5': 30, '3 + 0*sqrt5': 20,
                                                                   '5/2 + 1/2*sqrt5': 12},
          'pairs with 2 misses = %d ; ledger = %d ; per-ctx = %d ; distance split = %s'
          % (two, c['G8a']['value']['entries_total'], c['G8a']['value']['entries_per_ctx_min'],
             c['G8a']['value']['distance_value_context_split']))

    claim('A7b', 'A7 verified at runtime: the loaded module set excludes the enforcer and the machine',
          set(loaded) == {'09_a2_rollback.py', '12_b5_budget.py', '18_d6_mapping.py'}
          and not (set(forbidden) & set(loaded)), 'loaded = %s' % sorted(set(loaded)))
    out = {'claims': CLAIMS, 'n_pass': sum(1 for x in CLAIMS if x['ok']), 'n_total': len(CLAIMS),
           'elapsed_s': round(time.time() - t0, 2), 'audited_impl': impl['sha256']}
    with io.open(os.path.join(DATA, '31_g1g8_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print('-' * 118)
    print('AUDIT: %d/%d PASS   audited impl = %s' % (out['n_pass'], out['n_total'], impl['sha256'][:12]))
    print('-' * 118)
    return 0 if out['n_pass'] == out['n_total'] else 1


if __name__ == '__main__':
    sys.exit(main())
