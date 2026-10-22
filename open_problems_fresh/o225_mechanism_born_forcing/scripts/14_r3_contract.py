#!/usr/bin/env python3
"""O225 scripts/14 -- R3 合約強制者（r3-centre-v1）。

掃描 scripts/15_r3_centre_theorem.py：禁 float 字面值、禁 math/random/numpy/scipy/statistics/cmath/secrets/decimal
＋ 合約標籤檢查（docs/05_r3_contract.md 須含 R3-P1..R3-P8）
＋ 陽性對照（含 float/import math 之片段必須被拒）
＋ SHA-256 凍結入 data/14_r3_freeze.json；GATE = OPEN 僅當全部通過
用法:  /usr/bin/python3 scripts/14_r3_contract.py
"""
import ast
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
CONTRACT = os.path.join(ROOT, 'docs', '05_r3_contract.md')
IMPLS = ['15_r3_centre_theorem.py']
FORBIDDEN_MODULES = {'math', 'random', 'numpy', 'scipy', 'statistics', 'cmath', 'secrets', 'decimal'}
CHECKS = []


def check(tag, name, ok, detail=''):
    CHECKS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def sha256(path):
    h = hashlib.sha256()
    with io.open(path, 'rb') as fh:
        h.update(fh.read())
    return h.hexdigest()


def scan_source(src, label):
    bad = []
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for al in node.names:
                if al.name.split('.')[0] in FORBIDDEN_MODULES:
                    bad.append('%s: import %s (line %d)' % (label, al.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if (node.module or '').split('.')[0] in FORBIDDEN_MODULES:
                bad.append('%s: from %s import (line %d)' % (label, node.module, node.lineno))
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id in FORBIDDEN_MODULES:
                bad.append('%s: %s.%s (line %d)' % (label, node.value.id, node.attr, node.lineno))
        elif isinstance(node, ast.Constant) and isinstance(node.value, float):
            bad.append('%s: float literal %r (line %d)' % (label, node.value, node.lineno))
    return bad


POSITIVE_CONTROL = '''
import math
def f(x):
    return math.sin(x) + 0.5
'''


def main():
    os.makedirs(DATA, exist_ok=True)
    print('=' * 96)
    print('O225 scripts/14 -- R3 contract enforcer (r3-centre-v1)')
    print('=' * 96, flush=True)
    check('C1', '合約檔存在（docs/05_r3_contract.md）', os.path.exists(CONTRACT), CONTRACT)
    missing_files = [f for f in IMPLS if not os.path.exists(os.path.join(HERE, f))]
    check('C2', '機器存在（scripts/15_r3_centre_theorem.py）', not missing_files,
          'missing = %s' % (missing_files if missing_files else '0'))
    if not os.path.exists(CONTRACT) or missing_files:
        print('GATE = CLOSED')
        return 1
    viol = []
    for f in IMPLS:
        viol += scan_source(io.open(os.path.join(HERE, f), encoding='utf-8').read(), f)
    check('C3', '機器無禁字集命中', not viol, 'violations = %s' % (viol if viol else '0'))
    pos = scan_source(POSITIVE_CONTROL, 'positive-control')
    check('C4', '陽性對照必須被拒（scanner 已受測）',
          any('float literal' in x for x in pos) and any('import math' in x for x in pos),
          'detected = %s' % pos)
    text = io.open(CONTRACT, encoding='utf-8').read()
    must = ['R3-P1', 'R3-P2', 'R3-P3', 'R3-P4', 'R3-P5', 'R3-P6a', 'R3-P6b', 'R3-P6c', 'R3-P7',
            'R3-P8a', 'R3-P8b', '定理', '尖銳性', '普適性', 'A₅']
    missing = [x for x in must if x not in text]
    check('C5', '合約含全部預註冊標籤（R3-P1..R3-P5、R3-P6a/b/c、R3-P7、R3-P8a/b、定理/尖銳性/普適性/商結構）',
          not missing, 'missing = %s' % (missing if missing else '0'))
    freeze = {'rules': 'r3-centre-v1',
              'contract': {'path': 'docs/05_r3_contract.md', 'sha256': sha256(CONTRACT),
                           'bytes': os.path.getsize(CONTRACT)},
              'impls': [{'path': 'scripts/' + f, 'sha256': sha256(os.path.join(HERE, f)),
                         'bytes': os.path.getsize(os.path.join(HERE, f))} for f in IMPLS],
              'enforcer': {'path': 'scripts/14_r3_contract.py', 'sha256': sha256(os.path.abspath(__file__))},
              'forbidden_modules': sorted(FORBIDDEN_MODULES), 'checks': CHECKS}
    allok = all(c['ok'] for c in CHECKS)
    freeze['GATE'] = 'OPEN' if allok else 'CLOSED'
    with io.open(os.path.join(DATA, '14_r3_freeze.json'), 'w', encoding='utf-8') as fh:
        json.dump(freeze, fh, indent=1, ensure_ascii=False)
    print('=' * 96)
    print('GATE = %s   (contract sha256 = %s...)' % (freeze['GATE'], freeze['contract']['sha256'][:16]))
    print('=' * 96)
    return 0 if allok else 1


if __name__ == '__main__':
    sys.exit(main())
