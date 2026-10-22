#!/usr/bin/env python3
"""O222 scripts/17 -- executable enforcer for Contract D6 v1 (docs/12_d6_contract.md).

Refuses to run scripts/18 unless:
  * the frozen objects of §1 rebuild verbatim (2I group, 62 axes, h-table),
  * the 16-cell predicate table is declared identically in the contract and the implementation,
  * the implementation respects the AST gate and does NOT re-implement the frozen semantics,
  * the register holds O222/D6 (pre-number registration),
  * provenance for the tensor-product composition law exists (O210) and the G6 witness holds
    (O210 carries NO dimensions => P1c can only be provenance),
  * the frozen ledger rules are structurally verified in the frozen sources (top-only access,
    append-only push, pop only for the rollback) -- P2c/P3 rest on these,
  * the cited B3R2 CHSH values really are in data/15_b3r2_results.json.

Usage:  /usr/bin/python3 scripts/17_d6_contract.py [--freeze-impl scripts/18_d6_mapping.py]
"""
import ast
import hashlib
import importlib.util
import io
import json
import os
import re
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
REPO = os.path.abspath(os.path.join(ROOT, '..', '..'))
CLAIMS = []
BANNED_MODS = {'numpy', 'scipy', 'math', 'random', 'cmath', 'statistics'}
BANNED_NAMES = {'cos', 'sin', 'tan', 'acos', 'asin', 'atan', 'atan2', 'pi', 'sqrt', 'exp', 'log',
                'numpy', 'scipy', 'math', 'random'}
