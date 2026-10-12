#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""O247 Q2 攻堅 06 — μ-ladder 對數過渡檢定 (判據預註冊)

調律者 2026-10-12: 「連續過渡公式應該在k-tree找」。
K_Tree 兩個譜 (O155/O157): λ_k (Dirichlet, 已測 scripts/04/05) + μ_m = φ^(291.5−m)
  — μ 係「離散→連續」自然階梯: log_φ(μ_m) = 291.5−m 整數等差 (metric 層)

本 script 檢定最後一個過渡載體: 「原子層量 x 嘅 μ-ladder 對數值 log_φ(x/M₀)
係咪命中整數/半整數 (291.5−m 家族)」— 即 x = M₀·φ^k 形式。

判據 (預註冊, 凍結):
  G1: 對 8 個原子層量計 k = log_φ(x/M₀); 命中 δ<0.05 窗口內整數/半整數 = PASS
      但必須過 MC null: 隨機 x (log-uniform) 命中概率 < 5%
  G2: 三點檢定: 過閘候選 (若有) 必須喺 ≥2 兄弟量命中先信
  G3: 負結果 = 「原子層唔係 M₀·φ^k 家族」禁區 (唔准再用 μ-ladder 砌原子質量)

觀測: M₀=27.900915; m_p/m_n/m_H/amu/m_He4/E_bind 同 scripts/04
"""
import math
import numpy as np

PHI = (1 + math.sqrt(5)) / 2
DELTA = 0.05
M0 = 27.900915
mp, mn = 938.27208816, 939.5654205
me = 0.51099895
amu = 931.49410242
mH = 938.7830745
mHe4 = 3727.3794066
Eb_He4 = 28.2957
Eb_Fe56_A = 8.7903
Eb_D2_A = 1.1123

obs = {
    "m_p":     mp,
    "m_n":     mn,
    "m_H":     mH,
    "amu":     amu,
    "m_He4":   mHe4,
    "E_bind(He4)":  Eb_He4,
    "E_bind(Fe56)/A": Eb_Fe56_A,
    "E_bind(D2)/A":  Eb_D2_A,
}

def k_of(x):
    return math.log(x / M0) / math.log(PHI)

def near_half_int(k, tol=DELTA):
    r = round(2 * k) / 2.0
    return abs(k - r) < tol, r

print("=" * 78)
print("G1  μ-ladder 對數過渡: k = log_φ(x/M₀) 對 整數/半整數 (窗=±%.0f%%)" % (DELTA * 100))
print("=" * 78)
res = []
for name, x in obs.items():
    k = k_of(x)
    hit, r = near_half_int(k)
    tag = "✔ 命中" if hit else "✗"
    print("%-16s x=%10.4f  k=%9.5f  最近半整數=%8.4f  偏移=%6.3f  %s" % (
        name, x, k, r, abs(k - r), tag))
    res.append((name, k, abs(k - r) < DELTA))

# MC null: 隨機 x ∈ [0.5, 5000] log-uniform, 命中最近半整數概率
rng = np.random.default_rng(20261012)
N = 100000
null_r = np.exp(rng.uniform(math.log(0.5), math.log(5000.0), size=N))
null_k = np.log(null_r / M0) / np.log(PHI)
null_off = np.abs(null_k - np.round(2 * null_k) / 2.0)
p_null = float(np.mean(null_off < DELTA))
n_hit = sum(1 for _, _, h in res if h)
p_hit = n_hit / len(res)
print()
print("MC null (N=%d): 隨機量命中半整數概率 = %.4f" % (N, p_null))
print("實際命中: %d/%d (%.4f)" % (n_hit, len(res), p_hit))
z = (p_hit - p_null) / math.sqrt(p_null * (1 - p_null) / len(res))
print("z = %.2f ⟹ %s" % (z, "PASS" if n_hit >= 3 and p_hit > 5 * p_null and z >= 3 else "FAIL"))

print()
print("=" * 78)
print("G2  三點檢定 (過閘候選先做; 否則跳)")
print("=" * 78)
if n_hit >= 3:
    for name, k, h in res:
        if h:
            r = round(2 * k) / 2.0
            print("  %-16s k=%.5f ≈ %s (φ^%.2f×M₀ = %.3f MeV)" % (name, k, r, r, PHI ** r * M0))
else:
    print("  冇過閘候選 — 跳過")

print()
print("=" * 78)
print("G3  判決記錄")
print("=" * 78)
if n_hit >= 3 and p_hit > 5 * p_null and z >= 3:
    print("  原子層量 ∈ M₀·φ^k 家族成立 — 但需三點檢定 + 樣本外盲測先升正式候選")
else:
    print("  負結果: 原子層量唔係 M₀·φ^k 家族")
    print("  禁區: 唔准再用 μ-ladder (φ 冪) 砌 原子質量/結合能 —— 已檢定, MC null 過唔到")
    print("  過渡公式載體: λ_k 譜 (04/05 已滅) + μ-ladder (本 script) ⟹ K_Tree 譜域無原子層")
    print("  唯一閉合: Rydberg α²m_e/2 (scripts/03, dev 1e-8) — 原子層離散骨架 = 能階, 唔係質量")