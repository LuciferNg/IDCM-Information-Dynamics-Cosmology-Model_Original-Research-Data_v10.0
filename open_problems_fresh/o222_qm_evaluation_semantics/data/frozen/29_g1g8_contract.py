#!/usr/bin/env python3
"""O222 scripts/29 -- G1+G8 ENFORCER (docs/20_g1g8_contract.md, g1g8-contract-v1).

Pins the two frozen upstreams, refuses float/random/heavy-lib implementations, requires the six frozen
ASCII anchors verbatim in BOTH the contract and the machine, checks the cell list and the upstream GATE.

Usage:  /usr/bin/python3 scripts/29_g1g8_contract.py --freeze-impl scripts/30_g1g8_gaps.py
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
DOC = os.path.join(ROOT, 'docs', '20_g1g8_contract.md')
RULES = 'g1g8-contract-v1'

UPSTREAM = {
    'scripts/09_a2_rollback.py': 'd8037bb16f690a2935c7028b3680d48df6540e01c938ade1d3b5858aed594ace',
    'scripts/12_b5_budget.py': 'f2cb54fa5df094a1e2f7b4910a4c16726a37160f39b194f0157988823aeb1e7a',
    # I7 (added by amendment A1): the D6 machine, whose ledger measured reach depth = 1
    'scripts/18_d6_mapping.py': 'a681ae8cf6bcfd69b50a9a3c776f8c43011c3b6c52149bc1f1f565abbe797cf7',
}
ANCHORS = ['s_coord(ctx) = idx[h(ctx)]', '|N(s) - s|^2 > 0', 'value-level consistency',
           'ledger entries per ctx', 'R_consistent = 1', 'R >= 2']
CELLS = ['G1a', 'G1b', 'G1c', 'G8a', 'G8b', 'G8c']
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
    impl_rel = args[args.index('--freeze-impl') + 1] if '--freeze-impl' in args else None
    if impl_rel is None:
        print('usage: scripts/29_g1g8_contract.py --freeze-impl scripts/30_g1g8_gaps.py')
        return 2
    print('=' * 118)
    print('O222 scripts/29 -- G1+G8 enforcer (%s)   impl = %s' % (RULES, impl_rel))
    print('=' * 118, flush=True)

    for rel, want in sorted(UPSTREAM.items()):
        got = sha(os.path.join(ROOT, rel))
        claim('U', 'frozen upstream %s pinned' % rel, got == want, 'sha256 %s' % got[:12])
    claim('U3', 'upstream GATE released by the C2+G7 round',
          'GATE = OPEN' in io.open(os.path.join(ROOT, 'logs/26_c2g7_contract.out'), encoding='utf-8').read(),
          'logs/26_c2g7_contract.out contains GATE = OPEN')

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
    floatlits = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, float)]
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
    claim('C2', 'the machine declares the six frozen cells G1a..G8c in order',
          "cell_order': ['G1a', 'G1b', 'G1c', 'G8a', 'G8b', 'G8c']" in src
          and all(('**%s**' % c) in doc for c in CELLS))
    claim('C3', 'the machine loads the two frozen interfaces and reads the single frozen order',
          '09_a2_rollback.py' in src and '12_b5_budget.py' in src
          and 'for a in range(N) for b in range(N)' in src)
    claim('C4', 'the machine writes its own result record',
          "'30_g1g8_results.json'" in src or 'data/30_g1g8_results.json' in src)
    claim('C5', 'the machine never imports the enforcer or the audit',
          '29_g1g8_contract' not in src and '31_g1g8_audit' not in src)
    defs = sorted(set(n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)))
    claim('C6', 'no unrestricted local protocol: the only permitted helper is the declared ledger replay, and it '
                'must be validated pair by pair against the frozen I7 replay_protocol (amendment A1)',
          set(defs) <= {'main', 'claim', 'load', 'q_str', 'ledger_replay', '_hist'} and 'b5.run_pair(' in src
          and 'd6.replay_protocol(' in src
          and 'the explicit ledger replay reproduces the frozen D6 protocol (I7) pair by pair' in src,
          'local defs = %s' % defs)
    claim('C7', 'the machine loads I7 (the D6 machine) by filename and reports the replay validation',
          '18_d6_mapping.py' in src and 'validation_vs_I7' in src)

    npass = sum(1 for c in CLAIMS if c['ok'])
    gate = 'OPEN' if npass == len(CLAIMS) else 'REFUSED'
    rec = {'rules': RULES, 'impl': {'path': impl_rel, 'sha256': sha(os.path.join(ROOT, impl_rel))},
           'upstream': UPSTREAM, 'anchors': ANCHORS, 'gate': gate,
           'frozen_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'claims': CLAIMS,
           'n_pass': npass, 'n_total': len(CLAIMS)}
    with io.open(os.path.join(DATA, '29_g1g8_freeze.json'), 'w', encoding='utf-8') as fh:
        json.dump(rec, fh, indent=1, ensure_ascii=False)
    with io.open(os.path.join(DATA, '29_g1g8_contract_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'claims': CLAIMS}, fh, indent=1, ensure_ascii=False)
    print('-' * 118)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('GATE = %s   impl frozen at %s' % (gate, rec['impl']['sha256'][:12]))
    print('-' * 118)
    return 0 if gate == 'OPEN' else 1


if __name__ == '__main__':
    sys.exit(main())
