#!/usr/bin/env python3
"""O222 scripts/14 -- executable enforcer for Contract B3R2 v1 (docs/10_b3r2_contract.md).

Refuses to run scripts/15 unless every frozen input reproduces:
  * the 2I group, the 62 lattice axes (verbatim vs data/04_b2_settings.json), the A2 h-table,
  * the frozen A2 (20/20) and B5 (8/8) result sets this round builds on,
  * the exact budget identities of I1-I4 (123/2, 123/176, 123/88 = 2 x E_min, 44 reads, tau_deco = 2),
  * the five pre-registered order rules are BIJECTIONS on the 3844 pairs (no collapsed prefix),
  * the fairness criterion is coverage-based (docs/10) and the rule IDs agree doc<->enforcer<->impl,
  * implementation AST gate: no trig / no float literal / no numpy-scipy-math / no random,
  * full-enumeration requirement declared for the authoritative feasible-CHSH values.

Usage:  /usr/bin/python3 scripts/14_b3r2_contract.py [--freeze-impl scripts/15_b3r2_orderfair.py]
"""
import ast
import hashlib
import importlib.util
import io
import json
import os
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
ORDER_IDS = ('lex', 'diag', 'antidiag', 'block', 'stride')


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-6s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def sha(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()


def order_key(oid, a, b):
    """the five pre-registered total orders (mirror of scripts/15; parity-checked)."""
    if oid == 'lex':
        return (a, b)
    if oid == 'diag':
        return ((b - a) % 62, a, b)
    if oid == 'antidiag':
        return ((a + b) % 62, a, b)
    if oid == 'block':
        return (max(a, b), min(a, b), a)
    if oid == 'stride':
        return ((b - 13 * a) % 62, b, a)
    raise KeyError(oid)


def main():
    argv = sys.argv[1:]
    impl = argv[argv.index('--freeze-impl') + 1] if '--freeze-impl' in argv else None
    print('=' * 112)
    print('O222 scripts/14 -- Contract B3R2 v1 enforcer (B3 round 2: order-fair allocation in 44 reads)')
    print('=' * 112, flush=True)

    import importlib.util as iu
    spec = iu.spec_from_file_location('a2', os.path.join(HERE, '09_a2_rollback.py'))
    m = iu.module_from_spec(spec)
    spec.loader.exec_module(m)
    axes, U, ids, types, hvec = m.load_inputs()
    G, idx, MUL = m.build_group()
    hydx = [idx[m.qkey(h)] for h in hvec]

    claim('C1', 'group rebuilt: |2I| = 120 (closed under multiplication)',
          len(G) == 120 and all(MUL[a][b] < 120 for a in range(120) for b in range(120)),
          '|2I| = %d' % len(G))

    frozen = json.load(io.open(os.path.join(DATA, '04_b2_settings.json'), encoding='utf-8'))
    same = all(tuple((F(c[0]), F(c[1])) for c in frozen['axes'][k]['vec']) == U[k] and
               frozen['axes'][k]['id'] == ids[k] and frozen['axes'][k]['type'] == types[k]
               for k in range(62))
    claim('C2', '62 frozen lattice axes reproduced verbatim (12 V / 20 F / 30 E)',
          same and len(set(types)) == 3, 'types = %s' % sorted(set(types)))

    claim('C3', 'A2 h-table bijective (62/62)', len(set(hydx)) == 62,
          'distinct = %d' % len(set(hydx)))

    a2 = json.load(io.open(os.path.join(DATA, '09_a2_results.json'), encoding='utf-8'))
    b5 = json.load(io.open(os.path.join(DATA, '12_b5_results.json'), encoding='utf-8'))
    ch = a2['chsh']
    base_ok = (len(a2['claims']) == 20 and all(c['ok'] for c in a2['claims'])
               and ch['E1_all4'] == '2' and ch['E2_all4'] == '3'
               and len(b5['claims']) == 8 and all(c['ok'] for c in b5['claims'])
               and b5['k_feasible_pairs'] == 15 and b5['reads_used_by_feasible_prefix'] == 43)
    claim('C4', 'frozen upstream: A2 20/20 (all4 = 2 / 3) and B5 8/8 (15 pairs / 43 reads)',
          base_ok, 'A2 all4 = %s/%s ; B5 pairs/reads = %s/%s' %
          (ch['E1_all4'], ch['E2_all4'], b5['k_feasible_pairs'], b5['reads_used_by_feasible_prefix']))

    BUD, EMIN, COST = F(123, 2), F(123, 176), F(123, 88)
    reads44 = BUD / COST
    claim('C5', 'budget identities I1-I4 exact: reads = 44 = N_d ; cost = 123/88 = 2 x E_min ; '
                '44 reads consume the whole budget ; tau_deco = 2 passes',
          reads44 == 44 and COST == 2 * EMIN and 44 * COST == BUD and F(88) / reads44 == 2,
          'reads = %s ; cost = %s ; 44*cost = %s' % (reads44, COST, 44 * COST))

    # C6: the five order rules are bijections on the 3844 pairs
    bij = {}
    for oid in ORDER_IDS:
        keys = [order_key(oid, a, b) for a in range(62) for b in range(62)]
        bij[oid] = (len(set(keys)) == 3844)
    claim('C6', 'all five pre-registered order rules are bijections on 3844 pairs '
                '(every prefix well-defined)', all(bij.values()), json.dumps(bij))

    # C7: fairness criterion is coverage-based and identical in contract and impl
    doc = io.open(os.path.join(ROOT, 'docs', '10_b3r2_contract.md'), encoding='utf-8').read()
    crit = ['cov_a', 'cov_b', 'constructible', '可構成']
    doc_ids = [oid for oid in ORDER_IDS if ('`%s`' % oid) in doc]
    claim('C7', 'contract states the coverage criterion (cov_a / cov_b >= 2) and lists all five rule IDs',
          all(c in doc for c in crit) and len(doc_ids) == 5, 'doc rule IDs = %s' % doc_ids)

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
        claim('C8', 'impl AST gate: no trig / no float literal / no numpy-scipy-math / no random',
              not bad, bad[0] if bad else 'clean')
        impl_ids = [oid for oid in ORDER_IDS if ("'%s'" % oid) in src]
        claim('C9', 'order-rule parity: the impl implements exactly the five pre-registered IDs',
              len(impl_ids) == 5 and ('order_key' in src or 'ORDER_KEY' in src),
              'impl IDs = %s' % impl_ids)
        has_full = ('FULL' in src.upper() or 'full_enum' in src) and 'NOT CONSTRUCTIBLE' in src.upper()
        claim('C10', 'impl declares full enumeration AND separates "not constructible" from "|S| = 0"',
              has_full, 'full=%s' % has_full)
        funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'read']
        claim('C11', 'machine semantics are imported, not re-implemented (no local read(G, ctx) fork)',
              not funcs, 'local read() defs = %s' % [f.name for f in funcs])
    else:
        for t, n in (('C8', 'impl AST gate'), ('C9', 'order-rule parity'),
                     ('C10', 'full-enumeration + constructibility declaration'),
                     ('C11', 'machine semantics imported')):
            claim(t, n, False, 'no implementation supplied yet')

    # C12: provenance (the round quotes only frozen upstream)
    prov = [('open_problems_fresh/o222_qm_evaluation_semantics/docs/07_b5_contract.md', ['123/88', 'per-read']),
            ('open_problems_fresh/o222_qm_evaluation_semantics/docs/06_a2_results.md', ['all4', '3']),
            ('open_problems_fresh/o222_qm_evaluation_semantics/docs/09_closeout_audit.md', ['12,517,800'])]
    hit = []
    for rel, needles in prov:
        p = os.path.join(REPO, rel)
        blob = io.open(p, encoding='utf-8', errors='ignore').read() if os.path.exists(p) else ''
        hit.append(all(n in blob for n in needles))
    claim('C12', 'provenance: B5 contract carries the read cost ; A2 results carry all4 ; closeout carries 12,517,800',
          all(hit), 'per-file = %s' % hit)

    # C13: register has this round registered BEFORE numbers
    reg = io.open(os.path.join(REPO, 'problem_register', 'register.jsonl'), encoding='utf-8').read()
    claim('C13', 'register: O222/B3R2 registered (pre-number registration discipline)',
          'O222/B3R2' in reg, 'found=%s' % ('O222/B3R2' in reg))

    if impl_path and os.path.exists(impl_path):
        rec = {'rules_version': 'b3r2-contract-v1',
               'doc': {'path': 'docs/10_b3r2_contract.md',
                       'sha256': sha(os.path.join(ROOT, 'docs', '10_b3r2_contract.md'))},
               'enforcer_sha256': sha(os.path.abspath(__file__)),
               'impl': {'path': impl, 'sha256': sha(impl_path)},
               'frozen_at': __import__('time').strftime('%Y-%m-%dT%H:%M:%S%z'),
               'inputs': {'budget': str(BUD), 'E_min': str(EMIN), 'per_read_cost': str(COST),
                          'reads_per_pass': str(reads44), 'tau_deco_passes': '2',
                          'order_ids': list(ORDER_IDS),
                          'tables': {'E1': 'C1_num/120', 'E2': 'C2 (den 3, memo-effective)'},
                          'machine': 'scripts/09_a2_rollback.py via scripts/12_b5_budget.run_pair'},
               'gate': 'OPEN'}
        with io.open(os.path.join(DATA, '14_b3r2_freeze.json'), 'w', encoding='utf-8') as fh:
            json.dump(rec, fh, indent=1, ensure_ascii=False)
        print('\nfrozen impl %s = %s' % (impl, sha(impl_path)))
        print('GATE = OPEN   (data/14_b3r2_freeze.json)')
    else:
        print('\nGATE = CLOSED (no implementation; rerun with --freeze-impl scripts/15_b3r2_orderfair.py)')

    with io.open(os.path.join(DATA, '14_b3r2_contract_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules_version': 'b3r2-contract-v1', 'claims': CLAIMS}, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)' % (npass, len(CLAIMS), len(CLAIMS) - npass))
    print('=' * 112)
    return 1 if impl is None else (0 if npass == len(CLAIMS) else 1)


if __name__ == '__main__':
    sys.exit(main())
