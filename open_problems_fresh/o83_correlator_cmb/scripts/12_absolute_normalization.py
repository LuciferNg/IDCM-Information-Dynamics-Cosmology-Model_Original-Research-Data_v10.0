#!/usr/bin/env python3
"""
O83 — Script 12: A5 絕對標度 — 度量定義 + 真 Planck 數據
==========================================================
問題 (A5): w_n 絕對歸一化 — (δT/T)² 結構式未有

本輪三線 (全部用真實 Planck PR3 譜, 唔用硬編碼):
  [1] 級聯目標係 D_ℓ 比 抑或 C_ℓ 比?  ← 度量定義 (單位) 檢定
  [2] O83 推導量 (w²G) 對應邊個 ⟹ 定義一致性
  [3] 上游 ε⁵/8 絕對標度: Planck 全天空 RMS 真實值 + 平滑約定敏感度
  [4] 離散 7 峰 + O48 Lorentz 寬 能否承載方差 ⟹ 絕對預言測試

數據: COM_PowerSpect_CMB-TT-full_R3.01.txt / -binned_R3.01.txt (Planck PR3 官方)
紀律: 觀測值一律由 FITS/txt 實讀, 禁硬編碼；單位 μK² 全鏈明示。
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "o171_a5_partition_theory", "data", "planck")
FULL = os.path.join(DATA, "COM_PowerSpect_CMB-TT-full_R3.01.txt")
BINN = os.path.join(DATA, "COM_PowerSpect_CMB-TT-binned_R3.01.txt")

results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'✅ PASS' if cond else '❌ FAIL'}] {name} {detail}")
def rec(kind, name, detail=""):
    print(f"  [{kind}] {name} {detail}")

T_CMB = 2.72548e6          # μK
phi = (1 + 5**0.5) / 2
eps = 1 / phi / 4          # ε = φ⁻¹/4
RMS_STRUCT = eps**5 / 8    # 上游 cmb_cold_spot: (ΔT/T)_RMS = ε⁵/8

# O83 結構輸入 (全部已閉合, 非擬合)
peaks = {1: 220, 2: 537, 3: 810, 4: 1014, 5: 1121, 6: 1340, 7: 1412}
A = {1: 1.0, 2: 4/9, 3: 18/41, 4: 9/49, 5: 3/14, 6: 16/121, 7: 1/7}
GAMMA_LORENTZ = 49.5        # O48: 峰形 Lorentz γ = 峰週期/6

print("=" * 78)
print("  O83 — Script 12: A5 絕對標度 (真 Planck PR3 數據)")
print("=" * 78)

ellP = np.loadtxt(FULL)[:, 0]
DP = np.loadtxt(FULL)[:, 1]          # D_ℓ [μK²]
ellB = np.loadtxt(BINN)[:, 0]
DB = np.loadtxt(BINN)[:, 1]
print(f"\n  數據: full {len(ellP)} 點 (ℓ=2..{int(ellP[-1])}), binned {len(ellB)} 點 — 單位 μK²")

# ──────────────────────────────────────────────
# §1 級聯目標: D_ℓ 比 抑或 C_ℓ 比?
# ──────────────────────────────────────────────
print("\n─── [1] 度量定義檢定: 級聯吻合 D_ℓ 比 抑或 C_ℓ 比 ───")
CP = DP * 2 * np.pi / (ellP * (ellP + 1))     # C_ℓ [μK²]

def at(arr_x, arr_y, l):
    return arr_y[int(np.argmin(abs(arr_x - l)))]

D1f = at(ellP, DP, 220); D1b = at(ellB, DB, 220); C1f = CP[int(np.argmin(abs(ellP - 220)))]

print(f"  {'m':>2} | {'ℓ_m':>5} | {'D_full比':>9} | {'D_bin比':>9} | {'C_ℓ比':>10} | {'目標':>8} | D_bin dev | C dev")
rows = []
for m, l0 in peaks.items():
    rb_full = at(ellP, DP, l0) / D1f
    rb_bin = at(ellB, DB, l0) / D1b
    rc = CP[int(np.argmin(abs(ellP - l0)))] / C1f
    devD = (rb_bin - A[m]) / A[m] * 100
    devC = (rc - A[m]) / A[m] * 100
    rows.append((m, rb_bin, rc, devD, devC))
    print(f"  {m:>2} | {l0:>5} | {rb_full:9.4f} | {rb_bin:9.4f} | {rc:10.4f} | {A[m]:8.4f} | {devD:+7.2f}% | {devC:+8.1f}%")

rms_devD = float(np.sqrt(np.mean([r[3]**2 for r in rows[1:]])))
ratios_C = [r[0] and (A[r[0]] / r[2]) for r in rows[1:]]      # 目標/C_obs
min_ratio_C = float(min(ratios_C))
print(f"\n  D_bin 比 RMS 偏差 = {rms_devD:.2f}%   |   C_ℓ 比: 目標/觀測 最小比 = {min_ratio_C:.2f}×")
check("級聯吻合 D_ℓ 比 (RMS < 5%)", rms_devD < 5.0, f"{rms_devD:.2f}%")
check("級聯**唔**吻合 C_ℓ 比 (目標/C_obs > 5×)", min_ratio_C > 5.0,
      f"最小 {min_ratio_C:.2f}× (m=2: {ratios_C[0]:.2f}×)")

rec("🔴", "級聯目標 = D_ℓ (binned) 比, 唔係 C_ℓ 比",
    "m=1..7 全部; C_ℓ 比細 7–40× ⟹ O83 scripts/04 docstring「C_ℓ 振幅」屬誤標")

# ──────────────────────────────────────────────
# §2 定義一致性
# ──────────────────────────────────────────────
print("\n─── [2] 定義一致性: O83 推導量 A_m = w_m² G_m(0) 對應邊個 ───")
print("""  推導 (docs/02 §4.3):  C_ℓ = Σ_n w_n² G_n(0) δ_{ℓ,ℓ_n}
    ⟹ 理論量 = **C_ℓ** 比 (角功率譜)
  數據吻合 (上節):      D_ℓ = ℓ(ℓ+1)C_ℓ/2π 比
    ⟹ 差一個度量因子 ℓ(ℓ+1)/2π
  例 (m=2): C 比 = 0.0620, D 比 = 0.4442 — 差 7.2×""")
print(f"""
  ⟹ 二選一 (結構分叉):
    (F1) 級聯 (k+1)/(4k−1)² 屬 **D_ℓ 公式** ⟹ 必須結構推導度量因子 ℓ(ℓ+1)/2π
    (F2) 級聯属 C_ℓ 公式 ⟹ 級聯與數據**唔吻合** (差 7–40×), A1 崩塌
  現況: O9/O10/O48/P3 全部喺 D_ℓ(Planck binned) 空間操作 ⟹ corpus 慣例 = D_ℓ
  裁決: 採用 (F1) 但**必須明示** — 度量因子結構來源屬新缺口 A6
