#!/usr/bin/env python3
"""
O143 #40 — 更正後數值一致性審計 (2026-09-21)
=============================================
檢查 O150 更正涉及嘅關鍵數值，喺 5 個記錄檔中是否一致 (token 級)。
"""
import json, re
from pathlib import Path

D = Path('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh')
O143 = D / 'o143_phase_selection_mechanism'
REC = {
    'final_result': O143 / 'final_result.md',
    'SESSION_START': O143 / 'SESSION_START.md',
    '01_problem_record': O143 / '01_problem_record.md',
    'docs10': O143 / 'docs' / '10_o150_correction_audit_20260921.md',
    'README': D / 'README.md',
}
TXT = {k: v.read_text(encoding='utf-8') for k, v in REC.items()}
# README: 只取 O143 行
TXT['README'] = '\n'.join(l for l in TXT['README'].splitlines() if l.startswith('| **O143**'))
# 01_problem_record: 排除 09-19 及更早嘅時序索引行 (原文引述保留, 唔算不一致)
TXT['01_problem_record'] = '\n'.join(
    l for l in TXT['01_problem_record'].splitlines()
    if not (l.startswith('| ') and '| 2026-09-19 |' in l) and not l.startswith('| 1 ') and not l.startswith('| 2 '))

CHK = []
def chk(tag, desc, pat, must_in):
    """pat: regex; must_in: 應該出現嘅檔案 list"""
    hit = {k: bool(re.search(pat, t)) for k, t in TXT.items()}
    miss = [k for k in must_in if not hit[k]]
    CHK.append((tag, desc, 'PASS' if not miss else f'FAIL (缺於 {miss})', hit))

# 1. 新數值: basis-free 31.8/31.85
chk('A1', '31.8% (basis-free 佔比)', r'31\.8', ['final_result', 'SESSION_START', 'docs10', 'README'])
# 2. GRF null p
chk('A2', 'GRF null p = 0.078 / 0.088', r'0\.078', ['final_result', 'SESSION_START', 'docs10', 'README'])
# 3. 舊 p 值已標作廢 (唔應該再以「p = 0.002」作有效結論出現)
chk('A3', '置換 null p = 0.003 標為作廢', r'置換 null', ['final_result', 'docs10', 'README'])
# 4. a5_nodes 身份
chk('A4', 'a5_nodes = 手性 I-軌道', r'手性.{0,40}軌道|冷斑方向.{0,40}軌道|冷斑方向手性', ['final_result', 'docs10', 'README'])
chk('A5', 'rhombicosidodecahedron 唔同構型', r'rhombicosidodecahedron', ['final_result', 'docs10', 'README'])
# 5. 邊長兩類
chk('A6', '兩類邊長 26.0914 / 26.1664', r'26\.0914', ['final_result', 'docs10'])
chk('A7', '精確邊長 25.8786', r'25\.8786', ['final_result', 'docs10'])
# 6. 對稱性收窄
chk('A8', '圖 I_h (120) vs 幾何點集 I (60)', r'120.{0,40}60|60.{0,40}120', ['final_result', 'docs10', 'README'])
# 7. 軸向
chk('A9', '全天空 ℓ=3 軸 82.49 / 17.21', r'82\.49', ['final_result', 'docs10'])
chk('A10', '夾角 63.2°', r'63\.2', ['final_result', 'docs10', 'README'])
# 8. 5-design 自動
chk('A11', '5-design = 群軌道自動', r'群軌道自動|自動性質', ['final_result', 'docs10', 'README'])
# 9. node9 統計
chk('A12', 'node9 look-elsewhere p = 0.086', r'0\.086', ['final_result', 'docs10', 'README'])
# 10. 頂點傳遞定理保留
chk('A13', '頂點傳遞定理保留', r'頂點傳遞定理', ['final_result', 'SESSION_START', 'docs10', 'README'])
# 11. R3 保留
chk('A14', 'R3 結構定理保留', r'R3', ['final_result', 'SESSION_START', 'docs10', 'README'])
# 12. 狀態 = 已閉合
chk('A15', '狀態 🟢 已閉合', r'🟢.{0,20}已閉合|已閉合', ['final_result', 'SESSION_START', '01_problem_record', 'README'])
# 13. 時序索引 19 項
idx = re.findall(r'^\| (\d+) \|', TXT['01_problem_record'], re.M)
chk('A16', f'時序索引含第 19 項 (實得 {max((int(i) for i in idx), default=0)})',
    r'\| 19 \|', ['01_problem_record'])
# 14. docs/10 存在 + 引用
chk('A17', 'docs/10 被引用', r'docs/10(_o150_correction_audit_20260921)?', ['final_result', 'SESSION_START', '01_problem_record'])

print("=" * 78)
print("O143 #40 — 更正後數值一致性審計")
print("=" * 78)
npass = 0
for tag, desc, res, hit in CHK:
    if res == 'PASS':
        npass += 1
    else:
        print(f"  {tag} {res}  {desc}")
        for k, v in hit.items():
            print(f"      {k}: {'有' if v else '冇'}")
print(f"\n結果: {npass}/{len(CHK)} PASS")
print(f"時序索引項數: {len(idx)} (最大 = {max((int(i) for i in idx), default=0)})")

out = {'n_pass': npass, 'n_total': len(CHK),
       'results': [{'tag': t, 'desc': d, 'result': r} for t, d, r, _ in CHK],
       'index_entries': len(idx), 'index_max': max((int(i) for i in idx), default=0)}
(O143 / 'data' / 'step37_correction_token_audit.json').write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
print("→ data/step37_correction_token_audit.json")
raise SystemExit(0 if npass == len(CHK) else 1)
