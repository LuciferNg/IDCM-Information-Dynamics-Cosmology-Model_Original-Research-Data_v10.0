#!/usr/bin/env python3
"""O225 scripts/20 -- R5 合約執行器（規則 `r5-tie-global-v1`）。

C1/C2 合約 doc 之 Q1–Q9 標籤與關鍵詞 / C3/C4 scripts/21,22 禁字集掃描 / C5 陽性對照 / C6 陰性對照
C7 上游 O222 凍結輸入（含 scripts/30、18_d6_mapping）＋合約 doc 之 SHA-256 摘錄 ＋ GATE。
用法: /usr/bin/python3 scripts/20_r5_contract.py
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
DOCS = os.path.join(ROOT, 'docs')
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RULES = 'r5-tie-global-v1'
FORBIDDEN = ('math', 'random', 'numpy', 'scipy', 'statistics', 'cmath', 'decimal', 'secrets', 'mpmath')
LABELS = tuple('Q%d' % i for i in range(1, 10))
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def scan_source(src, fname):
    issues = []
    try:
        tree = ast.parse(src)
    except SyntaxError as err:
        return ['SyntaxError: %s' % err], {}
    n_import = n_float = 0
    has_frac = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                n_import += 1
                if a.name.split('.')[0] in FORBIDDEN:
                    issues.append('%s: forbidden import %s (line %d)' % (fname, a.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            n_import += 1
            if (node.module or '').split('.')[0] in FORBIDDEN:
                issues.append('%s: forbidden from-import %s (line %d)' % (fname, node.module, node.lineno))
            if node.module == 'fractions':
                has_frac = True
        elif isinstance(node, ast.Constant) and isinstance(node.value, float):
            n_float += 1
            issues.append('%s: float literal %r (line %d)' % (fname, node.value, node.lineno))
    return issues, {'imports': n_import, 'float_literals': n_float, 'has_fractions': has_frac}


def sha256(path):
    with io.open(path, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    os.makedirs(DATA, exist_ok=True)
    print('=' * 112)
    print('O225 scripts/20 -- R5 CONTRACT ENFORCER   (rules: %s)' % RULES)
    print('=' * 112, flush=True)
    doc = io.open(os.path.join(DOCS, '09_r5_contract.md'), encoding='utf-8').read()
    missing = [L for L in LABELS if ('**' + L) not in doc and (L + ' [') not in doc]
    keys = ['K_Mb', 'ledger_replay', 'H_r', '軌道-穩定子', '正五邊形', '中心不變', 'P1 gate', '重數']
    missk = [k for k in keys if k not in doc]
    claim('C1', '合約 doc 含 Q1–Q9 全部判據標籤', not missing, 'missing = %s' % missing)
    claim('C2', '合約 doc 含關鍵定義詞', not missk, 'missing = %s ; chars = %d' % (missk, len(doc)))

    files = ['scripts/21_r5_tie_global.py', 'scripts/22_r5_audit.py']
    issues, stats = [], {}
    for rel in files:
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p):
            issues.append('%s: MISSING' % rel)
            continue
        iss, st = scan_source(io.open(p, encoding='utf-8').read(), rel)
        issues += iss
        stats[rel] = st
    claim('C3', 'scripts/21,22 通過禁字集掃描（無禁模組、無 float 字面值）', not issues, 'issues = %s' % issues)
    claim('C4', 'scripts/21,22 皆 from fractions import Fraction', all(v['has_fractions'] for v in stats.values()) if stats else False, '%s' % stats)
    iss_pos, _ = scan_source('import math\nx = 2.25\nfrom scipy import linalg\n', 'pos')
    claim('C5', '陽性對照：人造違規源必須被拒', len(iss_pos) >= 3, '%s' % iss_pos)
    iss_neg, _ = scan_source('from fractions import Fraction as F\ny = F(5, 8) * F(3, 8)\n', 'neg')
    claim('C6', '陰性對照：合法精確算術源必須通過', not iss_neg, '%s' % iss_neg)

    frozen = ['scripts/09_a2_rollback.py', 'scripts/12_b5_budget.py', 'scripts/18_d6_mapping.py',
              'scripts/30_g1g8_gaps.py', 'data/04_b2_settings.json', 'data/08_a2_h_table.json']
    rec = {}
    for rel in frozen:
        p = os.path.join(O222, rel)
        rec[rel] = {'sha256': sha256(p), 'bytes': os.path.getsize(p)}
    docsha = sha256(os.path.join(DOCS, '09_r5_contract.md'))
    out = {'rules': RULES, 'date': '2026-10-01', 'contract_doc': 'docs/09_r5_contract.md',
           'contract_sha256': docsha, 'o222_frozen': rec, 'gate': 'OPEN',
           'enforced': {'files': files, 'forbidden_modules': list(FORBIDDEN), 'float_literals_allowed': False,
                        'stats': stats}}
    claim('C7', '上游 O222 凍結輸入（含 scripts/30、18_d6_mapping）＋合約 doc SHA-256 落盤，GATE = OPEN',
          all(v['bytes'] > 0 for v in rec.values()) and docsha != '', 'contract sha = %s…' % docsha[:16])
    out['claims'] = CLAIMS
    with io.open(os.path.join(DATA, '20_r5_freeze.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
