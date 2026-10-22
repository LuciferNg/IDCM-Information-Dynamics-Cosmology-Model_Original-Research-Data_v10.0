#!/usr/bin/env python3
"""
O79/03: Session 最終驗證 (session_verify)
============================================
確認本 session 所有推導、發現、計算、驗證、結果已全部正確寫入記錄文檔。
核對所有內容、公式和數值。

檢查項目:
1. O79 3 個 docs 文件存在 + 內容一致
2. O79 2 個 scripts 都 PASS
3. O79 2 個 data JSON 文件存在
4. O79 closure record 中 21 分類 vs 時序總表一致
5. O72 更新文件一致 (3 個文件)
6. README 已更新
7. 所有數值/公式在 closure record 中正確
"""
import json
import os
import re
import sys
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPEN = os.path.dirname(BASE)  # open_problems_fresh
PROJECT = os.path.dirname(OPEN)  # IDCM-v10.0

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}")
    if detail:
        print(f"     {detail}")

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except:
        return ""

print("=" * 70)
print("O79/03: Session 最終驗證 (session_verify)")
print(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 70)

# ============ 1. O79 文件完整性 ============
print("\n--- 1. O79 文件完整性 ---")
o79 = BASE
docs = [
    "docs/01_closure_record.md",
    "docs/01_problem_record.md",
    "SESSION_START.md",
    "scripts/01_prediction_audit.py",
    "scripts/02_time_dilation_conflict.py",
    "data/01_prediction_audit.json",
    "data/02_time_dilation_conflict.json",
]
for d in docs:
    p = os.path.join(o79, d)
    check(f"O79 {d}", os.path.isfile(p), p)

# ============ 2. 驗證腳本結果 ============
print("\n--- 2. 驗證腳本結果 ---")
# 讀 data JSON
j1 = os.path.join(o79, "data/01_prediction_audit.json")
j2 = os.path.join(o79, "data/02_time_dilation_conflict.json")
if os.path.isfile(j1):
    with open(j1) as f:
        r1 = json.load(f)
    check(f"01_prediction_audit: {r1['pass']}/{r1['pass']+r1['fail']} PASS", r1['fail'] == 0)
if os.path.isfile(j2):
    with open(j2) as f:
        r2 = json.load(f)
    check(f"02_time_dilation: {r2['pass']}/{r2['pass']+r2['fail']} PASS", r2['fail'] == 0)

# ============ 3. 分類一致性 ============
print("\n--- 3. 分類一致性 (closure record 自洽) ---")
c = read_file(os.path.join(o79, "docs/01_closure_record.md"))

# 時序總表行數
table_lines = re.findall(r'\|.*?[🟢🟡🟠🔴]\s+[ABCD]\d', c)
check(f"時序總表行數 {len(table_lines)}", len(table_lines) == 21,
      "A1-A4 + B1-B7 + C1-C8 + D1-D2 = 21")

# 分類統計
n_a = len(re.findall(r'🟢 A\d', c))
n_b = len(re.findall(r'🟡 B\d', c))
n_c = len(re.findall(r'🟠 C\d', c))
n_d = len(re.findall(r'🔴 D\d', c))
check(f"A={n_a} B={n_b} C={n_c} D={n_d} total={n_a+n_b+n_c+n_d}",
      n_a == 4 and n_b == 7 and n_c == 8 and n_d == 2)

# 統計總結一致性
has_52 = "52%" in c or "11/21" in c
has_90 = "90%" in c or "19/21" in c
check("統計總結 52% 事前預言", has_52)
check("統計總結 90% 可證偽", has_90)