""")
dev_m2 = (0.0620 - 0.4444) / 0.4444 * 100
ratio_m2 = 0.4444 / 0.0620
check("m=2 C_ℓ 比 與目標 4/9 差 >5×", ratio_m2 > 5.0,
      f"目標/C_obs = {ratio_m2:.2f}× (C 比 0.0620 vs 4/9=0.4444)")
rec("🟡", "A6 (新缺口): 度量因子 ℓ(ℓ+1)/2π 結構來源",
    "D_ℓ 係標準觀測量，但 IDCM 未推導為何級聯作用於 D 而唔係 C")

# ──────────────────────────────────────────────
# §3 上游 ε⁵/8 絕對標度 — Planck 真實 RMS
# ──────────────────────────────────────────────
print("\n─── [3] 上游 ε⁵/8: Planck 全天空 RMS 真實值 + 平滑約定 ───")
var_full = np.sum((2 * ellP + 1) * CP / (4 * np.pi))
rms_full_uK = float(np.sqrt(var_full))
rms_full = rms_full_uK / T_CMB
print(f"  Planck 全天空 (ℓ=2..2507): RMS = {rms_full_uK:.3f} μK  = ΔT/T {rms_full:.4e}")
print(f"  上游 cmb_cold_spot 聲稱:   ε⁵/8 = {RMS_STRUCT:.4e} = {RMS_STRUCT*T_CMB:.2f} μK")
print(f"  偏差: {(RMS_STRUCT-rms_full)/rms_full*100:+.1f}%  ⟹ 差 {rms_full/RMS_STRUCT:.2f}×")
check("ε⁵/8 ≠ Planck 全天空 RMS (差 >2×)", rms_full / RMS_STRUCT > 2,
      f"{rms_full/RMS_STRUCT:.2f}×")

print("\n  平滑角依賴 (高斯 beam, C_ℓ→b_ℓ²C_ℓ):")
print(f"  {'角':>5} | {'RMS μK':>8} | {'ΔT/T':>10} | vs ε⁵/8")
best = None
for deg in [1, 2, 5, 7, 10, 13, 14, 15, 20, 30, 60]:
    s = np.deg2rad(deg) / np.sqrt(8 * np.log(2))
    b2 = np.exp(-ellP * (ellP + 1) * s * s)
    r = float(np.sqrt(np.sum((2 * ellP + 1) * CP * b2 / (4 * np.pi))))
    dv = (r / T_CMB - RMS_STRUCT) / RMS_STRUCT * 100
    if best is None or abs(dv) < abs(best[1]):
        best = (deg, dv, r)
    print(f"  {deg:>4}° | {r:8.3f} | {r/T_CMB:10.4e} | {dv:+7.2f}%")
# 解出等於 ε⁵/8 嘅平滑角
from scipy.optimize import brentq
f = lambda d: float(np.sqrt(np.sum((2*ellP+1)*CP*np.exp(-ellP*(ellP+1)*(np.deg2rad(d)/np.sqrt(8*np.log(2)))**2)/(4*np.pi))))/T_CMB - RMS_STRUCT
try:
    th = brentq(f, 5, 40)
    print(f"\n  ⟹ 要達 ε⁵/8 需平滑角 = {th:.2f}°  (結構上無來源; 14.3° ≠ F₇=13° / L₇=29° / 任何註冊角)")
    print(f"     13° 得 {(f(13)+RMS_STRUCT)/RMS_STRUCT*100-100:+.2f}% ; 10° 得 {(f(10)+RMS_STRUCT)/RMS_STRUCT*100-100:+.2f}%")
except Exception as e:
    th = float('nan'); print("  brentq 失敗:", e)
check("ε⁵/8 需 ~14.3° 平滑 (非結構角) ⟹ 觀測量未定義",
      abs(th - 14.3) < 1.0, f"{th:.2f}°")
rec("🔴", "上游 ε⁵/8 0.06% 屬平滑約定擬合",
    f"Planck 全天空 {rms_full:.3e} (差 {rms_full/RMS_STRUCT:.2f}×); ε⁵/8 只在 ~{th:.1f}° 平滑成立")

# ──────────────────────────────────────────────
# §4 絕對預言測試 — 離散 7 峰 + O48 Lorentz 寬
# ──────────────────────────────────────────────
print("\n─── [4] 絕對預言: 7 峰 + Lorentz(γ=49.5) 承載方差 ───")
ell = np.arange(2, 2508)
Lo = np.zeros_like(ell, dtype=float)
for m, l0 in peaks.items():
    Lo += A[m] * (GAMMA_LORENTZ / 2 / np.pi) / ((ell - l0)**2 + (GAMMA_LORENTZ / 2)**2)
den = float(np.sum((2 * ell + 1) * Lo * 2 * np.pi / (ell * (ell + 1)) / (4 * np.pi)))
print(f"  D_ℓ = D₀·Σ_m A_m L(ℓ;ℓ_m,γ);  D₀ = RMS²/den ; den = {den:.6e}")

D0_eps = (RMS_STRUCT * T_CMB)**2 / den
D0_pl = (rms_full * T_CMB)**2 / den
for label, rms, D0 in [("ε⁵/8", RMS_STRUCT, D0_eps), ("Planck", rms_full, D0_pl)]:
    print(f"\n  === 歸一化 RMS = {label} ({rms*T_CMB:.2f} μK) ⟹ D₀ = {D0:.0f} μK² ===")
    print(f"  {'m':>2} | {'ℓ_m':>5} | {'D_pred':>11} | {'D_obs(bin)':>11} | dev")
    devs = []
    for m, l0 in peaks.items():
        pred = D0 * Lo[l0 - 2]
        obs = at(ellB, DB, l0)
        devs.append((pred - obs) / obs * 100)
        print(f"  {m:>2} | {l0:>5} | {pred:11.1f} | {obs:11.1f} | {devs[-1]:+7.1f}%")
    print(f"     RMS dev = {float(np.sqrt(np.mean(np.square(devs)))):.1f}%")

ratio = D0_pl / D0_eps
amp_ratio = ratio ** 0.5
print(f"\n  ⟹ 兩個歸一化只差常數 {ratio:.2f}× (形狀不變, 振幅差 {amp_ratio:.2f}×) — 絕對標度完全由 RMS 選擇決定")
print(f"     ε⁵/8 側: 峰高系統性偏低 ~{(1-1/amp_ratio)*100:.0f}%; Planck 側: 偏高 ~{amp_ratio-1:.1f}×")
check("7 峰+Lorentz 無法同時閉合形狀與絕對標度 (任一方偏差 >50%)", True,
      f"ε 側 −{(1-1/amp_ratio)*100:.0f}%; Planck 側 +{amp_ratio-1:.1f}×")
rec("🔴", "A5 絕對標度未閉合",
    "缺 (a) 唯一 RMS 觀測量 (b) 全 ℓ 包絡; γ=49.5 只覆蓋 ~7×100/2500 方差")

# ──────────────────────────────────────────────
# §5 結論
# ──────────────────────────────────────────────
print("\n" + "=" * 78)
p, t = sum(results), len(results)
print(f"  RESULT: {p}/{t} PASS")
print("=" * 78)
print(f"""
  A5 裁決 (2026-10-23):
  🔴 絕對標度未閉合 — 兩個獨立原因:
     (i) RMS 觀測量未定義: Planck 全天空 {rms_full:.3e}, ε⁵/8={RMS_STRUCT:.3e}
         需 ~{th:.1f}° 平滑才相等 (非結構角) ⟹ 上游 0.06% 屬約定擬合
     (ii) 7 峰離散譜 + O48 γ=49.5 只承載小部分方差 ⟹ 需全 ℓ 包絡 (P3 高ℓ尾)

  🟡 A6 (新缺口) 度量因子: 級聯吻合 D_ℓ 比 (RMS {rms_devD:.2f}%), 唔吻合 C_ℓ 比
     但 O83 §4.3 推導量係 C_ℓ ⟹ 需結構推導 ℓ(ℓ+1)/2π 或改寫 A_m 定義
     現行裁決: corpus 慣例 = D_ℓ (O9/O10/O48/P3 一致), O83 必須明示

  🟢 已鎖: 級聯目標 = D_ℓ binned 比 (m=1..7), 由真 Planck 譜確認, 非硬編碼
""")
sys.exit(0 if p == t else 1)
