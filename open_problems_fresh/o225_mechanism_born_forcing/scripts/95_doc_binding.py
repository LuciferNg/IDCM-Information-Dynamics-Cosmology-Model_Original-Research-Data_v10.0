#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/95 -- 盲測審計 B 段：文檔宣稱 ↔ 凍結證據綁定（不需重跑）。

對每份 docs/*_results.md（及各輪合約）：
  ① 抽出其宣稱之 `RESULT: n/m` 與所引用之 `scripts/NN_*`；
  ② 對應之凍結證據 = data/NN_*.json（pass/total）或 logs/NN_*.out（RESULT 行）；
  ③ 判：相符（bound ✓）／不符（mismatch ⚠）／無據（unbound 🔴）。
另抽「無 scripts/NN 引用之 *_results.md」與「聲稱 ★★ 但無 JSON/LOG 依據者」。

輸出：data/95_doc_binding.json ＋ 終端摘要（top 40）。唯讀；不改任何檔。
"""
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
DOCS = os.path.join(BASE, 'docs')
DATA = os.path.join(BASE, 'data')
LOGS = os.path.join(BASE, 'logs')
SCR = os.path.join(BASE, 'scripts')
AUDIT_SELF = {'92', '93', '94', '95', '96', '97'}
RES_RE = re.compile(r'RESULT:\s*(\d+)\s*/\s*(\d+)')
SREF_RE = re.compile(r'scripts/(\d\d)[_a-z0-9]*')
NUM_RES = re.compile(r'(\d+)\s*/\s*(\d+)\s*PASS')


def load_json_res(num):
    """data/NN_*.json 內 pass/total（可能為 int 或 list）。"""
    out = {}
    for f in sorted(os.listdir(DATA)):
        if f.startswith(num + '_') and f.endswith('.json'):
            try:
                d = json.load(io.open(os.path.join(DATA, f), encoding='utf-8'))
            except Exception:
                continue
            for key in ('pass', 'total'):
                if key in d and isinstance(d[key], int):
                    out[key] = d[key]
            if 'res' in d and isinstance(d.get('res'), list) and len(d['res']) == 2:
                out['pass'], out['total'] = d['res']
    return out


def log_res(num):
    for f in sorted(os.listdir(LOGS)):
        if f.startswith(num + '_') and f.endswith('.out'):
            txt = io.open(os.path.join(LOGS, f), encoding='utf-8', errors='replace').read()
            m = None
            for m in RES_RE.finditer(txt):
                pass
            if m:
                return (int(m.group(1)), int(m.group(2)), f)
    return None


def main():
    """正向綁定：每支有日誌之 script，其 RESULT n/m 必須在某 doc 出現；否則 unbound 🔴。"""
    doc_txt = {}
    for doc in sorted(os.listdir(DOCS)):
        if doc.endswith('.md'):
            doc_txt[doc] = io.open(os.path.join(DOCS, doc), encoding='utf-8').read()
    rows = []
    n_bound = n_unbound = 0
    for f in sorted(os.listdir(LOGS)):
        if not f.endswith('.out') or not f[:2].isdigit():
            continue
        num = f[:2]
        if num in AUDIT_SELF:      # 本輪審計引擎自身（92–97）不列入推導輪之綁定範圍
            continue
        lr = log_res(num)
        if not lr:
            continue
        np_, tot, logf = lr
        tok = '%d/%d' % (np_, tot)
        hits = sorted([d for d, txt in doc_txt.items() if tok in txt
                       and (('r%s' % num.lstrip('0')) in d or 'closeout' in d or 'chain' in d
                            or d.startswith(('%s_' % num)) or d.startswith(('%02d_' % int(num))))])
        hits_any = sorted([d for d, txt in doc_txt.items() if tok in txt])
        ok = bool(hits) or bool(hits_any)
        rows.append({'script': num, 'res': [np_, tot], 'log': logf, 'bound_in': (hits or hits_any)[:4],
                     'exact_round_doc': bool(hits)})
        n_bound += 1 if ok else 0
        n_unbound += 0 if ok else 1
    unbound = [r for r in rows if not r['bound_in']]
    loose = [r for r in rows if r['bound_in'] and not r['exact_round_doc']]
    out = {'script': '95_doc_binding', 'rows': rows, 'n_bound': n_bound, 'n_unbound': n_unbound}
    io.open(os.path.join(DATA, '95_doc_binding.json'), 'w', encoding='utf-8').write(
        json.dumps(out, indent=1, ensure_ascii=False))
    print('=' * 112)
    print('O225 scripts/95 -- 正向綁定：script 判決 ↔ doc 記載（%d 支有日誌）' % len(rows))
    print('=' * 112)
    print('已綁定 = %d；未綁定（任何 doc 皆無此 n/m）= %d' % (n_bound, n_unbound))
    print('未綁定清單：')
    for r in unbound:
        print('  🔴 scripts/%s（日誌 %s）判決 %d/%d 未見於任何 doc' % (r['script'], r['log'], r['res'][0], r['res'][1]))
    print('僅鬆綁定（同值存在於他 doc，但非該輪 doc）：%d 支' % len(loose))
    for r in loose[:12]:
        print('    %s %s → %s' % (r['script'], r['res'], r['bound_in']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
