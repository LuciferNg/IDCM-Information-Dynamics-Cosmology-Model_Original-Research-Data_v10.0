#!/usr/bin/env python3
"""O222 scripts/23 -- executable enforcer for Contract G5 v1 (docs/16_g5_contract.md).

Refuses to run the G5 machine unless:
  * the frozen upstream implementations are the ones actually on disk (hashes read out of the freeze
    records, never re-typed),
  * the frozen objects rebuild verbatim INCLUDING the anti structural lemma (62 axes = 31 antipodal
    pairs; every row has exactly one anti column) that T3 depends on,
  * the contract and the implementation agree bidirectionally on the six cells,
  * the implementation respects the AST gate (notably: no `random` module -- the sampler must be a
    hand-written LCG) and IMPORTS the frozen semantics instead of re-implementing them,
  * the sampling rule, the prefix-length rule and the fallback thresholds are the SAME strings in the
    contract and in the implementation,
  * the upstream gates are OPEN/PASSing and the register holds O222/G5 before any number is produced.

Usage:  /usr/bin/python3 scripts/23_g5_contract.py [--freeze-impl scripts/24_g5_criterion.py]
"""
import ast
import hashlib
import importlib.util
import io
import json
import os
import re
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
REPO = os.path.abspath(os.path.join(ROOT, '..', '..'))
CLAIMS = []
BANNED_MODS = {'numpy', 'scipy', 'math', 'random', 'cmath', 'statistics'}
BANNED_NAMES = {'cos', 'sin', 'tan', 'acos', 'asin', 'atan', 'atan2', 'pi', 'sqrt', 'exp', 'log',
                'numpy', 'scipy', 'math', 'random'}
CELLS = ('P1', 'P2', 'P3', 'P4', 'P5', 'P6')
FORBIDDEN_DEFS = {'feasible_chsh', 'build_anti', 'order_list', 'order_key', 'simulate', 'run_pair',
                  'read', 'hierholzer', 'load_machine', 'load_a2', 'load_inputs', 'sweep'}
