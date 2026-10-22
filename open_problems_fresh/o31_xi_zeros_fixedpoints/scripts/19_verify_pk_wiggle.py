"""
O31 — 獨立驗證: P(k) Wiggle 8/8 匹配
=======================================
獨立重算 (不修改 scripts/09):
1. 讀取 boss_dr12_bao_wiggles.txt (82 點, 來自 o133 數據目錄)
2. 線性插值找 wiggle 零點
3. 與理論 nulls k_n = 2π(n+0.5)/λ_sync 匹配
4. 驗證 8/8 聲稱

數據來源: ../o133_pk_chain_spectrum/data/boss_dr12_bao_wiggles.txt
(只讀, 不寫入外部)
"""

import numpy as np
import os

LAMBDA_SYNC = 406.1  # h⁻¹ Mpc
N_SITES = 44
DATA_PATH = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o133_pk_chain_spectrum/data/boss_dr12_bao_wiggles.txt"

print("=" * 67)
print("  O31 — 獨立驗證: P(k) Wiggle 8/8 匹配")
print("=" * 67)

# 1. 載入數據
k_data, wiggle_data = [], []
with open(DATA_PATH) as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        parts = line.split()
        k_data.append(float(parts[0]))
        wiggle_data.append(float(parts[3]))

k = np.array(k_data)
wiggle = np.array(wiggle_data)
print(f"\n─── 1. 數據 ───")
print(f"  點數: {len(k)}")
print(f"  k 範圍: [{k[0]:.6f}, {k[-1]:.6f}] h/Mpc")

# 2. 找零點 (線性插值)
nulls_emp = []
for i in range(len(k) - 1):
    if wiggle[i] * wiggle[i+1] < 0:
        k1, k2 = k[i], k[i+1]
        w1, w2 = wiggle[i], wiggle[i+1]
        k0 = k1 - w1 * (k2 - k1) / (w2 - w1)
        nulls_emp.append(k0)
nulls_emp = np.array(nulls_emp)
print(f"\n─── 2. 實測零點 ───")
print(f"  找到 {len(nulls_emp)} 個 wiggle 零點")

# 3. 理論 nulls
nulls_theory = np.array([2 * np.pi * (n + 0.5) / LAMBDA_SYNC for n in range(1, N_SITES + 1)])
peaks_theory = np.array([2 * np.pi * n / LAMBDA_SYNC for n in range(1, N_SITES + 1)])

print(f"\n─── 3. 理論 nulls ───")
print(f"  k_n = 2π(n+0.5)/{LAMBDA_SYNC}")
print(f"  前 10 個: {np.round(nulls_theory[:10], 4)}")

# 4. 匹配: 每個理論 null 在數據範圍內, 是否有實測零點在 ±0.02 內
print(f"\n─── 4. 匹配 ───")
matched = []
for i, kn in enumerate(nulls_theory):
    if kn < k[0] - 0.005 or kn > k[-1] + 0.005:
        continue  # 超出數據範圍
    dist = np.min(np.abs(kn - nulls_emp))
    if dist < 0.02:
        idx = np.argmin(np.abs(kn - nulls_emp))
        matched.append((i+1, kn, nulls_emp[idx], dist))
        mark = "✅"
    else:
        mark = "❌"
    print(f"  n={i+1:2d}: 理論 k={kn:.5f}  最近實測={nulls_emp[np.argmin(np.abs(kn-nulls_emp))]:.5f}  差={dist:.5f} {mark}")

n_theory_in_range = sum(1 for kn in nulls_theory if k[0] - 0.005 <= kn <= k[-1] + 0.005)
print(f"\n─── 5. 結果 ───")
print(f"  理論 nulls 在數據範圍內: {n_theory_in_range}")
print(f"  成功匹配: {len(matched)}/{n_theory_in_range}")
if matched:
    print(f"  平均偏差: {np.mean([m[3] for m in matched])*1000:.2f} × 10⁻³ h/Mpc")

# 6. 結論
print(f"\n{'═'*67}")
if len(matched) >= 8:
    print(f"  ✅ 驗證通過: {len(matched)} 個理論 nulls 匹配 (聲稱 8/8)")
else:
    print(f"  ❌ 驗證失敗: 只有 {len(matched)} 個匹配 (聲稱 8/8)")
print(f"{'═'*67}")