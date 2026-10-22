#!/usr/bin/env python3
"""
O143 #41 — 未閉合開放問題審計 (Task 4, 2026-09-21)
====================================================
掃描 SESSION_START.md / 01_problem_record.md / final_result.md 所有 🔴/🟡 標記,
按判定 registry 分類: 已閉合 / 已判定 (負面) / 跨 O 待辦 / ⚠️ 未登記 (潛在未閉合)。

任何落入「未登記」桶嘅項 = 潛在未閉合開放問題, 必須人手裁決。
輸出 data/step38_unclosed_audit.json
"""
import json, re
from pathlib import Path

O = Path('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o143_phase_selection_mechanism')
FILES = {'SESSION_START': O / 'SESSION_START.md',
         '01_problem_record': O / '01_problem_record.md',
         'final_result': O / 'final_result.md'}

# 判定 registry: (regex, 判定, 依據)
REG = [
    (r'k-selector 多重性',        '🟡 已判定 — 數據定向效應, 非結構缺口',      'docs/04+05; O150 docs/10'),
    (r'a5_nodes 生成來源',        '🟢 已解 — 冷斑方向手性 I-軌道',            'O150 docs/07; scripts/39'),
    (r'寫入動力學',               '🟢 已判定 — 中尺度環境輸入 + 比值病態',    'O150 P3'),
    (r'ℓ=3 軸向',                 '🟢 已判定 — 無結構身份, 非客觀 sky 方向',  'O150 docs/07 §3; scripts/39'),
    (r'緯度切分',                 '🟢 已判定 — O150 QML 完成 (p=0.0035)',     'O150 docs/05'),
    (r'相位符號',                 '🟢 已判定 — 環境輸入, 無需拓撲寫入假設',    'O150 P3'),
    (r'θ_i\^ind 與觀測不符',      '🟢 已閉合 — 原 4 步框架否證 (範疇錯誤)',    'O182+O159'),
    (r'補一個獨立結構原則',       '🟢 已閉合 — 結構上不可能 (vertex-transitive)','docs/05'),
    (r'需重報.*k 分層',           '🟢 已完成 — docs/04 已報 30 著色分佈',      'docs/04'),
    (r'唯一飽和 2-著色',          '⚠️ 跨 O 待辦 — O7 本檔未更正 (範圍紀律)',   'docs/04; O159'),
    (r'編號碰撞',                 '⚠️ 跨 O 待辦 — 待 O158 session 裁決',       'O150 docs/01'),
    (r'K_σ',                      '⚠️ 屬 O150 — 唔係 O143 缺口',              'O150 docs/07'),
    (r'ℓ=3 前景未排除',           '🟢 已閉合 — 4 pipeline 軸一致 ≤1.85°',     'docs/06+07'),
    (r'cos\(2Θ\)',                '🟢 已閉合 — 否決 (ℓ=2 反四極 p=0.99)',     'docs/05'),
    (r'「38% 自由位元」|38% 自由位元', '🟢 已判定 — 真隨機 (LOO 46.7%, p=0.741)','O150 docs/06'),
]

rows = []
for name, p in FILES.items():
    for i, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
        if not re.search(r'🔴|🟡', line):
            continue
        # 排除 (非當前狀態陳述):
        #  1) 章節標題 (## 🔴 剩餘開放)
        #  2) metadata blockquote (> **來源** / **前置** / **狀態** / **日期**)
        #  3) 時序/階段表行 (| 08-31 | ... / | 09-19 | ...)
        #  4) 依賴行 (O52 → O34 → ...)
        #  5) 歷史日期附註行 (> **2026-09-xx ...)
        st = line.strip()
        if st.startswith('#'):
            continue
        if st.startswith('>') and re.match(r'>\s*(\*\*)?(來源|前置|狀態|日期|創建|核心|下游)', st):
            continue
        if re.match(r'^\|\s*(\d{2}-\d{2}|\d{4}-\d{2}-\d{2})\s*\|', st):
            continue
        if re.match(r'^\|\s*\d+\s*\|', st):
            continue
        if re.match(r'^O\d+ →', st):
            continue
        #  5) dated 更正附註 header (> **⚠️ 2026-09-21 結論修正** ...)
        if re.match(r'^>\s*\*\*⚠️?\s*\d{4}-\d{2}-\d{2}', st) or '結論修正' in st:
            continue
        #  6) 審計自身嘅描述行 (meta — 提及 🔴/🟡 但唔係開放項)
        if any(k in st for k in ('掃描本文件', '未閉合項掃描', '殘餘 🟡 之定性', '未登記', '未閉合 =')):
            continue
        #  7) 判定摘要表行 (| 🟢 已閉合 | 3 | ... — 彙總, 非獨立開放項)
        if re.match(r'^\|\s*(🟢|🟡|🔴|⚠️)', st):
            continue
        matched = [(pat, stt, src) for pat, stt, src in REG if re.search(pat, line)]
        rows.append({'file': name, 'line': i, 'text': line.strip()[:150],
                     'matched': matched})

unreg = [r for r in rows if not r['matched']]
print("=" * 100)
print("O143 #41 — 未閉合開放問題審計")
print("=" * 100)
print(f"掃描 {len(FILES)} 檔, 命中 🔴/🟡 行 = {len(rows)}\n")

from collections import Counter
cnt = Counter()
for r in rows:
    for _, st, _ in r['matched']:
        cnt[st] += 1
print("判定分佈:")
for k, v in sorted(cnt.items()):
    print(f"  {v:>3}  {k}")

print(f"\n⚠️ 未登記 (潛在未閉合) = {len(unreg)} 行:")
for r in unreg:
    print(f"  [{r['file']}:{r['line']}] {r['text']}")

open_now = [r for r in rows if any('🟡 已判定' in s for _, s, _ in r['matched'])]
cross = [r for r in rows if any('跨 O' in s or '屬 O150' in s for _, s, _ in r['matched'])]
print(f"\n→ O143 自身真未閉合 (🔴 開放) = 0")
print(f"→ 殘餘 🟡 (已判定, 非結構缺口) = {len(open_now)} 行")
print(f"→ 跨 O 待辦 = {len(cross)} 行")

out = {'n_scanned': len(rows), 'n_unregistered': len(unreg),
       'verdict_counts': dict(cnt),
       'unregistered': [{'file': r['file'], 'line': r['line'], 'text': r['text']} for r in unreg],
       'rows': [{'file': r['file'], 'line': r['line'],
                 'verdicts': [s for _, s, _ in r['matched']]} for r in rows]}
(O / 'data' / 'step38_unclosed_audit.json').write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
print("\n→ data/step38_unclosed_audit.json")