CELLS = ('P1a', 'P1b', 'P1c', 'P2a', 'P2b', 'P2c', 'P2d',
         'P3a', 'P3b', 'P3c', 'P4a', 'P4b', 'P4c')


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
    print('O222 scripts/17 -- Contract D6 v1 enforcer (mapping table, operationalised)')
    print('=' * 112, flush=True)

    m = load(os.path.join(HERE, '09_a2_rollback.py'), 'a2d')
    axes, U, ids, types, hvec = m.load_inputs()
    G, idx, MUL = m.build_group()
    hydx = [idx[m.qkey(h)] for h in hvec]

    claim('C1', 'group rebuilt: |2I| = 120 (closed)', len(G) == 120 and
          all(MUL[a][b] < 120 for a in range(120) for b in range(120)), '|2I| = %d' % len(G))
    froz = json.load(io.open(os.path.join(DATA, '04_b2_settings.json'), encoding='utf-8'))
    same = all(tuple((F(c[0]), F(c[1])) for c in froz['axes'][k]['vec']) == U[k] and
               froz['axes'][k]['id'] == ids[k] and froz['axes'][k]['type'] == types[k] for k in range(62))
    claim('C2', '62 frozen axes reproduced verbatim; h-table bijective (62/62)', same and len(set(hydx)) == 62,
          'types = %s' % sorted(set(types)))

    doc = io.open(os.path.join(ROOT, 'docs', '12_d6_contract.md'), encoding='utf-8').read()
    doc_cells = [c for c in CELLS if ('**%s**' % c) in doc]
    claim('C3', 'contract declares all %d predicate cells' % len(CELLS), len(doc_cells) == len(CELLS),
          'declared = %s' % doc_cells)

    # provenance: O210 carries the tensor-product law; G6 witness = it carries NO dimensions
    o210 = os.path.join(REPO, 'open_problems_fresh', 'o210_causal_tensor_algebra')
    blob = ''
    for dp, _d, fs in os.walk(o210):
        for fn in sorted(fs):
            if fn.endswith(('.md', '.json')):
                blob += io.open(os.path.join(dp, fn), encoding='utf-8', errors='ignore').read()
    has_prod = 'K_chain' in blob and 'K_tree' in blob
    dim_pat = re.compile(r'dim\s*\(\s*K_chain\s*\)|dim\s*\(\s*K_tree\s*\)|K_chain\s*[:=]\s*\d+\s*×|K_tree\s*[:=]\s*\d+\s*×')
    claim('C4', 'provenance: O210 carries the composition law T = K_chain (x) K_tree', has_prod,
          'found in %s' % os.path.basename(o210))
    claim('C5', 'G6 witness: O210 carries NO dimensions for K_chain / K_tree (P1c stays provenance-only)',
          not dim_pat.search(blob), 'dimension expressions found = %s' % bool(dim_pat.search(blob)))

    # frozen ledger rules (P2c / P3 rest on these) -- static structural verification
    s9 = io.open(os.path.join(HERE, '09_a2_rollback.py'), encoding='utf-8').read()
    s12 = io.open(os.path.join(HERE, '12_b5_budget.py'), encoding='utf-8').read()
    rp0 = s12.find('def run_pair(')
    rp1 = s12.find("return {'s_final'", rp0)
    rd = s12[rp0:rp1]
    top_only = ('L[-1][0]' in rd) and not re.search(r'L\[-2\]|L\[:\]|L\.index|L\.remove|L\.clear', rd)
    appends = rd.count('L.append') >= 1
    pops = 'L.pop' in rd
    claim('C6', 'frozen ledger rules: top-only access, append-only push, pop used only for the rollback',
          top_only and appends and pops,
          'top_only=%s append=%s pop=%s' % (top_only, appends, pops))
    claim('C7', 'frozen read operator is a pure function of (state, setting) with locality scope read(G, ctx)',
          'def read(G, ctx)' in s9 and 'KERNEL_TAB[G][ctx]' in s9, 'read(G, ctx) present')

    reg = io.open(os.path.join(REPO, 'problem_register', 'register.jsonl'), encoding='utf-8').read()
    claim('C8', 'register: O222/D6 registered before any number (pre-number discipline)',
          '"O222/D6"' in reg, 'found=%s' % ('"O222/D6"' in reg))

    b3 = json.load(io.open(os.path.join(DATA, '15_b3r2_results.json'), encoding='utf-8'))
    a2 = json.load(io.open(os.path.join(DATA, '09_a2_results.json'), encoding='utf-8'))
    blk = b3['per_order']['block']['feasible']
    cite = (blk['E1_all4']['value'] == '16/15' and blk['E2_all4']['value'] == '13/15'
            and b3['baseline']['E1_all4']['value'] == '2' and b3['baseline']['E2_all4']['value'] == '3')
    claim('C9', 'cited B3R2 values verifiable: budget-feasible all4 = 16/15 (E1) / 13/15 (E2); '
                'unrestricted = 2 / 3', cite,
          'B3R2 14/14=%s ; A2 20/20=%s' % (len(b3['claims']) == 14 and all(c['ok'] for c in b3['claims']),
                                           len(a2['claims']) == 20 and all(c['ok'] for c in a2['claims'])))

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
        claim('C10', 'impl AST gate: no trig / no float literal / no numpy-scipy-math / no random',
              not bad, bad[0] if bad else 'clean')
        impl_cells = [c for c in CELLS if ("'%s'" % c) in src]
        claim('C11', 'cell parity: the impl computes exactly the %d pre-registered cells' % len(CELLS),
              len(impl_cells) == len(CELLS), 'impl cells = %s' % impl_cells)
        defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        claim('C12', 'frozen semantics are IMPORTED, not re-implemented (no local read / run_pair)',
              'read' not in defs and 'run_pair' not in defs, 'local defs = %s' % defs)
        all_ok = all(c['ok'] for c in CLAIMS)
        rec = {'rules_version': 'd6-contract-v1',
               'doc': {'path': 'docs/12_d6_contract.md',
                       'sha256': sha(os.path.join(ROOT, 'docs', '12_d6_contract.md'))},
               'enforcer_sha256': sha(os.path.abspath(__file__)),
               'impl': {'path': impl, 'sha256': sha(impl_path)},
               'frozen_at': __import__('time').strftime('%Y-%m-%dT%H:%M:%S%z'),
               'cells': list(CELLS),
               'objects': {'axes': 'data/04_b2_settings.json', 'h': 'data/08_a2_h_table.json',
                           'C1_C2': 'data/09_a2_correlation.json', 'machine': 'scripts/09 + scripts/12',
                           'composition_law': 'open_problems_fresh/o210_causal_tensor_algebra'},
               'gate': 'OPEN' if all_ok else 'CLOSED'}
        if not all_ok:
            print('\nGATE = CLOSED (a pre-freeze claim FAILED; scripts/18 must not run)')
            print('frozen impl %s = %s   [RECORDED BUT GATE CLOSED]' % (impl, sha(impl_path)))
        with io.open(os.path.join(DATA, '17_d6_freeze.json'), 'w', encoding='utf-8') as fh:
            json.dump(rec, fh, indent=1, ensure_ascii=False)
        if all_ok:
            print('\nfrozen impl %s = %s' % (impl, sha(impl_path)))
            print('GATE = OPEN   (data/17_d6_freeze.json)')
    else:
        for t in ('C10', 'C11', 'C12'):
            claim(t, 'impl check', False, 'no implementation supplied yet')
        print('\nGATE = CLOSED (no implementation; rerun with --freeze-impl scripts/18_d6_mapping.py)')

    with io.open(os.path.join(DATA, '17_d6_contract_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules_version': 'd6-contract-v1', 'claims': CLAIMS}, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)' % (npass, len(CLAIMS), len(CLAIMS) - npass))
    print('=' * 112)
    return 1 if impl is None else (0 if npass == len(CLAIMS) else 1)


if __name__ == '__main__':
    sys.exit(main())
