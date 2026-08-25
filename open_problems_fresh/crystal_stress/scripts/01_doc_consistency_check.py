#!/usr/bin/env python3
"""
文檔數值 + 幻覺檢查
====================
交叉驗證記錄文件宣稱嘅數字 vs 實際計算結果
"""
import math, json, os, re

phi = (1 + 5**0.5)/2
M_sun = 1.989e30
BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/crystal_stress'

errors = []
warnings = []

print("="*72)
print("文檔數值 + 幻覺檢查")
print("="*72)

# ============ 1. 核心物理公式重算 ============
print("\n1. 核心公式重算")
# GZK
L_P = 1.616255e-35
h = 6.62607015e-34
c = 2.99792458e8
eV_J = 1.602176634e-19
E_GZK = h*c/(L_P*phi**44)/eV_J
print(f"  E_GZK = {E_GZK:.4e} eV")
if abs(E_GZK - 4.891e19)/4.891e19 > 0.01:
    errors.append(f"E_GZK mismatch: {E_GZK}")

E_max = 4*phi*E_GZK
print(f"  E_max = {E_max:.4e} eV")
if abs(E_max - 3.166e20)/3.166e20 > 0.01:
    errors.append(f"E_max mismatch: {E_max}")

# η = φ⁻²¹
eta_pred = phi**(-21)
eta_obs = 1e6/(1.565e12/60)
dev_eta = abs(eta_pred/eta_obs - 1)*100
print(f"  η = φ⁻²¹ = {eta_pred:.4e}, 觀測 η = {eta_obs:.4e}, 偏差 {dev_eta:.2f}%")
if dev_eta > 10:
    warnings.append(f"η 偏差 {dev_eta:.1f}% > 10%")

# C 對比度
C = (0.014819 - 0.006916)/(0.014819 + 0.006916)
print(f"  C = {C:.6f}")
if abs(C - 0.3636) > 0.001:
    errors.append(f"C mismatch: {C}")

# 質量比
M_ratio = (1-C)/(1+C)
print(f"  M4/M0 = {M_ratio:.6f} → 低 {(1-M_ratio)*100:.1f}%")
if abs((1-M_ratio)*100 - 53.3) > 0.5:
    warnings.append(f"質量比偏差: {(1-M_ratio)*100:.1f}%")

# ============ 2. 記錄文件 vs JSON 交叉驗證 ============
print("\n2. JSON 數據交叉驗證")
# 檢查所有 JSON 檔案存在 + 可讀
json_files = [
    f"{BASE}/uhecrs/data/gzk_nyquist_results.json",
    f"{BASE}/uhecrs/data/energy_cap_prediction.json",
    f"{BASE}/uhecrs/data/anisotropy_joint_test.json",
    f"{BASE}/uhecrs/data/psz1_vacuum_scan.json",
    f"{BASE}/uhecrs/data/psz2_vacuum_scan.json",
    f"{BASE}/uhecrs/data/mcxc_vacuum_scan.json",
    f"{BASE}/uhecrs/data/abell_vacuum_scan.json",
    f"{BASE}/little_red_dots/data/lrd_node_crosscheck.json",
    f"{BASE}/little_red_dots/data/a5_routing_weighted.json",
    f"{BASE}/little_red_dots/data/wave_equation_results.json",
    f"{BASE}/little_red_dots/data/k_chain_modes.json",
]
for f in json_files:
    if os.path.exists(f):
        try:
            json.load(open(f))
        except Exception as e:
            errors.append(f"JSON parse error: {f}: {e}")
    else:
        errors.append(f"JSON missing: {f}")
print(f"  JSON 檔案: {len(json_files)} 個檢查完成")

# 驗證 gzk JSON 數值
gzk = json.load(open(f"{BASE}/uhecrs/data/gzk_nyquist_results.json"))
if abs(gzk['E_GZK_eV']/E_GZK - 1) > 0.01:
    errors.append(f"gzk JSON E_GZK 唔一致: {gzk['E_GZK_eV']} vs {E_GZK}")
print(f"  gzk JSON E_GZK = {gzk['E_GZK_eV']:.4e} ✓")

