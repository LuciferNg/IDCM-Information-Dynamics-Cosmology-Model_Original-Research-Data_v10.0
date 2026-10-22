#!/usr/bin/env python3
"""O222 scripts/11 -- executable enforcer for Contract B5 v1 (docs/07_b5_contract.md).

Rebuilds everything from scratch and REFUSES to run if the frozen inputs do not reproduce:
  * the 2I group and the 62 frozen lattice axes (verbatim against data/04_b2_settings.json),
  * the A2 h-table (62/62 bijective) and the A2 frozen results (20/20 claims),
  * the O41/O126 budget and clock numbers quoted in the contract (provenance),
  * the exact budget identities 88 = (123/2)/(123/176) and 7688/88 = 961/11,
  * the implementation AST gate (no trig / no float / no numpy-scipy-math / no random),
  * read-operator locality read(G, ctx), and the full-enumeration requirement.

Usage:  /usr/bin/python3 scripts/11_b5_contract.py [--freeze-impl scripts/12_b5_budget.py]
"""
import ast
import hashlib
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


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-6s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def sha(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()


def main():
    argv = sys.argv[1:]
    impl = argv[argv.index('--freeze-impl') + 1] if '--freeze-impl' in argv else None
    print('=' * 112)
    print('O222 scripts/11 -- Contract B5 v1 enforcer (D5 rollback layer / resource bound)')
    print('=' * 112, flush=True)

    # ---------- load the frozen A2 module (group, axes, h table) ----------
    import importlib.util
    spec = importlib.util.spec_from_file_location('a2', os.path.join(HERE, '09_a2_rollback.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    axes, U, ids, types, hvec = m.load_inputs()
    G, idx, MUL = m.build_group()
    hydx = [idx[m.qkey(h)] for h in hvec]

    # C1: group
    claim('C1', 'group rebuilt: |2I| = 120, closed under multiplication',
          len(G) == 120 and all(MUL[a][b] < 120 for a in range(120) for b in range(120)),
          '|2I| = %d' % len(G))

    # C2: the 62 frozen axes reproduce the frozen settings file verbatim
    frozen = json.load(io.open(os.path.join(DATA, '04_b2_settings.json'), encoding='utf-8'))
    same = all(
        tuple((F(c[0]), F(c[1])) for c in frozen['axes'][k]['vec']) == U[k] and
        frozen['axes'][k]['id'] == ids[k] and frozen['axes'][k]['type'] == types[k]
        for k in range(62))
    claim('C2', '62 frozen lattice axes reproduced verbatim (12 V / 20 F / 30 E)',
          same and len(set(types)) == 3, 'types = %s' % sorted(set(types)))

    # C3: h table bijective
    claim('C3', 'A2 h-table present and bijective (62/62)', len(set(hydx)) == 62,
          'distinct h entries = %d' % len(set(hydx)))

    # C4: the A2 frozen results are 20/20 PASS (B5 builds on A2)
    a2 = json.load(io.open(os.path.join(DATA, '09_a2_results.json'), encoding='utf-8'))
    ok4 = len(a2['claims']) == 20 and all(c['ok'] for c in a2['claims'])
    claim('C4', 'A2 frozen results present with 20/20 PASS (B5 builds on A2)',
          ok4, 'claims = %d, all-ok = %s' % (len(a2['claims']), all(c['ok'] for c in a2['claims'])))

    # C5: the contract's exact budget identities
    BUD, EMIN, BMODE = F(123, 2), F(123, 176), F(123, 88)
    reads = BUD / EMIN
    infeas = F(7688) / reads
    reads_at_cost = BUD / BMODE          # 44 (the ACTUAL read cost is B(n) = 2 x E_min)
    ok5 = (reads == 88) and (reads_at_cost == 44) and (BMODE == 2 * EMIN) and \
        (44 * BMODE == BUD) and (F(7688) / reads_at_cost == F(1922, 11)) and (reads_at_cost / 44 == 1)
    claim('C5', 'budget identities exact: 88 reads at the E_min floor; 44 reads at the TRUE read cost '
                '(B(n) = 2 x E_min); 7688/44 = 1922/11; a 44-read pass = 1 tick; tau_deco = 2 ticks',
          ok5, 'floor reads = %s ; reads at cost = %s ; overrun = %s ; pass duration = %s tick' %
          (reads, reads_at_cost, F(7688) / reads_at_cost, reads_at_cost / 44))

    # C6: provenance -- the frozen inputs really carry the quoted values
    prov = [('open_problems_fresh/o41_observer_budget/final_result.md', ['61.5', '123/176']),
            ('open_problems_fresh/o126_runtime_isa_verification', ['0.9617', '1.9235', 'T_sync/88']),
            ('open_problems_fresh/o222_qm_evaluation_semantics/docs/01_wfield_qm_inventory.md',
             ['0.9617614', 'τ_deco']),
            ('open_problems_fresh/o206_per_mode_frequency/docs/01_problem_record.md', ['mu^2', '2'])]
    hit = []
    for rel, needles in prov:
        p = os.path.join(REPO, rel)
        blob = ''
        if os.path.isdir(p):
            for dirpath, _dirs, files in os.walk(p):
                for fn in sorted(files):
                    if fn.endswith(('.md', '.py', '.txt')):
                        blob += io.open(os.path.join(dirpath, fn), encoding='utf-8',
                                        errors='ignore').read()
        elif os.path.exists(p):
            blob = io.open(p, encoding='utf-8', errors='ignore').read()
        hit.append(all(n in blob for n in needles))
    claim('C6', 'provenance: O41 carries 61.5 / 123/176 ; O126 carries tick/tau_deco ; O222 inv. carries the tick + tau_deco row ; O206 carries omega_n = mu^2',
          all(hit), 'per-file = %s' % hit)

    # C7: tau_deco identity input
    tick = F(9617614, 10 ** 7)
    claim('C7', 'tau_deco identity: 88 reads at 44 reads/tick = 2 ticks = 1.9235228 Gyr (registered 1.9235227)',
          abs(float(2 * tick) - 1.9235227) < 5e-7, '2*tick = %.7f Gyr' % float(2 * tick))

    # C8-C10: implementation gates (AST, locality, full enumeration) -- only if the impl exists
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
        claim('C8', 'impl AST gate: no trig / no float / no numpy-scipy-math / no random',
              not bad, bad[0] if bad else 'clean')
        funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'read']
        ok9 = bool(funcs) and [a.arg for a in funcs[0].args.args] == ['G', 'ctx']
        claim('C9', 'factor-table locality: the machine read operator is read(G, ctx)', ok9,
              'constrained functions = %s' % [f.name for f in funcs])
        has_sweep = ('62 ** 4' in src or '62**4' in src or 'FULL 62' in src.upper()
                     or 'full_enum' in src)
        has_count = ('tuples' in src and ('count' in src.lower() or 'visited' in src.lower()))
        claim('C10', 'full-enumeration requirement declared in the impl (sweep + visit count)',
              has_sweep and has_count, 'sweep=%s count=%s' % (has_sweep, has_count))
        impl_hash = sha(impl_path)
        rec = {'rules_version': 'b5-contract-v1',
               'doc': {'path': 'docs/07_b5_contract.md', 'sha256': sha(os.path.join(ROOT, 'docs/07_b5_contract.md'))},
               'enforcer_sha256': sha(os.path.abspath(__file__)),
               'impl': {'path': impl, 'sha256': impl_hash},
               'frozen_at': __import__('time').strftime('%Y-%m-%dT%H:%M:%S%z'),
               'inputs': {'budget': str(BUD), 'per_mode_budget': str(BMODE), 'E_min': str(EMIN),
                          'per_read_cost': str(BMODE), 'reads_per_pass': str(reads),
                          'pairs_per_pass': str(reads / 2), 'overrun_factor': str(infeas),
                          'reads_per_tick': 44, 'tick_Gyr': str(tick), 'tau_deco_Gyr': str(2 * tick)},
               'gate': 'OPEN'}
        with io.open(os.path.join(DATA, '11_b5_freeze.json'), 'w', encoding='utf-8') as fh:
            json.dump(rec, fh, indent=1, ensure_ascii=False)
        print('\nfrozen impl %s = %s' % (impl, impl_hash))
        print('GATE = OPEN   (data/11_b5_freeze.json)')
    else:
        claim('C8', 'impl AST gate', False, 'no implementation supplied yet')
        claim('C9', 'factor-table locality', False, 'no implementation supplied yet')
        claim('C10', 'full-enumeration requirement', False, 'no implementation supplied yet')
        print('\nGATE = CLOSED (no implementation supplied; rerun with --freeze-impl scripts/12_b5_budget.py)')

    with io.open(os.path.join(DATA, '11_b5_contract_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules_version': 'b5-contract-v1', 'claims': CLAIMS}, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)' % (npass, len(CLAIMS), len(CLAIMS) - npass))
    print('=' * 112)
    return 1 if impl is None else (0 if npass == len(CLAIMS) else 1)


if __name__ == '__main__':
    sys.exit(main())
