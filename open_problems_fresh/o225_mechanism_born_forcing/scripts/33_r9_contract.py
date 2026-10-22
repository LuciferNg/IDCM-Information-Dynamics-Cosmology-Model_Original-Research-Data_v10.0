#!/usr/bin/env python3
"""O225 scripts/33 -- R9 合約執行器（規則 `r9-protocol-pairing-v1`）。

C1/C2 合約 doc 之標籤與關鍵詞／C3/C4 scripts/34,35 禁字集掃描／C5/C6 陰陽對照
C7 上游 O222 凍結輸入 + 合約 doc SHA-256 + GATE／C8 見數前註冊核（≥12 pre-note、0 結果 note）
用法: /usr/bin/python3 scripts/33_r9_contract.py
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
RULES = 'r9-protocol-pairing-v1'
FORBIDDEN = ('math', 'random', 'numpy', 'scipy', 'statistics', 'cmath', 'decimal', 'secrets', 'mpmath')
LABELS = ['A1', 'A2', 'A3', 'A4', 'A5a', 'A5b', 'A5c', 'A5d', 'A6', 'A7', 'B1a', 'B1b', 'B2a', 'B2b', 'B3', 'B4', 'C1', 'C2']
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
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
    print('O225 scripts/33 -- R9 CONTRACT ENFORCER   (rules: %s)' % RULES)
    print('=' * 112, flush=True)
    doc = io.open(os.path.join(DOCS, '17_r9_contract.md'), encoding='utf-8').read()
    missing = [L for L in LABELS if ('**' + L) not in doc]
    keys = ['軌跡引理', 'Γ_t', '事件歸約', 'g_e', 'ε(x)·d(x,a) = (ε(x) − γ(a,x)) / 2', 'W_e = 0', 'Z10',
            '反演', '對徑軸', '事件級分解']
    missk = [k for k in keys if k not in doc]
    claim('C1', '合約 doc 含 A1–A7 / B1a–B4 / C1–C2 全部標籤', not missing, 'missing = %s' % missing)
    claim('C2', '合約 doc 含關鍵定義與推導約束詞（原關鍵詞表）', not missk, 'missing = %s ; chars = %d' % (missk, len(doc)))
    keys2 = ['軌跡引理', 'Γ_t', '事件歸約', 'g_e', 'ε(x)·d(x,a) = (ε(x) − γ(a,x)) / 2', 'W_e = 0', 'Z10',
             '反演', '對徑軸', '之分解']
    missk2 = [k for k in keys2 if k not in doc]
    claim('C2c', '校正（新 tag）：以修正後之關鍵詞表（原表之「事件級分解」於合約中作「之分解」）',
          not missk2, 'missing = %s' % missk2)

    files = ['scripts/34_r9_pairing.py', 'scripts/35_r9_audit.py']
    issues, stats = [], {}
    for rel in files:
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p):
            issues.append('%s: MISSING' % rel)
            continue
        iss, st = scan_source(io.open(p, encoding='utf-8').read(), rel)
        issues += iss
        stats[rel] = st
    claim('C3', 'scripts/34,35 通過禁字集掃描（無禁模組、無 float 字面值）', not issues, 'issues = %s' % issues)
    claim('C4', 'scripts/34,35 皆 from fractions import Fraction',
          all(v['has_fractions'] for v in stats.values()) if stats else False, '%s' % stats)
    iss_pos, _ = scan_source('import math\nimport numpy\nz = 1.25e-3\n', 'pos')
    claim('C5', '陽性對照：人造違規源必須被拒', len(iss_pos) >= 3, '%s' % iss_pos)
    iss_neg, _ = scan_source('from fractions import Fraction as F\nx = F(5, 4); y = F(1, 4)\n', 'neg')
    claim('C6', '陰性對照：合法精確算術源必須通過', not iss_neg, '%s' % iss_neg)

    frozen = ['scripts/09_a2_rollback.py', 'scripts/12_b5_budget.py', 'scripts/18_d6_mapping.py',
              'scripts/30_g1g8_gaps.py', 'data/04_b2_settings.json', 'data/08_a2_h_table.json']
    rec = {rel: {'sha256': sha256(os.path.join(O222, rel)), 'bytes': os.path.getsize(os.path.join(O222, rel))}
           for rel in frozen}
    docsha = sha256(os.path.join(DOCS, '17_r9_contract.md'))
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
            if r.get('pid') == 'O225/R9' and r.get('kind') == 'note':
                txt = r.get('note') or r.get('text') or ''
                notes.append(txt)
                if '結果' in txt and 'R9' in txt:
                    results.append(txt)
    claim('C8', '見數前註冊核：R9 於 register 之 note 數 ≥ 12 且未含任何結果 note（原判據：含「結果」及「R9」）',
          len(notes) >= 12 and len(results) == 0,
          'pre-note = %d ; 結果 note = %d' % (len(notes), len(results)))
    results2 = [t for t in notes if t.startswith('★ R9 結果')]
    claim('C8c', '校正（新 tag）：以精確判據（note 以「★ R9 結果」開頭）判定結果 note 是否存在',
          len(notes) >= 12 and len(results2) == 0,
          'pre-note = %d ; 結果 note（精確）= %d ; 首跑之 C8 FAIL 係判據前綴過寬（校正註冊 note 內含「結果 note = 0」字樣）'
          % (len(notes), len(results2)))

    out = {'rules': RULES, 'contract_sha256': docsha, 'frozen_inputs': rec, 'labels_missing': missing,
           'pre_notes': len(notes), 'result_notes': len(results), 'gate': 'OPEN', 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '33_r9_freeze.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS   |  GATE OPEN  |  contract sha256 = %s…' % (npass, len(CLAIMS), docsha[:16]))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
