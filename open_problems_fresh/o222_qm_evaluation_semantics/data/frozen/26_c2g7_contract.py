#!/usr/bin/env python3
"""O222 scripts/26 -- C2+G7 ENFORCER (docs/18_c2g7_contract.md, c2g7-contract-v1).

Pins the frozen inputs, refuses any implementation that touches float/random/heavy libs, checks that the
seven frozen ASCII anchors appear verbatim in BOTH the contract document and the machine, checks the
cell list, and reads the upstream GATE.  Writes data/26_c2g7_freeze.json + data/26_c2g7_contract_audit.json.

Usage:  /usr/bin/python3 scripts/26_c2g7_contract.py --freeze-impl scripts/27_c2g7_measure.py
"""
import ast
import hashlib
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
DOC = os.path.join(ROOT, 'docs', '18_c2g7_contract.md')
RULES = 'c2g7-contract-v1'

UPSTREAM = {
    'scripts/09_a2_rollback.py': 'd8037bb16f690a2935c7028b3680d48df6540e01c938ade1d3b5858aed594ace',
    'scripts/12_b5_budget.py': 'f2cb54fa5df094a1e2f7b4910a4c16726a37160f39b194f0157988823aeb1e7a',
    'scripts/15_b3r2_orderfair.py': '14e17e7cdff25b04cda70fe93010827505cec6f8b2059cc435f3f8775d9c375d',
}
ANCHORS = ['p_k = uniform', 'sum_s K[s][a] = 0', '|S| <= 2', 'vertex enumeration', 'sign_rank > 1',
           'diag(K', 'sqrt(p)sqrt(p)^T', '30000000', 'c2g7-contract-v1']
CELLS = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7']
BANNED_MODS = {'numpy', 'scipy', 'math', 'random', 'statistics', 'sympy', 'mpmath'}
BANNED_NAMES = {'pi', 'log', 'cos', 'sin', 'tan', 'exp', 'sqrt', 'log2', 'atan'}
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def sha(path):
    return hashlib.sha256(io.open(path, 'rb').read()).hexdigest()


def main():
    args = sys.argv[1:]
    impl_rel = None
    if '--freeze-impl' in args:
        impl_rel = args[args.index('--freeze-impl') + 1]
    if impl_rel is None:
        print('usage: scripts/26_c2g7_contract.py --freeze-impl scripts/27_c2g7_measure.py')
        return 2
    print('=' * 118)
    print('O222 scripts/26 -- C2+G7 enforcer (%s)   impl = %s' % (RULES, impl_rel))
    print('=' * 118, flush=True)

    ok_up = True
    for rel, want in sorted(UPSTREAM.items()):
        got = sha(os.path.join(ROOT, rel))
        ok_up &= (got == want)
        claim('U', 'frozen upstream %s pinned' % rel, got == want, 'sha256 %s' % got[:12])
    claim('U4', 'upstream GATE released by the G5 round', 'GATE = OPEN' in io.open(
        os.path.join(ROOT, 'logs/23_g5_contract.out'), encoding='utf-8').read(),
        'logs/23_g5_contract.out contains GATE = OPEN')

    cors = json.load(io.open(os.path.join(DATA, '09_a2_correlation.json'), encoding='utf-8'))
    claim('I2', 'correlation record structure (denominator 120, 62x62 tables, C1/C2/C1rev)',
          cors['denominator'] == 120 and len(cors['C1_num']) == 62 and len(cors['C2']) == 62
          and all(len(r) == 62 for r in cors['C1_num']) and all(len(r) == 62 for r in cors['C2']),
          'sha256 %s' % sha(os.path.join(DATA, '09_a2_correlation.json'))[:12])

    src = io.open(os.path.join(ROOT, impl_rel), encoding='utf-8').read()
    doc = io.open(DOC, encoding='utf-8').read()
    tree = ast.parse(src)
    miss = []
    for nm in BANNED_NAMES:
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == nm:
                miss.append('var:' + nm)
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods |= {a.name.split('.')[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module.split('.')[0])
    bad_mods = sorted(mods & BANNED_MODS)
    floatlits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            floatlits.append(node.value)
    claim('A1', 'machine imports no banned module', not bad_mods, 'imports = %s' % sorted(mods))
    claim('A2', 'machine declares no banned identifier', not miss, 'hits = %s' % sorted(set(miss)))
    claim('A3', 'machine contains no non-integer float literal', not floatlits, 'literals = %s' % floatlits[:6])
    claim('A4', 'no eval/exec/compile in the machine',
          not [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id in ('eval', 'exec', 'compile')])
    claim('A5', 'no random sampling anywhere in the machine', 'random' not in mods and 'random' not in src)

    bad = [a for a in ANCHORS if a not in src or a not in doc]
    claim('C1', 'all %d frozen ASCII anchors appear in BOTH the contract and the machine' % len(ANCHORS),
          not bad, 'missing = %s' % bad)
    claim('C2', 'the machine declares the seven frozen cells C1..C7 in order',
          "cell_order': ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7']" in src
          and all(('**%s**' % c) in doc for c in CELLS))
    claim('C3', 'the machine loads the two frozen interfaces (scripts/12 machine, scripts/15 anti)',
          '12_b5_budget.py' in src and '15_b3r2_orderfair.py' in src)
    claim('C4', 'the machine writes its own append-only result record',
          'data/27_c2g7_results.json' in src or "'27_c2g7_results.json'" in src)
    claim('C5', 'the machine never imports the enforcer or the audit', '26_c2g7_contract' not in src
          and '28_c2g7_audit' not in src)

    write = len(CLAIMS)
    npass = sum(1 for c in CLAIMS if c['ok'])
    gate = 'OPEN' if npass == write else 'REFUSED'
    rec = {'rules': RULES, 'impl': {'path': impl_rel, 'sha256': sha(os.path.join(ROOT, impl_rel))},
           'upstream': UPSTREAM, 'anchors': ANCHORS, 'gate': gate,
           'frozen_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
           'claims': CLAIMS, 'n_pass': npass, 'n_total': write}
    with io.open(os.path.join(DATA, '26_c2g7_freeze.json'), 'w', encoding='utf-8') as fh:
        json.dump(rec, fh, indent=1, ensure_ascii=False)
    with io.open(os.path.join(DATA, '26_c2g7_contract_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'claims': CLAIMS}, fh, indent=1, ensure_ascii=False)
    print('-' * 118)
    print('RESULT: %d/%d PASS' % (npass, write))
    print('GATE = %s   impl frozen at %s' % (gate, rec['impl']['sha256'][:12]))
    print('-' * 118)
    return 0 if gate == 'OPEN' else 1


if __name__ == '__main__':
    sys.exit(main())
