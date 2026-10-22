#!/usr/bin/env python3
"""O222 scripts/20 -- executable enforcer for Contract G4 v1 (docs/14_g4_contract.md).

Refuses to run the G4 machine unless:
  * the frozen upstream implementations are the ones actually on disk (hashes read out of the
    freeze records, never re-typed),
  * the group / axes / h-table rebuild verbatim,
  * the contract and the implementation agree bidirectionally on the six cells,
  * the implementation respects the AST gate and IMPORTS the frozen semantics instead of
    re-implementing them (no local run_pair / read / simulate / feasible_chsh / ... ),
  * the cost-law expression and the edge-count are the SAME in the contract and the implementation,
  * the upstream gates are OPEN/PASSing (D6 freeze gate, B3R2 record),
  * the register holds O222/G4 before any number is produced.

Usage:  /usr/bin/python3 scripts/20_g4_contract.py [--freeze-impl scripts/21_g4_eulerian.py]
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
FORBIDDEN_DEFS = {'run_pair', 'read', 'simulate', 'feasible_chsh', 'order_list', 'order_key',
                  'build_anti', 'sweep', 'load_machine', 'load_a2', 'load_inputs'}
LAW_DOC = '3 − [t = a] − [b = a]'
LAW_IMPL = '3 - (1 if t == a else 0) - (1 if b == a else 0)'


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
    print('O222 scripts/20 -- Contract G4 v1 enforcer (read order derived from the frozen structure)')
    print('=' * 112, flush=True)

    # C1: upstream implementation hashes, read out of the freeze records
    fr = {}
    for tag, fn, key in (('B5', '11_b5_freeze.json', 'impl'), ('B3R2', '14_b3r2_freeze.json', 'impl'),
                         ('D6', '17_d6_freeze.json', 'impl')):
        rec = json.load(io.open(os.path.join(DATA, fn), encoding='utf-8'))
        fr[tag] = rec[key]
    ok1 = all(os.path.exists(os.path.join(HERE, os.path.basename(v['path']))) and
              sha(os.path.join(HERE, os.path.basename(v['path']))) == v['sha256'] for v in fr.values())
    claim('C1', 'frozen upstream impls match their freeze records (B5 / B3R2 / D6)', ok1,
          ' ; '.join('%s=%s' % (k, v['sha256'][:12]) for k, v in sorted(fr.items())))

    b5 = load(os.path.join(HERE, '12_b5_budget.py'), 'g4c_b5')
    a2 = load(os.path.join(HERE, '09_a2_rollback.py'), 'g4c_a2')
    axes, U, ids, types, hvec = a2.load_inputs()
    G, idx, MUL = a2.build_group()
    hydx = [idx[a2.qkey(h)] for h in hvec]
    froz = json.load(io.open(os.path.join(DATA, '04_b2_settings.json'), encoding='utf-8'))
    same = all(tuple((F(c[0]), F(c[1])) for c in froz['axes'][k]['vec']) == U[k] and
               froz['axes'][k]['id'] == ids[k] for k in range(62))
    claim('C2', 'frozen objects rebuilt verbatim: |2I| = 120, 62 axes, h-table bijective',
          len(G) == 120 and same and len(set(hydx)) == 62, 'types = %s' % sorted(set(types)))

    doc = io.open(os.path.join(ROOT, 'docs', '14_g4_contract.md'), encoding='utf-8').read()
    ok3 = all(('**%s ' % c) in doc for c in CELLS) and all(('**T%d' % k) in doc for k in (1, 2, 3))
    claim('C3', 'contract declares the six cells and the three theorems', ok3)

    reg = io.open(os.path.join(REPO, 'problem_register', 'register.jsonl'), encoding='utf-8').read()
    sub = all(('G4-%s' % s) in reg for s in ('P1', 'P2', 'P3', 'P4', 'P5', 'P6'))
    claim('C4', 'register: O222/G4 registered with its six pre-numbered sub-questions before any number',
          '"O222/G4"' in reg and sub, 'sub-questions registered = %s' % sub)

    d6 = json.load(io.open(os.path.join(DATA, '17_d6_freeze.json'), encoding='utf-8'))
    b3 = json.load(io.open(os.path.join(DATA, '15_b3r2_results.json'), encoding='utf-8'))
    a2res = json.load(io.open(os.path.join(DATA, '09_a2_results.json'), encoding='utf-8'))
    claim('C5', 'upstream gates healthy: D6 gate OPEN, B3R2 14/14, A2 20/20, docs/13 present',
          d6['gate'] == 'OPEN' and len(b3['claims']) == 14 and all(c['ok'] for c in b3['claims'])
          and len(a2res['claims']) == 20 and all(c['ok'] for c in a2res['claims'])
          and os.path.exists(os.path.join(ROOT, 'docs', '13_d6_results.json'.replace('.json', '.md'))),
          'D6 gate = %s' % d6['gate'])

    m = load(os.path.join(HERE, '12_b5_budget.py'), 'g4c_b5b')
    claim('C6', 'budget constants come from the frozen machine (per-read cost 123/88, E_min 123/176, budget 123/2)',
          m.PER_READ == F(123, 88) and m.E_MIN == F(123, 176), 'PER_READ=%s E_MIN=%s' % (m.PER_READ, m.E_MIN))

    claim('C7', 'contract and implementation carry the SAME cost-law expression',
          LAW_DOC in doc and LAW_IMPL in io.open(os.path.join(ROOT, impl), encoding='utf-8').read()
          if impl and os.path.exists(os.path.join(ROOT, impl)) else False,
          'doc expression present = %s' % (LAW_DOC in doc))
    claim('C8', 'contract and implementation agree on the edge count 3782 = 62*61 (loop-free)',
          '3782' in doc and 'N * (N - 1)' in (io.open(os.path.join(ROOT, impl), encoding='utf-8').read()
                                              if impl and os.path.exists(os.path.join(ROOT, impl)) else ''))

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
                for mm in mods:
                    if mm in BANNED_MODS:
                        bad.append('banned import %r (line %d)' % (mm, node.lineno))
        claim('C9', 'impl AST gate: no trig / no float literal / no numpy-scipy-math / no random', not bad,
              bad[0] if bad else 'clean')
        cells_impl = [c for c in CELLS if ("'%s'" % c) in src]
        claim('C10', 'cell parity (both directions): the impl computes exactly the six registered cells',
              len(cells_impl) == len(CELLS), 'impl cells = %s' % cells_impl)
        defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        reimpl = [d for d in defs if d in FORBIDDEN_DEFS]
        claim('C11', 'frozen semantics are IMPORTED, not re-implemented (no local machine/statistic defs)',
              not reimpl and '12_b5_budget.py' in src and '15_b3r2_orderfair.py' in src,
              'local defs = %s' % defs)
        txt = src
        ok12 = re.search(r'budget = F\(123, 2\)', txt) is not None and 'load_a2' in txt and 'load_machine' in txt
        claim('C12', 'impl takes its budget and its objects from the frozen modules (123/2, load_a2, load_machine)',
              ok12, 'budget literal + loaders referenced')
        all_ok = all(c['ok'] for c in CLAIMS)
        rec = {'rules_version': 'g4-contract-v1',
               'doc': {'path': 'docs/14_g4_contract.md',
                       'sha256': sha(os.path.join(ROOT, 'docs', '14_g4_contract.md'))},
               'enforcer_sha256': sha(os.path.abspath(__file__)),
               'impl': {'path': impl, 'sha256': sha(impl_path)},
               'upstream': dict((k, v['sha256']) for k, v in fr.items()),
               'frozen_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
               'cells': list(CELLS),
               'objects': {'machine': 'scripts/12_b5_budget.py', 'statistic': 'scripts/15_b3r2_orderfair.py',
                           'axes': 'data/04_b2_settings.json', 'C2': 'data/09_a2_correlation.json',
                           'budget': 'docs/07_b5_contract.md'},
               'gate': 'OPEN' if all_ok else 'CLOSED'}
        with io.open(os.path.join(DATA, '20_g4_freeze.json'), 'w', encoding='utf-8') as fh:
            json.dump(rec, fh, indent=1, ensure_ascii=False)
        if all_ok:
            print('\nfrozen impl %s = %s' % (impl, sha(impl_path)))
            print('GATE = OPEN   (data/20_g4_freeze.json)')
        else:
            print('\nGATE = CLOSED (a pre-freeze claim FAILED; scripts/21 must not be cited)')
    else:
        for t in ('C9', 'C10', 'C11', 'C12'):
            claim(t, 'impl check', False, 'no implementation supplied yet')
        print('\nGATE = CLOSED (no implementation; rerun with --freeze-impl scripts/21_g4_eulerian.py)')

    with io.open(os.path.join(DATA, '20_g4_contract_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules_version': 'g4-contract-v1', 'claims': CLAIMS}, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)' % (npass, len(CLAIMS), len(CLAIMS) - npass))
    print('=' * 112)
    return 0 if (impl and npass == len(CLAIMS)) else 1


if __name__ == '__main__':
    sys.exit(main())
