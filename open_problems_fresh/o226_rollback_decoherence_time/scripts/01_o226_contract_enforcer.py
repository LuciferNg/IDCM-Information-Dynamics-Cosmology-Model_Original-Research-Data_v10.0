#!/usr/bin/env python3
"""O226 scripts/01 -- contract enforcer (GATE) for `o226-r1-contract-v1`.

Checks in order:
  C1  the frozen contract file exists and its sha256 equals the value pinned here
  C2  every required section / pre-registration tag is literally present in the contract
  C3  every declared frozen input (F1-F7) exists on disk (read-only pins)
  C4  AST scan of the analysis engines (scripts 02-06): the machine path may not use
      float/math/random/numpy/statistics -- exact arithmetic only (contract I6)
  C5  no forbidden re-derivation of upstream conclusions (only imports of the frozen JSON data)
Exit code 0 only when every check passes; prints RESULT: n/m PASS and GATE = OPEN/CLOSED.
"""
import ast
import hashlib
import io
import json
import time
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
O222 = os.path.join(os.path.dirname(ROOT), 'o222_qm_evaluation_semantics')
CONTRACT = os.path.join(ROOT, 'docs', '01_o226_contract.md')
CONTRACT_SHA = 'f8d7d8fe6790cfdb1f905271a1e4e2e2cea2732311c5d3b6cc7d1f31a28b476d'
RULES = 'o226-r1-contract-v1'
CLAIMS = []

FORBIDDEN_IMPORTS = ('math', 'random', 'numpy', 'statistics', 'cmath', 'decimal')
FORBIDDEN_NAMES = ('pi', 'log', 'sqrt', 'exp', 'sin', 'cos')

REQUIRED = [
    '§0 本輪判決對象', 'J1', 'J2', 'J3', 'J4',
    'Pr-1.1', 'Pr-1.2', 'Pr-1.3', 'Pr-1.4', 'Pr-1.5', 'Pr-1.6',
    'Pr-2.1', 'Pr-2.2', 'Pr-2.3', 'Pr-2.4', 'Pr-2.5', 'Pr-2.6',
    'Pr-3.1', 'Pr-3.2', 'Pr-3.3',
    'Pr-4.1', 'Pr-4.2', 'Pr-4.3', 'Pr-4.4', 'Pr-4.5',
    '四道硬測試', '樣本外盲測', '唔准事後改判準', '層分離聲明',
    'B′ = 123', 'B″ = 123/4', 'c‴ = 3θ',
]
PINS = [
    (os.path.join(O222, 'data', '04_b2_settings.json'), 'F1 62 axes'),
    (os.path.join(O222, 'data', '08_a2_h_table.json'), 'F2 h table'),
    (os.path.join(O222, 'data', '09_a2_correlation.json'), 'F3 frozen C1/C2'),
    (os.path.join(O222, 'docs', '42_r28_residuals.md'), 'F4 pass accounts'),
    (os.path.join(O222, 'docs', '43_r29_rt1_boundary.md'), 'F5 RT1 canonical'),
    (os.path.join(O222, 'docs', '08_b5_results.md'), 'F6 resource identities'),
    (os.path.join(O222, 'scripts', '12_b5_budget.py'), 'F7 tick constant'),
]


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name,
                              ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


def scan(path):
    """AST scan: returns (imports, float-ish literals, forbidden names used)."""
    src = io.open(path, encoding='utf-8').read()
    tree = ast.parse(src)
    bad_imports, bad_names, float_lits = [], [], 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for al in node.names:
                if al.name.split('.')[0] in FORBIDDEN_IMPORTS:
                    bad_imports.append(al.name)
        elif isinstance(node, ast.ImportFrom):
            if (node.module or '').split('.')[0] in FORBIDDEN_IMPORTS:
                bad_imports.append(node.module)
        elif isinstance(node, ast.Name):
            if node.id in FORBIDDEN_NAMES:
                bad_names.append(node.id)
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, float):
                float_lits += 1
    return bad_imports, bad_names, float_lits


