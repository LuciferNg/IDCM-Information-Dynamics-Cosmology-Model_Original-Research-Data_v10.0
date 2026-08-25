#!/usr/bin/env python3
"""
19_bimodal_gradient.py — P9 可證偽預測: 溫度梯度雙峰分佈
==========================================================
Gemini P9 預測:
1. 正常邊 (88 條, 冷-熱): |ΔT| 大 → 高梯度峰
2. 阻挫邊 (32 條, 冷-冷/熱-熱): |ΔT| 小 → 低梯度峰
→ 120 條邊嘅 |ΔT| 直方圖應該雙峰 (bimodal)

IDCM 節點溫度模型:
- 節點 i 溫度 = σ_i × A (σ_i = 錨定著色 ±1, A = 5ε⁵/8 × T_cmb)
- 但實際 CMB 有起伏 → 節點溫度 = σ_i × A + 背景噪聲 η

計算:
- 正常邊: |ΔT| ≈ 2A ≈ 2 × 5.5e-5 × 2.725 = 300 μK
- 阻挫邊: |ΔT| ≈ 0 (同色) ± 噪聲

對比 ΛCDM: 高斯隨機場 → 無網絡結構雙峰
"""
import numpy as np
import math
from collections import defaultdict, deque

# ============ 載入節點 + 建圖 ============
nodes = []
with open("data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))

vecs = []
for ra, dec in nodes:
    r, d = math.radians(ra), math.radians(dec)
    vecs.append(np.array([math.cos(d)*math.cos(r),
                          math.cos(d)*math.sin(r),
                          math.sin(d)]))
vecs = np.array(vecs)

THRESHOLD = 28.0
adj = defaultdict(set)
edges_list = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < THRESHOLD:
            adj[i].add(j)
            adj[j].add(i)
            edges_list.append((i, j))

# ============ 錨定著色 ============
color = {}
color[0] = 1
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in color:
            color[w] = 1 - color[u]
            q.append(w)

# 阻挫邊
frustration = set()
for u, v in edges_list:
    if color[u] == color[v]:
        frustration.add((u, v))

normal = [(u, v) for u, v in edges_list if (u, v) not in frustration]

# ============ IDCM 參數 ============
phi = (1 + 5**0.5) / 2
eps = (1/phi) / 4
T_cmb = 2.72548  # K
RMS = eps**5 / 8
A_node = 5 * RMS  # 節點振幅 = 5ε⁵/8
print("=" * 66)
print("P9 預測: 溫度梯度雙峰分佈")
print("=" * 66)
print(f"RMS = ε⁵/8 = {RMS:.6e}")
print(f"節點振幅 A = 5ε⁵/8 = {A_node:.6e}")
print(f"邊: 正常 {len(normal)} (冷-熱), 阻挫 {len(frustration)} (同色)")
print(f"比例: 阻挫 = {100*len(frustration)/len(edges_list):.1f}%")

# ============ 模擬 CMB 節點溫度 ============
# 背景噪聲 (ΛCDM 式高斯場喺節點位置) — 標準差 = RMS
rng = np.random.default_rng(42)
noise_sigma = RMS * T_cmb  # 溫度單位 μK? 用 K

# 模型 A: IDCM 純結構 (無噪聲)
T_idcm = np.array([(1 if color[i] == 1 else -1) * A_node * T_cmb for i in range(60)])

# 模型 B: IDCM + 噪聲 (信噪比 5:1)
SNR = 5
noise = rng.normal(0, A_node * T_cmb / SNR, 60)
T_mixed = T_idcm + noise

# 模型 C: 純 ΛCDM 高斯 (無結構)
T_lcdm = rng.normal(0, RMS * T_cmb, 60)

def edge_dT(T):
    """每條邊嘅 |ΔT|"""
    return np.array([abs(T[u] - T[v]) for u, v in edges_list])

dT_idcm = edge_dT(T_idcm)
dT_mixed = edge_dT(T_mixed)
dT_lcdm = edge_dT(T_lcdm)

# ============ 雙峰分析 ============
def bimodality(dT, label):
    """雙峰檢測: 正常邊 vs 阻挫邊嘅 |ΔT|"""
    dT_fr = np.array([abs(T_mixed[u] - T_mixed[v]) if False else 0 for u, v in []])  # placeholder
    fr_vals = []
    norm_vals = []
    # 用傳入嘅 dT 同 frustration
    for i, (u, v) in enumerate(edges_list):
        if (u, v) in frustration:
            fr_vals.append(dT[i])
        else:
            norm_vals.append(dT[i])
    fr_vals = np.array(fr_vals)
    norm_vals = np.array(norm_vals)
    sep = (norm_vals.mean() - fr_vals.mean()) / (fr_vals.std() + 1e-12)
    print(f"\n{label}:")
    print(f"  阻挫邊 |ΔT|: mean = {fr_vals.mean():.2e} K")
    print(f"  正常邊 |ΔT|: mean = {norm_vals.mean():.2e} K")
    print(f"  分離度 (separation): {sep:.2f}σ")
    if sep > 3:
        print(f"  ✅ 明顯雙峰 (分離 > 3σ)")
    else:
        print(f"  ⚠️ 分離不足")
    return sep

sep_idcm = bimodality(dT_idcm, "IDCM 純結構")
sep_mixed = bimodality(dT_mixed, "IDCM + 噪聲 (SNR=5)")
sep_lcdm = bimodality(dT_lcdm, "純 ΛCDM 高斯")

print(f"\n" + "=" * 66)
print(f"判定:")
print(f"  IDCM 純結構分離度: {sep_idcm:.2f}σ")
print(f"  IDCM+噪聲分離度:   {sep_mixed:.2f}σ")
print(f"  ΛCDM 高斯分離度:   {sep_lcdm:.2f}σ")
print(f"  → 如果 sep_IDCM >> sep_ΛCDM, 雙峰係 IDCM 獨特預測")

# ============ 直方圖數據 (儲存) ============
with open("data/bimodal_gradient.txt", "w") as f:
    f.write("# edge_type dT_idcm dT_mixed dT_lcdm\n")
    for i, (u, v) in enumerate(edges_list):
        ft = 'F' if (u, v) in frustration else 'N'
        f.write(f"{ft} {dT_idcm[i]:.6e} {dT_mixed[i]:.6e} {dT_lcdm[i]:.6e}\n")
print(f"\n✅ 雙峰數據已存: data/bimodal_gradient.txt")
