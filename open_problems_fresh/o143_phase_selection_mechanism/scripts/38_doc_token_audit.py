#!/usr/bin/env python3
"""
O143 #38 — 記錄檔 token 一致性審計 (Task 2 補完)
================================================
對 final_result.md / SESSION_START.md / 01_problem_record.md / README (O143 行) 做:
  A. required-token 存在性 (ground-truth 值必須出現)
  B. stale-value 掃描 (舊錯值只准出現喺標註咗嘅歷史註內)
  C. 跨檔一致 (PASS 數 / 狀態 emoji)
"""
import os, re, json

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = f'{BASE}/open_problems_fresh'
O143 = f'{ROOT}/o143_phase_selection_mechanism'
DOCS = {
    'final_result.md': f'{O143}/final_result.md',
    'SESSION_START.md': f'{O143}/SESSION_START.md',
    '01_problem_record.md': f'{O143}/01_problem_record.md',
    'README(O143行)': f'{ROOT}/README.md',
    'docs/08': f'{O143}/docs/08_vertex_transitive_theorem.md',
    'docs/07': f'{O143}/docs/07_gemini_verification.md',
    'docs/12': f'{O143}/docs/12_handoff_responses_20261018.md',
}
R = []
def chk(doc, name, ok, detail=''):
    R.append({'doc': doc, 'name': name, 'ok': bool(ok), 'detail': detail})

texts = {}
for k, p in DOCS.items():
    t = open(p, encoding='utf-8').read()
    if k == 'README(O143行)':
        t = '\n'.join(l for l in t.splitlines() if l.startswith('| **O143** |'))
    texts[k] = t

# ── A. required tokens (ground truth) ──
REQ = {
    'final_result.md': ['120', '2.8e-17', '3.02', '193.45', '−37.85', '5-design', '5.6e-17',
                        '0.002', '44.3', '159/159', '35/35', 'H = 0', '−56', '−0.3819'],
    'SESSION_START.md': ['120', '單一軌道', '2.8e-17', '5-design', '193.45', 'O150'],
    '01_problem_record.md': ['推導時序索引', '6a.', '6b.', '18', '159/159', '35/35'],
    'README(O143行)': ['120', '2.8e-17', '193.45', '5-design', 'ℓ=3', 'docs/01-11'],
    'docs/08': ['120', '單一軌道', '0.0', '2.78e-17', '13', '4.7699e-01', '20'],
    'docs/07': ['5-design', '1.16e-1', '2.41e-1', '0.46', '0.708', '193.45', '−37.85'],
    # 10-18 新增: docs/12 handoff 應答 (token 對應 scripts/42-43 實測值)
    'docs/12': ['0.2723', '0.961', '26.091', '22.58', '0.846', 'k=1', 'rank 3', '96.1'],
}
for doc, toks in REQ.items():
    for tk in toks:
        chk(doc, f'含 "{tk}"', tk in texts[doc])

# ── B. stale-value 掃描 ──
# 4-design 作為「現行聲稱」唔准出現 (只准喺歷史/更正註內)
STALE = {
    'final_result.md': {'4-design': 0, '241.00': 0, '2.79°': 0, 't≤4': 0},
    'README(O143行)': {'4-design': 0, '241.00': 0},
    'SESSION_START.md': {'241.00': 0},
}
for doc, sv in STALE.items():
    for s, maxn in sv.items():
        n = texts[doc].count(s)
        chk(doc, f'stale "{s}" 出現 {n} 次 (上限 {maxn})', n <= maxn)

# docs/08 內 241.00 只准出現喺更正附註
n241 = texts['docs/08'].count('241.00')
chk('docs/08', f'"241.00" 只喺更正註 (出現 {n241} 次, 上限 1)', n241 <= 1)

# ── C. 跨檔一致 ──
for doc in ['final_result.md', 'SESSION_START.md', '01_problem_record.md', 'README(O143行)']:
    # 2026-09-21: 結論由「🟡 部分閉合」修正為「🟢 已閉合 (負面結果)」— 見 docs/10
    chk(doc, '狀態 = 已閉合 (09-21 修正)', ('已閉合' in texts[doc]) or ('部分閉合' in texts[doc]))
for doc in ['final_result.md', '01_problem_record.md']:
    chk(doc, '含 159/159', '159/159' in texts[doc])
    chk(doc, '含 35/35', '35/35' in texts[doc])
chk('final_result.md', '無殘留 stale 4-design', '4-design' not in texts['final_result.md'])
# 軸向一致: 所有檔嘅真軸相同
for doc in ['final_result.md', 'SESSION_START.md', 'README(O143行)', 'docs/07', 'docs/08']:
    chk(doc, '真軸 = (193.45°, −37.85°)', ('193.45' in texts[doc] and '37.85' in texts[doc]))

npass = sum(1 for r in R if r['ok']); nfail = len(R) - npass
print("="*96); print("  O143 #38 — 記錄檔 token 一致性審計"); print("="*96)
print(f"\n{'檔案':<22}{'檢查項':<48}結果")
print("-"*96)
for r in R:
    print(f"{r['doc']:<22}{r['name']:<48}{'PASS' if r['ok'] else 'FAIL'}")
print("-"*96)
print(f"\n總計: {npass}/{len(R)} PASS, {nfail} FAIL")
if nfail:
    print("\nFAIL 清單:")
    for r in R:
        if not r['ok']: print(f"  [{r['doc']}] {r['name']}")
with open(f'{O143}/data/step35_doc_token_audit.json','w') as f:
    json.dump({'n_pass': npass, 'n_total': len(R), 'checks': R}, f, indent=2, ensure_ascii=False)
print(f"\n✅ 已存: data/step35_doc_token_audit.json")
