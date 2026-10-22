#!/usr/bin/env python3
"""O225 scripts/10 -- R2 合約強制者（r2-g1-dyn-v1）。

掃描 scripts/11_r2_g1_table.py 與 scripts/12_r2_dyn17.py：
  禁 float 字面值、禁 math/random/numpy/scipy/statistics/cmath/secrets import 與屬性使用
  ＋ 合約標籤檢查（docs/03_r2_contract.md 須含 P1..P17、D1..D4）
  ＋ 陽性對照（含 float/import math 之片段必須被拒）＋ 陽性控制（掃描器須報出真值）
  ＋ SHA-256 凍結入 data/10_r2_freeze.json；GATE = OPEN 僅當全部通過
用法:  /usr/bin/python3 scripts/10_r2_contract.py
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
CONTRACT = os.path.join(ROOT, 'docs', '03_r2_contract.md')
IMPLS = ['11_r2_g1_table.py', '12_r2_dyn17.py']
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
import random
def f(x):
    return random.random() + 0.25
'''


def main():
    os.makedirs(DATA, exist_ok=True)
    print('=' * 96)
    print('O225 scripts/10 -- R2 contract enforcer (r2-g1-dyn-v1)')
    print('=' * 96, flush=True)
    check('C1', '合約檔存在（docs/03_r2_contract.md）', os.path.exists(CONTRACT), CONTRACT)
    missing_files = [f for f in IMPLS if not os.path.exists(os.path.join(HERE, f))]
    check('C2', '兩部機器存在（scripts/11_r2_g1_table.py、scripts/12_r2_dyn17.py）', not missing_files,
          'missing = %s' % (missing_files if missing_files else '0'))
    if not os.path.exists(CONTRACT) or missing_files:
        print('GATE = CLOSED')
        return 1
    viol = []
    for f in IMPLS:
        viol += scan_source(io.open(os.path.join(HERE, f), encoding='utf-8').read(), f)
    check('C3', '兩部機器皆無禁字集命中', not viol, 'violations = %s' % (viol if viol else '0'))
    pos = scan_source(POSITIVE_CONTROL, 'positive-control')
    check('C4', '陽性對照必須被拒（scanner 已受測）',
          any('float literal' in x for x in pos) and any('import random' in x for x in pos),
          'detected = %s' % pos)
    text = io.open(CONTRACT, encoding='utf-8').read()
    must = ['P%d' % i for i in range(1, 18)] + ['D1', 'D2', 'D3', 'D4', 'M-value', 'M-div']
    missing = [x for x in must if x not in text]
    check('C5', '合約含全部預註冊標籤（P1..P17、D1..D4、兩判準）', not missing,
          'missing = %s' % (missing if missing else '0'))
    freeze = {'rules': 'r2-g1-dyn-v1',
              'contract': {'path': 'docs/03_r2_contract.md', 'sha256': sha256(CONTRACT),
                           'bytes': os.path.getsize(CONTRACT)},
              'impls': [{'path': 'scripts/' + f, 'sha256': sha256(os.path.join(HERE, f)),
                         'bytes': os.path.getsize(os.path.join(HERE, f))} for f in IMPLS],
              'enforcer': {'path': 'scripts/10_r2_contract.py', 'sha256': sha256(os.path.abspath(__file__))},
              'forbidden_modules': sorted(FORBIDDEN_MODULES), 'checks': CHECKS}
    allok = all(c['ok'] for c in CHECKS)
    freeze['GATE'] = 'OPEN' if allok else 'CLOSED'
    with io.open(os.path.join(DATA, '10_r2_freeze.json'), 'w', encoding='utf-8') as fh:
        json.dump(freeze, fh, indent=1, ensure_ascii=False)
    print('=' * 96)
    print('GATE = %s   (contract sha256 = %s...)' % (freeze['GATE'], freeze['contract']['sha256'][:16]))
    print('=' * 96)
    return 0 if allok else 1


if __name__ == '__main__':
    sys.exit(main())
