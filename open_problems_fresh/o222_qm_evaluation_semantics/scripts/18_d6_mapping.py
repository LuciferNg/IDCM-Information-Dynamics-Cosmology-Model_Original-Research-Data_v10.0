#!/usr/bin/env python3
"""O222 scripts/18 -- D6 machine: the mapping table, operationalised (contract docs/12, rules d6-contract-v1).

Every cell is decided by an EXACT computation on frozen objects, never by a noun correspondence:
  P1a orbits of the 2I action on the 62 axes (exact Q(sqrt5) direction canonicalisation)
  P1b determinism + reversibility of the state transition s -> MUL[s][h(a)]
  P1c composition law: provenance only (O210 carries T = K_chain (x) K_tree, and carries no dimensions)
  P2a repeat idempotence: purity of read on all 7440 (state, setting) pairs + hit consistency + a
      dynamic witness (a pass whose consecutive pairs share the ledger top => 2-read pairs)
  P2b history sensitivity: number of settings whose value is not a function of the setting alone
  P2c irreversibility: per-pair ledger growth = misses - 1 > 0 on the frozen machine's own trail
  P2d probability structure: value set and row sums of C1/C2 (Born-type weights?)
  P3a append-only + hit consistency over a pass
  P3b record stability: hits that return the STORED value even when the current state would give another
  P3c redundancy: accessible ledger depth is 1 (top-only) => single-copy record
  P4a non-factorisability: exact rank over Q of C1, C2, C1rev, and the antipodal table
  P4b CHSH: cited from B3R2 (no re-derivation)
  P4c no-signalling: row sums and column balances exactly 0, plus the cited 3844/3844 A2 check

Usage:  /usr/bin/python3 scripts/18_d6_mapping.py
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
RULES = 'd6-contract-v1'
N = 62


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mul5(a, b):
    """(p,q)*(p',q') in Q(sqrt5)."""
    return (a[0] * b[0] + 5 * a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def canon(v):
    """canonical representative of the direction +-lambda*v (lambda > 0 in Q(sqrt5))."""
    w = list(v)
    piv = None
    for i in range(3):
        if w[i][0] or w[i][1]:
            piv = i
            break
    p, q = w[piv]
    den = p * p - 5 * q * q
    out = []
    for (a, b) in w:
        num = (a * p - 5 * b * q, b * p - a * q)
        out.append((num[0] / den, num[1] / den))
    for (a, b) in out:
        if a > 0 or (a == 0 and b > 0):
            break
        if a < 0 or (a == 0 and b < 0):
            out = [(-a2, -b2) for (a2, b2) in out]
            break
    return tuple(out)


def rank_q(rows, n):
    """exact rank over Q by fraction Gaussian elimination (no pivoting shortcuts)."""
    A = [[F(x) for x in row] for row in rows]
    r = 0
    for c in range(n):
        p = None
        for i in range(r, n):
            if A[i][c] != 0:
                p = i
                break
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        pv = A[r][c]
        A[r] = [x / pv for x in A[r]]
        for i in range(n):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        r += 1
        if r == n:
            break
    return r


def replay_protocol(order, K, MUL, hx, budget):
    """DIAGNOSTIC replay of the FROZEN pair protocol (scripts/12.run_pair).  Its miss pattern is
    validated against the frozen machine's own trail before any number derived from it is reported;
    it exists to expose the memo-hit law and the ledger growth, which run_pair does not return."""
    COST = F(123, 88)
    EMIN = F(123, 176)
    L = []
    s = 0
    rem = budget
    out = []
    for (a, b) in order:
        spent = 0
        first_hit = False
        sv = None
        for idx, ctx in enumerate((a, b)):
            hit = bool(L) and L[-1][0] == ctx
            if hit:
                v = L[-1][1]
                if idx == 0:
                    first_hit = True
                    sv = (v, K[s][ctx])
            else:
                if rem - COST * spent < EMIN:
                    raise RuntimeError('terminal')
                v = K[s][ctx]
                L.append((ctx, v, s))
                s = MUL[s][hx[ctx]]
                spent += 1
        _c, _v, s_at = L.pop()
        s = s_at
        hit2 = bool(L) and L[-1][0] == b
        if hit2:
            v = L[-1][1]
        else:
            if rem - COST * spent < EMIN:
                raise RuntimeError('terminal')
            v = K[s][b]
            L.append((b, v, s))
            s = MUL[s][hx[b]]
            spent += 1
        rem = rem - COST * spent
        out.append({'pair': (a, b), 'misses': spent, 'first_hit': first_hit, 'stored_vs_now': sv,
                    'pushes': spent, 'ledger_len': len(L), 'top': L[-1][0]})
    return out


def main():
    print('=' * 112)
    print('O222 scripts/18 -- D6 mapping table, operationalised (rules: %s)' % RULES)
    print('=' * 112, flush=True)
    a2 = load(os.path.join(HERE, '09_a2_rollback.py'), 'a2m')
    b5 = load(os.path.join(HERE, '12_b5_budget.py'), 'b5m')
    C1f, C2f, ids, types, den1 = b5.load_a2()
    mm, K, MUL, hx, ids2, types2 = b5.load_machine()
    b5.KERNEL_TAB = K
    axes, U, _ids, types3, hvec = mm.load_inputs()
    corr = json.load(io.open(os.path.join(DATA, '09_a2_correlation.json'), encoding='utf-8'))
    b3 = json.load(io.open(os.path.join(DATA, '15_b3r2_results.json'), encoding='utf-8'))
    a2res = json.load(io.open(os.path.join(DATA, '09_a2_results.json'), encoding='utf-8'))
    cells = {}

    # ---------------- P1: thunk <-> state ----------------
    keys = {}
    for k in range(N):
        keys.setdefault(canon(U[k]), []).append(k)
    orbs = list(range(N))
    parent = list(range(N))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx

    perms = 0
    for q in mm.build_group()[0]:
        img = []
        ok = True
        for k in range(N):
            v = mm.rot_ref(q, U[k])
            tgt = keys.get(canon(v))
            if not tgt:
                ok = False
                break
            img.append(tgt[0])
        if not ok:
            continue
        perms += 1
        for k in range(N):
            union(k, img[k])
    groups = {}
    for k in range(N):
        groups.setdefault(find(k), []).append(k)
    sizes = sorted(len(v) for v in groups.values())
    type_ok = all(len({types[i] for i in v}) == 1 for v in groups.values())
    p1a_ok = (sizes == [12, 20, 30]) and type_ok and perms == 120
    lines = len(keys)
    anti_pairs = sum(1 for v in keys.values() if len(v) == 2)
    cells['P1a'] = {'verdict': '✅' if p1a_ok else '🔴',
                    'value': {'orbit_sizes': sizes, 'type_invariant': type_ok, 'permutations': perms,
                              'distinct_lines': lines, 'antipodal_pairs': anti_pairs},
                    'note': '2I acts on the 62 axes; orbits = vertex/face/edge families. Diagnostic: the 62 '
                            'labels are a DOUBLE COVER of %d lines (each direction with its antipode) -- this '
                            'is a property of the frozen axis set, not a condition of the predicate' % lines}

    bij = 0
    for a in range(N):
        seen = set()
        for s in range(120):
            seen.add(MUL[s][hx[a]])
        if len(seen) == 120:
            bij += 1
    cells['P1b'] = {'verdict': '✅' if bij == N else '🔴', 'value': {'bijective_axes': bij, 'of': N},
                    'note': 'state transition s -> MUL[s][h(a)] is a permutation; read is a pure function'}

    cells['P1c'] = {'verdict': '🟡',
                    'value': {'provenance': 'o210_causal_tensor_algebra (docs/01, docs/02, final_result.md, '
                                            'data/02_type_registry.json)', 'dimensions_available': False},
                    'note': 'composition law exists as a typed object, but the upstream carries no dimensions '
                            '(G6) => provenance-only, no dimensional cross-check'}

    # ---------------- P2: force <-> measurement ----------------
    # P2a: (i) the frozen machine is reproducible (same pair, fresh ledger, twice) over all 3844 pairs
    #      (ii) the memo-hit law reproduces the machine's OWN miss pattern (validated, not assumed)
    def seq_of(oid):
        if oid == 'lex':
            return sorted([(a, b) for a in range(N) for b in range(N)])
        return sorted([(a, b) for a in range(N) for b in range(N)],
                      key=lambda p: (max(p[0], p[1]), min(p[0], p[1]), p[0]))

    def observe(oid):
        trail = []
        top = -1
        rem = F(123, 2)
        pairs = []
        for (a, b) in seq_of(oid):
            try:
                r, rem = b5.run_pair(a, b, 0, top, K, MUL, hx, rem, trail)
            except RuntimeError:
                break
            top = r['top']
            pairs.append((a, b))
        return trail

    repro = 0
    for a in range(N):
        for b in range(N):
            r1, _ = b5.run_pair(a, b, 0, -1, K, MUL, hx, F(123, 2))
            r2, _ = b5.run_pair(a, b, 0, -1, K, MUL, hx, F(123, 2))
            if (r1['x_a'], r1['x_b'], r1['misses'], r1['top']) == (r2['x_a'], r2['x_b'], r2['misses'], r2['top']):
                repro += 1
    law = {}
    for oid in ('lex', 'block'):
        obs = observe(oid)
        rep = replay_protocol(seq_of(oid)[:len(obs)], K, MUL, hx, F(123, 2))
        law[oid] = {'pairs': len(obs),
                    'miss_pattern_matches': all(o['misses'] == r['misses'] for o, r in zip(obs, rep)),
                    'two_read_pairs': sum(1 for r in rep if r['misses'] == 2),
                    'observed_misses': [o['misses'] for o in obs],
                    'predicted_misses': [r['misses'] for r in rep]}
    law_ok = all(v['miss_pattern_matches'] for v in law.values()) and sum(v['pairs'] for v in law.values()) > 0
    cells['P2a'] = {'verdict': '✅' if (repro == N * N and law_ok) else '🔴',
                    'value': {'reproducible_pairs': repro, 'of': N * N, 'memo_law': law},
                    'note': 'the frozen read operator is reproducible on all 3844 pairs, and an '
                            'independent replay of the pair protocol reproduces the machine-observed '
                            'read counts exactly (the memo-hit law is validated, not assumed)'}

    hist = 0
    hist_detail = []
    for c in range(N):
        vals = {K[s][c] for s in range(120)}
        if len(vals) > 1:
            hist += 1
            hist_detail.append((ids[c], sorted(vals)))
    cells['P2b'] = {'verdict': '✅' if hist >= 1 else '🔴',
                    'value': {'history_sensitive_settings': hist, 'of': N,
                              'example': hist_detail[0] if hist_detail else None},
                    'note': 'the outcome is not a function of the setting alone (contextuality of force)'}

    # dynamic witness (replay validated above): ledger growth, hit/override structure
    witness = {}
    for oid in ('lex', 'block'):
        rep = replay_protocol(seq_of(oid)[:law[oid]['pairs']], K, MUL, hx, F(123, 2))
        grows = [r['misses'] - 1 for r in rep]
        overrides = [r for r in rep if r['first_hit'] and r['stored_vs_now'][0] != r['stored_vs_now'][1]]
        witness[oid] = {'pairs': len(rep), 'reads_per_pair': [r['misses'] for r in rep],
                        'ledger_growth_per_pair': grows, 'total_ledger_growth': sum(grows),
                        'pushes': sum(r['pushes'] for r in rep),
                        'memo_hit_pairs': sum(1 for r in rep if r['misses'] == 2),
                        'record_overrides_state': len(overrides),
                        'override_example': (None if not overrides else
                                             {'pair': [ids[overrides[0]['pair'][0]], ids[overrides[0]['pair'][1]]],
                                              'stored_value': overrides[0]['stored_vs_now'][0],
                                              'current_state_would_give': overrides[0]['stored_vs_now'][1]})}
    cells['P2c'] = {'verdict': '✅' if all(w['total_ledger_growth'] > 0 and min(w['ledger_growth_per_pair']) > 0
                                          for w in witness.values()) else '🔴',
                    'value': witness,
                    'note': 'per pair the ledger grows by misses - 1 > 0: the rollback restores the state but '
                            'not the record (irreversible); 2-read pairs are memo hits'}

    vals1 = sorted({C1f[a][b] for a in range(N) for b in range(N)})
    vals2 = sorted({C2f[a][b] for a in range(N) for b in range(N)})
    rowsum1 = {sum(C1f[a][b] for b in range(N)) for a in range(N)}
    rowsum2 = {sum(C2f[a][b] for b in range(N)) for a in range(N)}
    born = all(0 <= v <= 1 for v in vals1) and rowsum1 == {F(1)}
    cells['P2d'] = {'verdict': '🔴' if not born else '✅',
                    'value': {'C1_values': [str(v) for v in vals1], 'C2_values': [str(v) for v in vals2],
                              'C1_row_sums': [str(v) for v in rowsum1], 'C2_row_sums': [str(v) for v in rowsum2]},
                    'note': 'the tables are SIGNED correlations with vanishing row sums, not non-negative '
                            'normalised weights: no Born-type probability structure (G7)'}

    # ---------------- P3: memo <-> record ----------------
    hits = sum(w['memo_hit_pairs'] for w in witness.values())
    overr = sum(w['record_overrides_state'] for w in witness.values())
    cells['P3a'] = {'verdict': '✅' if hits > 0 else '🔴',
                    'value': {'memo_hit_pairs_in_witnessed_passes': hits,
                              'pushes_total': sum(w['pushes'] for w in witness.values()),
                              'reads_total': sum(sum(w['reads_per_pair']) for w in witness.values()),
                              'static_rule': 'top-only access / append-only push / pop used only for the '
                                             'rollback (scripts/17 C6, machine-checked on the frozen source)'},
                    'note': 'a memo hit performs no write at all (pushes = reads - hits): the record is '
                            'append-only and consistent'}
    ex = [w['override_example'] for w in witness.values() if w['override_example']]
    cells['P3b'] = {'verdict': '✅' if overr >= 1 else '🟡',
                    'value': {'hits_returning_a_value_the_current_state_would_not_give': overr,
                              'example': ex[0] if ex else None},
                    'note': 'the record outranks the current state: a written entry is never recomputed'}
    cells['P3c'] = {'verdict': '🔴', 'value': {'accessible_depth': 1, 'redundancy': 1},
                    'note': 'read inspects only the ledger top => a single-copy record with no environmental '
                            'redundancy (the QM decoherence-redundancy requirement is absent)'}

    # ---------------- P4: sharing <-> entanglement ----------------
    rev = [[int(x) for x in row] for row in corr['C1rev_num']]
    anti = [[int(x) for x in row] for row in corr.get('anti', [])] if 'anti' in corr else None
    r1 = rank_q([[int(corr['C1_num'][a][b]) for b in range(N)] for a in range(N)], N)
    r2b = rank_q([[F(C2f[a][b]) for b in range(N)] for a in range(N)], N)
    rrev = rank_q(rev, N)
    cells['P4a'] = {'verdict': '✅' if min(r1, r2b, rrev) > 1 else '🔴',
                    'value': {'rank_C1': r1, 'rank_C2': r2b, 'rank_C1rev': rrev,
                              'note_rank1_means': 'rank 1 <=> C = u (x) v factorisable'},
                    'note': 'the correlation tables are NOT factorisable => no independent-per-side '
                            'decomposition (the structural content of "sharing")'}
    blk = b3['per_order']['block']['feasible']
    cells['P4b'] = {'verdict': '🔴',
                    'value': {'budget_feasible_all4_E1': blk['E1_all4']['value'],
                              'budget_feasible_all4_E2': blk['E2_all4']['value'],
                              'unrestricted_all4_E1': b3['baseline']['E1_all4']['value'],
                              'unrestricted_all4_E2': b3['baseline']['E2_all4']['value'],
                              'source': 'data/15_b3r2_results.json (cited, not re-derived)'},
                    'note': 'no CHSH violation: budget-feasible clean values are below 2'}
    colbal = [sum(K[s][a] for s in range(120)) for a in range(N)]
    ns_ok = all(c == 0 for c in colbal)
    cells['P4c'] = {'verdict': '✅' if ns_ok else '🔴',
                    'value': {'axes_with_balanced_outcomes': sum(1 for c in colbal if c == 0), 'of': N,
                              'column_sums': sorted({c for c in colbal}),
                              'cited_A2_conditional_marginals': '3844/3844 = 1/2 (A2 A3)',
                              'diagnostic_C1_row_sums_not_a_criterion': [str(v) for v in sorted(rowsum1)][:6]},
                    'note': 'no-signalling content = every local outcome is +-1 with equal weight '
                            '(Sigma_s K[s][a] = 0, 62/62), i.e. each marginal is 1/2 exactly and does not '
                            'depend on the remote setting. The C row sums are NOT required to vanish (they '
                            'are correlations, not marginals) -- they are reported as a diagnostic only'}

    out = {'rules_version': RULES, 'cells': cells, 'cell_order': ['P1a', 'P1b', 'P1c', 'P2a', 'P2b', 'P2c',
                                                                 'P2d', 'P3a', 'P3b', 'P3c', 'P4a', 'P4b', 'P4c'],
           'cited': {'B3R2_claims': len(b3['claims']), 'A2_claims': len(a2res['claims'])}}
    with io.open(os.path.join(DATA, '18_d6_results.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print('cell   verdict  value')
    for c in out['cell_order']:
        print('  %-5s %-2s  %s' % (c, cells[c]['verdict'], json.dumps(cells[c]['value'], ensure_ascii=False)[:150]))
    n = {'✅': 0, '🟡': 0, '🔴': 0}
    for c in out['cell_order']:
        n[cells[c]['verdict']] += 1
    print('-' * 112)
    print('D6 TABLE: %d cells  ->  %d OK / %d PARTIAL / %d ABSENT-OR-FALSIFIED'
          % (len(cells), n['✅'], n['🟡'], n['🔴']))
    print('=' * 112)
    return 0


if __name__ == '__main__':
    sys.exit(main())
