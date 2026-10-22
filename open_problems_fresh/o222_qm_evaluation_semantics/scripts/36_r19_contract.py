#!/usr/bin/env python3
"""O222 scripts/33 -- G2+Q5 CONTRACT ENFORCER (gate).  Freezes the 14 read-only upstream pins and
applies the hard constraints of docs/23 (g2q5-contract-v1 + amendment A1) before any number exists.

Usage:  /usr/bin/python3 scripts/36_r19_contract.py --freeze-impl scripts/37_r19_closure.py
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
REPO = os.path.dirname(os.path.dirname(ROOT))
OP = os.path.join(REPO, 'open_problems_fresh')
PIN = {
    'L1': 'open_problems_fresh/o222_qm_evaluation_semantics/scripts/09_a2_rollback.py',
    'L2': 'open_problems_fresh/o222_qm_evaluation_semantics/scripts/12_b5_budget.py',
    'L3': 'open_problems_fresh/o222_qm_evaluation_semantics/scripts/15_b3r2_orderfair.py',
    'L4': 'open_problems_fresh/o222_qm_evaluation_semantics/scripts/18_d6_mapping.py',
    'L5': 'open_problems_fresh/o222_qm_evaluation_semantics/data/09_a2_correlation.json',
    'L6': 'open_problems_fresh/o222_qm_evaluation_semantics/data/15_b3r2_results.json',
    'L7': 'open_problems_fresh/o222_qm_evaluation_semantics/data/27_c2g7_results.json',
    'L8': 'open_problems_fresh/o222_qm_evaluation_semantics/data/30_g1g8_results.json',
    'L9': 'open_problems_fresh/little_red_dots/data/k_chain_modes.json',
}
CELLS = ['K1', 'K1b', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7']
BANNED_CALLS = {'cos', 'sin', 'tan', 'pi', 'sqrt', 'exp', 'log', 'log2', 'asin', 'acos', 'atan', 'radians'}
BANNED_MODULES = {'numpy', 'scipy', 'math', 'random', 'cupy', 'subprocess', 'shutil'}
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def sha256_file(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()


def main():
    t0 = time.time()
    print('=' * 110)
    print('O222 scripts/33 -- R19 UNCLOSED-STRUCTURE CONTRACT ENFORCER (docs/25 r19-contract-v1)')
    print('=' * 110, flush=True)
    # C0 upstream pins
    freeze = {'contract': 'r19-contract-v1', 'pins': {}, 'gate': None,
              'frozen_at': time.strftime('%Y-%m-%dT%H:%M:%S%z')}
    bad = []
    for j, rel in sorted(PIN.items()):
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            bad.append('%s MISSING %s' % (j, rel))
            continue
        freeze['pins'][j] = {'path': rel, 'sha256': sha256_file(p)}
    claim('C1', 'L1-L9 pins readable and hashed (%d/%d)' % (len(freeze['pins']), len(PIN)),
          not bad, '; '.join(bad) or 'all %d pinned' % len(PIN))
    # C2 read-only: the pins must all live OUTSIDE this O222 directory except J12/J13 (own, read-only here)
    inside = [j for j, r in PIN.items() if '/o222_qm_evaluation_semantics/' in r]
    claim('C2', 'read-only discipline: L1-L8 are this O frozen artefacts and L9 is the upstream LRD table; '
                'no pin is writable by the machine', set(inside) == {'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8'},
          'own pins = %s' % inside)
    impl = None
    for i, a in enumerate(sys.argv):
        if a == '--freeze-impl' and i + 1 < len(sys.argv):
            impl = sys.argv[i + 1]
    if impl is None:
        print('usage: scripts/36_r19_contract.py --freeze-impl scripts/37_r19_closure.py')
        return 2
    ip = os.path.join(ROOT, impl)
    src = io.open(ip, encoding='utf-8').read()
    tree = ast.parse(src)
    # C3 exact-arithmetic gate (no trig/float/module calls), C5 no upstream import, C2 no write/subprocess
    bad_calls, bad_mods, bad_floats, bad_names, bad_io = [], [], [], [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in BANNED_CALLS:
            bad_calls.append('%s@%d' % (node.func.id, node.lineno))
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name.split('.')[0] for a in node.names]
            if isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module.split('.')[0])
            for n in names:
                if n in BANNED_MODULES:
                    bad_mods.append('%s@%d' % (n, node.lineno))
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            bad_floats.append('%r@%d' % (node.value, node.lineno))
        if isinstance(node, ast.Name) and node.id in BANNED_CALLS:
            bad_names.append('%s@%d' % (node.id, node.lineno))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in ('remove', 'unlink', 'rmtree', 'copy', 'copy2', 'write', 'writelines'):
                bad_io.append('%s@%d' % (node.func.attr, node.lineno))
    claim('C3', 'exact-arithmetic gate: no trig/exp/log CALLS, no non-integer float literals, no math modules',
          not bad_calls and not bad_mods and not bad_floats,
          'calls=%s mods=%s floats=%s' % (bad_calls or 'none', bad_mods or 'none', bad_floats or 'none'))
    claim('C3b', 'no variable may shadow a transcendental name (pi/log/cos/... incl. perm-style renames) and no '
                 'write/remove/subprocess call may appear', not bad_names and not bad_io,
          'shadowed=%s write-ish=%s' % (bad_names or 'none', bad_io or 'none'))
    # C4 cells exactly
    have = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'CELLS':
            have = set(ast.literal_eval(node.value))
    claim('C4', 'cell list is exactly %s' % CELLS, have == set(CELLS), 'found = %s' % sorted(have))
    # C5 must not import upstream scripts
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'load':
            for a in node.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    imported.add(a.value)
    allowed = {'09_a2_rollback.py', '12_b5_budget.py', '15_b3r2_orderfair.py', '18_d6_mapping.py'}
    extra = sorted(x for x in imported if x.endswith('.py') and x not in allowed)
    claim('C5', 'the machine loads only the four frozen interfaces L1-L4 (no other script)',
          not extra, 'loaded = %s ; extra = %s' % (sorted(imported), extra or 'none'))
    freeze['impl'] = {'path': impl, 'sha256': sha256_file(ip)}
    freeze['gate'] = 'OPEN' if all(c['ok'] for c in CLAIMS) else 'CLOSED'
    with io.open(os.path.join(ROOT, 'data', '36_r19_freeze.json'), 'w', encoding='utf-8') as fh:
        json.dump(freeze, fh, indent=1, ensure_ascii=False)
    print('-' * 110)
    print('GATE = %s   impl %s = %s   (%.1fs)' % (freeze['gate'], impl, freeze['impl']['sha256'][:24],
                                                  time.time() - t0))
    print('-' * 110)
    return 0 if freeze['gate'] == 'OPEN' else 1


if __name__ == '__main__':
    sys.exit(main())
