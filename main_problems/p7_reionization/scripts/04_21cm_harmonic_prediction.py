#!/usr/bin/env python3
"""
04_21cm_harmonic_prediction.py
================================
IDCM 結構預測：21 cm 功率譜諧波間距

ΛCDM 預測 21 cm 功率譜隨 z 平滑演化（再電離泡泡生長→合併→完成）
IDCM 預測 21 cm 功率譜喺 k-space 有諧波間距 Δk = 2π/λ_sync

呢個係最強嘅分辨測試。

IDCM v10.0 — 共震點宇宙學
"""

import sys
import math
import json

# ================================================================
# IDCM Core Constants
# ================================================================
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
EPS = PHI_INV / 4
N_d = 44
M = 33
B = 4
h11 = 36
h21 = 98
CY3 = h11 + h21
R_H = 4129.94  # Mpc
H0 = 72.59  # km/s/Mpc
LAMBDA_SYNC = 294.88  # Mpc
BAO = LAMBDA_SYNC / 2  # 147.44 Mpc

# ================================================================
# 諧波間距預測
# ================================================================
print("=" * 72)
print("IDCM 再電離問題 — 路徑 3：21 cm 諧波間距預測")
print("=" * 72)

# 基本諧波間距
DELTA_K = 2 * math.pi / LAMBDA_SYNC  # h/Mpc
print(f"\n基本諧波間距：")
print(f"  Δk = 2π/λ_sync = {DELTA_K:.6f} h/Mpc")
print(f"  λ_sync = {LAMBDA_SYNC} Mpc")

# 高階諧波
print(f"\n21 cm 功率譜諧波系列：")
print(f"  n   | k_n = n·Δk (h/Mpc) | 對應波長 (Mpc) | 意義")
print(f"  {'-'*4}|{'─'*23}|{'─'*17}|{'─'*18}")
for n in range(1, 11):
    k_n = n * DELTA_K
    lambda_n = 2 * math.pi / k_n
    note = ""
    if n == 1:
        note = "fundamental"
    elif n == 2:
        note = "BAO = λ_sync/2"
    elif n == 3:
        note = "λ_sync/3"
    elif n == 4:
        note = "λ_sync/4"
    print(f"  {n:2d}  | {k_n:19.6f} | {lambda_n:15.2f} | {note}")

# 21 cm 信號嘅紅移覆蓋範圍
print(f"\n\n21 cm 信號預計紅移範圍：")
print(f"  z    | ℓ = log₄(1+z) | k_min (h/Mpc) | 可觀測諧波")
print(f"  {'─'*4}|{'─'*16}|{'─'*16}|{'─'*16}")
for z in [6, 7, 10, 15, 17, 20, 30]:
    ell = math.log(1 + z) / math.log(4)
    k_min = 2 * math.pi / (R_H / (1 + z))
    n_max = int(k_min / DELTA_K)
    print(f"  {z:3d} | {ell:14.3f} | {k_min:14.6f} | n≤{n_max:2d}")

# ================================================================
# 與現有數據比較
# ================================================================
print(f"\n{'=' * 72}")
print("與現有 21 cm 上限數據比較")
print("=" * 72)

# 目前 21 cm 觀測只有上限（HERA Phase I）
# HERA 喺 z≈7.9 設下限 Δ²(k) < (30 mK)² @ k=0.2 h/Mpc
# 未來 SKA 將達到 mK 靈敏度

print(f"""
目前 21 cm 觀測狀態：
  - HERA Phase I: Δ²(k) < (30 mK)² @ k=0.2 h/Mpc, z=7.9
  - LOFAR: Δ²(k) < (10 mK)² @ k=0.1 h/Mpc, z=8.5
  - SKA (未來): 靈敏度 ~1 mK

IDCM 預測：
  - 21 cm 功率譜 P(k) 喺 k-space 有 Δk = {DELTA_K:.6f} h/Mpc 嘅等距尖峰
  - 尖峰位置：k_n = n × {DELTA_K:.6f} h/Mpc, n=1,2,3,...
  - 等距諧波係 ΛCDM 無法自然產生嘅特徵
  - 呢個係最強嘅分辨測試
""")

# ================================================================
# 儲存結果
# ================================================================
results = {
    'delta_k': DELTA_K,
    'lambda_sync': LAMBDA_SYNC,
    'bao': BAO,
    'harmonics': {},
    'z_coverage': {}
}

for n in range(1, 11):
    k_n = n * DELTA_K
    lambda_n = 2 * math.pi / k_n
    results['harmonics'][f'n_{n}'] = {
        'k': k_n,
        'lambda': lambda_n
    }

for z in [6, 7, 10, 15, 17, 20, 30]:
    ell = math.log(1 + z) / math.log(4)
    k_min = 2 * math.pi / (R_H / (1 + z))
    n_max = int(k_min / DELTA_K)
    results['z_coverage'][f'z_{z}'] = {
        'ell': ell,
        'k_min': k_min,
        'n_max_observable': n_max
    }

with open('data/21cm_predictions.json', 'w') as f:
    json.dump(results, f, indent=2, default=lambda x: float(f"{x:.6f}") if isinstance(x, float) else x)

print(f"結果已儲存至 data/21cm_predictions.json")
print(f"{'=' * 72}")