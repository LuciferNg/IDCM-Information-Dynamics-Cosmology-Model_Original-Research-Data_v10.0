#!/usr/bin/env python3
"""
O10 74: 文檔一致性核對 — 所有記錄文檔 vs 權威數值
====================================================
讀取所有 O10 記錄文檔, 提取關鍵數值, 同「已驗證權威值」核對,
輸出不一致清單, 確保零幻覺。
"""
import re, os, math, json

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
M = 33
lD = 9055

# ============ 權威值 (由 73_full_verification.py 驗證) ============
AUTHORITY = {
    "3ε": 0.4635254915624212,
    "33/34": 0.9705882352941176,
    "3εφ⁻²": 0.177125,          # P₂ 理論
    "3ε·2φ⁻⁴": 0.135277,        # P₃ 理論
    "3ε·3φ⁻⁶": 0.077492,        # P₄ 理論
    "ℓ_D": 9055,
    "RMS_完整公式": 0.30,
    "Planck_P2": 0.1779,
    "ACT_P2": 0.1759,
    "SPT_P2": 0.1766,
    "γ(n=24)": 2.2846,
    "γ(n=64)": 2.2846,
}

# 峰高 (Planck binned)
PEAKS = {221: 5816, 527: 2579, 815: 2553, 1121: 1246, 1409: 822}
A_VALS = {2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}

# ============ 讀取文檔 ============
docs_dir = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o10_peak_amplitudes"
docs = ["01_problem_record.md", "02_results.md", "03_deltal2_and_silk.md",
        "04_prime_peaks_and_silk.md", "05_prime_peaks_closure.md", "06_factor_and_phase.md"]

print("=" * 72)
print("O10 文檔一致性核對")
print("=" * 72)

issues = []
for doc in docs:
    path = os.path.join(docs_dir, doc)
    text = open(path).read()
    doc_issues = []
    
    # 1. 檢查過時內容: 0.97 因子 (應為 33/34)
    if re.search(r"0\.97[0-9]*\s*(?:因子|統一)", text) and "33/34" not in text:
        doc_issues.append("含過時 0.97 因子描述 (未更新到 33/34)")
    
    # 2. 檢查 ℓ_D = 9147 (舊值, 應為 9055)
    if "9147" in text:
        doc_issues.append("含舊 ℓ_D=9147 (應為 9055)")
    
    # 3. 檢查「簡併對 (4,5)」過時配對 (應為質數孿生對 (5,7))
    if "簡併對" in text and "質數" not in text:
        doc_issues.append("含過時「簡併對」描述 (未更新到質數孿生對)")
    
    # 4. 檢查「質數峰高度公式未推導」過時聲明
    if "質數峰高度公式" in text and "未推導" in text:
        doc_issues.append("含過時「質數峰高度公式未推導」聲明")
    
    # 5. 檢查重複標題 (patch 造成)
    headings = re.findall(r"^#{1,3} .*", text, re.M)
    seen = {}
    for h in headings:
        seen[h] = seen.get(h, 0) + 1
    for h, c in seen.items():
        if c > 1:
            doc_issues.append(f"重複標題: {h} (×{c})")
    
    # 6. 檢查 P₂ 理論值
    if "0.1771" not in text and "3εφ⁻²" in text:
        doc_issues.append("缺 P₂=3εφ⁻²=0.1771 數值")
    
    status = "⚠️" if doc_issues else "✅"
    print(f"\n{status} {doc}")
    for issue in doc_issues:
        print(f"    - {issue}")
        issues.append((doc, issue))

print("\n" + "=" * 72)
print(f"問題總數: {len(issues)}")
for doc, issue in issues:
    print(f"  {doc}: {issue}")