PARITY = ['c(a,a2) >= 2', 'min(21', '1103515245', '20260930', '600', '30000000']


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def sha(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    argv = sys.argv[1:]
    impl = argv[argv.index('--freeze-impl') + 1] if '--freeze-impl' in argv else None
    print('=' * 112)
    print('O222 scripts/23 -- Contract G5 v1 enforcer (rectangle criterion: exact / necessary / sufficient)')
    print('=' * 112, flush=True)

    fr = {}
    for tag, fn in (('B5', '11_b5_freeze.json'), ('B3R2', '14_b3r2_freeze.json'),
                    ('D6', '17_d6_freeze.json'), ('G4', '20_g4_freeze.json')):
        rec = json.load(io.open(os.path.join(DATA, fn), encoding='utf-8'))
        fr[tag] = rec
    ok1 = all(os.path.exists(os.path.join(ROOT, v['impl']['path'])) and
              sha(os.path.join(ROOT, v['impl']['path'])) == v['impl']['sha256'] for v in fr.values())
    claim('C1', 'frozen upstream impls match their freeze records (B5 / B3R2 / D6 / G4)', ok1,
          ' ; '.join('%s=%s' % (k, v['impl']['sha256'][:12]) for k, v in sorted(fr.items())))

    b5 = load(os.path.join(HERE, '12_b5_budget.py'), 'g5c_b5')
    a2 = load(os.path.join(HERE, '09_a2_rollback.py'), 'g5c_a2')
    b3r = load(os.path.join(HERE, '15_b3r2_orderfair.py'), 'g5c_b3')
    axes, U, ids, types, hvec = a2.load_inputs()
    G, idx, MUL = a2.build_group()
    hydx = [idx[a2.qkey(h)] for h in hvec]
    mm, K, MUL2, hx, ids2, types2 = b5.load_machine()
    anti = b3r.build_anti(mm, U)
    n_anti = sum(1 for a in range(62) for b in range(62) if anti[a][b])
    per_row = [sum(1 for b in range(62) if anti[a][b]) for a in range(62)]
    froz = json.load(io.open(os.path.join(DATA, '04_b2_settings.json'), encoding='utf-8'))
    same = all(tuple((F(c[0]), F(c[1])) for c in froz['axes'][k]['vec']) == U[k] and
               froz['axes'][k]['id'] == ids[k] for k in range(62))
    claim('C2', 'frozen objects rebuilt: |2I| = 120, 62 axes, h bijective, and the anti structural lemma '
                '(31 antipodal pairs, exactly one anti column per row)',
          len(G) == 120 and same and len(set(hydx)) == 62 and n_anti == 31 * 2
          and min(per_row) == 1 and max(per_row) == 1,
          'anti True entries = %d (31 pairs), per-row min/max = %d/%d' % (n_anti, min(per_row), max(per_row)))

    doc = io.open(os.path.join(ROOT, 'docs', '16_g5_contract.md'), encoding='utf-8').read()
    ok3 = all(('**%s ' % c) in doc for c in CELLS) and all(('**T%d' % k) in doc for k in (1, 2, 3, 4, 5))
    claim('C3', 'contract declares the six cells and the five theorems', ok3)

    reg = io.open(os.path.join(REPO, 'problem_register', 'register.jsonl'), encoding='utf-8').read()
    sub = all(('G5-%s' % s) in reg for s in ('P1', 'P2', 'P3', 'P4', 'P5', 'P6'))
    claim('C4', 'register: O222/G5 registered with its six pre-numbered sub-questions before any number',
          '"O222/G5"' in reg and sub, 'sub-questions = %s' % sub)

    b3 = json.load(io.open(os.path.join(DATA, '15_b3r2_results.json'), encoding='utf-8'))
    g4 = json.load(io.open(os.path.join(DATA, '21_g4_results.json'), encoding='utf-8'))
    claim('C5', 'upstream gates healthy: D6 / B3R2 / G4 gates OPEN or all-PASS, docs/15 + data/21 present',
          fr['D6']['gate'] == 'OPEN' and fr['G4']['gate'] == 'OPEN'
          and all(c['ok'] for c in b3['claims']) and g4['cells']['P1']['verdict'] == '✅'
          and os.path.exists(os.path.join(ROOT, 'docs', '15_g4_results.md')),
          'D6=%s G4=%s B3R2=%d claims' % (fr['D6']['gate'], fr['G4']['gate'], len(b3['claims'])))

    impl_path = os.path.join(ROOT, impl) if impl else None
    if impl_path and os.path.exists(impl_path):
        src = io.open(impl_path, encoding='utf-8').read()
        tree = ast.parse(src)
        bad = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, float):
                bad.append('float literal %r (line %d)' % (node.value, node.lineno))
            if isinstance(node, ast.Name) and node.id in BANNED_NAMES:
                bad.append('banned name %r (line %d)' % (node.id, node.lineno))
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name.split('.')[0] for a in node.names] if isinstance(node, ast.Import) \
                    else [(node.module or '').split('.')[0]]
                for mm2 in mods:
                    if mm2 in BANNED_MODS:
                        bad.append('banned import %r (line %d)' % (mm2, node.lineno))
        claim('C6', 'impl AST gate: no trig / no float literal / no numpy-scipy-math / NO random module '
                    '(the sampler must be a hand-written LCG)', not bad, bad[0] if bad else 'clean')
        cells_impl = [c for c in CELLS if ("'%s'" % c) in src]
        claim('C7', 'cell parity (both directions): the impl computes exactly the six registered cells',
              len(cells_impl) == len(CELLS), 'impl cells = %s' % cells_impl)
        defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        reimpl = [d for d in defs if d in FORBIDDEN_DEFS]
        claim('C8', 'frozen semantics IMPORTED, not re-implemented (no local criterion/sampler/machine defs)',
              not reimpl and '12_b5_budget.py' in src and '15_b3r2_orderfair.py' in src
              and '21_g4_eulerian.py' in src, 'local defs = %s' % defs)
        miss = [p for p in PARITY if p not in src or p not in doc]
        claim('C9', 'contract<->impl string parity: criterion, prefix rule, LCG constants, fallback caps',
              not miss, 'missing in one side = %s' % miss)
        claim('C10', 'the impl states the pre-registered sample size and the degenerate small-n prefixes',
              ('K = 1000' in src or 'K = 1000' in doc) and 'L_small' in src and 'L_small' in doc,
              'sampler + small-n rules present in both')
        claim('C11', 'the impl carries no assertion of a target value (no hard-coded proportions or rz(n))',
              not re.search(r'\brz\s*\(\s*[345]\s*\)\s*==', src) and 'assert ' not in src,
              'no target-value assertions')
        claim('C12', 'the impl reads its prefixes and its anti matrix from the frozen modules (no local geometry)',
              'load_a2' in src and 'load_machine' in src and 'build_anti' in src, '')
        all_ok = all(c['ok'] for c in CLAIMS)
        rec = {'rules_version': 'g5-contract-v1',
               'doc': {'path': 'docs/16_g5_contract.md',
                       'sha256': sha(os.path.join(ROOT, 'docs/16_g5_contract.md'))},
               'enforcer_sha256': sha(os.path.abspath(__file__)),
               'impl': {'path': impl, 'sha256': sha(impl_path)},
               'upstream': dict((k, v['impl']['sha256']) for k, v in fr.items()),
               'frozen_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
               'cells': list(CELLS),
               'objects': {'criterion': 'scripts/15_b3r2_orderfair.py::feasible_chsh(all4)',
                           'anti': 'scripts/15_b3r2_orderfair.py::build_anti',
                           'machine': 'scripts/12_b5_budget.py', 'eulerian': 'scripts/21_g4_eulerian.py',
                           'settings': 'data/04_b2_settings.json'},
               'gate': 'OPEN' if all_ok else 'CLOSED'}
        with io.open(os.path.join(DATA, '23_g5_freeze.json'), 'w', encoding='utf-8') as fh:
            json.dump(rec, fh, indent=1, ensure_ascii=False)
        if all_ok:
            print('\nfrozen impl %s = %s' % (impl, sha(impl_path)))
            print('GATE = OPEN   (data/23_g5_freeze.json)')
        else:
            print('\nGATE = CLOSED (a pre-freeze claim FAILED; scripts/24 must not be cited)')
    else:
        for t in ('C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12'):
            claim(t, 'impl check', False, 'no implementation supplied yet')
        print('\nGATE = CLOSED (rerun with --freeze-impl scripts/24_g5_criterion.py)')

    with io.open(os.path.join(DATA, '23_g5_contract_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules_version': 'g5-contract-v1', 'claims': CLAIMS}, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)' % (npass, len(CLAIMS), len(CLAIMS) - npass))
    print('=' * 112)
    return 0 if (impl and npass == len(CLAIMS)) else 1


if __name__ == '__main__':
    sys.exit(main())