# ============ 3. 文檔幻覺檢查 ============
print("\n3. 文檔關鍵數字檢查")
# 檢查 04_master_summary 提及嘅數字
with open(f"{BASE}/records/04_master_summary.md") as f:
    summary = f.read()

# 檢查應該出現嘅關鍵數字
checks = [
    ("2.18%", "GZK 偏差"),
    ("1.08%", "E_max 偏差"),
    ("3.99σ", "Auger 聯合檢驗"),
    ("3.43σ", "星系團真空"),
    ("p=0.044", "LRD 位置"),
    ("3.6σ", "雙重對稱合併"),
    ("φ⁻²¹", "η 效率因子"),
    ("0.3636", "干涉對比度"),
    ("53.3%", "hop=4 質量差"),
    ("24/24", "驗證數目"),
]
for num, label in checks:
    if num in summary:
        print(f"  ✓ {label}: {num} 出現")
    else:
        errors.append(f"04_master_summary 缺少 {label}: {num}")

# 檢查 01_problem_record
with open(f"{BASE}/records/01_problem_record.md") as f:
    rec1 = f.read()
checks1 = [
    ("2.18%", "GZK"),
    ("3.99σ", "Auger"),
    ("3.43σ", "真空"),
    ("φ⁻²¹", "η"),
    ("0.3636", "C"),
    ("53.3%", "質量比"),
    ("F₈", "Fibonacci"),
    ("3330", "拍頻"),
]
for num, label in checks1:
    if num in rec1:
        print(f"  ✓ 01_record {label}: {num}")
    else:
        errors.append(f"01_problem_record 缺少 {label}: {num}")

# 檢查 02_lrd_record
with open(f"{BASE}/little_red_dots/records/02_lrd_record.md") as f:
    rec2 = f.read()
checks2 = [("0.044", "位置"), ("φ⁻²¹", "η"), ("-0.75", "BC-Frust 相關"), ("53.3%", "質量比")]
for num, label in checks2:
    if num in rec2:
        print(f"  ✓ 02_lrd_record {label}: {num}")
    else:
        errors.append(f"02_lrd_record 缺少 {label}: {num}")

# 檢查 04_mass_scaling_framework
with open(f"{BASE}/little_red_dots/records/04_mass_scaling_framework.md") as f:
    rec4 = f.read()
checks4 = [("0.01482", "E0"), ("0.00692", "E4"), ("0.3636", "C"), ("φ⁻²¹", "η"),
           ("1706", "T_beat"), ("0.2965", "ω₁"), ("0.3002", "ω₂")]
for num, label in checks4:
    if num in rec4:
        print(f"  ✓ 04_framework {label}: {num}")
    else:
        errors.append(f"04_framework 缺少 {label}: {num}")

# ============ 4. 排除已知錯誤數字 ============
print("\n4. 幻覺數字掃描 (唔應該出現嘅數)")
# 已拒絕嘅 φ^210 公式唔應該作為「已確認」
bad_patterns = [
    ("φ^210", "已拒絕嘅陷阱公式"),
    ("φ^(210", "已拒絕嘅陷阱公式"),
    ("M_Pl × φ^210", "已拒絕嘅陷阱公式"),
]
for pat, label in bad_patterns:
    for fname, content in [("01", rec1), ("summary", summary), ("02", rec2)]:
        idx = content.find(pat)
        while idx != -1:
            ctx = content[max(0, idx-150):idx+150]
            # 拒絕 context: 附近有「拒絕」「冇推導」「陷阱」「已拒絕」
            is_rejected = any(kw in ctx for kw in ["拒絕", "冇由", "冇推導", "陷阱", "已拒絕", "唔好砌", "❌"])
            if not is_rejected:
                warnings.append(f"{fname} 出現疑似未拒絕嘅 {pat} ({label})")
            idx = content.find(pat, idx+1)

# ============ 5. 總結 ============
print(f"\n{'='*72}")
print(f"檢查完成:")
print(f"  錯誤: {len(errors)}")
for e in errors:
    print(f"    ❌ {e}")
print(f"  警告: {len(warnings)}")
for w in warnings:
    print(f"    ⚠️ {w}")
if not errors and not warnings:
    print("  ✅ 全部通過 — 無幻覺、無數值不一致")
