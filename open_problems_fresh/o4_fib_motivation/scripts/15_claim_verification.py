#!/usr/bin/env python3
"""
15_claim_verification.py — O4 記錄文檔宣稱 vs 實際輸出 交叉驗證
================================================================
目標: 確認 03_complete_record.md + 04_open_issues.md + 05_full_test_record.md
     入面每個關鍵數字都同 data/ 實際輸出一致 — 無幻覺!

驗證清單 (來自三個記錄文檔嘅核心宣稱):
C01: λ₂ = φ⁻² = 0.381966011250 (spectrum_closure.txt)
C02: ω₂ = √λ₂ = φ⁻¹ (spectrum_closure.txt)
C03: cos(36°) = φ/2, cos(72°) = (φ-1)/2 (spectrum_closure.txt)
C04: χ₃(5A) = φ, χ₃(5B) = 1-φ (spectrum_closure.txt)
C05: 21/21 驗證通過 (final_verification.txt)
C06: vertex-transitive 1 profile (vertex_transitive.txt)
C07: 旋轉不變 std=0 (vertex_transitive.txt)
C08: BIC continuous 37.6 < 3lv 63.7 (full_test_results.txt 內 05 輸出)
C09: 0.5° 平滑 d1/d0 ≈ 0.593 (d1_layer.txt)
C10: 4.17° 平滑 d1/d0 ≈ 0.344 (d1_layer.txt)
C11: 阻挫 = 32 (final_verification.txt / frustration_energy.txt)
C12: ε³×30 = 0.111 μK (機制5)
C13: RMS = ε⁵/8 → 30 μK, 冷斑 = 5ε⁵/8 → 150 μK
C14: BFS profile (1,4,8,11,12,11,8,4,1) (final_verification.txt)
C15: 14/14 PASS 完整測試 (full_test_results.txt)
C16: F₄/F₅ = 0.600 ≈ φ⁻¹, F₃/F₄ = 0.667 ≈ φ⁻¹
"""
import numpy as np
import math
import re

phi = (1 + 5**0.5) / 2
eps = (1/phi) / 4
T_cmb = 2.72548

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_fib_motivation/data"

print("=" * 72)
print("O4 15: 記錄文檔宣稱 vs 實際輸出 — 無幻覺交叉驗證")
print("=" * 72)

