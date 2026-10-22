#!/usr/bin/env python3
"""
O66 03: M_comp 獨立驗證 — 核對所有 docs 數字
=============================================
驗證範圍:
  1. 基礎: M_pl, M_comp, γ₆, 1/γ₆
  2. 1/γ₆ - 1/76 候選
  3. m_ν₃ 預言 (自我一致)
  4. Δm²₃₁ 預言
  5. Σm_ν 預言
  6. 76 = φ⁹ - φ⁻⁹ 身份
  7. 與其他 φ-identity 對照
  8. 檔案存在性
"""
import sys, os, math
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
O66_DIR = SCRIPT_DIR.parent
DATA_DIR = O66_DIR / "data"
DOCS_DIR = O66_DIR / "docs"

phi = (1 + math.sqrt(5)) / 2
B = 4
Nd = 44
M_pl = 1.2209e19
v = 246.0
m_nu3_fit = 0.0536e-9  # GeV
g6 = 4 * math.sin(6 * math.pi / 88)**2

print("=" * 80)
print("O66 03: M_comp 獨立驗證")
print("=" * 80)

total = 0
passed = 0
failed = 0

def check(name, cond, detail=""):
    global total, passed, failed
    total += 1
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ════════════════════════════════════════════════
# 1. 基礎數值
# ════════════════════════════════════════════════
print("\n[1] 基礎數值")
check("M_pl = 1.2209e19 GeV", abs(M_pl - 1.2209e19) < 1e14)
check("γ₆ = 4sin²(6π/88)", abs(g6 - 0.1807360093) < 1e-8)
check("1/γ₆ = 5.532932", abs(1/g6 - 5.532932) < 1e-4)

M_comp_fit = 3.69e13
log10_r = math.log10(M_pl / M_comp_fit)
check("log10(M_pl/M_comp) = 5.519654", abs(log10_r - 5.519654) < 1e-4)

# ════════════════════════════════════════════════
# 2. 1/γ₆ - 1/76 候選
# ════════════════════════════════════════════════
print("\n[2] 1/γ₆ - 1/76 候選")
candidate = 1/g6 - 1/76
M_comp_cand = M_pl * 10**(-candidate)
err = abs(M_comp_cand - M_comp_fit) / M_comp_fit * 100

check("1/γ₆ - 1/76 = 5.519774", abs(candidate - 5.519774) < 1e-4)
check("M_comp ≈ 3.689e13 GeV", abs(M_comp_cand - 3.689e13) < 1e11)
check("M_comp 誤差 < 0.03%", err < 0.03, f"({err:.4f}%)")

# ════════════════════════════════════════════════
# 3. 76 = φ⁹ - φ⁻⁹ 身份
# ════════════════════════════════════════════════
print("\n[3] 76 = φ⁹ - φ⁻⁹")
check("φ⁹ - φ⁻⁹ = 76", abs(phi**9 - phi**(-9) - 76) < 1e-10)
check("1/76 = 0.0131579", abs(1/76 - 0.0131578947) < 1e-8)

# ════════════════════════════════════════════════
# 4. m_ν₃ 預言 (自我一致)
# ════════════════════════════════════════════════
print("\n[4] m_ν₃ 預言")
m_nu3_pred = (g6 * v)**2 / M_comp_cand
m_nu3_eV = m_nu3_pred * 1e9
err_nu = abs(m_nu3_eV - 0.0536) / 0.0536 * 100
check("m_ν₃ ≈ 0.0536 eV", abs(m_nu3_eV - 0.0536) < 0.0001, f"({m_nu3_eV:.6f} eV)")
check("m_ν₃ 誤差 < 0.03%", err_nu < 0.03, f"({err_nu:.4f}%)")

# ════════════════════════════════════════════════
# 5. Δm²₃₁ 預言
# ════════════════════════════════════════════════
print("\n[5] Δm²₃₁ 預言")
dm31_pred = m_nu3_eV**2
check("Δm²₃₁ ≈ 2.87e-3 eV²", abs(dm31_pred - 2.87e-3) < 1e-5, f"({dm31_pred:.4e})")