def main():
    print('=' * 104)
    print('O226 scripts/01 -- contract enforcer (rules: %s)' % RULES)
    print('=' * 104, flush=True)

    raw = io.open(CONTRACT, 'rb').read()
    sha = hashlib.sha256(raw).hexdigest()
    text = raw.decode('utf-8')
    claim('C1', 'frozen contract sha256 matches the pinned value', sha == CONTRACT_SHA,
          'sha256 = %s' % sha)

    missing = [t for t in REQUIRED if t not in text]
    claim('C2', 'all required sections and pre-registration tags literally present',
          not missing, 'required = %d ; missing = %s' % (len(REQUIRED), missing))

    absent = [lab for (p, lab) in PINS if not os.path.isfile(p)]
    claim('C3', 'every declared frozen input pin exists on disk (read-only)',
          not absent, 'pins = %d ; absent = %s' % (len(PINS), absent))

    rows = []
    ok_ast = True
    for n in range(2, 7):
        cands = [f for f in sorted(os.listdir(HERE)) if f.startswith('%02d_' % n) and f.endswith('.py')]
        if not cands:
            rows.append((n, None, 'NOT FOUND'))
            ok_ast = False
            continue
        p = os.path.join(HERE, cands[0])
        bi, bn, fl = scan(p)
        # scripts 03-06 may print with float() but the machine path (02) may not contain float literals
        bad = bool(bi) or bool(bn) or (n == 2 and fl > 0)
        ok_ast = ok_ast and not bad
        rows.append((n, cands[0], 'imports=%s names=%s float_lits=%d' % (bi, bn, fl)))
    claim('C4', 'AST scan: no float/math/random/numpy in the engines (machine = 0 float literals)',
          ok_ast, ' | '.join('%02d:%s' % (r[0], r[2]) for r in rows))

    # C5: engines may read upstream JSON data but must never import / exec upstream code
    bad_import = []
    for n in range(2, 7):
        cands = [f for f in sorted(os.listdir(HERE)) if f.startswith('%02d_' % n) and f.endswith('.py')]
        if not cands:
            continue
        path = os.path.join(HERE, cands[0])
        src = io.open(path, encoding='utf-8').read()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for al in node.names:
                    if al.name.split('.')[0] in ('subprocess',):
                        bad_import.append('%02d:import %s' % (n, al.name))
            if isinstance(node, ast.Call):
                fn = node.func
                nm = getattr(fn, 'attr', None)
                if nm == 'spec_from_file_location':
                    tgt = node.args[1] if len(node.args) > 1 else None
                    allowed = (isinstance(tgt, ast.Call) and isinstance(tgt.func, ast.Attribute) and
                               tgt.func.attr == 'join' and len(tgt.args) > 1 and
                               isinstance(tgt.args[1], ast.Constant) and
                               tgt.args[1].value == '02_o226_ledger_machine.py')
                    if not allowed:
                        bad_import.append('%02d:spec_from_file_location with a non-local target' % n)
                if nm == 'insert' and isinstance(fn, ast.Attribute) and getattr(fn.value, 'id', '') == 'path':
                    bad_import.append('%02d:sys.path mutation' % n)
        for ln in src.split('\n'):
            low = ln.lower()
            if 'o222' in low and 'os.path.join' not in low and 'O222' not in ln:
                bad_import.append('%02d:%s' % (n, ln.strip()[:70]))
    claim('C5', 'engines 02-06 never import/exec upstream code: the only permitted dynamic load is the '
                'local frozen machine scripts/02_o226_ledger_machine.py',
          not bad_import, 'offenders = %s' % bad_import)

    # ================= R2 additions (C6/C7/C4b/C5b): R1 checks C1-C5 are left untouched =========
    R2_SHA = '784e6a2beaaf1025ea9a04bc27c9d9a574d1343f49877db5f684c72a2e81258b'
    r2p = os.path.join(ROOT, 'docs', '06_o226_r2_contract.md')
    ok_r2 = os.path.isfile(r2p)
    h2 = hashlib.sha256(io.open(r2p, 'rb').read()).hexdigest() if ok_r2 else '-'
    claim('C6', 'R2 contract docs/06_o226_r2_contract.md is frozen: sha256 matches the pinned value',
          ok_r2 and h2 == R2_SHA, 'sha256 = %s' % h2)

    tags = ['Pr-5.1', 'Pr-5.2', 'Pr-5.3', 'Pr-5.4', 'Pr-5.5', 'Pr-5.6', 'Pr-5.7',
            'T1', 'T2', 'T3', 'T4', 'T5', 'I10', 'I11', 'I12', 'I13', 'I14', 'I15', 'I16']
    body = io.open(r2p, encoding='utf-8').read() if ok_r2 else ''
    miss2 = [t for t in tags if t not in body]
    claim('C7', 'R2 contract carries every pre-registration tag and judgement item literally',
          ok_r2 and not miss2, 'required = %d ; missing = %s' % (len(tags), miss2))

    rows2 = []
    ok2 = True
    for n in (8, 9):
        cands = [f for f in sorted(os.listdir(HERE)) if f.startswith('%02d_' % n) and f.endswith('.py')]
        if not cands:
            rows2.append((n, 'NOT FOUND'))
            ok2 = False
            continue
        bi, bn, fl = scan(os.path.join(HERE, cands[0]))
        bad = bool(bi) or bool(bn) or (n == 8 and fl > 0)
        ok2 = ok2 and not bad
        rows2.append((n, '%s imports=%s names=%s float_lits=%d' % (cands[0], bi, bn, fl)))
    claim('C4b', 'R2 AST scan (scripts 08-09 obey the same exact-arithmetic ban; the R2 machine = 0 '
                 'float literals) -- additive check, C4 untouched',
          ok2, ' | '.join('%02d:%s' % r for r in rows2))

    PERMIT = {8: {'02_o226_ledger_machine.py'}, 9: set()}
    bad2 = []
    for n in (8, 9):
        cands = [f for f in sorted(os.listdir(HERE)) if f.startswith('%02d_' % n) and f.endswith('.py')]
        if not cands:
            continue
        src = io.open(os.path.join(HERE, cands[0]), encoding='utf-8').read()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                for al in node.names:
                    if al.name.split('.')[0] == 'subprocess':
                        bad2.append('%02d:import %s' % (n, al.name))
            if isinstance(node, ast.Call):
                nm = getattr(node.func, 'attr', None)
                if nm == 'spec_from_file_location':
                    tgt = node.args[1] if len(node.args) > 1 else None
                    ok = (isinstance(tgt, ast.Call) and isinstance(tgt.func, ast.Attribute) and
                          tgt.func.attr == 'join' and len(tgt.args) > 1 and
                          isinstance(tgt.args[1], ast.Constant) and tgt.args[1].value in PERMIT[n])
                    if not ok:
                        bad2.append('%02d:non-permitted dynamic load' % n)
                if nm == 'insert' and isinstance(node.func, ast.Attribute) and getattr(node.func.value, 'id', '') == 'path':
                    bad2.append('%02d:sys.path mutation' % n)
        for ln in src.split('\n'):
            low = ln.lower()
            if 'o222' in low and 'os.path.join' not in low and 'O222' not in ln:
                bad2.append('%02d:%s' % (n, ln.strip()[:70]))
    claim('C5b', 'R2 engines: 08 may load only the local R1 machine, 09 must be self-contained '
                 '(no dynamic load at all); no upstream code, no sys.path mutation',
          not bad2, 'offenders = %s' % bad2)

    # ================= R3 additions (C8/C9/C4c/C5c): R1/R2 checks left untouched ================
    R3_SHA = '77cfc7754e2c0ccce47d961b5c30538ee4cc48f5685c39b8d418c5a503308828'
    r3p = os.path.join(ROOT, 'docs', '09_o226_r3_contract.md')
    ok_r3 = os.path.isfile(r3p)
    h3 = hashlib.sha256(io.open(r3p, 'rb').read()).hexdigest() if ok_r3 else '-'
    claim('C8', 'R3 contract docs/09_o226_r3_contract.md is frozen: sha256 matches the pinned value',
          ok_r3 and h3 == R3_SHA, 'sha256 = %s' % h3)
    tags3 = ['Pr-6.1', 'Pr-6.2', 'Pr-6.3', 'Pr-6.4', 'Pr-6.5', 'Pr-6.6', 'Pr-6.7', 'Pr-6.8',
             'T6', 'T7', 'T8', 'T9', 'I17', 'I18', 'I19', 'I20', 'I21', 'I22', 'H1', 'H2', 'H3', 'H4']
    body3 = io.open(r3p, encoding='utf-8').read() if ok_r3 else ''
    miss3 = [t for t in tags3 if t not in body3]
    claim('C9', 'R3 contract carries every pre-registration tag, judgement item and hypothesis tag '
                'literally', ok_r3 and not miss3, 'required = %d ; missing = %s' % (len(tags3), miss3))
    rows3 = []
    ok3 = True
    for n in (10, 11):
        cands = [f for f in sorted(os.listdir(HERE)) if f.startswith('%02d_' % n) and f.endswith('.py')]
        if not cands:
            rows3.append((n, 'NOT FOUND'))
            ok3 = False
            continue
        bi, bn, fl = scan(os.path.join(HERE, cands[0]))
        bad = bool(bi) or bool(bn) or (n == 10 and fl > 0)
        ok3 = ok3 and not bad
        rows3.append((n, '%s imports=%s names=%s float_lits=%d' % (cands[0], bi, bn, fl)))
    claim('C4c', 'R3 AST scan (scripts 10-11 obey the same exact-arithmetic ban; the R3 machine = 0 '
                 'float literals) -- additive check',
          ok3, ' | '.join('%02d:%s' % r for r in rows3))
    PERMIT3 = {10: {'02_o226_ledger_machine.py'}, 11: set()}
    bad3 = []
    for n in (10, 11):
        cands = [f for f in sorted(os.listdir(HERE)) if f.startswith('%02d_' % n) and f.endswith('.py')]
        if not cands:
            continue
        src = io.open(os.path.join(HERE, cands[0]), encoding='utf-8').read()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                for al in node.names:
                    if al.name.split('.')[0] == 'subprocess':
                        bad3.append('%02d:import %s' % (n, al.name))
            if isinstance(node, ast.Call):
                nm = getattr(node.func, 'attr', None)
                if nm == 'spec_from_file_location':
                    tgt = node.args[1] if len(node.args) > 1 else None
                    ok = (isinstance(tgt, ast.Call) and isinstance(tgt.func, ast.Attribute) and
                          tgt.func.attr == 'join' and len(tgt.args) > 1 and
                          isinstance(tgt.args[1], ast.Constant) and tgt.args[1].value in PERMIT3[n])
                    if not ok:
                        bad3.append('%02d:non-permitted dynamic load' % n)
                if nm == 'insert' and isinstance(node.func, ast.Attribute) and getattr(node.func.value, 'id', '') == 'path':
                    bad3.append('%02d:sys.path mutation' % n)
        for ln in src.split('\n'):
            low = ln.lower()
            if 'o222' in low and 'os.path.join' not in low and 'O222' not in ln:
                bad3.append('%02d:%s' % (n, ln.strip()[:70]))
    claim('C5c', 'R3 engines: 10 may load only the local R1 machine, 11 must be self-contained '
                 '(no dynamic load at all); no upstream code, no sys.path mutation',
          not bad3, 'offenders = %s' % bad3)

    # ================= R4 additions (C10/C11/C4d/C5d): R1/R2/R3 checks left untouched ============
    R4_SHA = '59b325b3dedfef85f60871bf633570fc707586130a565fbf52d068efbc7d2e5a'
    r4p = os.path.join(ROOT, 'docs', '12_o226_r4_contract.md')
    ok_r4 = os.path.isfile(r4p)
    h4 = hashlib.sha256(io.open(r4p, 'rb').read()).hexdigest() if ok_r4 else '-'
    claim('C10', 'R4 contract docs/12_o226_r4_contract.md is frozen: sha256 matches the pinned value',
          ok_r4 and h4 == R4_SHA, 'sha256 = %s' % h4)
    tags4 = ['Pr-7.1', 'Pr-7.2', 'Pr-7.3', 'Pr-7.4', 'Pr-7.5', 'Pr-7.6', 'Pr-7.7', 'Pr-7.8', 'Pr-7.9',
             'U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'I23', 'I24', 'I25', 'I26', 'I27', 'I28']
    body4 = io.open(r4p, encoding='utf-8').read() if ok_r4 else ''
    miss4 = [t for t in tags4 if t not in body4]
    claim('C11', 'R4 contract carries every pre-registration tag, judgement item and item tag literally',
          ok_r4 and not miss4, 'required = %d ; missing = %s' % (len(tags4), miss4))
    rows4 = []
    ok4 = True
    for n in (12, 13):
        cands = [f for f in sorted(os.listdir(HERE)) if f.startswith('%02d_' % n) and f.endswith('.py')]
        if not cands:
            rows4.append((n, 'NOT FOUND'))
            ok4 = False
            continue
        bi, bn, fl = scan(os.path.join(HERE, cands[0]))
        bad = bool(bi) or bool(bn) or (n == 12 and fl > 0)
        ok4 = ok4 and not bad
        rows4.append((n, '%s imports=%s names=%s float_lits=%d' % (cands[0], bi, bn, fl)))
    claim('C4d', 'R4 AST scan (scripts 12-13 obey the same exact-arithmetic ban; the R4 machine = 0 '
                 'float literals) -- additive check',
          ok4, ' | '.join('%02d:%s' % r for r in rows4))
    PERMIT4 = {12: {'02_o226_ledger_machine.py'}, 13: set()}
    bad4 = []
    for n in (12, 13):
        cands = [f for f in sorted(os.listdir(HERE)) if f.startswith('%02d_' % n) and f.endswith('.py')]
        if not cands:
            continue
        src = io.open(os.path.join(HERE, cands[0]), encoding='utf-8').read()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                for al in node.names:
                    if al.name.split('.')[0] == 'subprocess':
                        bad4.append('%02d:import %s' % (n, al.name))
            if isinstance(node, ast.Call):
                nm = getattr(node.func, 'attr', None)
                if nm == 'spec_from_file_location':
                    tgt = node.args[1] if len(node.args) > 1 else None
                    ok = (isinstance(tgt, ast.Call) and isinstance(tgt.func, ast.Attribute) and
                          tgt.func.attr == 'join' and len(tgt.args) > 1 and
                          isinstance(tgt.args[1], ast.Constant) and tgt.args[1].value in PERMIT4[n])
                    if not ok:
                        bad4.append('%02d:non-permitted dynamic load' % n)
                if nm == 'insert' and isinstance(node.func, ast.Attribute) and getattr(node.func.value, 'id', '') == 'path':
                    bad4.append('%02d:sys.path mutation' % n)
        for ln in src.split('\n'):
            low = ln.lower()
            if 'o222' in low and 'os.path.join' not in low and 'O222' not in ln:
                bad4.append('%02d:%s' % (n, ln.strip()[:70]))
    claim('C5d', 'R4 engines: 12 may load only the local R1 machine, 13 must be self-contained '
                 '(no dynamic load at all); no upstream code, no sys.path mutation',
          not bad4, 'offenders = %s' % bad4)

    # ================= R5 additions (C12/C13/C4e/C5e): earlier checks left untouched ===============
    R5_SHA = '84c9b2ec50d238beb70a6c7f2fbfaf044cd405978c5f0f2567ab179449f1f865'
    r5p = os.path.join(ROOT, 'docs', '15_o226_r5_contract.md')
    ok_r5 = os.path.isfile(r5p)
    h5 = hashlib.sha256(io.open(r5p, 'rb').read()).hexdigest() if ok_r5 else '-'
    claim('C12', 'R5 contract docs/15_o226_r5_contract.md is frozen: sha256 matches the pinned value',
          ok_r5 and h5 == R5_SHA, 'sha256 = %s' % h5)
    tags5 = ['Pv-1', 'Pv-2', 'Pv-3', 'Pv-4', 'Pv-5', 'Pv-6', 'Pv-7',
             'V1', 'V2', 'V3', 'V4', 'I29', 'I30', 'I31', 'I32', 'I33', 'I34']
    body5 = io.open(r5p, encoding='utf-8').read() if ok_r5 else ''
    miss5 = [t for t in tags5 if t not in body5]
    claim('C13', 'R5 contract carries every pre-registration tag, judgement item and item tag literally',
          ok_r5 and not miss5, 'required = %d ; missing = %s' % (len(tags5), miss5))
    rows5 = []
    ok5x = True
    for n in (14, 15):
        cands = [f for f in sorted(os.listdir(HERE)) if f.startswith('%02d_' % n) and f.endswith('.py')]
        if not cands:
            rows5.append((n, 'NOT FOUND'))
            ok5x = False
            continue
        bi, bn, fl = scan(os.path.join(HERE, cands[0]))
        bad = bool(bi) or bool(bn) or (n == 14 and fl > 0)
        ok5x = ok5x and not bad
        rows5.append((n, '%s imports=%s names=%s float_lits=%d' % (cands[0], bi, bn, fl)))
    claim('C4e', 'R5 AST scan (scripts 14-15 obey the same exact-arithmetic ban; the R5 machine = 0 '
                 'float literals) -- additive check',
          ok5x, ' | '.join('%02d:%s' % r for r in rows5))
    PERMIT5 = {14: {'02_o226_ledger_machine.py'}, 15: set()}
    bad5 = []
    for n in (14, 15):
        cands = [f for f in sorted(os.listdir(HERE)) if f.startswith('%02d_' % n) and f.endswith('.py')]
        if not cands:
            continue
        src = io.open(os.path.join(HERE, cands[0]), encoding='utf-8').read()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                for al in node.names:
                    if al.name.split('.')[0] == 'subprocess':
                        bad5.append('%02d:import %s' % (n, al.name))
            if isinstance(node, ast.Call):
                nm = getattr(node.func, 'attr', None)
                if nm == 'spec_from_file_location':
                    tgt = node.args[1] if len(node.args) > 1 else None
                    ok = (isinstance(tgt, ast.Call) and isinstance(tgt.func, ast.Attribute) and
                          tgt.func.attr == 'join' and len(tgt.args) > 1 and
                          isinstance(tgt.args[1], ast.Constant) and tgt.args[1].value in PERMIT5[n])
                    if not ok:
                        bad5.append('%02d:non-permitted dynamic load' % n)
                if nm == 'insert' and isinstance(node.func, ast.Attribute) and getattr(node.func.value, 'id', '') == 'path':
                    bad5.append('%02d:sys.path mutation' % n)
        for ln in src.split('\n'):
            low = ln.lower()
            if 'o222' in low and 'os.path.join' not in low and 'O222' not in ln:
                bad5.append('%02d:%s' % (n, ln.strip()[:70]))
    claim('C5e', 'R5 engines: 14 may load only the local R1 machine, 15 must be self-contained '
                 '(no dynamic load at all); no upstream code, no sys.path mutation',
          not bad5, 'offenders = %s' % bad5)

    # ================ chain completeness (closeout round; additive: C14/C15/C4f/C5f) ================
    # Standing requirement: scripts/ must carry the WHOLE derivation chain.  This block turns that into a
    # machine-checked property of the gate (scripts/16 re-checks it independently as its K section).
    CHAIN = [
        ('R1', 'docs/01_o226_contract.md', 'docs/02_round1_verdicts.md', 'data/02_ledger_machine.json',
         ['01_o226_contract_enforcer.py', '02_o226_ledger_machine.py', '03_o226_time_mapping.py',
          '04_o226_budget_theorem.py', '05_o226_multi_round.py', '06_o226_staleness.py',
          '07_o226_independent_audit.py', '_probe_smoke.py', '_probe_j4.py']),
        ('R2', 'docs/06_o226_r2_contract.md', 'docs/07_o226_r2_verdicts.md', 'data/07_class_machine.json',
         ['08_o226_class_machine.py', '09_o226_class_audit.py']),
        ('R3', 'docs/09_o226_r3_contract.md', 'docs/11_o226_r3_verdicts.md', 'data/08_value_closed_form.json',
         ['10_o226_value_closed_form.py', '11_o226_value_audit.py']),
        ('R4', 'docs/12_o226_r4_contract.md', 'docs/14_o226_r4_verdicts.md', 'data/09_w_closed_form.json',
         ['12_o226_w_closed_form.py', '13_o226_w_audit.py']),
        ('R5', 'docs/15_o226_r5_contract.md', 'docs/17_o226_r5_verdicts.md', 'data/10_orbit_factorisation.json',
         ['14_o226_orbit_factorisation.py', '15_o226_orbit_audit.py']),
        ('CL', 'docs/18_o226_closeout_audit.md', 'docs/19_o226_uncleared_and_handoff.md',
         'data/11_closeout_audit.json', ['16_o226_closeout_audit.py', '17_o226_closeout_verify.py']),
    ]
    miss = []
    for rnd, cdoc, vdoc, dfile, scripts in CHAIN:
        for rel in (cdoc, vdoc, dfile) + tuple('scripts/' + s for s in scripts):
            if not os.path.isfile(os.path.join(ROOT, rel)):
                miss.append('%s:%s' % (rnd, rel))
    disk = sorted(f for f in os.listdir(HERE) if f.endswith('.py'))
    listed = sorted(s for _, _, _, _, ss in CHAIN for s in ss)
    claim('C14', 'chain completeness: every chain round carries its contract doc, its verdict/handoff doc, '
                 'its data file and all of its scripts; and every .py in scripts/ is listed by the chain '
                 'record (nothing missing, no unrecorded script)',
          not miss and disk == listed,
          'missing = %s ; on disk but unlisted = %s ; listed but absent = %s'
          % (miss, sorted(set(disk) - set(listed)), sorted(set(listed) - set(disk))))
    JRN = ['01_o226_contract_enforcer.out', '02_o226_ledger_machine.out', '03_o226_time_mapping.out',
           '04_o226_budget_theorem.out', '05_o226_multi_round.out', '06_staleness.out',   # recorded name
           '07_o226_independent_audit.out', '08_o226_class_machine.out', '09_o226_class_audit.out',
           '10_o226_value_closed_form.out', '11_o226_value_audit.out', '12_o226_w_closed_form.out',
           '13_o226_w_audit.out', '14_o226_orbit_factorisation.out', '15_o226_orbit_audit.out',
           '16_o226_closeout_audit.out', '17_o226_closeout_verify.out']
    badlog, nodata = [], []
    for lg in JRN:
        lp = os.path.join(ROOT, 'logs', lg)
        if not os.path.isfile(lp):
            badlog.append(lg + '(absent)')
            continue
        # A journal touched within the declared 300 s window is being written by an ancestor pass (e.g. this
        # gate run by scripts/16, whose journal the shell is appending to) -- such a journal is verified by
        # scripts/16 (R1/R3) and scripts/17 (M1) instead of by content here.
        if 'RESULT:' not in io.open(lp, encoding='utf-8', errors='replace').read():
            if time.time() - os.path.getmtime(lp) >= 300:
                badlog.append(lg + '(no RESULT)')
    srcs = {f: io.open(os.path.join(HERE, f), encoding='utf-8').read() for f in disk}
    for fn in sorted(os.listdir(os.path.join(ROOT, 'data'))):
        if fn.endswith('.json') and not any(fn in t for t in srcs.values()):
            nodata.append(fn)
    claim('C15', 'chain coverage: every chain script has its canonical journal (logs/<...>.out carrying a '
                 'RESULT line; the _probe_* diagnostics have none by design) and every data/*.json has at '
                 'least one producing script', not badlog and not nodata,
          'journals missing/empty = %s ; data with no producer = %s' % (badlog, nodata))
    XF, frows = set(), []
    for fn in ('16_o226_closeout_audit.py', '17_o226_closeout_verify.py'):
        p = os.path.join(HERE, fn)
        bi, bn, fl = scan(p)
        tree2 = ast.parse(io.open(p, encoding='utf-8').read())
        esc = [s.value for s in ast.walk(tree2) if isinstance(s, ast.Constant)
               and isinstance(s.value, str) and '../' in s.value]
        subs = [a.name for n in ast.walk(tree2) if isinstance(n, ast.Import) for a in n.names
                if a.name.split('.')[0] == 'subprocess']
        okrow = not bi and not bn and fl == 0 and not esc and bool(subs) == fn.startswith('16')
        if not okrow:
            XF.add(fn)
        frows.append('%s imports=%s names=%s float_lits=%d "../"=%d subprocess=%s'
                     % (fn, bi, bn, fl, len(esc), bool(subs)))
    claim('C4f', 'closeout AST scan: 16 and 17 obey the exact-arithmetic ban (0 float literals, no banned '
                 'imports/names) and never address a parent-relative path; only 16 (the chain re-runner) may '
                 'import subprocess, 17 stays read-only -- additive check', not XF, ' | '.join(frows))
    PERMITF = {16: {'02_o226_ledger_machine.py'}, 17: set()}
    badf = []
    for n in (16, 17):
        cands = [f for f in disk if f.startswith('%02d_' % n)]
        src = io.open(os.path.join(HERE, cands[0]), encoding='utf-8').read()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Call):
                nm = getattr(node.func, 'attr', None)
                if nm == 'spec_from_file_location':
                    tgt = node.args[1] if len(node.args) > 1 else None
                    ok = (isinstance(tgt, ast.Call) and isinstance(tgt.func, ast.Attribute)
                          and tgt.func.attr == 'join' and len(tgt.args) > 1
                          and isinstance(tgt.args[1], ast.Constant) and tgt.args[1].value in PERMITF[n])
                    if not ok:
                        badf.append('%02d:non-permitted dynamic load' % n)
                if nm == 'insert' and getattr(getattr(node.func, 'value', None), 'id', '') == 'path':
                    badf.append('%02d:sys.path mutation' % n)
    claim('C5f', 'closeout load restrictions: 16/17 perform no non-permitted dynamic load and no sys.path '
                 'mutation (they re-read frozen data only) -- additive check', not badf,
          'offenders = %s' % badf)

    gate = all(c['ok'] for c in CLAIMS)
    out = {'rules_version': RULES, 'contract_sha256': sha, 'claims': CLAIMS, 'gate': 'OPEN' if gate else 'CLOSED'}
    with io.open(os.path.join(ROOT, 'data', '01_contract_gate.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 104)
    print('RESULT: %d/%d PASS   GATE = %s' % (npass, len(CLAIMS), out['gate']))
    print('=' * 104)
    return 0 if gate else 1


if __name__ == '__main__':
    sys.exit(main())
