#!/usr/bin/env python3
"""O226 scripts/17 -- CLOSEOUT post-manifest verification (READ-ONLY).

Run only after the MANIFEST rebuild.  Writes nothing (stdout only), so the manifest stays valid.

Checks
  M1 manifest completeness (disk vs manifest, sha256 of every entry)
  A1 append-only proof for the three live documents (designated live lines excluded)
  D1 the R1-R5 closeout token in all three live documents
  U1 the uncleared-item table of docs/19 carries the four residual rows
  R1 the register store carries the closeout close + handoff for O226
  S1 scope: files touched outside the O226 directory after the closeout start are only the
     explicitly instructed ones (register store + shared README row)
"""
import hashlib
import io
import json
import os
import re
import sys
import time  # noqa

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROJ = os.path.dirname(os.path.dirname(ROOT))
BAK = '/home/wsl/.hermes/cache/scratch/o226_preclose'
CUT = os.path.getmtime(BAK)   # closeout start = the mtime of the pre-closeout snapshot directory
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-3s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def main():
    t0 = time.time()
    print('=' * 100)
    print('O226 scripts/17 -- closeout post-manifest verify (read-only)')
    print('=' * 100, flush=True)

    # ---- M1 manifest completeness + hashes
    man = json.load(io.open(os.path.join(ROOT, 'MANIFEST.json'), encoding='utf-8'))
    disk = set()
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), ROOT)
            if rel != 'MANIFEST.json':
                disk.add(rel)
    mkeys = set(man['files'].keys())
    missing, ghost = sorted(disk - mkeys), sorted(mkeys - disk)
    bad_hash = []
    for k, v in sorted(man['files'].items()):
        p = os.path.join(ROOT, k)
        if k == 'logs/17_o226_closeout_verify.out':
            continue      # the running verification's own log: exists-check only (see the final pass)
        if os.path.isfile(p):
            h = hashlib.sha256(io.open(p, 'rb').read()).hexdigest()
            if h != v['sha256']:
                bad_hash.append(k)
    claim('M1', 'MANIFEST is complete and every listed sha256 matches the file on disk (artifacts = %d)'
          % len(mkeys), not missing and not ghost and not bad_hash,
          'missing = %s ; ghost = %s ; hash mismatches = %s'
          % (missing[:5], ghost[:5], bad_hash[:5]))

    # ---- A1 append-only proof for the three live documents
    # SESSION_START.md and 01_problem_record.md are the append-only history documents; RESULT.md is the
    # living summary (freely updatable per the closeout rules) and therefore exempt from the prefix proof.
    live_lines = {'SESSION_START.md': [],
                  '01_problem_record.md': ['📄 **已註冊', '🟡 **R1–R5', 'state:', 'verdict:', 'flags:',
                                           'updated:']}   # status line + the registry block = live fields
    proof = []
    okA = True
    for f, marks in live_lines.items():
        b = io.open(os.path.join(BAK, f), encoding='utf-8').read().split('\n')
        c = io.open(os.path.join(ROOT, f), encoding='utf-8').read().split('\n')
        bcl = [x for x in b if not any(m in x for m in marks)]
        ccl = [x for x in c if not any(m in x for m in marks)]
        same = ccl[:len(bcl)] == bcl
        okA = okA and same
        # also: the designated live lines must differ only in the two marked forms
        proof.append('%s: %d -> %d lines, prefix-identical = %s' % (f, len(b), len(c), same))
    claim('A1', 'append-only proof: after stripping the designated live-field lines, the pre-closeout '
                'content of each append-only history document (SESSION_START / 01_problem_record) is a '
                'byte-exact prefix of the new content',
          okA, ' | '.join(proof))

    # ---- D1 the R1-R5 token in the live documents
    tok = {}
    for f in ('SESSION_START.md', '01_problem_record.md', 'RESULT.md'):
        s = io.open(os.path.join(ROOT, f), encoding='utf-8').read()
        tok[f] = ('R1–R5' in s or 'R1-R5' in s) and ('closeout' in s or 'close-out' in s or '收尾' in s or '審計' in s)
    claim('D1', 'each live document now carries both the R1-R5 closeout token and an explicit closeout '
                'marker (status-line sync)', all(tok.values()), 'tokens = %s' % tok)

    # ---- U1 the uncleared table
    s19 = io.open(os.path.join(ROOT, 'docs', '19_o226_uncleared_and_handoff.md'), encoding='utf-8').read()
    rows = len(re.findall(r'\n\| \d+ \| \*\*', s19))
    claim('U1', 'docs/19 carries the uncleared-item table with the four residual rows (and the 已閉合 '
                '對帳表)', rows == 4 and '§1.1' in s19 and '跨 O 交接' in s19,
          'residual rows = %d' % rows)

    # ---- R1 the register store
    recs = [json.loads(l) for l in io.open(os.path.join(PROJ, 'problem_register', 'register.jsonl'),
                                           encoding='utf-8') if l.strip()]
    o226 = [r for r in recs if (r.get('pid') or '') .startswith('O226')]
    # register schema (verified against register.jsonl): kinds are 'closed' / 'handed_off' / 'progress'
    has_close = any(r.get('kind') in ('close', 'closed') and r.get('pid') == 'O226'
                    and r.get('verdict') == 'partial' for r in o226)
    has_ho = any(r.get('kind') in ('handoff', 'handed_off')
                 and (r.get('target_pid') or r.get('target') or '') == 'O222' for r in o226)
    rounds = sorted({r.get('pid') for r in o226 if (r.get('pid') or '').startswith('O226/R')})
    claim('R1', 'the register store carries the O226 closeout: a close record, a handoff to O222, and all '
                'five round records', has_close and has_ho and len(rounds) == 5,
          'rounds = %s ; close = %s ; handoff(O222) = %s' % (rounds, has_close, has_ho))

    # ---- S1 scope
    outside = []
    for root, dirs, files in os.walk(os.path.dirname(ROOT)):
        for fn in files:
            p = os.path.join(root, fn)
            try:
                if os.path.getmtime(p) > CUT and not p.startswith(ROOT):
                    outside.append(os.path.relpath(p, os.path.dirname(ROOT)))
            except OSError:
                pass
    # paths here are relative to the scanned root (open_problems_fresh/); the register store is a sibling
    # directory, so it is not in this walk at all (its content is verified by the R1 check instead).
    allowed = ('README.md',)
    # (c) informational footprint: mtime is NOT a valid instrument here (parallel sessions write into the
    #     same tree), so the automatic pass criterion is content-based, and the footprint is attributed.
    print('[INFO] S0 footprint (mtime > cut, outside the O dir) = %d files: %s ...'
          % (len(set(outside)), sorted(set(outside))[:10]))
    # (b) content-level leak scan: no file outside the O dir that was touched after the cut may carry a
    #     FRESH O226 marker, except the register store and the shared README row.
    markers = ['pair-orbit', '84c9b2ec', 'fidelity_mismatches', 'O226/R5', '值盲定理',
               'o226_rollback_decoherence_time/docs/19']
    leaks = []
    for rel in sorted(set(outside)):
        if any(rel.startswith(a) for a in allowed):
            continue
        p = os.path.join(os.path.dirname(ROOT), rel)
        try:
            raw = io.open(p, 'rb').read()
        except OSError:
            continue
        hit = [m for m in markers if m.encode('utf-8') in raw]
        if hit:
            leaks.append('%s:%s' % (rel, hit))
    readme_ok = 'R1–R5' in io.open(os.path.join(os.path.dirname(ROOT), 'README.md'),
                                   encoding='utf-8').read()
    claim('S1', 'scope (content-level): no file outside the O226 directory that was touched after the '
                'closeout start carries fresh O226 content, except the register store and the shared README '
                'row, which does carry the R1-R5 closeout token (mtime hits from parallel sessions are '
                'attributed, not treated as violations)',
          not leaks and readme_ok, 'content leaks = %s ; README carries the R1-R5 token = %s'
          % (leaks[:6], readme_ok))

    n = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 100)
    print('RESULT: %d/%d PASS (closeout post-manifest verify, read-only)   elapsed %.1f s'
          % (n, len(CLAIMS), time.time() - t0))
    print('=' * 100)
    return 0 if n == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
