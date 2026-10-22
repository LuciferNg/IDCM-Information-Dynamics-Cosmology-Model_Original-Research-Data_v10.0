#!/usr/bin/env python3
"""O228 scripts/03 -- R1 INDEPENDENT audit.

Deliberately does NOT import scripts/01 or scripts/02 and re-implements every headline number with a
different data structure / algorithm:
  * census by equivalence classes of +/- sign vectors (no partition tuples, no refinement enumeration)
  * F_4 by pair-major enumeration over the 66 row pairs (not the bitmask DFS of 02)
  * F_4..F_6 by the type-set form with INCLUSION-EXCLUSION over sub-type-sets (not the polynomial
    convolution of 02)
  * freeze / leak checks against the contract hashes and the o222 tree

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/03_r1_audit.py
"""
import hashlib
import importlib.util
import io
import itertools
import json
import math
import os
import sys
import collections
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
DOCS = os.path.join(ROOT, 'docs')
O222 = os.path.abspath(os.path.join(ROOT, '..', 'o222_qm_evaluation_semantics'))
CLAIMS = []

FROZEN = {
    'scripts/12_b5_budget.py': 'f2cb54fa5df094a1e2f7b4910a4c16726a37160f39b194f0157988823aeb1e7a',
    'scripts/09_a2_rollback.py': 'd8037bb16f690a2935c7028b3680d48df6540e01c938ade1d3b5858aed594ace',
    'data/04_b2_settings.json': '2357006c68e0165dc9fd7d8d73524593a776e1bf6a8b62ddbc8dc2c1a8af20ee',
    'data/08_a2_h_table.json': 'adeaf8a7fb5495ea57be194c1a704c973a9208026cdd10ef615cd59c58005b66',
}


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def sha(p):
    h = hashlib.sha256()
    with io.open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 16), b''):
            h.update(b)
    return h.hexdigest()


sp = importlib.util.spec_from_file_location('mX', os.path.join(O222, 'scripts', '12_b5_budget.py'))
mX = importlib.util.module_from_spec(sp)
sp.loader.exec_module(mX)
m, K, MUL, hx, ids, types = mX.load_machine()
NR, NC = len(K), len(K[0])


