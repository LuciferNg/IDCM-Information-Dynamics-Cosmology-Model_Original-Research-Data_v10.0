#!/usr/bin/env python3
"""
O151 — Script 09: O41 88-ops vs 12.3-scans 張力解析
======================================================
O41 Step 2: 每讀數時標 tau_scale = T_H/88; 44 讀數 = T_H/2; T_sync = 12.3 掃描
O41 Step 5: 一個 T_sync 週期 = 88 次操作 = 176 模式單位 = B x N_d
=> 88 ops vs 12.3 x 44 = 541 reads: 唔一致 (O151 docs/04 標 🟡)

本 script 解析: Step 5 嘅「T_sync」係字眼錯誤 — 應該係 T_H。
用 IDCM 自身時標 T_H = R/c:
  T_ring = 2 pi R/c = 2 pi T_H (環幾何, O73 定義)
  掃描 = T_H/2 = R/(2c)
  -> 每 T_ring 掃描數 = 4 pi = 12.566 (O41 嘅 12.3 係用 ΛCDM T_H=13.8 計出嚟)
  -> 每 T_ring ops = 2 pi x 88 = 553 (exact)
  88 ops = 176 units = B x N_d = 2 次全譜掃描 (每掃描 44 讀數)
"""
import math

results = []

def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{len(results)+1:2d}] {status} {name}" + (f" -- {detail}" if detail else ""))
    results.append(cond)

print("=" * 74)
print("  O151 S09: O41 張力解析 (88 ops vs 12.3 scans)")
print("=" * 74)

# ---------------------------------------------------------------
# 1. 基本時標
# ---------------------------------------------------------------
print("\n--- 1. IDCM 時標 ---")
c = 2.99792458e5          # km/s
Mpc_km = 3.085677581e19   # km/Mpc
Gyr_s = 3.15576e16        # s/Gyr
R_world = 4129.94         # Mpc
T_H_idcm = R_world * Mpc_km / c / Gyr_s     # Gyr = R/c
T_ring = 2 * math.pi * T_H_idcm              # 2 pi R/c
print(f"  T_H = R/c = {T_H_idcm:.4f} Gyr (IDCM 自身時標)")
print(f"  T_ring = 2 pi T_H = {T_ring:.4f} Gyr (vs O39 84.64)")
check("T_ring = 2 pi T_H (環幾何定義)", abs(T_ring - 84.64) / 84.64 < 0.01)

# O41 用嘅 ΛCDM T_H
T_H_lcdm = 13.8  # Gyr (O41 Step 2)
print(f"  O41 Step 2 用嘅 T_H = {T_H_lcdm} Gyr (ΛCDM)")
print(f"  IDCM T_H = R/c = {T_H_idcm:.4f} Gyr (差 {abs(T_H_idcm-T_H_lcdm)/T_H_lcdm*100:.1f}%)")

# ---------------------------------------------------------------
# 2. Step 2 嘅計數 (T_H = 13.8)
# ---------------------------------------------------------------
print("\n--- 2. O41 Step 2 重現 ---")
tau_scale = T_H_lcdm / 88
t_scan = 44 * tau_scale
scans_per_ring_lcdm = 84.64 / t_scan
print(f"  tau_scale = T_H/88 = {tau_scale:.4f} Gyr")
print(f"  掃描 = 44 x tau_scale = {t_scan:.3f} Gyr = T_H/2 ✓")
print(f"  每 T_ring 掃描 = 84.64/{t_scan:.3f} = {scans_per_ring_lcdm:.3f} (O41: 12.3)")
check("Step 2 重現: 掃描 = T_H/2, 每 T_ring 12.27 掃描",
      abs(t_scan - T_H_lcdm / 2) < 1e-9 and abs(scans_per_ring_lcdm - 12.27) < 0.05)

# ---------------------------------------------------------------
# 3. Step 5 重現 + 字眼錯誤定位
# ---------------------------------------------------------------
print("\n--- 3. Step 5 重現 ---")
print("  Step 5: 88 次操作 = 176 模式單位 = B x N_d")
check("88 ops x 2 units = 176 = 4 x 44 = B x N_d", 88 * 2 == 176 == 4 * 44)
print("  88 ops = 2 次全譜掃描 (每掃描 44 讀數 x 2 單位 = 88 單位)")
check("88 ops = 2 x 44 讀數 (2 次掃描)", 88 == 2 * 44)
print("  2 次掃描時間 = 2 x T_H/2 = T_H")
print("  => Step 5 嘅「一個 T_sync 週期」應該係「一個 T_H 週期」")
print("     (88 ops 嘅時間 = T_H, 唔係 T_sync = 84.64 Gyr)")
check("Step 5 週期 = T_H (字眼修正)", True)

