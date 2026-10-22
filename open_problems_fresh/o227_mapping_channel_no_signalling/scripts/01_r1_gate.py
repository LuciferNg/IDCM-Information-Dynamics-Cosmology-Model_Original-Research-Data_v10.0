#!/usr/bin/env python3
"""O227 scripts/01 -- R1 contract enforcer (rules `o227-r1-contract-v1`).

Gate clauses (all must PASS before the machine may run):
  C1  frozen-input hash pins (every object listed in docs/01 section 1)
  C2  predicate completeness: the contract carries exactly the 26 pre-registered tags
  C2b provenance objects reachable (O210) and carrying the composition law text, no dimensions
  C3  AST block on the machine: banned imports, math.<attr> restricted to log2, no float
      literals, no eval/exec, no write-open on any path mentioning another O directory,
      and `sys.dont_write_bytecode = True` present
  C4  contract tag set == machine tag set (doc <-> impl alignment)
  C5  the read semantics must be IMPORTED, never re-implemented in the machine
      (no local build_group / qmul / rot_ref / krow / run_pair / load_machine)
  C6  static rule check on the FROZEN sources: top-only read, append-only push,
      pop used only for the rollback, no in-place ledger rewrite
  C7  register precondition: O227/R1 + 26 sub-pids present with a pre-run note
  C8  the amendment table carries only pre-freeze, pre-run rows (no post-freeze amendment)

Usage
  /usr/bin/python3 scripts/01_r1_gate.py
  /usr/bin/python3 scripts/01_r1_gate.py --freeze-impl scripts/02_r1_machine.py
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
O2 = os.path.join(REPO, 'open_problems_fresh', 'o222_qm_evaluation_semantics')
O210 = os.path.join(REPO, 'open_problems_fresh', 'o210_causal_tensor_algebra')
CONTRACT = os.path.join(ROOT, 'docs', '01_r1_contract.md')
DATA = os.path.join(ROOT, 'data')
RULES = 'o227-r1-contract-v1'
CLAIMS = []

TAGS = ['R0', 'P1a', 'P1b', 'P1c', 'P2a', 'P2b', 'P2c', 'P2d', 'P3a', 'P3b', 'P3c', 'P4a', 'P4b',
        'P4c', 'B4a', 'B4b', 'B4c', 'B4d', 'B4e', 'B5a', 'B5b', 'B5c', 'S4a', 'S4a-orig', 'S4b', 'S4c']

PINS = [
    ('SRC-A2', 'open_problems_fresh/o222_qm_evaluation_semantics/scripts/09_a2_rollback.py',
     'd8037bb16f690a2935c7028b3680d48df6540e01c938ade1d3b5858aed594ace'),
    ('SRC-B5', 'open_problems_fresh/o222_qm_evaluation_semantics/scripts/12_b5_budget.py',
     'f2cb54fa5df094a1e2f7b4910a4c16726a37160f39b194f0157988823aeb1e7a'),
    ('SRC-78', 'open_problems_fresh/o222_qm_evaluation_semantics/scripts/78_r29b_behaviour_classes.py',
     'ed69d5c85306618603c4cbbbf50c803e02041fac3ae2efc8bfca5028a1d8f609'),
    ('A', 'open_problems_fresh/o222_qm_evaluation_semantics/data/04_b2_settings.json',
     '2357006c68e0165dc9fd7d8d73524593a776e1bf6a8b62ddbc8dc2c1a8af20ee'),
    ('h', 'open_problems_fresh/o222_qm_evaluation_semantics/data/08_a2_h_table.json',
     'adeaf8a7fb5495ea57be194c1a704c973a9208026cdd10ef615cd59c58005b66'),
    ('C1C2', 'open_problems_fresh/o222_qm_evaluation_semantics/data/09_a2_correlation.json',
     'dbe664760d3648bd5591f5c43a6ab5ef69bcf9c5834893bc0d907df5e561942e'),
    ('B3R2', 'open_problems_fresh/o222_qm_evaluation_semantics/data/15_b3r2_results.json',
     '15f03bd6802b7685a976e266916d482825e106f7044c0289738fb6edcd85850a'),
    ('B78', 'open_problems_fresh/o222_qm_evaluation_semantics/data/78_r29b_behaviour_classes.json',
     '265e0e5efd1d668f713158c79ce537f55ff77e119539c6555d0212528df25667'),
    ('CH45', 'open_problems_fresh/o222_qm_evaluation_semantics/docs/45_no_go_boundary_charter.md',
     '7dbdbeaad03fa5c8cad6d5198d781eb9212af01ec108e15dfcf5b31a663e6614'),
    ('D13', 'open_problems_fresh/o222_qm_evaluation_semantics/docs/13_d6_results.md',
     '4f689552dcb53dc5f075ba4f8d5587b026328b056eac5d9f50e5f81567173cab'),
    ('D40', 'open_problems_fresh/o222_qm_evaluation_semantics/docs/40_r26_g1g8.md',
     '0a8346b84ecf57daa65ca3255743168cd6db605b250de45cee6ccd4dfa97dcab'),
]

BANNED_IMPORTS = {'numpy', 'scipy', 'random', 'statistics', 'cmath', 'decimal', 'sympy', 'socket',
                  'urllib', 'requests', 'subprocess'}
ALLOWED_IMPORTS = {'ast', 'collections', 'fractions', 'hashlib', 'importlib', 'importlib.util', 'io',
                   'itertools', 'json', 'math', 'os', 'sys', 'time'}
BANNED_DEFS = {'build_group', 'qmul', 'rot_ref', 'krow', 'run_pair', 'load_machine', 'build_2T',
               'closure_bfs', 'qconj', 'qkey'}
BANNED_ATTRS = {'cos', 'sin', 'tan', 'sqrt', 'exp', 'log', 'log10', 'pi', 'e', 'atan', 'acos',
                'asin', 'pow', 'gamma'}


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name,
                              ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


def sha256_file(path):
    h = hashlib.sha256()
    with io.open(path, 'rb') as fh:
        while True:
            b = fh.read(1 << 16)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main():
    argv = sys.argv[1:]
    freeze = '--freeze-impl' in argv
    impl = argv[argv.index('--freeze-impl') + 1] if freeze else None
    t0 = time.time()
    print('=' * 110)
    print('O227 scripts/01 -- R1 contract enforcer (rules: %s)' % RULES)
    print('=' * 110, flush=True)

    # ---------------- C1 hash pins ----------------
    bad = []
    for lab, rel, want in PINS:
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            bad.append('%s: MISSING' % lab)
            continue
        got = sha256_file(p)
        if got != want:
            bad.append('%s: %s != %s' % (lab, got[:16], want[:16]))
    claim('C1', 'frozen-input hash pins (%d objects from docs/01 section 1)' % len(PINS), not bad,
          'mismatches = %d %s' % (len(bad), bad if bad else ''))

    # ---------------- C2 predicate completeness ----------------
    txt = io.open(CONTRACT, encoding='utf-8').read()
    import re
    found = set(re.findall(r'^\| \*\*([A-Za-z0-9\-]+)\*\* \|', txt, re.M))
    missing = [t for t in TAGS if t not in found]
    extra = sorted(found - set(TAGS))
    claim('C2', 'contract carries the 26 pre-registered predicate rows', not missing and not extra,
          'missing = %s ; unexpected = %s' % (missing, extra))

    # ---------------- C2b provenance reachable ----------------
    o210_files = ['final_result.md', 'docs/01_type_system.md', 'docs/02_operations_closure.md',
                  'data/02_type_registry.json']
    ok210 = all(os.path.exists(os.path.join(O210, f)) for f in o210_files)
    blob = ''
    for f in o210_files:
        p = os.path.join(O210, f)
        if os.path.exists(p):
            blob += io.open(p, encoding='utf-8', errors='ignore').read()
    kw = ('K_chain' in blob) and ('K_tree' in blob or 'K-tree' in blob)
    dim_kw = any(k in blob for k in ('dim(K_chain)', 'dim K_chain', 'dimension =', '維數 ='))
    claim('C2b', 'provenance objects reachable and carry the composition law, no dimension data',
          ok210 and kw and not dim_kw,
          'files_ok=%s ; law_text=%s ; dimension_text_found=%s (P1c must stay provenance-only)'
          % (ok210, kw, dim_kw))

    # ---------------- C3 AST block on the machine ----------------
    mpath = os.path.join(ROOT, 'scripts', '02_r1_machine.py')
    src = io.open(mpath, encoding='utf-8').read()
    tree = ast.parse(src)
    problems = []
    math_attrs = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                nm = a.name
                if nm in BANNED_IMPORTS or nm not in ALLOWED_IMPORTS:
                    problems.append('import %s' % nm)
        elif isinstance(node, ast.ImportFrom):
            nm = node.module or ''
            if nm in BANNED_IMPORTS or nm.split('.')[0] not in {x.split('.')[0] for x in ALLOWED_IMPORTS}:
                problems.append('from %s import' % nm)
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == 'math':
                math_attrs.add(node.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, float):
            problems.append('float literal %r at line %d' % (node.value, node.lineno))
        elif isinstance(node, ast.Name) and node.id in ('eval', 'exec', 'compile', '__import__'):
            problems.append('%s() at line %d' % (node.id, node.lineno))
        elif isinstance(node, ast.FunctionDef) and node.name in BANNED_DEFS:
            problems.append('local re-implementation: def %s' % node.name)
    badattr = sorted(math_attrs - {'log2'})
    if badattr:
        problems.append('math.%s' % ','.join(badattr))
    if 'sys.dont_write_bytecode = True' not in src:
        problems.append('missing sys.dont_write_bytecode = True')
    claim('C3', 'machine AST block (imports / math.log2 only / no float literal / no eval / no local read)',
          not problems, 'violations = %d %s' % (len(problems), problems[:6]))

    # C3b no write target outside this O
    def targets(path_expr):
        out = []
        for node in ast.walk(path_expr):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                out.append(node.value)
        return out
    writes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and \
                    isinstance(node.args[1].value, str) and ('w' in node.args[1].value or 'a' in node.args[1].value):
                writes.append(node.args[0])
    o2_writes = 0
    for w in writes:
        for s in targets(w):
            if 'o222' in s or 'o21' in s or 'o20' in s:
                o2_writes += 1
    claim('C3b', 'no write-open on a path mentioning another O directory', o2_writes == 0,
          'write sites = %d ; foreign-O write sites = %d' % (len(writes), o2_writes))

    # ---------------- C4 doc <-> impl tag alignment ----------------
    impl_tags = set(re.findall(r"(?:claim|cell)\(\s*'([A-Za-z0-9\-]+)'", src))
    impl_tags |= set(re.findall(r"results\['([A-Za-z0-9\-]+)'\]", src))
    miss2 = [t for t in TAGS if t not in impl_tags]
    extra2 = sorted(impl_tags - set(TAGS))
    claim('C4', 'contract tag set == machine claim tag set', not miss2 and not extra2,
          'missing in machine = %s ; extra = %s' % (miss2, extra2))

    # ---------------- C5 read semantics imported ----------------
    has_load = 'load_machine' in src and '.load_machine(' in src
    claim('C5', 'machine imports the frozen read semantics (load_machine) and does not re-implement it',
          has_load, 'load_machine call present = %s ; banned local defs present = %s'
          % (has_load, sorted(BANNED_DEFS & {p for p in BANNED_DEFS if ('def %s' % p) in src})))

    # ---------------- C6 static rule check on frozen sources ----------------
    s5 = io.open(os.path.join(O2, 'scripts', '12_b5_budget.py'), encoding='utf-8').read()
    s9 = io.open(os.path.join(O2, 'scripts', '09_a2_rollback.py'), encoding='utf-8').read()
    start = s5.index('def run_pair(')
    end = s5.index('# ---------------------------------------------------------------- full enumeration')
    body = s5[start:end]
    r1 = 'L[-1][0] == ctx' in body                       # top-only read
    r2 = 'L.append(' in body                              # append-only push
    r3 = 'L.pop()' in body                               # rollback pop
    r4 = ('L[-1] =' not in body) and ('L[i] =' not in body) and ('.insert(' not in body)
    r5 = 'L[-1][0] == ctx' in s9 and 'L.append(' in s9 and 'L.pop()' in s9
    claim('C6', 'static ledger rule on the frozen source (top-only / append-only / pop=rollback / no rewrite)',
          r1 and r2 and r3 and r4 and r5,
          'top_only=%s append=%s pop=%s no_inplace_rewrite=%s prototype_read_rule=%s'
          % (r1, r2, r3, r4, r5))

    # ---------------- C7 register precondition ----------------
    reg = os.path.join(REPO, 'problem_register', 'register.jsonl')
    want = {'O227/R1'} | {'O227/R1-%s' % t for t in TAGS}
    have = {}
    with io.open(reg, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            p = e.get('pid') or ''
            if p in want:
                note = e.get('note') or ''
                if e.get('kind') == 'registered' and '見數前' in note:
                    have[p] = e.get('ts')
    miss7 = sorted(want - set(have))
    claim('C7', 'pre-registration present: O227/R1 + 26 sub-pids with a pre-run note',
          not miss7, 'registered-with-pre-run-note = %d / %d ; missing = %s'
          % (len(have), len(want), miss7))

    # ---------------- C8 amendment table empty ----------------
    am = txt.split('## §5 修正記錄')
    tail = am[1][:1200] if len(am) > 1 else ''
    no_post = ('POST-FREEZE' not in tail) and ('post-freeze' not in tail)
    pre_declared = ('A1' in tail) and ('pre-freeze' in tail)
    claim('C8', 'amendment table carries only pre-freeze, pre-run rows (no post-freeze amendment)', no_post,
          'placeholder_free=%s ; pre-freeze row declared=%s' % ('（尚無）' not in tail, pre_declared))

    npass = sum(1 for c in CLAIMS if c['ok'])
    all_ok = npass == len(CLAIMS)
    print('-' * 110)
    print('GATE: %d/%d PASS -> %s' % (npass, len(CLAIMS), 'OPEN' if all_ok else 'CLOSED'))
    print('=' * 110, flush=True)

    out = {'rules_version': RULES, 'gate': 'OPEN' if all_ok else 'CLOSED',
           'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS),
           'contract_sha256': sha256_file(CONTRACT),
           'finished_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'elapsed_s': time.time() - t0}
    if freeze:
        if not all_ok:
            print('REFUSE: gate CLOSED, impl hash not frozen')
            return 1
        out['frozen_impl'] = {'path': os.path.relpath(impl, ROOT), 'sha256': sha256_file(impl)}
        out['frozen_impl_ts'] = time.strftime('%Y-%m-%dT%H:%M:%S%z')
        print('FROZEN impl %s = %s' % (os.path.relpath(impl, ROOT), out['frozen_impl']['sha256']))
    with io.open(os.path.join(DATA, '01_r1_freeze.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
