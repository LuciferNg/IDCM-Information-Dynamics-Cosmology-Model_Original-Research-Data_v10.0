#!/usr/bin/env python3
"""
O57 三期 26: 真 Curve Volumes + e^{-V} 質量譜
===============================================
用 O53 已有嘅 cy36_98_intersection_full.json (36³ κ_ijk):

  1. 載入真 κ_ijk
  2. 用全正 Kähler 參數 (t_i = 1) 計 curve volumes
  3. 對比 155 adjacency curves
  4. e^{-V} 質量譜 vs SM
  5. 檢查 J* 係咪有效 Kähler 參數

物理: m_f ∝ e^{-V_cycle}, V_cycle = ∫_C J = Σ t_i κ_ijk
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 三期 26: 真 Curve Volumes + e^-V")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 載入真 κ_ijk ============
print("\n[1] 載入真 κ_ijk (36³)")
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
print(f"  κ shape: {kappa.shape}")
print(f"  κ 非零: {np.count_nonzero(kappa)}")
print(f"  κ min: {kappa.min()}, max: {kappa.max()}")

# 對稱性
sym = np.allclose(kappa, kappa.transpose(1, 0, 2)) and np.allclose(kappa, kappa.transpose(2, 1, 0))
check("κ_ijk 全對稱", sym)
check("κ 非零 = 1341", np.count_nonzero(kappa) == 1341, f"({np.count_nonzero(kappa)})")

# ============ 2. Curve volumes (t_i = 1) ============
print("\n[2] Curve volumes (t_i = 1)")
# curve C_jk = D_j·D_k, volume = Σ_i t_i κ_ijk
# 用 t_i = 1 (全正, 喺 Kähler cone)
t = np.ones(36)
vols = np.einsum('i,ijk->jk', t, kappa)  # 36×36
vols = (vols + vols.T) / 2
np.fill_diagonal(vols, 0)

n_pos = (vols > 1e-8).sum()
n_neg = (vols < -1e-8).sum()
n_zero = (np.abs(vols) < 1e-8).sum()
print(f"  Positive curves: {n_pos}")
print(f"  Negative curves: {n_neg}")
print(f"  Zero curves: {n_zero}")
print(f"  Volume range: [{vols.min():.3f}, {vols.max():.3f}]")

# 155 個 adjacency curves 有幾多 positive?
# 155 adjacency = sr_ideal complement (from scripts/11)
sr = d2 = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))["sr_ideal"]
sr_set = set()
for s in sr:
    sr_set.add((min(s), max(s)))
adj = []
for i in range(1, 37):
    for j in range(i+1, 37):
        if (i, j) not in sr_set:
            adj.append((i, j))
print(f"  Adjacency pairs: {len(adj)}")

# 155 adjacency 對應嘅 curve volumes
adj_vols = [vols[i-1, j-1] for i, j in adj]
adj_pos = sum(1 for v in adj_vols if v > 1e-8)
adj_neg = sum(1 for v in adj_vols if v < -1e-8)
print(f"  Adjacency curves positive: {adj_pos}, negative: {adj_neg}")

# ============ 3. 用 J* ============
print("\n[3] J* 做 Kähler 參數")
jd = json.load(open(os.path.join(O53, "Jstar_36D.json")))
Jstar = np.array(jd.get("Jstar_36D", jd))
print(f"  Jstar: {Jstar.shape}, min={Jstar.min():.4f}, max={Jstar.max():.4f}")

# 檢查 J* 正負
print(f"  J* positive entries: {(Jstar > 0).sum()}/36")
print(f"  J* negative entries: {(Jstar < 0).sum()}/36")

# J* 計 volumes
vols_j = np.einsum('i,ijk->jk', Jstar, kappa)
vols_j = (vols_j + vols_j.T) / 2
np.fill_diagonal(vols_j, 0)
adj_vols_j = [vols_j[i-1, j-1] for i, j in adj]
adj_pos_j = sum(1 for v in adj_vols_j if v > 1e-10)
adj_neg_j = sum(1 for v in adj_vols_j if v < -1e-10)
print(f"  J* adjacency curves positive: {adj_pos_j}, negative: {adj_neg_j}")
check("J* 全正 (有效 Kähler)", (Jstar > 0).all(), f"({(Jstar > 0).sum()}/36)")

# ============ 4. e^{-V} 質量譜 ============
print("\n[4] e^-V 質量譜 (t_i = 1)")
# 用 positive curve volumes 做質量
pos_vols = vols[vols > 1e-8]
print(f"  Positive volumes: {len(pos_vols)}")
if len(pos_vols) > 0:
    masses = np.exp(-pos_vols)
    print(f"  e^-V: min={masses.min():.4e}, max={masses.max():.4f}")
    print(f"  e^-V 範圍比: {masses.max()/masses.min():.1e}")
    # 同 SM 比 (15 粒子, 10^8 範圍)
    print(f"  SM 質量比: m_t/m_ν ≈ 10^8")
    print(f"  需要 e^-V 範圍: {1.7e5/1e-3:.1e}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("三期 26 總結:")
print("=" * 72)

results = {
    "test": "O57 三期 26: Curve Volumes",
    "kappa_nonzero": int(np.count_nonzero(kappa)),
    "t1_positive_curves": int(n_pos),
    "adj_positive": int(adj_pos),
    "adj_negative": int(adj_neg),
    "jstar_all_positive": bool((Jstar > 0).all()),
    "passed": passed, "failed": failed
}
with open("data/26_curve_volumes.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 三期 26 完成!")
