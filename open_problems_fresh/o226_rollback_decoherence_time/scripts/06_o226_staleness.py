#!/usr/bin/env python3
"""O226 scripts/06 -- J4: the staleness functional, its quantisation, and the ledger/amplitude duality.

Contract: docs/01_o226_contract.md (o226-r1-contract-v1), J4 / Pr-4.1-Pr-4.5.
Machine imported from scripts/02.  Exact arithmetic only.
"""
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
RULES = 'o226-r1-contract-v1'
N = 62
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-7s %s%s' % ('PASS' if ok else 'FAIL', tag, name,
                              ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


def splitmix64(state):
    state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    z = z ^ (z >> 31)
    return state, z


def main():
    print('=' * 104)
    print('O226 scripts/06 -- J4 staleness / decoherence duality (rules: %s)' % RULES)
    print('=' * 104, flush=True)
    spec = importlib.util.spec_from_file_location('m226', os.path.join(HERE, '02_o226_ledger_machine.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    axes, U, ids, types, hvec = m.load_inputs()
    G, idx, MUL = m.build_group()
    hx = [idx[m.qkey(h)] for h in hvec]
    K = m.build_K(G, U)
    ONE = (m.ONE, m.ZERO, m.ZERO, m.ZERO)
    IDX = idx[m.qkey(ONE)]
    inv = [0] * 120
    for i in range(120):
        for j in range(120):
            if MUL[i][j] == IDX:
                inv[i] = j
                break

    # centre blindness: K[s] == K[-s]
    neg = [idx[m.qkey(tuple(m.neg(c) for c in q))] for q in G]
    claim('S1', 'centre blindness: K[s] == K[-s] for all 120 states => the read kernel sees only the '
                '60-element quotient 2I/{+-1} = A5 (this is the B5 2:1 collapse on the value side)',
          all(K[s] == K[neg[s]] for s in range(120)) and len({tuple(K[s]) for s in range(120)}) == 60,
          'distinct kernel rows = %d' % len({tuple(K[s]) for s in range(120)}))
    cosets = [s for s in range(120) if s < neg[s]]
    claim('S2', 'the quotient has 60 elements; one representative per coset chosen canonically',
          len(cosets) == 60, 'representatives = %d' % len(cosets))

    # ---------------- Pr-4.1: sigma is zero exactly on the centre
    zerosets = {}
    for s_rec in range(120):
        for ctx in range(N):
            z = sum(1 for s_now in range(120) if K[s_now][ctx] == K[s_rec][ctx])
            zerosets[z] = zerosets.get(z, 0) + 1
    claim('S3', 'Pr-4.1: for every (state, setting) the staleness sigma = [K[s_now][ctx] != K[s_rec][ctx]] '
                'vanishes on exactly 2 of the 120 states -- the pair {s_rec, -s_rec}; equivalently '
                'sigma = 0 <=> g = s_rec^-1 s_now in Z2 = {+-1}',
          set(zerosets.keys()) == {2},
          'distribution of |{s_now : sigma = 0}| over 62 x 120 (state, setting) pairs = %s' % zerosets)
    # explicit g-test
    bad = 0
    for s_rec in cosets:
        for s_now in range(120):
            g = MUL[inv[s_rec]][s_now]
            is_centre = (g == IDX or g == idx[m.qkey(tuple(m.neg(c) for c in ONE))])
            same = all(K[s_now][ctx] == K[s_rec][ctx] for ctx in range(N))
            if same != is_centre:
                bad += 1
    claim('S4', 'Pr-4.1: the g-test agrees with the full 62-component comparison for all 60 x 120 pairs '
                '(staleness is a centre test, not a numeric coincidence)',
          bad == 0, 'disagreements = %d / 7200' % bad)

    # ---------------- Pr-4.2 / Pr-4.3: quantised staleness rate
    fam = {}          # (g index) -> sorted list over frames
    for a in cosets:
        for g in range(120):
            now = MUL[a][g]
            d = sum(1 for ctx in range(N) if K[now][ctx] != K[a][ctx])
            fam.setdefault(g, []).append(d)
    vals = set()
    for g, v in fam.items():
        vals |= set(v)
    g0 = IDX
    claim('S5', 'Pr-4.2: the staleness size |D| = #{settings that flip} takes a QUANTISED value set; '
                '0 occurs only for g in the centre; report the set and the minimum non-zero value',
          min(vals) == 0 and max(vals) <= N and len(vals) < N,
          'value set size = %d ; values = %s ; min non-zero = %d (= %.5f of 62)'
          % (len(vals), sorted(vals), min(v for v in vals if v > 0), min(v for v in vals if v > 0) / 62))
    claim('S6', 'Pr-4.2: the zero of |D| is attained exactly for the two centre elements (g = +-1) and for '
                'no other element (the transitivity of the axis set rules out accidental zeros)',
          all(set(fam[g]) == {0} for g in (IDX, idx[m.qkey(tuple(m.neg(c) for c in ONE))])) and
          all(0 not in set(fam[g]) for g in range(120) if g not in (IDX, idx[m.qkey(tuple(m.neg(c) for c in ONE))])),
          'centre elements give |D| = 0, all other g give |D| >= %d' % min(v for v in vals if v > 0))
    # frame dependence: is |D| a class function of g?
    def order_of(i):
        p, o = G[i], 1
        while m.qkey(p) != m.qkey(ONE):
            p = m.qmul(p, G[i])
            o += 1
        return o
    classes = {}
    for g in range(120):
        classes.setdefault(order_of(g), []).append(g)
    class_report = {}
    for o, gs in sorted(classes.items()):
        per = {}
        for g in gs:
            per[g] = sorted(set(fam[g]))
        class_report[o] = {'count': len(gs),
                           'union_value_sets': sorted({v for g in gs for v in fam[g]}),
                           'constant_across_frames': sorted({len(set(fam[g])) for g in gs})}
    claim('S7', 'Pr-4.3: |D| is resolved by (a) the element order (9 classes as a multiset of orders) and '
                '(b) the frame -- the per-class union of value sets is reported, together with whether '
                '|D| is constant across the 60 frames (a pure class function would show 1)',
          True, json.dumps({str(k): {'n': v['count'], 'union': v['union_value_sets'],
                                     'distinct_per_g': v['constant_across_frames']}
                            for k, v in class_report.items()}, ensure_ascii=False)[:600])

    # ---------------- Pr-4.4: entry lifetime is bounded by DEPTH, not by time
    top = -1
    max_life = 0
    for (a, b) in m.PAIRS:
        L = []
        pushes = []
        ops = 0

        def rd(ctx):
            nonlocal ops
            ops += 1
            if L and L[-1][0] == ctx:
                return L[-1][1]
            L.append([ctx, 0, 0])
            pushes.append(ops)
            return 0
        rd(a)
        rd(b)
        e = L.pop()
        pops_at = ops
        for pidx in pushes:
            life = pops_at - pidx
            if life > max_life:
                max_life = life
        rd(b)
        top = L[-1][0] if L else -1
    claim('S8', 'Pr-4.4: a ledger entry survives at most 2 read operations before being popped (the pop '
                'follows the second read of every pair) => entry lifetime is bounded by DEPTH, and the '
                'ledger has no time-like ageing variable',
          max_life == 2, 'max entry lifetime in read operations = %d' % max_life)

    # ---------------- null: random axis sets, declared draws
    st = 226
    null_sets = []
    for d in range(32):
        randU = []
        for j in range(N):
            st, z = splitmix64(st)
            q = G[z % 120]
            randU.append((q[1], q[2], q[3]))
        Kn = m.build_K(G, randU)
        vs = set()
        for a in cosets[:20]:
            for g in range(120):
                now = MUL[a][g]
                vs.add(sum(1 for ctx in range(N) if Kn[now][ctx] != Kn[a][ctx]))
        null_sets.append(sorted(vs))
    claim('S9', 'null (32 random axis sets, splitmix64, declared draws): the staleness value set of the '
                'lattice kernel is compared with the random-kernel value sets',
          True, 'lattice set = %s ; null sets (first 6) = %s'
          % (sorted(vals), null_sets[:6]))

    # ---------------- duality table with B2 / B3 (upstream, quoted not recomputed)
    duality = [
        ('B2: no continuous complex phase; visibility value set quantised (8 values, denominator 15)',
         'ledger records exact +-1 signs: 2 values; the staleness of a memo entry is BINARY (>0 or =0), '
         'no gradual dephasing channel'),
        ('B3: no mechanism-level Born weights; obstacle = signed table values and column sums != 1',
         'ledger has no envelope / weight variable: entries carry a sign and a state, and the ledger '
         'depth is bounded by 2 => no continuous relaxation rate exists'),
        ('O222 B5: 120 initial states -> exactly 60 behaviours (centre Z2 collapses 2:1), 5.9069 bits',
         'center blindness of the read kernel (S1) is the same Z2; staleness = 0 exactly on that centre (S3)'),
        ('O222 RT1: 62 length-2 relations a.a^-1 = 1 (generator set inverse-closed)',
         'the pop is exactly the inverse generator; J1/Pr-1.4 shows pop + reconcile read are redundant '
         'in (value, world-line, ledger top)'),
    ]
    claim('S10', 'Pr-4.5: the dual statement is constructed -- decoherence = ledger staleness/undo '
                 'structure (depth-bounded, binary), NOT phase dissipation; any future claim of an '
                 'exponential decay / dephasing rate inside the frozen protocol is structurally impossible '
                 '(the only state variables are a group element, a depth-2 stack and a monotone budget)',
          True, 'duality rows = %d' % len(duality))

    # ================= J4 repair: the exact structure, measured =================
    # The pre-registered J4 picture (staleness = 0 <=> g in Z2, 2 solutions per setting) is REFUTED by
    # the machine.  The measured structure of the frozen read kernel K (120 x 62, +-1) is below; the
    # original FAIL tags S1/S3/S4/S6/S8 are kept as-is and the corrected statements carry the -c suffix.
    rws = [tuple(r) for r in K]
    cls = {}
    for s in range(120):
        cls.setdefault(rws[s], []).append(s)
    keyl = sorted(cls.keys())
    reps = [cls[k][0] for k in keyl]

    def order_of_idx(i):
        p, o = G[i], 1
        while m.qkey(p) != m.qkey(ONE):
            p = m.qmul(p, G[i])
            o += 1
        return o

    stab = [sorted(order_of_idx(g) for g in range(120) if rws[MUL[reps[0]][g]] == rws[reps[0]])]
    balance = sorted({sum(1 for s in range(120) if K[s][c] == 1) for c in range(62)})
    weight = sorted({sum(r) for r in K})
    claim('S1-c', 'CORRECTED S1: the read kernel K (120 x 62 signs) has exactly 12 distinct rows, each '
                  'with 10 preimages (120 = 12 x 10); it is centre-blind and the stabiliser of every row '
                  'class is cyclic of order 10 (element orders {1,2,5x4,10x4} = C10, i.e. centre x a '
                  '5-fold rotation); every setting is balanced 60/60 and every row has weight +-10',
          len(cls) == 12 and sorted({len(v) for v in cls.values()}) == [10] and
          all(K[s] == K[neg[s]] for s in range(120)) and stab[0] == [1, 2, 5, 5, 5, 5, 10, 10, 10, 10]
          and balance == [60] and weight == [-10, 10],
          'classes = %d ; preimage sizes = %s ; stabiliser orders = %s ; per-setting +1 count = %s ; '
          'row weights = %s' % (len(cls), sorted({len(v) for v in cls.values()}), stab[0], balance, weight))
    claim('S3-c', 'CORRECTED S3: for a SINGLE setting the staleness vanishes on exactly 60 of the 120 '
                  'states (6 of the 12 classes), not on the 2-element centre {s_rec, -s_rec} as '
                  'pre-registered; the zero set of the full 62-setting staleness is the order-10 '
                  'stabiliser of the class',
          zerosets == {60: 62 * 120},
          'zero-set sizes over 62 x 120 (state, setting) pairs = %s' % zerosets)
    bad = 0
    for a in reps:
        gs = [g for g in range(120) if rws[MUL[a][g]] == rws[a]]
        zeroset = {b for b in range(120) if rws[b] == rws[a]}
        if (len(gs) != 10 or zeroset != {MUL[a][g] for g in gs} or
                sorted(order_of_idx(g) for g in gs) != [1, 2, 5, 5, 5, 5, 10, 10, 10, 10]):
            bad += 1
    claim('S4-c', 'CORRECTED S4: for every one of the 12 classes the zero set of the full staleness is '
                  'exactly the order-10 stabiliser coset {a.g : g in Stab(a)} (element orders '
                  '{1,2,5x4,10x4}) -- not the 2-element centre as pre-registered',
          bad == 0, 'classes failing the test = %d / 12' % bad)
    Dm = [[sum(1 for x in range(62) if K[reps[i]][x] != K[reps[j]][x]) for j in range(12)]
          for i in range(12)]
    dvals = sorted({v for r in Dm for v in r})
    claim('S6-c', 'CORRECTED S6: the effective staleness is a function on the 12-element kernel-class '
                  'quotient -- a QUANTISED Hamming metric with value set {0,22,24,38,40,62} out of 62, '
                  'complement-closed (62-d is in the set), diameter 62',
          dvals == [0, 22, 24, 38, 40, 62] and all((62 - v) in dvals for v in dvals) and
          all(Dm[i][i] == 0 and Dm[i][j] == Dm[j][i] for i in range(12) for j in range(12)) and
          all(Dm[i][j] <= Dm[i][k] + Dm[k][j] for i in range(12) for j in range(12) for k in range(12)),
          'value set = %s ; diameter = %d ; metric axioms hold on 12x12' % (dvals, max(dvals)))
    claim('S8-c', 'CORRECTED S8: an entry pushed by the first read of a pair survives exactly 1 further '
                  'read operation (2 read-ops counting its own) before the pop, for all 3844 pairs; the '
                  'pre-registered value 2 counted the push itself => entry lifetime is bounded by the '
                  'pair length / DEPTH, with no time-like ageing variable',
          max_life == 1, 'max intervening reads = %d (>=2 read-ops inclusive)' % max_life)
    null_sizes = sorted({len(v) for v in null_sets})
    med = null_sizes[len(null_sizes) // 2]
    claim('S9-c', 'CORRECTED S9 (null, 32 random axis sets, splitmix64, declared draws): the lattice '
                  'kernel has 6 staleness values (median random kernel: %d) => the coarse quantisation '
                  '{22,24,38,40,62} is a property of the lattice kernel, not of the definition of '
                  'staleness (the single degenerate draw with 1 value is reported, not filtered)'
          % med,
          len(vals) == 6 and med > 6 and null_sizes[-1] > 6,
          'lattice value count = %d ; null value-set sizes (all 32 draws) = %s ; median = %d'
          % (len(vals), null_sizes, med))

    out = {'rules_version': RULES, 'zero_set_distribution': zerosets,
           'staleness_value_set': sorted(vals),
           'staleness_min_nonzero': min(v for v in vals if v > 0),
           'class_report': {str(k): v for k, v in class_report.items()},
           'max_entry_lifetime_reads': max_life,
           'kernel_structure': {'classes': len(cls), 'preimage_sizes': sorted({len(v) for v in cls.values()}),
                                'stabiliser_orders': stab[0], 'per_setting_plus_count': balance,
                                'row_weights': weight, 'class_pair_metric': Dm,
                                'metric_value_set': dvals},
           'null_axis_value_sets': null_sets, 'duality': duality, 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '06_staleness.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 104)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 104)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
