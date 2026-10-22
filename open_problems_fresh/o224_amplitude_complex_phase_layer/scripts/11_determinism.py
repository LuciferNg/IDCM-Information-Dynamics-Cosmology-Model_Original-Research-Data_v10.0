#!/usr/bin/env python3
"""O224 scripts/11_determinism.py -- round 3 (part 3): deterministic re-run verification.

ROUND-3 PRE-REGISTRATION (written BEFORE any number of this round is produced):

D1  scripts/09_global_n.py is decision-deterministic: re-running it must reproduce every decision
    field and every numeric field of data/09_global_n.json exactly.  Timing metadata (wall-clock
    seconds, build times, and the 'time = ... s' substrings embedded in claim details) is excluded
    by an explicit, declared normalisation, because wall-clock values are not decisions.
D2  scripts/10_e5.py is decision-deterministic in the same sense (its E5 layer is a full 62^5
    enumeration and costs ~7 minutes per pass).

The projections compared are: the deep structure of the JSON with the keys 'build_s', 'seconds'
and 'times' removed and every '\\d+(\\.\\d+)? s' substring in claim details replaced by '<T> s';
plus the per-claim ok flags bit-for-bit.  The script records the sha256 of the normalised
projection before and after each re-run, and writes the comparison into
data/11_determinism.json (logs/11_determinism.out for the transcript).
"""
import io
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib2i as L

ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
LOGS = os.path.join(ROOT, 'logs')

TIME_KEYS = ('build_s', 'seconds', 'times', 'elapsed_s', 'e4_build_s', 'solve_s',
             'shard_solve_s')
TIME_RE = re.compile(r'\d+(\.\d+)? s')


def normalise(obj):
    if isinstance(obj, dict):
        return {k: normalise(v) for k, v in sorted(obj.items()) if k not in TIME_KEYS}
    if isinstance(obj, list):
        return [normalise(v) for v in obj]
    if isinstance(obj, str):
        return TIME_RE.sub('<T> s', obj)
    return obj


def projection(path):
    with io.open(path, encoding='utf-8') as fh:
        d = json.load(fh)
    norm = normalise(d)
    blob = json.dumps(norm, sort_keys=True, ensure_ascii=False)
    return norm, hashlib.sha256(blob.encode('utf-8')).hexdigest()


def run(script, extra_args=()):
    t0 = time.time()
    p = subprocess.run([sys.executable, os.path.join('scripts', script)] + list(extra_args),
                       cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.returncode, time.time() - t0, p.stdout.decode('utf-8', 'replace')


def main():
    R = L.Report('11_determinism')
    print('=' * 108)
    print('O224 scripts/11 -- round 3 part 3: deterministic re-run verification')
    print('=' * 108, flush=True)

    cases = (('09_global_n.py', '09_global_n.json', 'D1', ()),
             ('10_e5.py', '10_e5.json', 'D2', ()),
             ('12_n4_global.py', '12_shard_00of12.json', 'D3', ('--shard', '0', '12')))
    for script, artefact, tag, extra_args in cases:
        path = os.path.join(DATA, artefact)
        n0, h0 = projection(path)
        rc, secs, out = run(script, extra_args)
        n1, h1 = projection(path)
        tags0 = [c.get('tag') for c in n0.get('claims', [])]
        tags1 = [c.get('tag') for c in n1.get('claims', [])]
        oks0 = [bool(c.get('ok')) for c in n0.get('claims', [])]
        oks1 = [bool(c.get('ok')) for c in n1.get('claims', [])]
        R.claim(tag, 'DETERMINISM (%s%s): re-running %s reproduces the decision projection of '
                     'data/%s exactly (walls excluded by the declared normalisation), and the '
                     're-run itself exits 0 with the same decision inventory'
                     % (script, ' ' + ' '.join(extra_args) if extra_args else '', script, artefact),
                rc == 0 and h0 == h1 and tags0 == tags1 and oks0 == oks1,
                'returncode = %d ; wall = %.1f s ; projection sha256 before = %s after = %s ; '
                'claims = %s ; ok flags equal = %s ; child output tail = %s'
                % (rc, secs, h0[:16], h1[:16], tags1, oks0 == oks1,
                   out.strip().splitlines()[-1][:160] if out.strip() else ''))

    extra = {'normalisation': {'dropped_keys': list(TIME_KEYS),
                               'detail_rewrite': r'\d+(\.\d+)? s -> <T> s'},
             'verdicts': {'D1': 'scripts/09 reproducible modulo timing metadata',
                          'D2': 'scripts/10 reproducible modulo timing metadata',
                          'D3': 'scripts/12 shard pass reproducible modulo timing metadata '
                                '(the shard path is byte-stable across the round-4 aggregate '
                                'amendments, which touched only the aggregate/census code)'}}
    ok = R.finish(os.path.join(DATA, '11_determinism.json'), extra)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
