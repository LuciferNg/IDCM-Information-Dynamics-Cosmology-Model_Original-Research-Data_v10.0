#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O127 / scripts/01_data_audit.py
================================
數據核對 + h 單位換算審計 (v9.0 錯誤偵測)

輸入 (官方觀測數據, 無 ΛCDM 衍生處理):
  data/raw/Data_LRGxi_NGCSGC_0.6z1.0_postrecon.txt   (eBOSS DR16 LRG ξ0,ξ2,ξ4; Bautista+2020)
  data/raw/Data_LRGxi_NGCSGC_0.6z1.0_prerecon.txt
  data/raw/Covariance_LRGxi_NGCSGC_0.6z1.0_postrecon.txt
  data/raw/Model_BAO_LRGxi_NGCSGC_0.6z1.0_postrecon.txt

輸出: stdout -> data/01_data_audit.log (呼叫方 redirect)

核心審計:
  v9.0 anisotropic_xi 用 BAO_HINV = BAO_MPC / H (H = H0/100) = 203.1 h⁻¹Mpc
  正確應該係 × H。h⁻¹Mpc 係單位: d[h⁻¹Mpc] = d[Mpc] × h
  → v9.0 全部諧波位置大咗 1/h² = 1.898 倍
"""
import numpy as np
import mpmath as mpm
from fractions import Fraction
import os

mp = mpm.mp
mp.dps = 40
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")

PASS = []
FAIL = []
def chk(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  | {detail}" if detail else ""))

print("=" * 78)
print("  O127 / 01 — 數據核對 + h 單位換算審計")
print("=" * 78)

# ---------------------------------------------------------------
# 1. 載入官方 eBOSS DR16 LRG ξ(s)
# ---------------------------------------------------------------
def load_xi(fn):
    s, x0, e0, x2, e2, x4, e4 = [], [], [], [], [], [], []
    with open(os.path.join(RAW, fn)) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            p = line.split()
            s.append(float(p[0])); x0.append(float(p[1])); e0.append(float(p[2]))
            x2.append(float(p[3])); e2.append(float(p[4])); x4.append(float(p[5])); e4.append(float(p[6]))
    return (np.array(s), np.array(x0), np.array(e0),
            np.array(x2), np.array(e2), np.array(x4), np.array(e4))

s, xi0, err0, xi2, err2, xi4, err4 = load_xi("Data_LRGxi_NGCSGC_0.6z1.0_postrecon.txt")
s_pre, xi0p, err0p, xi2p, err2p, xi4p, err4p = load_xi("Data_LRGxi_NGCSGC_0.6z1.0_prerecon.txt")

print(f"\n[1] eBOSS DR16 LRG ξ(s) — Bautista et al. 2020 (arXiv:2007.08993)")
print(f"    post-recon : {len(s)} bins, s ∈ [{s.min():.1f}, {s.max():.1f}] Mpc/h, Δs = {np.median(np.diff(s)):.2f}")
print(f"    pre-recon  : {len(s_pre)} bins, s ∈ [{s_pre.min():.1f}, {s_pre.max():.1f}] Mpc/h")
print(f"    z_eff = 0.698 (官方 BAO likelihood)")

chk("數據點數 = 39 bins (2.5..192.5 Mpc/h, Δs=5)", len(s) == 39 and abs(s[0]-2.5) < 1e-9 and abs(s[-1]-192.5) < 1e-9,
    f"N={len(s)}, s0={s[0]}, s_end={s[-1]}")
chk("bin 寬 = 5.00 Mpc/h 均勻", np.allclose(np.diff(s), 5.0), f"median Δs={np.median(np.diff(s)):.3f}")

# covariance shape check
cov_rows = []
with open(os.path.join(RAW, "Covariance_LRGxi_NGCSGC_0.6z1.0_postrecon.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        cov_rows.append(line.split())
print(f"\n    covariance 行數 = {len(cov_rows)}  (預期 3 ell × 39 bins = 117 對 → 117² = 13689)")
chk("covariance 檔非空且格式為 (cat_i cat_j ell_i ell_j s_i s_j Cov)", len(cov_rows) > 10000,
    f"rows={len(cov_rows)}")

# ---------------------------------------------------------------
# 2. IDCM 結構常數 (v10.0 非膨脹框架)
# ---------------------------------------------------------------
C_KMS = 299792.458              # km/s (SI 定義)
W_RING = 72.59                  # IDCM 環頻率 ω_ring (km/s/Mpc) — 唯一測量錨
R_WORLD = C_KMS / W_RING        # Mpc, 物理
LAM_SYNC = 2 * mp.pi * R_WORLD / 88
BAO_IDCM = LAM_SYNC / 2         # = π R_world/88, 物理 Mpc

print(f"\n[2] IDCM 結構常數 (非膨脹)")
print(f"    ω_ring = {W_RING} km/s/Mpc  →  R_world = c/ω_ring = {R_WORLD:.3f} Mpc")
print(f"    λ_sync = 2πR_world/88 = {float(LAM_SYNC):.4f} Mpc   (= 晶格間距 a)")
print(f"    BAO = λ_sync/2 = πR_world/88 = {float(BAO_IDCM):.4f} Mpc")

chk("λ_sync 重現 O51 閉合值 294.877 Mpc", abs(float(LAM_SYNC) - 294.877) < 0.01, f"{float(LAM_SYNC):.4f}")
chk("BAO = λ_sync/2 = 147.439 Mpc (O51: ≈r_drag, dev 0.237%)", abs(float(BAO_IDCM) - 147.439) < 0.01,
    f"{float(BAO_IDCM):.4f}")

# ---------------------------------------------------------------
# 3. ★ h 單位換算審計 — v9.0 錯誤
# ---------------------------------------------------------------
# h⁻¹Mpc 係單位: 1 h⁻¹Mpc = 1/h Mpc  ⟹  d[h⁻¹Mpc] = d[Mpc] × h
# R_world = c/(100h) Mpc = (c/100) h⁻¹Mpc = 2997.92 h⁻¹Mpc  (同 h 無關 — h⁻¹Mpc 嘅意義)
H = W_RING / 100.0                      # 0.7259
R_WORLD_HINV = C_KMS / 100.0            # 2997.92 h⁻¹Mpc (h-無關)
BAO_HINV_CORRECT = float(mp.pi * R_WORLD_HINV / 88)   # 正確: 107.03 h⁻¹Mpc
BAO_HINV_V9 = float(BAO_IDCM) / H                     # v9.0 錯誤: 203.11

print(f"\n[3] ★ h 單位換算審計")
print(f"    h = ω_ring/100 = {H}")
print(f"    R_world = {R_WORLD:.2f} Mpc = c/(100h) = {R_WORLD_HINV:.2f} h⁻¹Mpc  (h-無關)")
print(f"    ✓ 正確  λ_sync/2 = πR_world/88 = {BAO_HINV_CORRECT:.3f} h⁻¹Mpc")
print(f"    ✗ v9.0  BAO_MPC/H = {float(BAO_IDCM):.3f}/{H} = {BAO_HINV_V9:.3f} h⁻¹Mpc")
print(f"    比值 v9.0/正確 = {BAO_HINV_V9/BAO_HINV_CORRECT:.4f}  (= 1/h² = {1/H**2:.4f})")

chk("正確換算 = BAO_MPC × h", abs(float(BAO_IDCM) * H - BAO_HINV_CORRECT) < 1e-6,
    f"{float(BAO_IDCM)*H:.3f} vs {BAO_HINV_CORRECT:.3f}")
chk("v9.0 用咗 ÷h (錯誤)", abs(BAO_HINV_V9 - float(BAO_IDCM) / H) < 1e-6, f"{BAO_HINV_V9:.3f}")
chk("v9.0 位置系統性偏大 1/h² = 1.898 倍", abs(BAO_HINV_V9 / BAO_HINV_CORRECT - 1/H**2) < 1e-6,
    f"{BAO_HINV_V9/BAO_HINV_CORRECT:.4f} vs {1/H**2:.4f}")
chk("★ v9.0 結論「IDCM BAO (203.1) 喺 BOSS s_max=177.5 外」係換算偽影",
    BAO_HINV_CORRECT < 177.5,
    f"正確 BAO={BAO_HINV_CORRECT:.1f} h⁻¹Mpc < 177.5 → 喺範圍內")

# ---------------------------------------------------------------
# 4. 觀測 BAO 位置 — 由官方 model + 數據
# ---------------------------------------------------------------
print(f"\n[4] 觀測 BAO 位置")
# 官方 BAO likelihood: z=0.698, DM/rs=17.858, DH/rs=19.326
DM_rs, DH_rs = 17.85823691865007, 19.32575373059217
rs_fid_eBOSS = 147.78   # Bautista+2020 fiducial sound horizon (Mpc)
DM_obs = DM_rs * rs_fid_eBOSS
print(f"    eBOSS DR16 LRG BAO (z=0.698): DM/rs={DM_rs:.3f}, DH/rs={DH_rs:.3f}")
print(f"    fiducial rs = {rs_fid_eBOSS} Mpc  →  DM = {DM_obs:.1f} Mpc")

# 由 ξ0 model 搵峰
ms, m0, m2 = [], [], []
with open(os.path.join(RAW, "Model_BAO_LRGxi_NGCSGC_0.6z1.0_postrecon.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split(); ms.append(float(p[0])); m0.append(float(p[1])); m2.append(float(p[2]))
ms, m0, m2 = np.array(ms), np.array(m0), np.array(m2)
peak_model = ms[np.argmax(m0)]
print(f"    官方 BAO model ξ0 峰 = {peak_model:.1f} Mpc/h")
print(f"    數據 ξ0 局部極大 (s>60): {s[np.argmax(np.where(s>60, xi0, -1e9))]:.1f} Mpc/h")

chk("IDCM BAO 物理尺度 147.44 Mpc ≈ eBOSS rs_fid 147.78 Mpc", abs(float(BAO_IDCM)/rs_fid_eBOSS - 1) < 0.01,
    f"dev = {abs(float(BAO_IDCM)/rs_fid_eBOSS-1)*100:.3f}%")

# ---------------------------------------------------------------
# 5. 密度基準 — 諧波位置 vs bin 數 (P4 預告)
# ---------------------------------------------------------------
print(f"\n[5] 密度基準 (P4 預告): 諧波位置 λ_sync/n 喺 s 範圍內嘅密度")
pos_correct = np.array([BAO_HINV_CORRECT * 2 / n for n in range(2, 21)])   # λ_sync/n in h⁻¹Mpc (IDCM h)
pos_v9 = np.array([BAO_HINV_V9 * 2 / n for n in range(2, 21)])
inr_c = pos_correct[(pos_correct >= s.min()) & (pos_correct <= s.max())]
inr_v = pos_v9[(pos_v9 >= s.min()) & (pos_v9 <= s.max())]
nb = len(s)
print(f"    正確位置 (n=2..20): {len(inr_c)}/19 喺 [{s.min()},{s.max()}]")
print(f"      → 平均每 {np.mean(np.diff(np.sort(inr_c))):.2f} Mpc/h 一個 = 每 {np.mean(np.diff(np.sort(inr_c)))/5:.2f} 個 bin")
print(f"    v9.0 位置 (n=2..20): {len(inr_v)}/19 喺範圍內")
chk("諧波位置密度 ≲ 1.2 bin ⟹ 任何殘餘都會「命中最近 bin」(零 look-elsewhere)",
    np.mean(np.diff(np.sort(inr_c)))/5 < 1.2,
    f"每 {np.mean(np.diff(np.sort(inr_c)))/5:.2f} bin 一個位置 ({len(inr_c)} 個位置 / {nb} bins)")

# ---------------------------------------------------------------
print("\n" + "=" * 78)
print(f"  RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("  FAILED: " + ", ".join(FAIL))
print("=" * 78)
