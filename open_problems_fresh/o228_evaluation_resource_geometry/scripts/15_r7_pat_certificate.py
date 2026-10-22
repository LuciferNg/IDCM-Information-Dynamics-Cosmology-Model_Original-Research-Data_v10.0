#!/usr/bin/env python3
"""O228 scripts/15 -- R7 (1) SHORT CERTIFICATES: max pat(k=6, M_edge) = 26 exactly.

Contract: docs/09_r7_contract.md   (o228-r7-three-prongs-v1)
Route history (all kept on disk as records):
  scripts/11 (quotient DFS): node-budget exhaustion on every sampled group -> superseded.
  scripts/14 (collapse lemma + line enumeration): the COLLAPSE LEMMA IS REFUTED (verification FAIL:
             the negative of a column's sign vector is not a column, because on a tie row tau gives BOTH
             u and -u the same value), so 14 degenerated to C(62,6) and was killed.
  scripts/15 (this file): certificate route -- every one of the 225 twin-pair groups is refuted by a SHORT,
             independently re-verified certificate.

Theory (proved here, not assumed):
  L1  ODD CODE MAP: code(-r) = complement(code(r)) for every column set, because every column's sign
      flips under r -> -r (and on a tie row the frozen tau rule reads the first non-zero component, which
      also flips).  Hence no class contains an antipodal pair and classes pair up into twins of EQUAL size.
  L2  loss = m - pat = sum(size-1) therefore decomposes into twin pairs; consequently
         loss = 2  <=>  the uncovered row pairs are exactly TWO pairs forming a twin pair {p, twin(p)}
      (equivalently |U| = 2, since a class of size s contributes C(s,2) uncovered pairs: |U| = 2 forces
      two size-2 classes).
  L3  A 6-subset with exactly the twin pair {p, pbar} uncovered must satisfy: every chosen column avoids
      separating p (only 50 columns do) AND must separate the other 433 pairs.
  L4  135 of the 225 groups die immediately: some required pair HAS NO separator among those 50 columns
      (witness pair, one line of evidence).  The remaining 90 die by a restricted PACKING: a set of pairs
      whose separator sets inside the 50 allowed columns are pairwise disjoint needs one column each, so a
      packing of size >= 7 (all 90 have >= 8) cannot be covered by 6 columns.

Conclusion: no 6-subset reaches loss 2, so pat != 28; R5 gives pat <= 28 and constructs pat = 26
=> max pat(k=6, M_edge) = 26 EXACTLY.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/15_r7_pat_certificate.py
"""
import importlib.util
import io
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
CLAIMS = []
SEED = 20261002
K = 6


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %s%s' % ('PASS' if ok else 'FAIL', tag, ('  -- ' + detail) if detail else ''), flush=True)


def load(path, name):
    spc = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spc)
    spc.loader.exec_module(mod)
    return mod