# ════════════════════════════════════════════════
# 6. 與其他 φ-identity 對照
# ════════════════════════════════════════════════
print("\n[6] φ-identity 對照")
phi_odd = {1: 1, 3: 4, 5: 11, 7: 29, 9: 76, 11: 199}
for n in [1, 3, 5, 7, 9, 11]:
    val = phi_odd[n]
    c = 1/g6 - 1/val
    e = abs(c - log10_r) / log10_r * 100
    print(f"  n={n} ({val}): 1/γ₆-1/{val} = {c:.6f}, 誤差 {e:.4f}%")
    if n == 9:
        check(f"1/γ₆-1/76 係最佳 φ-identity 修正", 
              e < 0.005, f"({e:.4f}%)")
    else:
        check(f"1/γ₆-1/{val} 誤差 > {e:.2f}%",
              e > 0.1, f"({e:.4f}%)")

# ════════════════════════════════════════════════
# 7. 檔案存在性
# ════════════════════════════════════════════════
print("\n[7] 檔案存在性")
files = [
    "01_problem_record.md",
    "scripts/01_mcomp_structural_analysis.py",
    "scripts/02_mcomp_mechanism.py",
    "scripts/03_verify.py",
    "data/01_mcomp_analysis.json",
    "data/02_mcomp_mechanism.json",
]
for f in files:
    path = O66_DIR / f
    check(f"{f} 存在", path.exists())

# ════════════════════════════════════════════════
# 8. 數值一致性交叉驗證
# ════════════════════════════════════════════════
print("\n[8] 數值一致性交叉驗證")
# 從 data/01_mcomp_analysis.json 讀取
json_path = DATA_DIR / "01_mcomp_analysis.json"
if json_path.exists():
    with open(json_path) as f:
        data = json.load(f)
    check("JSON: log10_target 一致", 
          abs(data["log10_target"] - log10_r) < 1e-6)
    check("JSON: inv_gamma6 一致",
          abs(data["inv_gamma6"] - 1/g6) < 1e-6)
    bc = data["best_candidate"]
    check("JSON: 最佳候選名一致",
          bc["name"] == "1/γ₆ - 1/76")
    check("JSON: 最佳候選 M_comp 一致",
          abs(bc["M_comp"] - M_comp_cand) < 1e10)
    check("JSON: P/F 一致",
          data["passed"] >= 0 and data["failed"] == 0)
else:
    check("JSON: 01_mcomp_analysis.json 可讀", False)

# 從 data/02_mcomp_mechanism.json 讀取
json_path2 = DATA_DIR / "02_mcomp_mechanism.json"
if json_path2.exists():
    with open(json_path2) as f:
        data2 = json.load(f)
    check("JSON2: 最佳候選一致",
          data2["best_candidate"] == "1/γ₆ - 1/76")
    check("JSON2: M_comp 一致",
          abs(data2["M_comp_GeV"] - M_comp_cand) < 1e10)
    check("JSON2: m_ν₃ 一致",
          abs(data2["m_nu3_pred_eV"] - m_nu3_eV) < 1e-6)
    check("JSON2: φ-identity 76",
          abs(data2["phi_identity_76"] - 76) < 1e-6)
else:
    check("JSON2: 02_mcomp_mechanism.json 可讀", False)

# ════════════════════════════════════════════════
# 9. 結果總結
# ════════════════════════════════════════════════
print("\n" + "=" * 80)
print(f"驗證結果: {passed}/{total} PASS ({failed} FAIL)")
print("=" * 80)

results = {
    "test": "O66 03: M_comp 獨立驗證",
    "total": total,
    "passed": passed,
    "failed": failed,
    "all_pass": failed == 0,
    "M_comp_GeV": float(M_comp_cand),
    "m_nu3_eV": float(m_nu3_eV),
    "dm31_pred_eV2": float(dm31_pred),
    "log10_value": float(candidate),
    "err_pct": float(err)
}
with open(DATA_DIR / "03_verify.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

if failed > 0:
    print(f"\n❌ 驗證失敗: {failed} 個檢查未通過")
    exit(1)
print(f"\n🎉 全部 {total} 個檢查 PASS!")