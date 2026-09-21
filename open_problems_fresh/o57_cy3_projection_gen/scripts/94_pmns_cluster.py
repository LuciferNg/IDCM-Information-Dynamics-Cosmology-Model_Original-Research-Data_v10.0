#!/usr/bin/env python3
"""
O57 十九期 94: ★★ PMNS 湧現 — Q_ij 3-cluster 幾何
====================================================
目標: 由 Q_ij (185×32) 嘅 3-cluster 結構推 U_PMNS

假設:
  3 個 cluster (81/70/34) = 3 代
  cluster 中心向量 c₁, c₂, c₃ (32-dim)
  U_PMNS = cluster 中心嘅 Gram/Schmidt 矩陣

驗證:
  θ₁₂ ≈ 33.4°, θ₂₃ ≈ 49°, θ₁₃ ≈ 8.5° (NuFIT 2024)
  需要 Q_ij 重新計算 (CYTools) 或由 scripts/80 數據
"""
import sys, os, math
import json
import numpy as np

print("=" * 72)
print("O57 十九期 94: PMNS 湧現 (Q_ij 3-cluster)")
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

# ============ 1. 實驗 PMNS ============
print("\n[1] 實驗 PMNS (NuFIT 2024)")
s12, s23, s13 = 33.41, 49.1, 8.54  # degrees
print(f"  θ₁₂ = {s12}° (太陽), θ₂₃ = {s23}° (大氣), θ₁₃ = {s13}° (反應堆)")

# ============ 2. Q_ij 3-cluster ============
print("\n[2] Q_ij 3-cluster (scripts/81)")
clusters = {
    "Gen1": {"size": 81, "mean": 0.8325},
    "Gen2": {"size": 70, "mean": 0.1368},
    "Gen3": {"size": 34, "mean": -0.0748},
}
for name, info in clusters.items():
    print(f"  {name}: {info['size']} curves, mean Q = {info['mean']:.4f}")

# cluster 中心向量 (32-dim) — 需要 Q_ij 行平均
# scripts/80 有 Q_ij 但數據冇存到 center vectors
# 用 scripts/81 嘅 cluster means 近似 + 需要實際向量

# ============ 3. 關鍵: Q_ij 行空間嘅 cluster 結構 ============
print("\n[3] 混合角從幾何?")
print("""
  之前 (八期 57-58): 3-form 張量 M_gen 混合角 ~1°
    → 完全唔啱 (PMNS 係大角!)
  而家 (十九期): Q_ij 3-cluster (81/70/34)
    → cluster 大小比 = 81:70:34
    → 唔係 1:1:1 (非對稱!)
    → 非對稱 = 大混合角嘅來源?
""")

# ============ 4. cluster 大小比 同 混合角 ============
print("[4] cluster 大小比分析")
sizes = [81, 70, 34]
total = sum(sizes)
fracs = [s/total for s in sizes]
print(f"  cluster 分數: {[f'{f:.3f}' for f in fracs]}")
print(f"  最大/最小 = {81/34:.2f}")
print(f"  81/70 = {81/70:.3f}")
print(f"  70/34 = {70/34:.3f} ≈ 2.06 ≈ 2?")
check("70/34 ≈ 2", abs(70/34 - 2) < 0.1, f"({70/34:.2f} vs 2)")

# sin²θ 候選
print(f"\n  sin²θ₁₂ 候選:")
print(f"    81/185 = {81/185:.4f} (vs 0.303)")
print(f"    70/185 = {70/185:.4f} (vs 0.303)")
print(f"    34/185 = {34/185:.4f} (vs 0.303)")
print(f"  sin²θ₂₃ 候選:")
print(f"    81/134 = {81/134:.4f} (vs 0.572)")
print(f"    70/134 = {70/134:.4f} (vs 0.572)")
print(f"    34/134 = {34/134:.4f} (vs 0.572)")
print(f"  sin²θ₁₃ 候選:")
print(f"    34/185 = {34/185:.4f} (vs 0.02203)")

# ============ 5. 三角形 (tribimaximal 參考) ============
print("\n[5] Tribimaximal 參考")
print(f"  TBM: sin²θ₁₂ = 1/3 = 0.333, sin²θ₂₃ = 1/2 = 0.5, sin²θ₁₃ = 0")
print(f"  實驗: sin²θ₁₂ = 0.303, sin²θ₂₃ = 0.572, sin²θ₁₃ = 0.022")

# ============ 6. 幾何候選: 34 = 2×17 = F_proj? ============
print("\n[6] 結構識別")
print(f"  34 (Gen3) = 2×17 = 2×F_proj (O54 kernel 模式數!)")
print(f"  81 (Gen1) = 3⁴ = 9²")
print(f"  70 (Gen2) = 2×35 = 2×5×7")
print(f"  185 = 5×37")
print(f"  81+70+34 = 185 (總)")
print(f"  185 = 117 + 68 = 117 + 2×34?")
check("34 = 2×F_proj(17)", 34 == 2*17, "34 = 2×17")

# ============ 7. PMNS 角 從 cluster 比? ============
print("\n[7] PMNS 角 從 cluster 比 (嘗試)")
# tan²θ₁₂ 候選: 70/81 = 0.864 (vs 0.435), 34/81 = 0.42 (vs 0.435!)
t12_2 = 34/81
t23_2 = 81/70
t13_2 = 34/185
print(f"  tan²θ₁₂ = 34/81 = {t12_2:.4f} (實驗 0.435, 誤差 {abs(t12_2-0.435)/0.435*100:.1f}%)")
print(f"  tan²θ₂₃ = 81/70 = {t23_2:.4f} (實驗 1.337, 誤差 {abs(t23_2-1.337)/1.337*100:.1f}%)")
print(f"  sin²θ₁₃ = 34/185 = {t13_2:.4f} (實驗 0.02203, 誤差 {abs(t13_2-0.02203)/0.02203*100:.1f}%)")

# ============ 8. 總結 ============
print("\n" + "=" * 72)
print("十九期 94 總結:")
print("=" * 72)
print(f"""
  Q_ij 3-cluster → PMNS?
  ─────────────────────────────────
  Cluster: [81, 70, 34] (185 總)
  34 = 2×17 = 2×F_proj (O54 kernel 模式數!)

  候選角:
  sin²θ₁₃ = 34/185 = 0.184 (實驗 0.022) ❌
  tan²θ₁₂ = 34/81 = 0.420 (實驗 0.435) 🟡 3.4%
  tan²θ₂₃ = 81/70 = 1.157 (實驗 1.337) ❌

  → 直接比唔中
  → 需要更精細幾何 (cluster 中心向量, 唔係大小)
  → 或者 PMNS 唔係 cluster 大小, 係 cluster 內結構
""")

results = {
    "test": "O57 十九期 94: PMNS 湧現 (cluster)",
    "clusters": [81, 70, 34],
    "F_proj_relation": "34 = 2×17 = 2×F_proj",
    "t12_2_candidate": float(t12_2),
    "t23_2_candidate": float(t23_2),
    "s13_2_candidate": float(t13_2),
    "passed": passed, "failed": failed
}
with open("data/94_pmns_cluster.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十九期 94 完成!")
