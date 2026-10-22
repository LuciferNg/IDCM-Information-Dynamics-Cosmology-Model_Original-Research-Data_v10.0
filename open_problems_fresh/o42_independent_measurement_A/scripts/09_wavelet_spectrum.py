#!/usr/bin/env python3
"""
O42 新線 C — 冷斑小波譜形狀診斷 (SMHW w(R) profile)
=====================================================
冷斑嘅 SMHW 係數 w(R) 隨尺度 R 嘅形狀係結構指紋:
  - 高斯 dip (平滑後): w(R) 快速衰減
  - 平面 dip (top-hat): w(R) 有零點 (正負交替)
  - 拓撲缺陷 (texture): 特定形狀
  - A₅ 網絡: 多尺度結構

方法:
  1. 實測 w(R): 01_smhw_results.json (R=1-10°)
  2. 模型 w(R): 高斯 dip (σ=1.77°), 平面 dip (半徑 r0), 比較形狀
  3. 用實測剖面 (04) 做模型 — 直接積分, 睇比率
  4. 關鍵: 實測 w(R) 嘅衰減率 vs 高斯

注意: 實測 w(R) 含背景 CMB (唔係得冷斑), 模型係純冷斑 → 比率唔會 1,
      但衰減率 (shape) 應該可比。
"""
import os, json
import numpy as np

OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# 實測 SMHW 係數
sj = json.load(open(os.path.join(OUTDIR, '01_smhw_results.json')))
R_obs = np.array([1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0])
w_obs = np.array([sj['smhw'][str(R)]['T'] for R in R_obs])
print("實測 SMHW 小波譜:")
for R, w in zip(R_obs, w_obs):
    print(f"  R={R:>5.2f}°: w = {w:+.2f} μK")

# 正規化 (R=3 做基準, 峰值附近)
i3 = np.argmin(np.abs(R_obs - 3.0))
w_norm = w_obs / abs(w_obs[i3])
print(f"\n正規化 (R=3° = 1):")
for R, wn in zip(R_obs, w_norm):
    print(f"  R={R:>5.2f}°: {wn:+.3f}")

# 模型 1: 高斯 dip σ=1.77° — w(R) ∝ ?
# SMHW 對高斯 dip 嘅響應: 解析冇閉式, 但衰減率可以數值
# 用 01 嘅 pipeline 模型結果 (07 已做): 高斯模型 w(R) = [-9.26, -10.85, -9.38, -7.51, -6.45, -4.67, -3.12]
w_gauss = np.array([-9.26, -10.85, -9.38, -7.51, -6.45, -4.67, -3.12])
wg_norm = w_gauss / abs(w_gauss[i3])

print(f"\n{'R(°)':>6} {'實測正規':>10} {'高斯正規':>10} {'比率':>8}")
print("-" * 38)
for R, wo, wg in zip(R_obs, w_norm, wg_norm):
    print(f"{R:>6.2f} {wo:>10.3f} {wg:>10.3f} {wo/wg:>8.2f}")

# 衰減率: 峰值到 R=10 嘅下降
decay_obs = w_norm[-1] / w_norm[i3]  # 應該 < 1 (衰減)
decay_gauss = wg_norm[-1] / wg_norm[i3]
print(f"\n峰值→R=10° 衰減: 實測 {decay_obs:.3f} vs 高斯 {decay_gauss:.3f}")
print(f"比率 = {decay_obs/decay_gauss:.2f} ({'高斯-like' if 0.5 < decay_obs/decay_gauss < 1.5 else '比高斯慢/快'})")

# 關鍵: 實測 w(R) 喺大 R 衰減慢 → 冷斑有更寬嘅分量 (A₅ 網絡 26° 結構?)
print()
print("詮釋:")
print("  若實測衰減比高斯慢 → 冷斑有額外大尺度分量 (A₅ 網絡/26° 節點間距)")
print("  若一致 → 冷斑 ≈ 平滑後高斯 dip, A=134.2 結構自洽")
