#!/usr/bin/env python3
"""O224 scripts/16_windows_global.py (round 5) -- EXACT global extremes of every Bell window of the
n = 4 Mermin expression over the whole 62^8 setting space.

ROUND-5 PRE-REGISTRATION (written before any number of this round is produced).

WHY.  Round 4 closed the raw window exactly (512/120) and deduced the party window by a
subset+attainer equality sandwich; the stricter windows were left as brackets only (eight in
[320,512], eight_anti in [224,512]).  This round closes all of them with exact integers.

EXACTNESS MODEL (no float, no sampling, no approximation anywhere in a result path):
  * every value is an integer in units of 1/120;
  * the only algebraic step is the round-4 identity M4 = F(c,c',d) + G(c,c',d'), itself verified in
    round 4 by the unfactorised four-term forms and by direct 8-term evaluation (4/4 and 5/5);
  * for each outer group (a,a',b,b') the script attacks the FULL 62^4 array over (c,c',d,d') by a
    top-K extension argument, K taken from the number of PAIR constraints:
        an optimal pair (d*,d') may be assumed to have d* among the top-K of F restricted to the
        admissible d-set S(c,c') and d' among the top-K of G restricted to S(c,c'), where
        K = 1 + (axes excluded for a given partner by the pair constraint) = 2 for "d != d'",
        and 3 for "d != d' AND (d,d') non-antipodal".
        Swap proof: for any K distinct axes at most K-1 can be unusable against a fixed partner, so
        one remaining axis has value >= the replaced one; ties are covered because the K stored
        indices achieve the top-K VALUES and every combination of them is checked against the pair
        condition evaluated on the actual (d,d') values -- no constraint is ever dropped.  The
        admissible-set masking S(c,c') is applied BEFORE the top-K, so it is not part of K.
  * the reduction is then TESTED, not trusted: at every produced winner's group the script redoes
    the COMPLETE 62^4 enumeration with the 4-D array fully materialised (the "no simplification"
    check), and repeats reduced-vs-full on a deterministic list of 18 declared groups.

WINDOWS (as defined by round 3's implementation, restated verbatim for comparability):
  W0 raw_full : no constraint at all (d = d' allowed) -- the absolute polynomial extreme.
  W1 party    : a != a', b != b', c != c', d != d'  (within-pair distinctness only -- the
                physically legitimate Bell configuration set).
  W2 eight    : all eight settings pairwise distinct.
  W3 anti_v3  : round 3's eight_anti as implemented -- the six outer pairwise distinct and pairwise
                non-antipodal; d and d' excluded from the six and their antipodes; d != d'; an
                ANTIPODAL (d,d') pair is ALLOWED (the round-4 precision finding).
  W4 anti_str : as W3 plus d and d' non-antipodal to each other (all eight pairwise non-antipodal).

PRE-REGISTERED CLAIMS.
  C1 COVERAGE: every party-1 ordered pair processed exactly once; outer count = 62^6.
  C2 PARTY WINDOW: exact extremes computed directly (not via the round-4 sandwich), reproducing
     round 4's raw-window global 512/120.
  C3 EIGHT WINDOW: exact extremes.
  C4 ANTI_V3 WINDOW: exact extremes.
  C5 ANTI_STRICT WINDOW: exact extremes.
  C6 RAW_FULL: exact extremes of the unconstrained polynomial.
  C7 CHAIN: raw_full >= party >= eight >= anti_v3 >= anti_str >= round-3 pool values (480/320/224),
     every entry an exact number.
  C8 WINNER VERIFICATION (four independent paths): for every window and both sides -- direct 8-term
     evaluation, explicit window-membership check, unfactorised four-term F/G expression, and a FULL
     62^4 materialised enumeration of the winner's group -- all agreeing with the sharded value.
  C9 REDUCTION vs FULL ON DECLARED GROUPS: identical window extremes from the reduced and the fully
     materialised paths for 18 declared groups (all five windows, both sides).

numpy is used strictly as an integer accelerator; zero new parameters; writes only inside this O
directory.
"""
import io
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib2i as L

ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
LOGS = os.path.join(ROOT, 'logs')
SENT = 1 << 29

