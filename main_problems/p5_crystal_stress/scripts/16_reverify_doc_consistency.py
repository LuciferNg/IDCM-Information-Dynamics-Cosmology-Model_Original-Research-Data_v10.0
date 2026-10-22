#!/usr/bin/env python3
"""
重驗 — 文檔一致性檢查 (新, 取代舊 scripts/01; 適配 docs/ 佈局)
============================================================
檢查 docs/ 內文檔聲稱嘅關鍵數字 vs 重驗結果, 並掃描幻覺數。
舊 scripts/01_doc_consistency_check.py 保持不變 (歷史; 指向舊 records/ 佈局, 已不適用)。
"""
import os, re, json, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CS = os.path.dirname(HERE)
DOCS = os.path.join(CS, 'docs')

def read(fn):
    p = os.path.join(DOCS, fn)
    if os.path.exists(p):
        return open(p, encoding='utf-8').read()
    p2 = os.path.join(CS, fn)          # 01_problem_record.md 已遷移至 root (2026-10-17)
    return open(p2, encoding='utf-8').read() if os.path.exists(p2) else ""

files = {f: read(f) for f in ['01_problem_record.md', '04_master_summary.md',
                              '06_gemini_insight_analysis.md', '07_o169_correction_reverify.md']}
print("=" * 74)
print("重驗 — 文檔一致性 (docs/)")
print("=" * 74)

# 每文檔必須含嘅關鍵數字
expect = {
    '01_problem_record.md': ["4.891", "3.166", "3.99", "3.43", "45/45", "docs/", "重驗註記"],
    '04_master_summary.md': ["φ⁻²¹", "0.3636", "53.3%", "45/45", "88/21", "重驗註記"],
    '06_gemini_insight_analysis.md': ["重驗註記"],
    '07_o169_correction_reverify.md': ["1.11911398", "0.11911398", "6/6"],
}
errors = []
for fn, keys in expect.items():
    for k in keys:
        if k in files[fn]:
            print(f"  ✓ {fn:<32} 含 {k}")
        else:
            print(f"  ❌ {fn:<32} 缺 {k}")
            errors.append(f"{fn} 缺 {k}")

# 幻覺掃描: 唔應該出現嘅舊值
halluc = {
    '01_problem_record.md': ["2φ⁻¹ℓ"],       # 已證偽伸長律不應在 01 主體結論
    '04_master_summary.md': ["24/24", "37/37"],  # 舊驗證數 (已修正為 45/45)
}
print("\n幻覺掃描 (舊值唔應殘留):")
for fn, bads in halluc.items():
    for b in bads:
        # 允許出現喺「重驗註記」段 (標註用途)
        body = files[fn].split("重驗註記")[0]
        if b in body:
            print(f"  ⚠️ {fn:<30} 舊值殘留: {b}")
            errors.append(f"{fn} 舊值 {b}")
        else:
            print(f"  ✓ {fn:<30} 無 {b} 殘留")

# 重驗 JSON 交叉核對
data = os.path.join(CS, 'data')
for jf, keys in [('reverify_energy.json', ['E_GZK_eV', 'E_max_eV']),
                 ('reverify_anisotropy.json', ['fisher', 'fisher_weighted']),
                 ('reverify_cluster_vacuum.json', ['fisher4_p']),
                 ('reverify_lrd_spectral.json', ['eta', 'C', 'E_strain_Msun'])]:
    p = os.path.join(data, jf)
    if os.path.exists(p):
        j = json.load(open(p))
        miss = [k for k in keys if k not in j]
        print(f"  {'✓' if not miss else '❌'} data/{jf:<30} keys={keys if not miss else miss}")
        if miss: errors.append(f"{jf} 缺 {miss}")
    else:
        print(f"  ❌ data/{jf} 唔存在"); errors.append(f"{jf} missing")

print("\n" + "=" * 74)
print(f"結果: {'✅ 全部通過' if not errors else '❌ ' + str(len(errors)) + ' 問題'}")
for e in errors:
    print(f"   - {e}")
sys.exit(0 if not errors else 1)
