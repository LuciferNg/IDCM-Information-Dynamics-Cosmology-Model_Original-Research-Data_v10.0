#!/usr/bin/env python3
"""O225 scripts/02 -- R1 合約強制者（enforcer）。

職責（缺一不可）：
  1. 讀 docs/01_r1_contract.md，記 SHA-256（預註冊文本不可事後靜默改動）
  2. AST 掃描 scripts/03_r1_barrier.py：禁字集（float 字面值 / math / random / numpy / scipy /
     statistics / cmath / secrets import 與屬性使用）
  3. 陽性對照（必須被拒）＋ 陰性對照（真 impl 必須通過）—— 未拒過任何嘢之 scanner = 未受測
  4. 凍結 scripts/02,03 之 SHA-256 入 data/02_r1_freeze.json；GATE = OPEN 僅當全部通過

用法:  /usr/bin/python3 scripts/02_r1_contract.py
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
CONTRACT = os.path.join(ROOT, 'docs', '01_r1_contract.md')
IMPL = os.path.join(HERE, '03_r1_barrier.py')
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
    """return list of violations"""
    bad = []
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for al in node.names:
                if al.name.split('.')[0] in FORBIDDEN_MODULES:
                    bad.append('%s: import %s (line %d)' % (label, al.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if (node.module or '').split('.')[0] in FORBIDDEN_MODULES:
                bad.append('%s: from %s import ... (line %d)' % (label, node.module, node.lineno))
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id in FORBIDDEN_MODULES:
                bad.append('%s: attribute %s.%s (line %d)' % (label, node.value.id, node.attr, node.lineno))
        elif isinstance(node, ast.Constant) and isinstance(node.value, float):
            bad.append('%s: float literal %r (line %d)' % (label, node.value, node.lineno))
    return bad


POSITIVE_CONTROL = '''
import math
def f(x):
    return math.sqrt(x) * 1.5e-3 + 0.5
'''


def main():
    os.makedirs(DATA, exist_ok=True)
    print('=' * 96)
    print('O225 scripts/02 -- R1 contract enforcer')
    print('=' * 96, flush=True)
    check('C1', '合約檔存在（docs/01_r1_contract.md）', os.path.exists(CONTRACT), CONTRACT)
    check('C2', '機器 impl 存在（scripts/03_r1_barrier.py）', os.path.exists(IMPL), IMPL)
    if not (os.path.exists(CONTRACT) and os.path.exists(IMPL)):
        print('GATE = CLOSED (missing file)')
        return 1

    impl_src = io.open(IMPL, encoding='utf-8').read()
    violations = scan_source(impl_src, 'impl')
    check('C3', 'impl 無禁字集命中（float 字面值 / math / random / numpy / scipy / statistics / cmath / secrets）',
          not violations, 'violations = %s' % (violations if violations else '0'))

    pos_bad = scan_source(POSITIVE_CONTROL, 'positive-control')
    has_float = any('float literal' in x for x in pos_bad)
    has_import = any('import math' in x for x in pos_bad)
    check('C4', '陽性對照（含 float 字面值 + import math）必須被拒 —— scanner 已受測',
          has_float and has_import, 'detected = %s' % pos_bad)

    text = io.open(CONTRACT, encoding='utf-8').read()
    must = ['P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'P11', 'P12', 'P13', 'D5', 'm_min']
    missing = [x for x in must if x not in text]
    check('C5', '合約含全部預註冊謂詞標籤（P4..P13）與 D5 定義', not missing,
          'missing = %s' % (missing if missing else '0'))

    freeze = {
        'rules': 'r1-barrier-v1',
        'contract': {'path': 'docs/01_r1_contract.md', 'sha256': sha256(CONTRACT),
                     'bytes': os.path.getsize(CONTRACT)},
        'impl': {'path': 'scripts/03_r1_barrier.py', 'sha256': sha256(IMPL),
                 'bytes': os.path.getsize(IMPL)},
        'enforcer': {'path': 'scripts/02_r1_contract.py', 'sha256': sha256(os.path.abspath(__file__)),
                     'bytes': os.path.getsize(os.path.abspath(__file__))},
        'forbidden_modules': sorted(FORBIDDEN_MODULES),
        'checks': CHECKS,
    }
    allok = all(c['ok'] for c in CHECKS)
    freeze['GATE'] = 'OPEN' if allok else 'CLOSED'
    with io.open(os.path.join(DATA, '02_r1_freeze.json'), 'w', encoding='utf-8') as fh:
        json.dump(freeze, fh, indent=1, ensure_ascii=False)
    print('=' * 96)
    print('GATE = %s   (contract sha256 = %s...)' % (freeze['GATE'], freeze['contract']['sha256'][:16]))
    print('=' * 96)
    return 0 if allok else 1


if __name__ == '__main__':
    sys.exit(main())