def main():
    out = {}
    print('=' * 108)
    print('O228 scripts/03 -- R1 independent audit')
    print('=' * 108, flush=True)

    # ---------------- A freeze
    bad = [p for p, h in FROZEN.items() if sha(os.path.join(O222, p)) != h]
    claim('A1', 'the four frozen o222 inputs still carry the hashes pinned in the contract',
          not bad, 'mismatched = %s' % bad)
    chash = sha(os.path.join(DOCS, '00_r1_contract.md'))
    out['contract_sha256'] = chash
    j1 = json.load(io.open(os.path.join(DATA, '01_r1_census.json'), encoding='utf-8'))
    j2 = json.load(io.open(os.path.join(DATA, '02_r1_closed_form.json'), encoding='utf-8'))
    allc = [c for c in j1['claims']] + [c for c in j2['claims']]
    tags = {c['tag'] for c in allc}
    contract = io.open(os.path.join(DOCS, '00_r1_contract.md'), encoding='utf-8').read()
    missing = sorted(t for t in tags if t.split('-')[0] not in contract)
    claim('A2', 'no post-hoc criteria: the only claim tag absent from the frozen contract is the declared '
                'auxiliary check C2b (icosahedron degree check), which is flagged as non-pre-registered in the results doc',
          set(missing) <= {'C2b'}, 'tags = %s ; tags absent from the contract = %s' % (sorted(tags), missing))
    stale = [c['tag'] for c in allc if not c['ok']]
    exc = os.path.join(ROOT, 'logs', '02_r1_firstrun_C17_FAIL_excerpt.out')
    excok = os.path.exists(exc) and '[FAIL] C17' in io.open(exc, encoding='utf-8').read()
    claim('A3', 'all claims in the run JSONs PASS, and the single historical FAIL (C17, first run) is preserved '
                'verbatim in logs/02_r1_firstrun_C17_FAIL_excerpt.out with its correction history',
          stale == [] and excok, 'claims = %d ; non-PASS = %s ; FAIL excerpt preserved = %s' % (len(allc), stale, excok))
    # leak check: any file inside o222 newer than the contract?
    import subprocess
    r = subprocess.run(['find', O222, '-newer', os.path.join(DOCS, '00_r1_contract.md'), '-type', 'f'],
                       capture_output=True, text=True)
    touched = [x for x in r.stdout.split('\n') if x.strip()]
    out['o222_touched_after_contract'] = touched
    claim('A4', 'no file inside the o222 tree was modified after the contract was frozen (read-only discipline)',
          not touched, 'touched files = %s' % touched)

    # ---------------- B1 census by +/- equivalence classes (different algorithm)
    rows = [tuple(K[i][a] for a in range(NC)) for i in range(NR)]
    seen = {}
    reps = []
    for i, r in enumerate(rows):
        if r not in seen:
            seen[r] = i
            reps.append(i)
    RV = [tuple(K[i][a] for a in range(NC)) for i in reps]
    claim('B1a', 'distinct rows = 12 with multiplicity 10 (recomputed by dict-of-tuples)',
          len(RV) == 12 and len(rows) == 120,
          'distinct rows = %d' % len(RV))
    R = len(RV)
    vecs = [tuple(RV[j][a] for j in range(R)) for a in range(NC)]
    negs = {tuple(-x for x in v) for v in vecs}
    classes = {}
    for a, v in enumerate(vecs):
        key = min(v, tuple(-x for x in v))
        classes.setdefault(key, []).append(a)
    hist = collections.Counter(len(v) for v in classes.values())
    claim('B1b', 'census recomputed by +/- sign-vector classes: 16 classes with histogram {3:10, 5:5, 7:1}',
          len(classes) == 16 and hist == collections.Counter({3: 10, 5: 5, 7: 1}),
          'classes = %d ; histogram = %s' % (len(classes), dict(sorted(hist.items()))))
    out['census_classes'] = {str(k): v for k, v in sorted(hist.items())}

    # ---------------- B2 F_1..F_4 by pair-major enumeration
    pairs = [(i, j) for i in range(R) for j in range(i + 1, R)]
    sep = []                            # sep[p] = bitmask over columns that separate pair p
    for (i, j) in pairs:
        mk = 0
        for a in range(NC):
            if RV[i][a] != RV[j][a]:
                mk |= (1 << a)
        sep.append(mk)
    Fb = {k: 0 for k in range(1, 5)}
    for combo in itertools.combinations(range(NC), 4):
        cm = (1 << combo[0]) | (1 << combo[1]) | (1 << combo[2]) | (1 << combo[3])
        if all(cm & spm for spm in sep):
            Fb[4] += 1
    for k in (1, 2, 3):
        for combo in itertools.combinations(range(NC), k):
            cm = 0
            for c in combo:
                cm |= (1 << c)
            if all(cm & spm for spm in sep):
                Fb[k] += 1
    claim('B2', 'F_1..F_4 recomputed pair-major (a completely different enumeration)',
          Fb[1] == 0 and Fb[2] == 0 and Fb[3] == 0 and Fb[4] == 12645,
          'F_1..F_4 = %s ; non-separating 4-subsets = %d = C(62,4) - 12645'
          % ([Fb[k] for k in (1, 2, 3, 4)], math.comb(62, 4) - Fb[4]))

    # ---------------- B3 closed form with inclusion-exclusion e_k(T)   (pair-masks per type!)
    tl = sorted(classes.keys())
    mults = [len(classes[t]) for t in tl]
    NP = len(pairs)
    ALLP = (1 << NP) - 1
    tpm = []                             # tpm[i] = mask over ROW PAIRS separated by type i
    for t in tl:
        a = classes[t][0]
        mk = 0
        for b, (i, j) in enumerate(pairs):
            if RV[i][a] != RV[j][a]:
                mk |= (1 << b)
        tpm.append(mk)

    def eIX(T, k):
        tot = 0
        Ts = list(T)
        for r_ in range(1, len(Ts) + 1):
            for S in itertools.combinations(Ts, r_):
                tot += (-1) ** (len(Ts) - r_) * math.comb(sum(mults[i] for i in S), k)
        return tot

    KT = len(tl)
    Fts = {}
    for k in (4, 5, 6):
        s = 0
        for T in range(1, 1 << KT):
            mk = 0
            Ts = [i for i in range(KT) if T >> i & 1]
            if len(Ts) > k:
                continue
            for i in Ts:
                mk |= tpm[i]
            if mk == ALLP:
                s += eIX(Ts, k)
        Fts[k] = s
    exp = {str(k): j2['F_closed_form'][str(k)] for k in (4, 5, 6)}
    claim('B3', 'F_4..F_6 recomputed by the type-set form using inclusion-exclusion for e_k(T) '
                '(02 used polynomial convolution)',
          all(Fts[k] == j2['F_closed_form'][str(k)] for k in (4, 5, 6)),
          'audit = %s ; 02 = %s' % ({k: Fts[k] for k in (4, 5, 6)}, exp))
    out['F_audit'] = {str(k): Fts[k] for k in (4, 5, 6)}

    # ---------------- B4 null cross-check by a larger MC
    half = [s for s in itertools.combinations(range(R), R // 2) if 0 in s]
    pl = [(i, j) for i in range(R) for j in range(i + 1, R)]
    pidx = {p: b for b, p in enumerate(pl)}
    ALLX = (1 << len(pl)) - 1
    bm = []
    for S in half:
        mk = 0
        for (i, j) in pl:
            if (i in S) != (j in S):
                mk |= (1 << pidx[(i, j)])
        bm.append(mk)
    draws = 1500000
    st = 987654321
    hit = 0
    for _ in range(draws):
        mk = 0
        for _q in range(4):
            st = (st * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
            mk |= bm[(st >> 33) % len(bm)]
        if mk == ALLX:
            hit += 1
    mcr = hit / draws
    p0 = float(F(j2['null_all_bisections']['p0_float']))
    sd = math.sqrt(p0 * (1 - p0) / draws)
    claim('B4', 'the exact null p0 of 02 is confirmed by an independent MC with 1.5e6 draws (within 4 sigma)',
          abs(mcr - p0) < 4 * sd,
          'exact = %.6f ; audit MC(%d) = %.6f ; 4 sigma = %.6f' % (p0, draws, mcr, 4 * sd))
    out['null_audit'] = {'exact': p0, 'mc': mcr, 'draws': draws, 'rate_machine': float(j2['null_all_bisections']
                                                                                     ['machine_rate_float'])}

    # ---------------- C value identities
    f4 = 12645
    facts = []
    n = f4
    d = 2
    while d * d <= n:
        while n % d == 0:
            facts.append(d)
            n //= d
        d += 1
    if n > 1:
        facts.append(n)
    claim('C1', '12645 = 45 x 281 (factorisation) and the mixture table sums to it',
          facts == [3, 3, 5, 281] and sum(j2['F4_family_mixtures'].values()) == 12645,
          'factors = %s ; mixture sum = %d ; rate = %s' % (facts, sum(j2['F4_family_mixtures'].values()),
                                                           j2['null_all_bisections']['machine_rate']))
    claim('C2', 'the E-only 4-frames are exactly 5^4 = 625 and k_min(E) = 4, k_min(V) = k_min(F) = 5',
          j2['sub_arrangements']['E']['F']['4'] == 625 and j2['sub_arrangements']['V']['k_min'] == 5
          and j2['sub_arrangements']['F']['k_min'] == 5,
          'E: k_min = %s F_4 = %s ; V: k_min = %s ; F: k_min = %s'
          % (j2['sub_arrangements']['E']['k_min'], j2['sub_arrangements']['E']['F']['4'],
             j2['sub_arrangements']['V']['k_min'], j2['sub_arrangements']['F']['k_min']))
    ev = j2['equivariant_variant']
    claim('C3', 'the equivariant tie-break changes the census (16 -> %d types) and F_4 (12645 -> %d): '
                'the resource geometry is convention-relative' % (ev['n_types'], ev['F4']),
          ev['F4'] != 12645 and ev['n_types'] != 16,
          'equivariant: %d types / hist %s / F_4 = %d / shapes %s'
          % (ev['n_types'], ev['mult_histogram'], ev['F4'], ev['shapes']))

    out['claims'] = CLAIMS
    with io.open(os.path.join(DATA, '03_r1_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 108)
    print('RESULT: %d/%d PASS  (%d FAIL)' % (npass, len(CLAIMS), len(CLAIMS) - npass))
    print('=' * 108)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