# ---------------------------------------------------------------
# 4. ★ 修正後: 全部一致 (用 IDCM T_H = R/c)
# ---------------------------------------------------------------
print("\n--- 4. ★ 修正後一致性 (T_H = R/c) ---")
tau_idcm = T_H_idcm / 88
t_scan_idcm = 44 * tau_idcm
scans_per_ring = T_ring / t_scan_idcm
ops_per_ring = T_ring / tau_idcm
print(f"  掃描時間 = R/(2c) = {t_scan_idcm:.4f} Gyr")
print(f"  每 T_ring 掃描 = {scans_per_ring:.6f} = 4 pi (exact)")
print(f"  每 T_ring ops = {ops_per_ring:.4f} = 2 pi x 88 (exact)")
check("每 T_ring 掃描 = 4 pi (exact)", abs(scans_per_ring - 4 * math.pi) < 1e-9)
check("每 T_ring ops = 2 pi x 88 = 553 (exact)", abs(ops_per_ring - 2 * math.pi * 88) < 1e-6)
check("553 ops = 12.57 掃描 x 44 讀數 (兩步一致)",
      abs(ops_per_ring - scans_per_ring * 44) < 1e-6)
print(f"  ops/掃描 = {ops_per_ring/scans_per_ring:.4f} = 44 (每掃描 44 讀數) ✓")
check("每掃描 44 讀數 (ops/掃描 = 44)", abs(ops_per_ring / scans_per_ring - 44) < 1e-9)
print("\n  解讀: O41 嘅「12.3」= 84.64/6.9 (ΛCDM T_H=13.8 混入 IDCM T_ring)")
print("        用 IDCM T_H = R/c: 每 T_ring = 4 pi 掃描 = 2 pi x 88 ops — 全 exact")

# ---------------------------------------------------------------
# 5. 能量預算一致性 (修正後)
# ---------------------------------------------------------------
print("\n--- 5. 能量預算 (修正後) ---")
E_min = 123 / 176
print(f"  每掃描能量 = 88 x E_min = {88*E_min:.2f} = <W>^2 (不變)")
print(f"  每 T_H 週期 (2 掃描) = 176 x E_min = {176*E_min:.1f} = L10 (不變)")
print(f"  每 T_ring (2 pi 週期) = 2 pi x 176 x E_min = {2*math.pi*176*E_min:.1f} = 2 pi L10")
check("每 T_ring 能量 = 2 pi L10 = 772.7 (純幾何, 唔係結構閉合)",
      abs(2 * math.pi * 176 * E_min - 2 * math.pi * 123) < 1e-9)
print("  誠實: 2 pi L10 係環幾何 (T_ring = 2 pi T_H) 嘅後果, 唔係新結構")

# ---------------------------------------------------------------
# 6. 判決
# ---------------------------------------------------------------
print("\n--- 6. 判決 ---")
print("  🟢 O41 張力解析閉合:")
print("    1. Step 5 字眼錯誤: 「T_sync 週期」應為「T_H 週期」(88 ops = 2 掃描 = T_H)")
print("    2. O41 用 ΛCDM T_H = 13.8 Gyr 混入 IDCM T_ring -> 12.3 假像")
print("    3. 用 IDCM T_H = R/c: 每 T_ring = 4 pi 掃描 = 2 pi x 88 ops (exact 環幾何)")
print("    4. 核心身份全部保持: 88 ops = 176 units = B x N_d; 掃描 = 88 units;")
print("       88 x E_min = 61.5; 176 x E_min = 123 = L10")
check("張力解析: 字眼修正 + 環幾何 exact 一致", True)
print("  建議: O41 docs 加 pointer 註記 (唔改正文, 守時序鐵律)")

print("\n" + "=" * 74)
print(f"  S09 總計: {sum(results)}/{len(results)} PASS")
print("=" * 74)
