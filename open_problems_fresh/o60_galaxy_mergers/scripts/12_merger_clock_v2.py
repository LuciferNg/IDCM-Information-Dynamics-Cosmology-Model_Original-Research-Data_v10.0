#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O60d 合併時鐘 — K_Chain 模式週期 vs 合併事件 (Gemini 方案 C)
==============================================================
Gemini 建議: 將 T_sync 的子諧波引入動態沉降時標。
我注意到 script 02 的模式週期表可能直接命中!

K_Chain 模式週期: T_n = T_sync·sin(π/88)/sin(nπ/88)
(= T_sync × ω₁/ω_n, 即模式 n 相對基頻嘅週期)

事件:
  LKH: 12.3 Gyr ago
  GSE: 10.5 Gyr ago
  Sgr: 6.0 Gyr ago
  t_iso: 14.48 Gyr (最老 GC)

測試: 事件時間 ≈ T_n (邊個模式?) 偏差 < 年齡誤差 (0.26 Gyr 相對, ~1 Gyr 絕對)?
"""
import numpy as np
import math

phi = (1 + 5**0.5) / 2
c = 299792.458
R_H = 4129.94
tau = R_H * 3.085677581e19 / c / 3.15576e7 / 1e9
T_sync = 2 * math.pi * tau

# Lucas / Fibonacci
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123]
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

print("=" * 72)
print("O60d: 合併時鐘 — K_Chain 模式週期 vs 合併事件")
print("=" * 72)
print(f"T_sync = {T_sync:.4f} Gyr, τ = {tau:.4f} Gyr")

# 模式週期
print(f"\n[1] K_Chain 模式週期 T_n = T_sync·sin(π/88)/sin(nπ/88):")
events = {"LKH": 12.3, "GSE": 10.5, "Sgr": 6.0, "t_iso": 14.48}
best = {}
for n in range(1, 45):
    T_n = T_sync * math.sin(math.pi/88) / math.sin(math.pi*n/88)
    for name, t in events.items():
        dev = abs(T_n - t) / t * 100
        if name not in best or dev < best[name][2]:  # 比較 dev (index 2), 唔係 T_n (index 1)!
            best[name] = (n, T_n, dev)

for name, t in events.items():
    n, Tn, dev = best[name]
    # 結構意義
    struct = ""
    if n == 7: struct = "★ L₄=7, DM 模式 m₇=13.8MeV!"
    elif n == 8: struct = "★ F₆=8"
    elif n == 15: struct = "★ 7+8=15 (和頻!), 30/2"
    elif n == 6: struct = "6 = F₅+1"
    elif n == 14: struct = "14 = 2×7 = 2L₄"
    print(f"  {name:6s}: {t:6.2f} Gyr → n={n:2d}, T_n={Tn:6.3f} Gyr, 偏差 {dev:5.2f}%  {struct}")

# 詳細表: 每個事件的最佳 3 個模式
print(f"\n[2] 每個事件最近 3 個模式:")
for name, t in events.items():
    cands = []
    for n in range(1, 45):
        T_n = T_sync * math.sin(math.pi/88) / math.sin(math.pi*n/88)
        cands.append((abs(T_n - t)/t*100, n, T_n))
    cands.sort()
    print(f"  {name} ({t} Gyr): " + ", ".join(f"n={n} ({Tn:.2f}, {dev:.1f}%)" for dev, n, Tn in cands[:3]))

# 檢查 n=7 的意義: DM 模式
print(f"""
[3] n=7 嘅特殊意義:
    m₇ = 13.8 MeV (IDCM DM 候選, n=7 hidden W-field mode)
    γ₇ = 4sin²(7π/88) = {4*math.sin(7*math.pi/88)**2:.4f}
    T₇ = {T_sync*math.sin(math.pi/88)/math.sin(7*math.pi/88):.3f} Gyr vs LKH 12.3 → 偏差 {(T_sync*math.sin(math.pi/88)/math.sin(7*math.pi/88)-12.3)/12.3*100:.2f}%
    → LKH 合併時間 = DM 模式週期! (結構閉合?)
""")

# 事件間隔 vs 模式週期差
print(f"[4] 事件間隔 vs 模式週期差:")
pairs = [("LKH-GSE", "LKH", "GSE"), ("GSE-Sgr", "GSE", "Sgr"), ("LKH-Sgr", "LKH", "Sgr")]
for label, a, b in pairs:
    gap_obs = events[a] - events[b]
    n_a, T_a, _ = best[a]
    n_b, T_b, _ = best[b]
    gap_pred = T_a - T_b
    print(f"  {label}: 觀測 {gap_obs:.1f} vs T_{{n_a}}-T_{{n_b}} = {gap_pred:.2f} → 偏差 {abs(gap_pred-gap_obs)/gap_obs*100:.1f}%")

# 時間點作為「觀察窗相位」: t_ago/τ
print(f"\n[5] 事件時間 / τ (觀察窗分數):")
for name, t in events.items():
    print(f"  {name}: {t}/{tau:.2f} = {t/tau:.4f}")

# 嚴格評估
print(f"""
[6] 嚴格評估:
    最佳匹配偏差:
      LKH: n=7, {best['LKH'][2]:.2f}% (絕對 {best['LKH'][2]/100*12.3:.2f} Gyr)
      GSE: n=8, {best['GSE'][2]:.2f}% ({best['GSE'][2]/100*10.5:.2f} Gyr)
      Sgr: n=15, {best['Sgr'][2]:.2f}% ({best['Sgr'][2]/100*6.0:.2f} Gyr)
      t_iso: n=6, {best['t_iso'][2]:.2f}% ({best['t_iso'][2]/100*14.48:.2f} Gyr)
    年齡誤差: 相對 0.26 Gyr (CARMA), 絕對 ~1 Gyr (isochrone 系統)
    → 偏差全部 < 0.3 Gyr = 相對誤差內 ✅
    → 但 4 事件 × 44 模式 = 176 組合, 過度擬合風險?
    → 需要更多合併事件 (其他星系) 驗證
    ★ 結構: n=7 (L₄=7, DM 模式), n=8 (F₆), n=15 (7+8, 和頻)
    ★ Sgr n=15 = n₇+n₈ (LKH+GSE 嘅和頻!) — 與 O54 和頻對偶一致
""")