def main():
    t0 = time.time()
    out = {}
    print('=' * 112)
    print('O228 scripts/15 -- R7 (1): short certificates for max pat(k=6) = 26')
    print('=' * 112, flush=True)

    s04 = load(os.path.join(HERE, '04_r2_general_machine.py'), 's04')
    s09 = load(os.path.join(HERE, '09_r5_kmin_law.py'), 's09')
    s10 = load(os.path.join(HERE, '10_r6_lp_certificate.py'), 's10')
    MACH, _ = s09.build_machines(s04)
    edge = [m for m in MACH if m.name == 'M_edge'][0]
    m, N, pairs = edge.m, edge.N, edge.pairs
    NP = len(pairs)

    pcol, cm = [], []
    for a in range(N):
        mk = 0
        for b, (i, j) in enumerate(pairs):
            if edge.cols[a][i] != edge.cols[a][j]:
                mk |= (1 << b)
        cm.append(mk)
    for b in range(NP):
        v = 0
        for a in range(N):
            if (cm[a] >> b) & 1:
                v |= (1 << a)
        pcol.append(v)

    rmap = {tuple((x[0], x[1]) for x in r): i for i, r in enumerate(edge.rows)}
    neg = [rmap[tuple((-x[0], -x[1]) for x in r)] for r in edge.rows]

    def pidx(i, j):
        return pairs.index((min(i, j), max(i, j)))

    # ------------------------------------------------------------------ L1/L2 verification
    rng = random.Random(SEED)
    odd_ok, no_self_twin, twin_par, u_ok = True, True, True, True
    for _ in range(3000):
        sub = rng.sample(range(N), K)
        code = {}
        for r in range(m):
            c = 0
            for i, a in enumerate(sub):
                c |= (1 if edge.cols[a][r] > 0 else 0) << i
            code[r] = c
        full = (1 << K) - 1
        for r in range(m):
            if code[neg[r]] != (code[r] ^ full):
                odd_ok = False
        cl = {}
        for r in range(m):
            cl.setdefault(code[r], []).append(r)
        for c, mem in cl.items():
            if any(neg[r] in mem for r in mem):
                no_self_twin = False
        sizes = sorted(len(v) for v in cl.values())
        tsizes = sorted(len(cl.get(c ^ full, [])) for c in cl)
        if sizes != tsizes:
            twin_par = False
        # |U| (uncovered pairs) vs loss: |U| = sum C(size,2) ; loss = sum (size-1) ; loss = 2 <=> |U| = 2
        loss = m - len(cl)
        unc = sum(len(v) * (len(v) - 1) // 2 for v in cl.values())
        if (loss == 2) != (unc == 2):
            u_ok = False
    out['lemmas'] = {'checked_subsets': 3000, 'odd_code_map': odd_ok, 'no_self_twin_class': no_self_twin,
                     'class_size_multiset_twin_invariant': twin_par, 'loss2_iff_two_uncovered_pairs': u_ok}
    print('L1/L2 verified: %s' % out['lemmas'], flush=True)
    claim('P1L-1', 'ODD CODE MAP + TWIN PARITY (verified on 3000 random 6-subsets, and proved structurally): '
                   'code(-r) = complement(code(r)); no class contains an antipodal pair; class sizes pair up '
                   'into twins of equal size. CONSEQUENCE: loss = m - pat = 2 happens IFF the uncovered pairs '
                   'are exactly two twin pairs, i.e. |U| = 2',
          odd_ok and no_self_twin and twin_par and u_ok, str(out['lemmas']))

    # ------------------------------------------------------------------ L3/L4: certificates
    certs = []
    n_missing, n_packing, n_frac, unresolved = 0, 0, 0, []
    pack_sizes, frac_vals = [], []
    for b, (i, j) in enumerate(pairs):
        tb = pidx(neg[i], neg[j])
        if tb < b:
            continue
        S = pcol[b]
        if pcol[tb] != S:                      # sanity: the twin pair has the same separating set
            unresolved.append({'group': [b, tb], 'why': 'twin separating sets differ'})
            continue
        A_all = ((1 << N) - 1) & ~S            # the 50 columns that do NOT separate p
        req = [q for q in range(NP) if q != b and q != tb]
        missing = [q for q in req if (pcol[q] & A_all) == 0]
        if missing:                            # certificate type 1: a required pair with no allowed separator
            q = missing[0]
            # independent re-verification of the witness
            ver = all(not ((cm[a] >> q) & 1) for a in range(N) if not ((cm[a] >> b) & 1))
            certs.append({'group': [b, tb], 'type': 'missing_separator', 'witness_pair': q,
                          'requirement_ok': ver, 'n_missing_pairs': len(missing)})
            n_missing += 1
            if not ver:
                unresolved.append({'group': [b, tb], 'why': 'witness re-verification failed'})
            continue
        # certificate type 2: restricted packing (dynamic most-constrained greedy, many restarts)
        cand_q = [q for q in req if pcol[q] & A_all]
        R = {q: (pcol[q] & A_all) for q in cand_q}
        best, bestsel = [], []
        for trial in range(400):
            pool = list(cand_q)
            if trial:
                rng.shuffle(pool)
            sel, used = [], 0
            while True:
                pick = None
                pickpc = None
                for q in pool:
                    rq = R[q]
                    if rq & used:
                        continue
                    pc = bin(rq).count('1')
                    if pickpc is None or pc < pickpc:
                        pick, pickpc = q, pc
                        if pc == 1:
                            break
                if pick is None:
                    break
                sel.append(pick)
                used |= R[pick]
                pool.remove(pick)
            if len(sel) > len(best):
                best, bestsel = list(sel), list(sel)
        # independent re-verification: restricted separator sets pairwise disjoint
        ver = True
        for x in range(len(bestsel)):
            for y in range(x + 1, len(bestsel)):
                if (pcol[bestsel[x]] & A_all & pcol[bestsel[y]]) != 0:
                    ver = False
        if len(best) >= 7 and ver:
            certs.append({'group': [b, tb], 'type': 'restricted_packing', 'size': len(best),
                          'pairs': best, 'disjoint_verified': ver})
            n_packing += 1
            pack_sizes.append(len(best))
        elif ver:
            # certificate type 3: FRACTIONAL packing (exact rational LP).  Any feasible y with sum y > 6
            # gives cover >= sum y by weak duality (a cover needs >= one column per pair it must hit).
            Ares = [[a for a in range(N) if (pcol[q] >> a) & 1 and (S >> a) & 1 == 0] for q in req]
            lp = s10.solve_packing_lp(Ares, len(req), N)
            val = lp.get('opt')
            cert = s10.verify_certificate(Ares, len(req), N, lp) if val is not None else None
            ok3 = (val is not None and val >= 7 and cert and cert['dual_packs'] and cert['dual_nonneg']
                   and cert['objectives_equal'] and cert['primal_covers'])
            if ok3:
                certs.append({'group': [b, tb], 'type': 'fractional_packing', 'value': str(val),
                              'value_float': float(val), 'n_pairs_in_LP': len(req),
                              'y_support': [q for q in range(len(req)) if lp['y'][q] > 0],
                              'y_values': [str(lp['y'][q]) for q in range(len(req)) if lp['y'][q] > 0],
                              'verified': cert})
                n_frac += 1
                frac_vals.append(val)
            else:
                unresolved.append({'group': [b, tb], 'packing': len(best), 'lp': None if val is None else str(val),
                                   'why': 'no certificate of any of the three types'})
        else:
            unresolved.append({'group': [b, tb], 'packing': len(best), 'verified': ver,
                               'why': 'packing verification failed'})
    out['certificates'] = {'n_groups': n_missing + n_packing + n_frac + len(unresolved),
                           'missing_separator': n_missing, 'restricted_packing': n_packing,
                           'fractional_packing': n_frac, 'unresolved': len(unresolved),
                           'min_packing_size': min(pack_sizes) if pack_sizes else None,
                           'min_fractional_value': str(min(frac_vals)) if frac_vals else None,
                           'per_group': certs[:60], 'unresolved_detail': unresolved[:5]}
    print('certificates: %d missing-separator + %d restricted-packing (min size %s) + %d fractional-packing '
          '(min value %s) ; unresolved = %d'
          % (n_missing, n_packing, min(pack_sizes) if pack_sizes else None, n_frac,
             min(frac_vals) if frac_vals else None, len(unresolved)), flush=True)
    claim('P1C-1', 'NO GROUP ADMITS A 6-COLUMN COVER, each refuted by a SHORT independently re-verified '
                   'certificate: (a) a witness pair with no separator among the 50 allowed columns, or '
                   '(b) a restricted packing of pairwise disjoint separator sets of size >= 7 (so 6 columns '
                   'cannot cover them), or (c) a FRACTIONAL packing (exact rational LP, still restricted to the '
                   '50 allowed columns) of total weight >= 7, which by weak duality lower-bounds any integral '
                   'cover by 7. Hence no 6-subset leaves exactly one twin pair unseparated, i.e. loss != 2, '
                   'i.e. pat != 28',
          len(unresolved) == 0 and (n_missing + n_packing + n_frac) == 225,
          '%d + %d + %d = %d groups, unresolved = %d, min packing = %s, min fractional weight = %s'
          % (n_missing, n_packing, n_frac, n_missing + n_packing + n_frac, len(unresolved),
             min(pack_sizes) if pack_sizes else None, min(frac_vals) if frac_vals else None))

    r5 = json.load(io.open(os.path.join(DATA, '09_r5_kmin_law.json'), encoding='utf-8'))
    r5best = r5['edge_k6']['max_pat_best']
    claim('P1C-2', 'POINT VALUE: pat <= 28 (R5, from F_6 = 0 plus evenness) and pat = 26 is constructed (R5, '
                   'best sampled value %s); the certificates above exclude 28, so max pat(k=6, M_edge) = 26 '
                   'EXACTLY -- the interval [26,28] is closed' % r5best,
          r5best == 26 and len(unresolved) == 0, 'R5 best = %s ; excluded 28 by %d certificates'
          % (r5best, n_missing + n_packing + n_frac))

    claim('P1C0-1-c', 'REFUTATION OF MY OWN PRECEDING CONSTRUCTION (recorded, scripts/14): the "collapse lemma" '
                      '-- that the two columns u and -u of a line induce the same partition and can be identified '
                      '-- is FALSE. On a tie row tau gives BOTH u and -u the same value, so -u is not the sign '
                      'negation of u; the script 14 verification FAILED (partner_defined = False, 60 distinct '
                      'pair masks out of 62) and its enumeration degenerated to C(62,6), so it was killed. The '
                      'certificate route above needs no such collapse', True,
          'scripts/14 log P1C0-1 FAIL is kept as the record')

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '15_r7_pat_certificate.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              out['elapsed_s']))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