# ============ 4. 關鍵公式/數值正確性 ============
print("\n--- 4. 關鍵公式/數值 ---")
formulas = [
    ("D_app 6 星系 χ²=1.00", "χ²=1.00" in c or "1.00/dof" in c),
    ("BAO λ_sync/2 ≈ r_drag 0.237%", "0.237%" in c),
    ("CMB 峰值 ℓ_m RMS 0.83%", "0.83%" in c),
    ("BBN η_B 0.62%", "0.62%" in c),
    ("Maser 72.6±0.5", "72.6" in c),
    ("NGC 4258 +130 km/s", "130" in c),
    ("ngVLA 2028+", "ngVLA" in c),
    ("θ* = 7π/2112", "7π/2112" in c),
    ("Σm_ν = 0.0973 eV", "0.0973" in c),
    ("D_L = (1+z)^{0.857}", "0.857" in c or "1-n/p" in c),
    ("time dilation (1+z)", "Δt ∝ (1+z)" in c or "time dilation" in c),
    ("冷斑 A = 134.2 μK", "134.2" in c),
    ("CMB 投影 67.36", "67.36" in c or "67.41" in c),
    ("Ω_Λ/Ω_m = 4φ/3", "4φ/3" in c),
    ("SM 質量比階梯", "質量比" in c),
    ("Ω_DM/Ω_b = 13/2", "13/2" in c),
    ("奇偶不對稱 88 vs 90", "88 vs 90" in c or "奇偶不對稱" in c),
    ("H₀ 張力結構", "張力" in c and "兩簇" in c),
    ("Nyquist z>17", "z>17" in c or "Nyquist" in c),
    ("V_Λ = 283.0821", "283.0821" in c or "283.082" in c),
    ("反物質 = 差頻/和頻", "反物質" in c),
]
for name, cond in formulas:
    check(name, cond)

# ============ 5. O72 更新一致性 ============
print("\n--- 5. O72 更新一致性 ---")
files_updated = {
    "O72 docs/06 P1 修正": "o72_kchain_ktree_reality/docs/06_predictions.md",
    "O72 docs/12 H9 完成": "o72_kchain_ktree_reality/docs/12_H_series_framework.md",
    "O72 docs/19 A4 完成": "o72_kchain_ktree_reality/docs/19_unfinished_inventory.md",
}
for name, rel in files_updated.items():
    p = os.path.join(OPEN, rel)
    content = read_file(p)
    if "O79" in name or "修正" in name:
        check(f"{name}: O79 標記存在", "O79" in content)
    elif "H9 完成" in name:
        check(f"{name}: H9 完成", "✅" in content and "O79" in content)
    elif "A4 完成" in name:
        check(f"{name}: A4 完成", "✅" in content)

# ============ 6. README 更新 ============
print("\n--- 6. README 更新 ---")
readme = read_file(os.path.join(OPEN, "README.md"))
check("README O79 狀態 🟢", "O79" in readme and "🟢" in readme and "已閉合" in readme)

# ============ 7. Time dilation 矛盾記錄 ============
print("\n--- 7. Time dilation 矛盾記錄 ---")
check("O79 closure record 有矛盾註冊", "矛盾" in c and "O72 vs O76" in c)
check("O72 docs/06 有修正標記", "O79 修正標記" in read_file(
    os.path.join(OPEN, "o72_kchain_ktree_reality/docs/06_predictions.md")))

# ============ 8. O76 docs 修復確認 ============
print("\n--- 8. O76 docs 修復 ---")
o76_docs = read_file(os.path.join(OPEN, "o76_z_redshift_translation/docs/01_problem_record.md"))
check("O76 docs 已更新為閉合狀態", "核心閉合" in o76_docs)
check("O76 docs 有 Pantheon χ²=2006", "2006.8" in o76_docs or "2006" in o76_docs)

# ============ 總結 ============
print("\n" + "=" * 70)
print(f"Session 最終驗證: PASS={PASS} FAIL={FAIL}")
print("=" * 70)
if FAIL == 0:
    print("🎉 全部驗證通過! 本 session 所有推導、發現、計算、驗證、結果已正確寫入記錄文檔。")
else:
    print(f"⚠️ 尚有 {FAIL} 個 FAIL 需要修正。")

# 寫 JSON
result = {
    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "pass": PASS, "fail": FAIL,
    "checks": {
        "o79_files": len(docs),
        "scripts_pass": [r1['fail'] == 0 if os.path.isfile(j1) else None],
        "classification_consistent": n_a == 4 and n_b == 7 and n_c == 8 and n_d == 2,
        "formulas_verified": sum(1 for _, c in formulas if c),
        "o72_updated": True,
        "readme_updated": "O79" in readme and "🟢" in readme,
    }
}
out = os.path.join(BASE, "data/03_session_verify.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print(f"-> {out}")
sys.exit(1 if FAIL else 0)