WINDOWS = ('raw_full', 'party', 'eight', 'anti_v3', 'anti_str')
K_OF = {'raw_full': 1, 'party': 2, 'eight': 2, 'anti_v3': 2, 'anti_str': 3}

# Integer range argument for the int16 accelerator buffers:
#   |E4| <= 120, so |A|,|R|,|U|,|V| <= 240 and |F|,|G| <= 480; every retained value is a sum of two
#   such entries, |value| <= 960 < SENT = 12000 < 2**15.  A sentinel entry combined with a real one
#   gives >= 12000 - 480 = 11520, and two sentinels give 24000 < 32767, so the sentinel never
#   collides with a real value and can never overflow int16.  All arithmetic stays exact integers.
SENT = 12000
NEG_SENT = -12000


def build_e4(nax, KA, NMUL, hxa):
    E4 = np.zeros((nax, nax, nax, nax), dtype=np.int32)
    s2b = NMUL[:, hxa]
    for a in range(nax):
        Aa = KA[:, a]
        s2 = s2b[:, a]
        for b in range(nax):
            s3 = NMUL[s2, hxa[b]]
            Wa = Aa * KA[s2, b]
            for c in range(nax):
                s4 = NMUL[s3, hxa[c]]
                E4[a, b, c, :] = (Wa * KA[s3, c]) @ KA[s4, :]
    return E4


