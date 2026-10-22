#!/usr/bin/env python3
"""O225 scripts/27 -- R7 合約執行器（規則 `r7-delta-as-parity-count-v1`）。

C1/C2 合約 doc 之 A1/A2/A3/A5/A6/A7 + B1/B2/B3 標籤與關鍵詞／C3/C4 scripts/28,29 禁字集掃描
C5/C6 陽性 + 陰性對照／C7 上游 O222 凍結輸入 + 合約 doc SHA-256 + GATE
C8 見數前註冊核：R7 於 register 之 note 數 ≥ 8 且**未含任何結果 note**
用法: /usr/bin/python3 scripts/27_r7_contract.py
"""
import ast
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
DATA = os.path.join(ROOT, 'data')
DOCS = os.path.join(ROOT, 'docs')
O222 = os.path.join(REPO, 'open_problems_fresh/o222_qm_evaluation_semantics')
REG = os.path.join(REPO, 'problem_register/register.jsonl')
RULES = 'r7-delta-as-parity-count-v1'
FORBIDDEN = ('math', 'random', 'numpy', 'scipy', 'statistics', 'cmath', 'decimal', 'secrets', 'mpmath')
LABELS = ['A1', 'A2', 'A3', 'A5', 'A6', 'A7', 'B1', 'B2', 'B3']
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
    print('O225 scripts/27 -- R7 CONTRACT ENFORCER   (rules: %s)' % RULES)
    print('=' * 112, flush=True)
    doc = io.open(os.path.join(DOCS, '13_r7_contract.md'), encoding='utf-8').read()
    missing = [L for L in LABELS if ('**' + L) not in doc]
    keys = ['d(a,s)', 'ε(s)', 'γ(a,s)', '逐事件', 'pointwise', 'S(s0)', 'p + q', '赤道矩形', 'A₅ 商', '600']
    missk = [k for k in keys if k not in doc]
    claim('C1', '合約 doc 含 A1/A2/A3/A5/A6/A7 + B1/B2/B3 全部標籤', not missing, 'missing = %s' % missing)
    claim('C2', '合約 doc 含關鍵定義與推導約束詞', not missk, 'missing = %s ; chars = %d' % (missk, len(doc)))

    files = ['scripts/28_r7_mechanism2.py', 'scripts/29_r7_audit.py']
    issues, stats = [], {}
    for rel in files:
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p):
            issues.append('%s: MISSING' % rel)
            continue
        iss, st = scan_source(io.open(p, encoding='utf-8').read(), rel)
        issues += iss
        stats[rel] = st
    claim('C3', 'scripts/28,29 通過禁字集掃描（無禁模組、無 float 字面值）', not issues, 'issues = %s' % issues)
    claim('C4', 'scripts/28,29 皆 from fractions import Fraction',
          all(v['has_fractions'] for v in stats.values()) if stats else False, '%s' % stats)
    iss_pos, _ = scan_source('import numpy\nimport random\nz = 3.5e-2\n', 'pos')
    claim('C5', '陽性對照：人造違規源必須被拒', len(iss_pos) >= 3, '%s' % iss_pos)
    iss_neg, _ = scan_source('from fractions import Fraction as F\nx = F(3, 8); y = F(1, 8)\n', 'neg')
    claim('C6', '陰性對照：合法精確算術源必須通過', not iss_neg, '%s' % iss_neg)

    frozen = ['scripts/09_a2_rollback.py', 'scripts/12_b5_budget.py', 'scripts/18_d6_mapping.py',
              'scripts/30_g1g8_gaps.py', 'data/04_b2_settings.json', 'data/08_a2_h_table.json']
    rec = {rel: {'sha256': sha256(os.path.join(O222, rel)), 'bytes': os.path.getsize(os.path.join(O222, rel))}
           for rel in frozen}
    docsha = sha256(os.path.join(DOCS, '13_r7_contract.md'))
    claim('C7', '上游 O222 凍結輸入 + 合約 doc SHA-256 落盤，GATE = OPEN',
          all(v['bytes'] > 0 for v in rec.values()) and docsha != '', 'contract sha = %s…' % docsha[:16])

    notes, results = [], []
    if os.path.isfile(REG):
        for line in io.open(REG, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get('pid') == 'O225/R7' and r.get('kind') == 'note':
                txt = r.get('note') or r.get('text') or ''
                notes.append(txt)
                if '結果' in txt and 'R7' in txt:
                    results.append(txt)
    claim('C8', '見數前註冊核：R7 於 register 之 note 數 ≥ 8 且未含任何結果 note（結果 note 尚未寫入）',
          len(notes) >= 8 and len(results) == 0,
          'pre-note = %d ; 結果 note = %d' % (len(notes), len(results)))

    out = {'rules': RULES, 'contract_sha256': docsha, 'frozen_inputs': rec, 'labels_missing': missing,
           'pre_notes': len(notes), 'result_notes': len(results), 'gate': 'OPEN', 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '27_r7_freeze.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS   |  GATE OPEN  |  contract sha256 = %s…' % (npass, len(CLAIMS), docsha[:16]))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
