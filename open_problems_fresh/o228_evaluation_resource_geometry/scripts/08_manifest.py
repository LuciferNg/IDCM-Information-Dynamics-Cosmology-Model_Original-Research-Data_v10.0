#!/usr/bin/env python3
"""O228 scripts/08 -- round manifest: sha256 of every deliverable + the read-only upstream pins.

Contract/discipline: 01_problem_record.md section 七 requires a MANIFEST each round (append-only).
Covers docs/, scripts/, data/, logs/ of this O plus the four frozen o222 files.
Output: data/00_o228_manifest.json  (the manifest itself is regenerated, and is declared as such).

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/08_manifest.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
O222 = os.path.abspath(os.path.join(ROOT, '..', 'o222_qm_evaluation_semantics'))
OUT = os.path.join(ROOT, 'data', '00_o228_manifest.json')
OUT2 = os.path.join(ROOT, 'MANIFEST.json')          # house convention: root MANIFEST.json
ROOT_FILES = ('01_problem_record.md', 'SESSION_START.md', 'final_result.md')
# self-referential: this script's own stdout log is (re)written by the very invocation that builds the
# manifest, so its bytes can never match the freshly written manifest.  Declared, not silently skipped.
SELF_OUT = ('logs/08_manifest.out',)
# audit self-products: rewritten by every run of the closeout audit itself, so their bytes can never match a
# manifest built by an earlier invocation.  Declared + excluded on BOTH sides (skill lesson #40); they are
# verified instead by the read-only closing check recorded in docs/21_closeout_audit.md.
SELF_PREFIX = ('logs/24_closeout', 'data/24_closeout')

UPSTREAM = {
    'scripts/12_b5_budget.py': 'f2cb54fa5df094a1e2f7b4910a4c16726a37160f39b194f0157988823aeb1e7a',
    'scripts/09_a2_rollback.py': 'd8037bb16f690a2935c7028b3680d48df6540e01c938ade1d3b5858aed594ace',
    'data/04_b2_settings.json': '2357006c68e0165dc9fd7d8d73524593a776e1bf6a8b62ddbc8dc2c1a8af20ee',
    'data/08_a2_h_table.json': 'adeaf8a7fb5495ea57be194c1a704c973a9208026cdd10ef615cd59c58005b66',
}


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    man = {'o': 'O228', 'round': 'R1-R4', 'date': '2026-10-02', 'files': {}, 'upstream': {}}
    n = 0
    for name in ROOT_FILES:
        p = os.path.join(ROOT, name)
        if os.path.isfile(p):
            man['files'][name] = sha(p)
            n += 1
    for sub in ('docs', 'scripts', 'data', 'logs'):
        d = os.path.join(ROOT, sub)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            p = os.path.join(d, name)
            rel = '%s/%s' % (sub, name)
            if not os.path.isfile(p) or p in (OUT, OUT2) or rel in SELF_OUT or rel.startswith(SELF_PREFIX):
                continue
            if name.endswith('.pyc'):
                continue
            man['files']['%s/%s' % (sub, name)] = sha(p)
            n += 1
    ok = True
    for rel, want in sorted(UPSTREAM.items()):
        got = sha(os.path.join(O222, rel))
        man['upstream']['o222_qm_evaluation_semantics/' + rel] = {'sha256': got, 'expected': want,
                                                                  'match': got == want}
        ok = ok and (got == want)
    man['n_files'] = n
    man['upstream_all_match'] = ok
    man['note'] = ('self-referential exclusions (declared): data/00_o228_manifest.json, MANIFEST.json, '
                   'logs/08_manifest.out (this script\'s own stdout) and every logs/24_closeout* / '
                   'data/24_closeout* (rewritten by each closeout-audit invocation). '
                   '*.pyc excluded; every other file under docs/scripts/data/logs plus the three root .md '
                   'files is covered.')
    for dst in (OUT, OUT2):
        with open(dst, 'w', encoding='utf-8') as fh:
            json.dump(man, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print('MANIFEST: %d files covered ; upstream sha256 all match = %s' % (n, ok))
    for k, v in sorted(man['upstream'].items()):
        print('   %-52s %s' % (k.split("/")[-1], 'OK' if v['match'] else 'MISMATCH'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
