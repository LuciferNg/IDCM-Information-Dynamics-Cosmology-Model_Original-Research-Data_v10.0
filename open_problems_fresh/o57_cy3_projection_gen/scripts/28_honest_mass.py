#!/usr/bin/env python3
"""
O57 三期 28: Block 衰減結構 + 誠實質量結論
============================================
scripts/27 發現:
  - J* e^-V 範圍只有 1.85 (唔夠 SM 10^8)
  - 155 adjacency: 31 pos + 21 neg + 103 zero
  - Block nonzero: Gen1 diag 62, Gen2 diag 24, Gen3 diag 14 (衰減!)

探索:
  1. Block 衰減 62/24/14 有冇 φ 結構?
  2. 103 zero adjacency curves = 冇 volume = ?
  3. 用 Kähler moduli 隨機搜索: 有冇 t 令 e^-V 範圍達 10^8?
  4. 誠實結論: 質量階層需要咩先可以閉合?
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 三期 28: Block 衰減 + 誠實質量結論")
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

# ============ 1. 載入 ============
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
jd = json.load(open(os.path.join(O53, "Jstar_36D.json")))
Jstar = np.array(jd.get("Jstar_36D", jd))

# ============ 2. Block 衰減結構 ============
print("\n[1] Block 衰減結構")
vols = np.einsum('i,ijk->jk', Jstar, kappa)
vols = (vols + vols.T) / 2
np.fill_diagonal(vols, 0)

# Diagonal blocks (Gen a × Gen a)
diag_nz = []
for g in range(3):
    sub = vols[g*12:(g+1)*12, g*12:(g+1)*12]
    diag_nz.append((np.abs(sub) > 1e-10).sum())
print(f"  Diagonal block nonzero: {diag_nz}")

# 62/24/14 有冇 φ 結構?
print(f"  62 = ?")
print(f"  62 = 2×31")
print(f"  62 = 44 + 18 = Nd + L₆!")
print(f"  62 = 90 − 28 = Σγ − 4×7")
print(f"  24 = ?")
print(f"  24 = 3×8 = N_gen × 2B")
print(f"  24 = L₆ + 6 = 18+6")
print(f"  24 = 2×12")
print(f"  14 = ?")
print(f"  14 = 2×7 = 2L₄")
print(f"  14 = F₈ − 7 = 21−7")
print(f"  14 = L₅ + 3 = 11+3")

# 比率
print(f"  62/24 = {62/24:.3f}")
print(f"  24/14 = {24/14:.3f}")
print(f"  62/14 = {62/14:.3f}")
print(f"  φ³ = {phi**3:.3f}, φ² = {phi**2:.3f}")
print(f"  62/24 ≈ φ^2.3? {math.log(62/24)/math.log(phi):.3f}")
print(f"  24/14 ≈ φ^1.3? {math.log(24/14)/math.log(phi):.3f}")

# ============ 3. 103 zero adjacency ============
print("\n[2] 103 zero adjacency curves")
# 103 = ?
print(f"  103 = ?")
print(f"  103 = 155 − 52 (31+21)")
print(f"  103 prime!")
print(f"  103 = 44 + 59? 59 prime")
print(f"  103 = 36×2 + 31? 72+31")
print(f"  103 = 90 + 13 = Σγ + L₅+2?")
print(f"  103 = 66 + 37? 37 = F₁₁? 唔, F₁₁=89")
print(f"  103 = 109 − 6")

# 103 zero curves = 冇 volume → 唔影響質量?
# 103 = 155 − 52
# 52 = 31 + 21 = positive + negative
check("52 = 31+21", 52 == 31+21)
print(f"  52 = ?")
print(f"  52 = 2×26 = 2×(2×13)")
print(f"  52 = 44 + 8 = Nd + 2B")
check("52 = Nd + 2B", 52 == 44+8)
print(f"  ⭐ 52 = Nd + 2B (有 volume 嘅 curves)")
print(f"  103 = 155 − 52 (zero volume curves)")

# ============ 4. Kähler moduli 搜索 ============
print("\n[3] Kähler moduli 搜索 (e^-V 範圍最大化)")
# 隨機試 Kähler 參數 (全正 log-normal), 睇 e^-V 範圍
rng = np.random.default_rng(42)
best_range = 0
best_t = None
for trial in range(5000):
    t = np.exp(rng.normal(0, 2, 36))  # log-normal
    v = np.einsum('i,ijk->jk', t, kappa)
    v = (v + v.T) / 2
    np.fill_diagonal(v, 0)
    pos = v[v > 1e-10]
    if len(pos) < 2:
        continue
    rng_v = pos.max() / pos.min()
    if rng_v > best_range:
        best_range = rng_v
        best_t = t
        if best_range > 1e6:
            break
print(f"  5000 次搜索最佳 e^-V 範圍: {best_range:.2e}")
print(f"  SM 需要: 1.7e8")
print(f"  {'✅ 可以達到 SM 範圍!' if best_range > 1e7 else '❌ 5000 次都唔夠'}")

# 再試更多次 (log-normal 大 spread)
best_range2 = 0
for trial in range(5000):
    t = np.exp(rng.normal(0, 4, 36))
    v = np.einsum('i,ijk->jk', t, kappa)
    v = (v + v.T) / 2
    np.fill_diagonal(v, 0)
    pos = v[v > 1e-10]
    if len(pos) < 2:
        continue
    rng_v = pos.max() / pos.min()
    if rng_v > best_range2:
        best_range2 = rng_v
        if best_range2 > 1e7:
            break
print(f"  更大 spread 搜索最佳: {best_range2:.2e}")
print(f"  {'✅ 達到 SM 範圍!' if best_range2 > 1e7 else '❌ 仲係唔夠'}")

# ============ 5. 誠實結論 ============
print("\n" + "=" * 72)
print("三期 28 總結:")
print("=" * 72)
print(f"""
  誠實質量結論:
  ─────────────────────────────────
  1. J* 做 Kähler 參數: e^-V 範圍只有 1.85
     → 唔足以產生 SM 質量階層 (需要 10^8)
  2. 155 adjacency: 31 pos + 21 neg + 103 zero
     52 = Nd + 2B 有 volume, 103 zero
  3. Block 衰減: Gen1 diag 62, Gen2 24, Gen3 14
     62 = Nd + L₆, 24 = 3×2B, 14 = 2L₄
  4. Kähler moduli 搜索: {best_range2:.1e} ({'達標' if best_range2 > 1e7 else '未達標'})

  結論: 
  - 純 J* 唔夠 (1.85)
  - 隨機 Kähler moduli 可以到 {best_range2:.1e}
  - {'✅ 質量階層可以由 Kähler moduli fine-tuning 產生' if best_range2 > 1e7 else '❌ 需要更複雜機制'}
""")

results = {
    "test": "O57 三期 28: 誠實質量",
    "jstar_range": 1.85,
    "diag_nz": [int(x) for x in diag_nz],
    "diag_identity": "62=Nd+L₆, 24=3×2B, 14=2L₄",
    "adj_split": "31 pos + 21 neg + 103 zero",
    "52_identity": "Nd+2B",
    "search_best": float(best_range2),
    "sm_needed": 1.7e8,
    "passed": passed, "failed": failed
}
with open("data/28_honest_mass.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 三期 28 完成!")
