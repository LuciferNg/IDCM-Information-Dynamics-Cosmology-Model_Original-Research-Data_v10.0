#!/usr/bin/env python3
"""O228 scripts/05 -- R2/D: protocol-level cost law (read-only replay of the frozen A2 pass).

Contract: docs/02_r2_contract.md, items P1/P2.
Nothing is re-derived from upstream: the frozen `run_pair` I/O semantics are imported and replayed
verbatim, and the counts are then compared with the frozen budget constants (BUDGET, PER_READ, E_MIN,
READS_PER_PASS, EPOCHS) and with R1's 31 axes = 31 lines.

Analysis-time prediction recorded in the R2 contract supplement (written before this script ran):
  per-pair misses in {2,3}; exactly 124 pairs cost 2 reads; total = 2*124 + 3*3720 = 11408.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/05_r2_protocol_cost.py
"""
import collections
import importlib.util
import io
import json
import os
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
O222 = os.path.abspath(os.path.join(ROOT, '..', 'o222_qm_evaluation_semantics'))
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def main():
    t0 = time.time()
    out = {}
    print('=' * 112)
    print('O228 scripts/05 -- R2/D: protocol-level cost law (frozen run_pair replayed read-only)')
    print('=' * 112, flush=True)
    sp = importlib.util.spec_from_file_location('mX', os.path.join(O222, 'scripts', '12_b5_budget.py'))
    mX = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mX)

    m, K, MUL, hx, ids, types = mX.load_machine()
    axes, U, ids_u, types_u, hvec = m.load_inputs()
    BUDGET, PER_READ, E_MIN = mX.BUDGET, mX.PER_READ, mX.E_MIN
    READS_PER_PASS, EPOCHS, TICK = mX.READS_PER_PASS, mX.EPOCHS, mX.TICK
    BIG = F(10 ** 9)

    # ---- replay the frozen-order sweep, no budget bound (pure I/O accounting)
    order = [(a, b) for a in range(62) for b in range(62)]
    top = -1
    misses, tops = [], []
    for (a, b) in order:
        r, _bud = mX.run_pair(a, b, 0, top, K, MUL, hx, BIG)
        misses.append(r['misses'])
        top = r['top']
        tops.append(top)
    hist = collections.Counter(misses)
    tot = sum(misses)
    two_miss = [(order[i], tops[i - 1] if i else -1) for i in range(len(order)) if misses[i] == 2]
    diag = [(a, b) for (a, b) in order if a == b]
    diag_two = [p for p in two_miss if p[0][0] == p[0][1]]
    offdiag_two = [p for p in two_miss if p[0][0] != p[0][1]]
    succ = sorted(p[0] for p in offdiag_two if p[0][1] == p[0][0] + 1)
    wrap = [p[0] for p in offdiag_two if p[0][1] == 0]
    out['per_pair_miss_histogram'] = {str(k): hist[k] for k in sorted(hist)}
    out['total_misses'] = tot
    out['two_miss_offdiagonal'] = len(offdiag_two)
    out['two_miss_diagonal'] = len(diag_two)
    out['successor_pairs'] = len(succ)
    out['wrap_pairs'] = wrap
    print('per-pair miss histogram = %s ; total misses = %d ; 2-miss pairs = %d (off-diagonal %d + diagonal %d)'
          % (out['per_pair_miss_histogram'], tot, len(two_miss), len(offdiag_two), len(diag_two)), flush=True)
    print('2-miss off-diagonal pairs are the b = a+1 successors (%d of them) plus the single wrap %s'
          % (len(succ), wrap), flush=True)

    claim('P1', 'BLIND/derived: replaying the frozen run_pair over the frozen-order 62x62 sweep, every pair '
                'costs 2 or 3 reads; exactly 124 pairs cost 2 (62 successors b = a+1, 62 diagonal pairs) and '
                '3720 cost 3; total misses = 11408 = 2*124 + 3*3720',
          set(hist.keys()) == {2, 3} and hist[2] == 124 and hist[3] == 3720 and tot == 11408
          and len(succ) == 61 and wrap == [(61, 0)] and len(diag_two) == 62,
          'histogram = %s ; total = %d ; 2-miss = %d (successors %d, diagonal %d, wrap %s)'
          % (out['per_pair_miss_histogram'], tot, hist[2], len(succ), len(diag_two), wrap))

    # ---- resource identities
    N2 = 62 * 62
    famcount = collections.Counter()
    for i in range(62):
        if ids_u[i].startswith('V'):
            famcount['vertex'] += 1
        elif ids_u[i].startswith('F'):
            famcount['face'] += 1
        else:
            famcount['edge'] += 1
    fam_lines = {'vertex': famcount['vertex'] // 2, 'face': famcount['face'] // 2, 'edge': famcount['edge'] // 2}
    nlines = sum(fam_lines.values())
    A2_SPEC_READS = 2 * N2                     # 2 reads per pair
    out.update({'n_pairs': N2, 'n_axis_lines': nlines, 'family_lines': fam_lines,
                'A2_spec_reads': A2_SPEC_READS, 'A2_spec_over_line_square': A2_SPEC_READS // (nlines ** 2),
                'BUDGET': str(BUDGET), 'PER_READ': str(PER_READ), 'E_MIN': str(E_MIN),
                'READS_PER_PASS_at_Emin': str(READS_PER_PASS), 'READS_AT_COST': str(BUDGET / PER_READ),
                'EPOCHS': list(EPOCHS), 'line_square': nlines ** 2})
    claim('P2', 'resource identity: 31 axis lines -> 31^2 = 961 = the epoch unit (EPOCHS = 0,961,1922,2883) -> '
                'the A2 spec pass 7688 = 2*62^2 = 8*31^2 reads ; the frozen per-pass budgets are '
                '88 reads at E_min and 44 = N_d reads at cost',
          nlines == 31 and N2 == 4 * 31 ** 2 and A2_SPEC_READS == 7688 and A2_SPEC_READS == 8 * 961
          and list(EPOCHS) == [0, 961, 1922, 2883] and BUDGET / E_MIN == 88 and BUDGET / PER_READ == 44
          and PER_READ == 2 * E_MIN,
          'lines = %d (V%d/F%d/E%d) ; 62^2 = %d = 4*31^2 ; A2 spec = 2*62^2 = %d = 8*31^2 ; '
          'reads/pass = BUDGET/E_MIN = %s ; reads-at-cost = BUDGET/PER_READ = %s = N_d ; EPOCHS = %s ; '
          'overrun of the A2 pass vs the 88-read pass = %s ; vs the 44-read cost = %s'
          % (nlines, fam_lines['vertex'], fam_lines['face'], fam_lines['edge'], N2, A2_SPEC_READS,
             BUDGET / E_MIN, BUDGET / PER_READ, list(EPOCHS), F(7688) / (BUDGET / E_MIN), F(7688) / (BUDGET / PER_READ)))

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '05_r2_protocol_cost.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              out['elapsed_s']))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