def mermin_terms(n):
    out = []
    for mask in range(1 << n):
        eps = tuple((mask >> j) & 1 for j in range(n))
        w = sum(eps)
        if w % 2 == 0:
            out.append((eps, 1 if (w // 2) % 2 == 0 else -1))
    return out


def group_masks(nax, a, ap, b, bp, adx, anti, four_isin):
    """axis masks for one outer group; returns (gate, masks, plane_cc).
    masks[w] = (Md, Pmat): Md is the (c,c',d) admissible-d mask (None = every axis),
    Pmat is the (d,d') pair mask."""
    four = (a, ap, b, bp)
    nf = ~four_isin
    neq_cc = adx[:, None] != adx[None, :]
    neq_dd = adx[:, None] != adx[None, :]
    d_ne_c = adx[None, None, :] != adx[:, None, None]
    d_ne_cp = adx[None, None, :] != adx[None, :, None]
    anti4 = np.ones(nax, bool)
    for s in four:
        anti4 &= ~anti[:, s]
    base2 = nf[None, None, :]
    base3 = base2 & anti4[None, None, :]
    M_d2 = base2 & d_ne_c & d_ne_cp
    M_d3 = base3 & d_ne_c & d_ne_cp & (~anti[:, None, :]) & (~anti[None, :, :])
    cc_ok2 = nf
    cc_ok3 = nf & anti4
    M_cc2 = cc_ok2[:, None] & cc_ok2[None, :] & neq_cc
    M_cc3 = cc_ok3[:, None] & cc_ok3[None, :] & neq_cc & (~anti)
    four_distinct = len(set(four)) == 4
    four_antifree = four_distinct and not any(anti[four[i], four[j]]
                                             for i in range(4) for j in range(i + 1, 4))
    gate = {'raw_full': True,
            'party': (a != ap) and (b != bp),
            'eight': four_distinct,
            'anti_v3': four_antifree,
            'anti_str': four_antifree}
    masks = {'raw_full': (None, None),
             'party': (None, neq_dd),
             'eight': (M_d2, neq_dd),
             'anti_v3': (M_d3, neq_dd),
             'anti_str': (M_d3, neq_dd & (~anti))}
    plane_cc = {'raw_full': None, 'party': neq_cc, 'eight': M_cc2,
                'anti_v3': M_cc3, 'anti_str': M_cc3}
    return gate, masks, plane_cc


def window_setup(nax, a, ap, b, bp, adx, anti, four_isin):
    """per-window exact data in LOCAL coordinates of the admissible d-axis slice B:
    (B, pmask_local, ccmask, excl_index_arrays).  excl arrays are the (i,j,local) triples to be
    sentinelled for the exclusions {c, c', anti(c), anti(c')} -- the axis-wise exclusions
    (the four settings and their antipodes) are handled by the slice B itself."""
    four = (a, ap, b, bp)
    nf = ~four_isin
    neq_cc = adx[:, None] != adx[None, :]
    neq_dd = adx[:, None] != adx[None, :]
    anti4 = np.ones(nax, bool)
    for s in four:
        anti4 &= ~anti[:, s]
    partner = np.asarray(anti).argmax(axis=1)      # the antipode partner of each axis

    def pack(B, pmask_local, ccmask, exkind):
        """exkind: 0 = no per-(c,c') exclusion (party); 1 = {c,c'} (eight);
        2 = {c,c',anti(c),anti(c')} (anti windows)."""
        loc = np.full(nax, -1, dtype=np.int64)
        loc[B] = np.arange(len(B))
        la = loc[partner]                   # local position of the antipode of each axis
        ex = []
        if exkind >= 1:
            for m in (np.broadcast_to(loc[:, None], (nax, nax)),
                      np.broadcast_to(loc[None, :], (nax, nax))):
                ii, jj = np.nonzero(m >= 0)
                if ii.size:
                    ex.append((ii, jj, m[ii, jj].astype(np.int64)))
        if exkind >= 2:
            for m in (np.broadcast_to(la[:, None], (nax, nax)),
                      np.broadcast_to(la[None, :], (nax, nax))):
                ii, jj = np.nonzero(m >= 0)
                if ii.size:
                    ex.append((ii, jj, m[ii, jj].astype(np.int64)))
        return (B, pmask_local, ccmask, ex)

    setup = {}
    B2 = adx[nf]
    setup['party'] = pack(adx, neq_dd, neq_cc, 0)
    cc2 = nf[:, None] & nf[None, :] & neq_cc
    setup['eight'] = pack(B2, neq_dd[np.ix_(B2, B2)], cc2, 1)
    B3 = adx[nf & anti4]
    cc3 = (nf & anti4)[:, None] & (nf & anti4)[None, :] & neq_cc & (~anti)
    setup['anti_v3'] = pack(B3, neq_dd[np.ix_(B3, B3)], cc3, 2)
    setup['anti_str'] = pack(B3, neq_dd[np.ix_(B3, B3)] & (~anti[np.ix_(B3, B3)]), cc3, 2)
    return setup


def top_k(Z, K):
    """top-K values and their indices along the last axis, by exact argmax iteration."""
    i1 = Z.argmax(-1)
    v1 = np.take_along_axis(Z, i1[..., None], -1)[..., 0]
    idx = [i1]
    val = [v1]
    if K > 1:
        Zc = Z.copy()
        np.put_along_axis(Zc, i1[..., None], NEG_SENT, -1)
        i2 = Zc.argmax(-1)
        val.append(np.take_along_axis(Zc, i2[..., None], -1)[..., 0])
        idx.append(i2)
        if K > 2:
            np.put_along_axis(Zc, i2[..., None], NEG_SENT, -1)
            i3 = Zc.argmax(-1)
            val.append(np.take_along_axis(Zc, i3[..., None], -1)[..., 0])
            idx.append(i3)
    return np.stack(idx, axis=-1), np.stack(val, axis=-1)


def reduce_window(A, Bm, K, pmask, ccmask, ex, nax):
    """exact max (and its argmax) of A[c,c',d] + Bm[c,c',d'] over the window, in local d coords."""
    ZA = A.copy()
    ZB = Bm.copy()
    for (ii, jj, kk) in ex:
        ZA[ii, jj, kk] = NEG_SENT
        ZB[ii, jj, kk] = NEG_SENT
    iA, vA = top_k(ZA, K)
    iB, vB = top_k(ZB, K)
    V = vA[..., :, None] + vB[..., None, :]
    okp = pmask[iA[..., :, None], iB[..., None, :]]
    V = np.where(okp, V, NEG_SENT)
    if ccmask is not None:
        V = np.where(ccmask[:, :, None, None], V, NEG_SENT)
    flat = V.reshape(-1)
    fi = int(flat.argmax())
    best = int(flat[fi])
    ccidx, kk = divmod(fi, K * K)
    c, cp = divmod(ccidx, nax)
    k1, k2 = divmod(kk, K)
    return best, (c, cp, int(iA[c, cp, k1]), int(iB[c, cp, k2]))


def reduced_group(F3, G3, w, setup, nax):
    """exact window extremes for one group: top-K extension argument (K <= 3), int16 exact."""
    out = []
    for sign in (1, -1):
        if w == 'raw_full':
            H = F3 if sign == 1 else -F3
            J = G3 if sign == 1 else -G3
            ih = H.argmax(-1)
            ij = J.argmax(-1)
            V = H.max(-1) + J.max(-1)
            fi = int(V.reshape(-1).argmax())
            c, cp = divmod(fi, nax)
            best = int(V.reshape(-1)[fi])
            out.append(((-best if sign == -1 else best), (c, cp, int(ih[c, cp]), int(ij[c, cp]))))
            continue
        B, pmask, ccmask, ex = setup[w]
        A = (F3 if sign == 1 else -F3)[:, :, B]
        Bm = (G3 if sign == 1 else -G3)[:, :, B]
        best, (c, cp, ld, ldp) = reduce_window(A, Bm, K_OF[w], pmask, ccmask, ex, nax)
        if best <= NEG_SENT // 2:
            out.append((None, None))
        else:
            val = -best if sign == -1 else best      # the sign-flipped side reports the MINIMUM
            out.append((val, (c, cp, int(B[ld]), int(B[ldp]))))
    (pos, argp), (neg, argn) = out
    if pos is None or neg is None:
        return None, None, None, None
    return pos, argp, neg, argn


def group_gate(a, ap, b, bp, anti):
    four = (a, ap, b, bp)
    four_distinct = len(set(four)) == 4
    four_antifree = four_distinct and not any(anti[four[i], four[j]]
                                             for i in range(4) for j in range(i + 1, 4))
    return {'raw_full': True,
            'party': (a != ap) and (b != bp),
            'eight': four_distinct,
            'anti_v3': four_antifree,
            'anti_str': four_antifree}



def full_group(F3, G3, masks, plane_cc, nax):
    """reference path: FULL 62^4 materialisation, no reduction at all (verification only)."""
    T = F3.astype(np.int32)[:, :, :, None] + G3.astype(np.int32)[:, :, None, :]
    res = {}
    for w in WINDOWS:
        Md, Pmat = masks[w]
        m = np.ones(T.shape, bool)
        if Md is not None:
            m &= Md[:, :, :, None]
            m &= Md[:, :, None, :]
        if Pmat is not None:
            m &= Pmat[None, None, :, :]
        if plane_cc[w] is not None:
            m &= plane_cc[w][:, :, None, None]
        V = np.where(m, T, -SENT)
        W = np.where(m, T, SENT)
        ip = int(V.reshape(-1).argmax())
        inn = int(W.reshape(-1).argmin())
        cp = np.unravel_index(ip, T.shape)
        cn = np.unravel_index(inn, T.shape)
        res[w] = (int(T[cp]), tuple(int(x) for x in cp), int(T[cn]), tuple(int(x) for x in cn))
    return res


def fg_of_group(X, a, ap, b, bp, nax):
    """F, G of one outer group as int16 exact arrays (values in [-480, 480])."""
    Xab = X[a, b].astype(np.int16)
    Xapbp = X[ap, bp].astype(np.int16)
    Xapb = X[ap, b].astype(np.int16)
    Xabp = X[a, bp].astype(np.int16)
    F3 = (Xab - Xapbp)[:, None, :] - (Xapb + Xabp)[None, :, :]
    G3 = (Xapbp - Xab)[None, :, :] - (Xapb + Xabp)[:, None, :]
    return F3, G3


def main():
    args = sys.argv[1:]
    G, idx, MUL, U, ids, types, hx, K = L.load_machine()
    n, nax = len(G), len(ids)
    KA = np.array(K, dtype=np.int32)
    NMUL = np.array(MUL, dtype=np.int32)
    hxa = np.array(hx, dtype=np.int32)
    anti = np.array(L.antipodal(U, nax), dtype=np.int32).reshape(nax, nax).astype(bool)
    terms4 = mermin_terms(4)
    adx = np.arange(nax)

    if args and args[0] == '--aggregate':
        return aggregate(nax, ids, anti, terms4)
    if len(args) == 3 and args[0] == '--shard':
        k, ns = int(args[1]), int(args[2])
    else:
        print('usage: 16_windows_global.py --shard K N   |   --aggregate')
        return 2

    R = L.Report('16_windows_global_shard_%02dof%02d' % (k, ns))
    t0 = time.time()
    X = build_e4(nax, KA, NMUL, hxa)
    t_build = time.time() - t0
    four_isin = np.zeros(nax, bool)

    pairs = [p for p in range(nax * nax) if p % ns == k]
    best = {w: {'pos': None, 'argpos': None, 'neg': None, 'argneg': None,
                'groups': 0, 'skipped': 0} for w in WINDOWS}
    for p in pairs:
        a, ap = divmod(p, nax)
        four_isin[:] = False
        four_isin[[a, ap]] = True
        for b in range(nax):
            for bp in range(nax):
                fi = four_isin.copy()
                fi[[b, bp]] = True
                gate = group_gate(a, ap, b, bp, anti)
                if not any(gate[w] for w in WINDOWS):
                    for w in WINDOWS:
                        best[w]['skipped'] += 1
                    continue
                setup = window_setup(nax, a, ap, b, bp, adx, anti, fi)
                F3, G3 = fg_of_group(X, a, ap, b, bp, nax)
                for w in WINDOWS:
                    if not gate[w]:
                        best[w]['skipped'] += 1
                        continue
                    pos, argp, neg, argn = reduced_group(F3, G3, w, setup, nax)
                    if pos is None:
                        best[w]['skipped'] += 1
                        continue
                    best[w]['groups'] += 1
                    if best[w]['pos'] is None or pos > best[w]['pos']:
                        best[w].update(pos=pos, argpos=(a, ap, b, bp) + tuple(argp))
                    if best[w]['neg'] is None or neg < best[w]['neg']:
                        best[w].update(neg=neg, argneg=(a, ap, b, bp) + tuple(argn))
    outer = len(pairs) * nax ** 4      # outer = (b,bp,c,c') per fixed (a,a') pair; sums to 62^6
    payload = {
        'shard': k, 'n_shards': ns, 'pairs': pairs,
        'groups_scanned': len(pairs) * nax * nax,
        'outer_tuples': outer,
        'e4_build_s': t_build, 'solve_s': time.time() - t0 - t_build,
        'absE4max': int(np.abs(X).max()),
        'windows': {w: {kk: (list(vv) if isinstance(vv, tuple) else vv)
                        for kk, vv in best[w].items()} for w in WINDOWS},
    }
    fn = os.path.join(DATA, '16_shard_%02dof%02d.json' % (k, ns))
    with io.open(fn, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, sort_keys=True)
    print('shard %d/%d: pairs %d, groups %d, |E4|max %d, %.1f s (E4 %.1f s)'
          % (k, ns, len(pairs), payload['groups_scanned'], payload['absE4max'],
             time.time() - t0, t_build))
    print('  ' + ' | '.join('%s %s/%s' % (w, best[w]['pos'], best[w]['neg']) for w in WINDOWS))
    print('  -> %s' % fn)
    return 0


def direct8(X, t8, terms4):
    a, ap, b, bp, c, cp, d, dp = t8
    s = [a, ap, b, bp, c, cp]
    tot = 0
    for e, coef in terms4:
        tot += coef * int(X[s[0 + e[0]], s[2 + e[1]], s[4 + e[2]], d if e[3] == 0 else dp])
    return tot


def window_member(w, t8, anti):
    a, ap, b, bp, c, cp, d, dp = t8
    six = (a, ap, b, bp, c, cp)
    if w == 'raw_full':
        return True
    if w == 'party':
        return a != ap and b != bp and c != cp and d != dp
    if w == 'eight':
        return len(set(t8)) == 8
    if w in ('anti_v3', 'anti_str'):
        if len(set(six)) != 6:
            return False
        if any(anti[six[i], six[j]] for i in range(6) for j in range(i + 1, 6)):
            return False
        if d in six or dp in six or d == dp:
            return False
        for s in six:
            if anti[d, s] or anti[dp, s]:
                return False
        if w == 'anti_str' and anti[d, dp]:
            return False
        return True
    return False


def aggregate(nax, ids, anti, terms4):
    import glob
    R = L.Report('16_windows_global')
    print('=' * 108)
    print('O224 scripts/16 (round 5) -- exact global extremes of all Bell windows')
    print('=' * 108, flush=True)
    files = sorted(glob.glob(os.path.join(DATA, '16_shard_*of*.json')))
    shards = [json.load(io.open(f, encoding='utf-8')) for f in files]
    ns = shards[0]['n_shards'] if shards else 0
    assert all(s['n_shards'] == ns for s in shards) and len(shards) == ns, (len(shards), ns)
    seen = sorted(p for s in shards for p in s['pairs'])
    outer = sum(s['outer_tuples'] for s in shards)
    R.claim('C1', 'COVERAGE: every party-1 ordered pair is processed by exactly one shard (3844 '
                  'pairs, no duplicate, no omission), and the outer tuple count sums to '
                  '62^6 = 56,800,235,584',
            seen == list(range(nax * nax)) and outer == nax ** 6,
            'pairs = %d (distinct %d, expected %d) ; outer tuples = %s (expected %s) ; shards = %d'
            % (len(seen), len(set(seen)), nax * nax, outer, nax ** 6, len(shards)))

    G_, idx, MUL, U, ids_, types, hx, K = L.load_machine()
    KA = np.array(K, dtype=np.int32)
    NMUL = np.array(MUL, dtype=np.int32)
    hxa = np.array(hx, dtype=np.int32)
    X = build_e4(nax, KA, NMUL, hxa)
    adx = np.arange(nax)

    got = {}
    for w in WINDOWS:
        pos = max(s['windows'][w]['pos'] for s in shards if s['windows'][w]['pos'] is not None)
        neg = min(s['windows'][w]['neg'] for s in shards if s['windows'][w]['neg'] is not None)
        argp = next(s['windows'][w]['argpos'] for s in shards if s['windows'][w]['pos'] == pos)
        argn = next(s['windows'][w]['argneg'] for s in shards if s['windows'][w]['neg'] == neg)
        got[w] = {'pos': pos, 'neg': neg, 'argpos': argp, 'argneg': argn,
                  'absmax': max(abs(pos), abs(neg))}

    with io.open(os.path.join(DATA, '12_n4_global.json'), encoding='utf-8') as fh:
        r4 = json.load(fh)
    raw4 = r4['raw_global']

    R.claim('C2', 'PARTY WINDOW: the party-window global extremes are computed directly (not by the '
                  'round-4 sandwich) and reproduce round 4\'s raw-window global 512/120 exactly',
            got['party']['pos'] == 512 and got['party']['neg'] == -512
            and raw4['max_num'] == 512 and raw4['min_num'] == -512,
            'party window: max %s/120 at %s ; min %s/120 at %s ; round-4 raw global %s/120'
            % (got['party']['pos'], got['party']['argpos'], got['party']['neg'],
               got['party']['argneg'], raw4['max_num']))

    for tag, w, name in (('C3', 'eight', 'EIGHT (all eight pairwise distinct)'),
                         ('C4', 'anti_v3', 'ANTI_V3 (round-3 eight_anti semantics)'),
                         ('C5', 'anti_str', 'ANTI_STRICT (all eight pairwise non-antipodal)'),
                         ('C6', 'raw_full', 'RAW_FULL (no constraint at all, d = d\' allowed)')):
        R.claim(tag, 'EXACT GLOBAL EXTREMES OF THE %s WINDOW: computed over all 62^6 outer groups '
                     'with the exact integer machinery, achieved configuration recorded' % name,
                got[w]['pos'] is not None and got[w]['neg'] is not None,
                '%s: max %s/120 at %s ; min %s/120 at %s ; |M4|max %s/120'
                % (w, got[w]['pos'], got[w]['argpos'], got[w]['neg'], got[w]['argneg'],
                   got[w]['absmax']))

    r3_pool = r4['round3_cross']['pool_values']
    chain_ok = (got['raw_full']['pos'] >= got['party']['pos'] >= got['eight']['pos']
                >= got['anti_v3']['pos'] >= got['anti_str']['pos']
                and got['eight']['pos'] >= r3_pool['eight']
                and got['anti_v3']['pos'] >= r3_pool['eight_anti']
                and got['party']['pos'] >= r3_pool['raw'])
    R.claim('C7', 'WINDOW CHAIN: raw_full >= party >= eight >= anti_v3 >= anti_strict >= the round-3 '
                  'pool values (480/320/224), every entry an exact number, so the round-4 brackets '
                  '[320,512] and [224,512] are replaced by exact values',
            chain_ok,
            'chain: %s ; round-3 pool = %s'
            % (' >= '.join('%s %s' % (w, got[w]['pos']) for w in WINDOWS), r3_pool))

    # ---------------- C8 winner verification, including a FULL 62^4 enumeration ----------------
    rows = []
    all_ok = True
    for w in WINDOWS:
        for side in ('pos', 'neg'):
            t8 = tuple(got[w]['arg' + side])
            a, ap, b, bp = t8[:4]
            fi = np.zeros(nax, bool)
            fi[[a, ap, b, bp]] = True
            gate, masks, plane_cc = group_masks(nax, a, ap, b, bp, adx, anti, fi)
            F3, G3 = fg_of_group(X, a, ap, b, bp, nax)
            f_pos, f_argp, f_neg, f_argn = full_group(F3, G3, masks, plane_cc, nax)[w]
            rp, rap, rn, ran = reduced_group(F3, G3, w,
                                             window_setup(nax, a, ap, b, bp, adx, anti, fi), nax)
            red_ok = (rp == got[w]['pos'] and rn == got[w]['neg'])
            want = got[w][side]
            v8 = direct8(X, t8, terms4)
            mem = window_member(w, t8, anti)
            c, cp, d, dp = t8[4:]
            F_d = (X[a, b, c, :] - X[ap, bp, c, :] - X[ap, b, cp, :] - X[a, bp, cp, :])
            G_d = (X[ap, bp, cp, :] - X[ap, b, c, :] - X[a, bp, c, :] - X[a, b, cp, :])
            v_unf = int(F_d[d]) + int(G_d[dp])
            full_ok = (f_pos == got[w]['pos'] and f_neg == got[w]['neg'])
            ok = (v8 == want and mem and v_unf == want and full_ok)
            all_ok = all_ok and ok
            rows.append('%s/%s: value %d, direct8 %d, member %s, unfactorised %d, full62^4 '
                        '(max %d min %d) -> %s'
                        % (w, side, want, v8, mem, v_unf, f_pos, f_neg, 'OK' if ok else 'MISMATCH'))
    R.claim('C8', 'WINNER VERIFICATION BY FOUR INDEPENDENT PATHS: for every window and both extreme '
                  'sides the achieved configuration agrees with (i) the direct 8-term Mermin '
                  'evaluation from the frozen s-index rule, (ii) an explicit window-membership '
                  'check, (iii) the unfactorised four-term F/G expression, and (iv) a FULL 62^4 '
                  'materialised enumeration of that group (no reduction at all) whose window '
                  'extremes must equal the sharded global values',
            all_ok, ' ; '.join(rows))

    # ---------------- C9 reduced vs full on declared groups ----------------
    declared = [(0, 1, 2, 3), (0, 60, 0, 53), (0, 1, 2, 4), (5, 5, 9, 9), (0, 1, 7, 3),
                (0, 1, 8, 6), (2, 3, 4, 5), (0, 1, 2, 5), (11, 10, 9, 8), (0, 61, 1, 60),
                (13, 28, 22, 43), (0, 0, 0, 0), (60, 0, 53, 0), (31, 31, 31, 31),
                (0, 31, 1, 30), (44, 45, 46, 47), (3, 7, 11, 15), (17, 19, 23, 29)]
    c9_ok = True
    c9_rows = []
    for (a, ap, b, bp) in declared:
        fi = np.zeros(nax, bool)
        fi[[a, ap, b, bp]] = True
        gate, masks, plane_cc = group_masks(nax, a, ap, b, bp, adx, anti, fi)
        setup = window_setup(nax, a, ap, b, bp, adx, anti, fi)
        F3, G3 = fg_of_group(X, a, ap, b, bp, nax)
        fg = full_group(F3, G3, masks, plane_cc, nax)
        for w in WINDOWS:
            if not gate[w]:
                continue
            rp, rap, rn, ran = reduced_group(F3, G3, w, setup, nax)
            fp, fap, fn, fan = fg[w]
            ok = (rp == fp and rn == fn)
            c9_ok = c9_ok and ok
            if not ok:
                c9_rows.append('MISMATCH %s group %s: reduced (%d,%d) vs full (%d,%d)'
                               % (w, (a, ap, b, bp), rp, rn, fp, fn))
    R.claim('C9', 'REDUCTION vs FULL ON DECLARED GROUPS: for 18 declared groups (including the '
                  'all-equal and antipodal-partner patterns) the top-K reduced path and the fully '
                  'materialised 62^4 enumeration return identical window extremes for all five '
                  'windows and both sides -- the reduction is tested, not trusted',
            c9_ok,
            'declared groups = %d ; mismatches = %s'
            % (len(declared), c9_rows if c9_rows else 'none'))

    extra = {'windows': got, 'units': 'common denominator 120', 'lhv_bound_num': 480,
             'round3_pool_values': r3_pool,
             'methods': {'reduction': 'top-K extension argument with K = 1 + pair-constraint '
                                      'exclusions (K=2 for d != d\', K=3 additionally for '
                                      'non-antipodal), K-grid enumerated exhaustively',
                         'verification': 'full 62^4 materialised enumeration at every produced '
                                         'winner group and on 18 declared groups',
                         'arithmetic': 'exact integers, units 1/120; numpy = integer accelerator',
                         'outer_groups': nax ** 4, 'windows': list(WINDOWS)},
             'verdicts': {w: 'max %s/120, min %s/120' % (got[w]['pos'], got[w]['neg'])
                          for w in WINDOWS}}
    ok = R.finish(os.path.join(DATA, '16_windows_global.json'), extra)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
