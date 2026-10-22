#!/usr/bin/env python3
"""O225 scripts/17 -- R4 合約執行器（規則 `r4-tie-parity-v1`）。

檢查：①合約 doc 之 P1–P8 標籤齊全 ②scripts/18,19 之禁字集（精確算術）
      ③陽性對照（人造違規源必須被拒）④上游 O222 凍結輸入 + 合約 doc 之 SHA-256 摘錄 + GATE。
用法: /usr/bin/python3 scripts/17_r4_contract.py
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
RULES = 'r4-tie-parity-v1'
FORBIDDEN = ('math', 'random', 'numpy', 'scipy', 'statistics', 'cmath', 'decimal', 'secrets', 'mpmath')
LABELS = ('P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8')
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-6s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def scan_source(src, fname):
    """回傳 (issues, stats)。禁：import 禁字模組、float 字面值、Float 建構 Fraction(float)。"""
    issues = []
    try:
        tree = ast.parse(src)
    except SyntaxError as err:
        return ['SyntaxError: %s' % err], {}
    n_import = n_float = n_div = 0
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
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            n_div += 1
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'Fraction':
            for a in node.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, float):
                    issues.append('%s: Fraction(float) at line %d' % (fname, node.lineno))
    return issues, {'imports': n_import, 'float_literals': n_float, 'divisions': n_div, 'has_fractions': has_frac}


def sha256(path):
    with io.open(path, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    os.makedirs(DATA, exist_ok=True)
    print('=' * 112)
    print('O225 scripts/17 -- R4 CONTRACT ENFORCER   (rules: %s)' % RULES)
    print('=' * 112, flush=True)
    doc = io.open(os.path.join(DOCS, '07_r4_contract.md'), encoding='utf-8').read()
    missing = [L for L in LABELS if (L + ' [') not in doc and (L + ' 【') not in doc and ('**' + L) not in doc]
    claim('C1', '合約 doc 含 P1–P8 全部判據標籤', not missing,
          'missing = %s ; 凍結日期行存在 = %s' % (missing, '2026-10-01' in doc))
    keys = ['u-奇', 'conj(r)·u', 'n_tie', '31', 'm_min', 'ax(s)', 'splitmix64']
    missk = [k for k in keys if k not in doc]
    claim('C2', '合約 doc 含關鍵定義詞', not missk, 'missing = %s ; chars = %d' % (missk, len(doc)))

    files = ['scripts/18_r4_tie_parity.py', 'scripts/19_r4_audit.py']
    all_issues = []
    stats = {}
    for rel in files:
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p):
            all_issues.append('%s: MISSING' % rel)
            continue
        src = io.open(p, encoding='utf-8').read()
        iss, st = scan_source(src, rel)
        all_issues += iss
        stats[rel] = st
    claim('C3', 'scripts/18,19 通過禁字集掃描（無禁模組、無 float 字面值）', not all_issues,
          'issues = %s ; stats = %s' % (all_issues, stats))
    claim('C4', 'scripts/18,19 皆以 Fraction 精確算術為主（from fractions import Fraction）',
          all(v['has_fractions'] for v in stats.values()) if stats else False, '%s' % stats)

    pos_src = 'import math\nx = 1.5\nfrom numpy import array\n'
    iss_pos, _ = scan_source(pos_src, 'positive_control')
    claim('C5', '陽性對照：人造違規源必須被拒（3 類違規全部命中）', len(iss_pos) >= 3,
          'detected = %d ; %s' % (len(iss_pos), iss_pos))
    neg_src = 'from fractions import Fraction as F\nx = F(1, 3) + F(2, 7)\ny = x * x\n'
    iss_neg, _ = scan_source(neg_src, 'negative_control')
    claim('C6', '陰性對照：合法精確算術源必須通過', not iss_neg, 'issues = %s' % iss_neg)

    frozen = ['scripts/09_a2_rollback.py', 'scripts/12_b5_budget.py',
              'data/04_b2_settings.json', 'data/08_a2_h_table.json']
    rec = {}
    for rel in frozen:
        p = os.path.join(O222, rel)
        rec[rel] = {'sha256': sha256(p), 'bytes': os.path.getsize(p)}
    docsha = sha256(os.path.join(DOCS, '07_r4_contract.md'))
    out = {'rules': RULES, 'date': '2026-10-01', 'contract_doc': 'docs/07_r4_contract.md',
           'contract_sha256': docsha, 'o222_frozen': rec, 'gate': 'OPEN',
           'enforced': {'files': files, 'forbidden_modules': list(FORBIDDEN),
                        'float_literals_allowed': False, 'stats': stats},
           'claims': CLAIMS}
    claim('C7', '上游 O222 凍結輸入 + 合約 doc 之 SHA-256 摘錄已落盤，GATE = OPEN',
          all(v['bytes'] > 0 for v in rec.values()) and docsha != '', 'contract sha = %s…' % docsha[:16])
    out['claims'] = CLAIMS
    with io.open(os.path.join(DATA, '17_r4_freeze.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