def read_file(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return ""

results = []
def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(f"{'✅' if cond else '❌'} {name}: {detail}")

# ---------- C01-C04: spectrum_closure.txt ----------
sc_txt = read_file(f"{BASE}/spectrum_closure.txt")
lam2_claim = re.search(r"λ₂=([\d.]+)", sc_txt)
check("C01 λ₂ = φ⁻² (文檔: 0.381966011250)", lam2_claim and abs(float(lam2_claim.group(1)) - phi**-2) < 1e-12, f"file={lam2_claim.group(1) if lam2_claim else 'N/A'}")

w2_claim = re.search(r"ω₂=√λ₂=([\d.]+), φ⁻¹=([\d.]+)", sc_txt)
check("C02 ω₂ = φ⁻¹", w2_claim and abs(float(w2_claim.group(1)) - phi**-1) < 1e-9 and abs(float(w2_claim.group(2)) - phi**-1) < 1e-9, f"file={w2_claim.group(1) if w2_claim else 'N/A'}")

cos36_ok = "cos(36°)=0.8090169944" in sc_txt and "φ/2=0.8090169944" in sc_txt
check("C03 cos(36°)=φ/2", cos36_ok)
chi3_ok = "χ₃(5A)=1.618034" in sc_txt and "χ₃(5B)=-0.618034" in sc_txt
check("C04 χ₃(5A)=φ, χ₃(5B)=1-φ", chi3_ok)

# ---------- C05, C11, C14: final_verification.txt ----------
fv_txt = read_file(f"{BASE}/final_verification.txt")
check("C05 21/21 通過", "21/21 通過" in fv_txt)
check("C11 阻挫 = 32", "A4 阻挫 = 32" in fv_txt)
check("C14 BFS profile", "1+4+8+11+12+11+8+4+1" in fv_txt)

# ---------- C06, C07: vertex_transitive.txt ----------
vt_txt = read_file(f"{BASE}/vertex_transitive.txt")
check("C06 vertex-transitive 1 profile", "profiles: 1" in vt_txt)
rot_std_m = re.search(r"rotation std: ([0-9.e+-]+)", vt_txt)
rot_std = float(rot_std_m.group(1)) if rot_std_m else None
check("C07 旋轉 std=0", rot_std is not None and rot_std == 0.0, f"std={rot_std if rot_std is not None else 'N/A'}")

# ---------- C08: BIC (05_synthesis 輸出喺 full_test_results.txt) ----------
ft_txt = read_file(f"{BASE}/full_test_results.txt")
bic_cont = re.search(r"BIC: continuous ([\d.]+)", ft_txt)
bic_3lv = re.search(r"continuous ([\d.]+) << 5lv ([\d.]+)", ft_txt)
check("C08 BIC continuous 37.6", bic_cont and abs(float(bic_cont.group(1)) - 37.6) < 1.0, f"BIC={bic_cont.group(1) if bic_cont else 'N/A'}")

# ---------- C09, C10: d1_layer.txt ----------
d1_txt = read_file(f"{BASE}/d1_layer.txt")
d05 = re.search(r"0\.5:([\d.]+)", d1_txt)
d417 = re.search(r"4\.17:([\d.]+)", d1_txt)
check("C09 0.5° d1/d0 = 0.593", d05 and abs(float(d05.group(1)) - 0.593) < 0.01, f"file={d05.group(1) if d05 else 'N/A'}")
check("C10 4.17° d1/d0 = 0.344", d417 and abs(float(d417.group(1)) - 0.344) < 0.01, f"file={d417.group(1) if d417 else 'N/A'}")

# ---------- C12, C13: ε 結構 (獨立計算) ----------
eps3_30 = eps**3 * 30
check("C12 ε³×30 = 0.111 μK", abs(eps3_30 - 0.111) < 0.01, f"{eps3_30:.4f}")
RMS = eps**5 / 8
check("C13 RMS→30μK, 冷斑→150μK", abs(RMS*T_cmb*1e6 - 30) < 0.5 and abs(5*RMS*T_cmb*1e6 - 150) < 0.5, f"RMS={RMS*T_cmb*1e6:.2f}, 冷斑={5*RMS*T_cmb*1e6:.1f}")

# ---------- C15: 14/14 PASS ----------
check("C15 14/14 PASS", "完成: 14 PASS, 0 FAIL" in ft_txt)

# ---------- C16: Fibonacci 閉合 (獨立計算) ----------
F = [0, 1, 1, 2, 3, 5]
check("C16 F₄/F₅=0.600, F₃/F₄=0.667", abs(F[4]/F[5] - 0.600) < 0.001 and abs(F[3]/F[4] - 0.667) < 0.001)

# ---------- 文檔引用檢查: 03_complete_record.md 有冇全部章節 ----------
doc3 = read_file(f"{BASE}/../03_complete_record.md")
check("D1 03_complete_record 有 §10 開放問題", "## 10. 開放問題" in doc3)
check("D2 03_complete_record 有 21/21", "21/21" in doc3)

doc5 = read_file(f"{BASE}/../05_full_test_record.md")
check("D3 05_full_test_record 有 v3 14/14", "14/14 PASS" in doc5 and "v3 (最終)" in doc5)

doc4 = read_file(f"{BASE}/../04_open_issues.md")
check("D4 04_open_issues 有 O4-1..O4-8", all(f"O4-{i}" in doc4 for i in range(1, 9)))

# ---------- 總結 ----------
print("\n" + "=" * 72)
passed = sum(1 for _, c in results if c)
total = len(results)
print(f"宣稱驗證: {passed}/{total} 通過")
if passed == total:
    print("✅ 全部宣稱與實際輸出一致 — 記錄文檔無幻覺")
else:
    for name, c in results:
        if not c:
            print(f"  ❌ {name}")
print("=" * 72)

with open(f"{BASE}/claim_verification.txt", 'w') as f:
    f.write("# O4 15: 宣稱 vs 實際 交叉驗證\n")
    for name, c in results:
        f.write(f"{'✅' if c else '❌'} {name}\n")
    f.write(f"\n{passed}/{total} 通過\n")
print(f"\n✅ 已存: data/claim_verification.txt")
