#!/usr/bin/env python3
"""
O57 八期 58: 3 代 × 3 組質量結構 — 修正 χ²
=============================================
八期 56 教訓: 單一 e^{-V} 階梯 fit 唔到 9 個費米子 (χ²/dof=2.2e6)

原因: 質量譜有「3 代 × 3 組 (u-type/d-type/lepton)」結構
  u,d,s,c,b,t: 夸克 (6 個)
  e,μ,τ: 輕子 (3 個)

新模型: 每組有自己嘅基線 + 共用 Lucas 能階?
  或者: 用 3×3 世代矩陣 (八期 57) 嘅本徵值?

測試:
  1. 用 3×3 M_gen 本徵值 (正) 做 3 個「世代基線」
  2. 每個世代有 3 個粒子 (u-type, d-type, lepton)
  3. 質量 = 世代基線 × 組權重
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 八期 58: 3 代 × 3 組結構")
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

# ============ 1. SM 質量 ============
print("\n[1] SM 質量 (3 代 × 3 組)")
# 3 代 × 3 組: (u-type, d-type, lepton)
sm = {
    "u": 2.16, "c": 1270, "t": 172760,       # u-type (up)
    "d": 4.67, "s": 93.4, "b": 4180,          # d-type (down)
    "e": 0.511, "μ": 105.66, "τ": 1776.86     # lepton
}
# 每組: 3 代質量
groups = {
    "u-type": [2.16, 1270, 172760],
    "d-type": [4.67, 93.4, 4180],
    "lepton": [0.511, 105.66, 1776.86]
}
print(f"  u-type: {groups['u-type']}")
print(f"  d-type: {groups['d-type']}")
print(f"  lepton: {groups['lepton']}")

# 每組內部比
for name, g in groups.items():
    g_sorted = np.sort(g)
    print(f"\n  {name} 質量比:")
    print(f"    gen2/gen1 = {g_sorted[1]/g_sorted[0]:.1f}")
    print(f"    gen3/gen2 = {g_sorted[2]/g_sorted[1]:.1f}")
    print(f"    gen3/gen1 = {g_sorted[2]/g_sorted[0]:.1f}")

# ============ 2. Lucas 階梯對比 ============
print("\n[2] Lucas 能階間距")
V = [1.0, 9.47213595, 22.18033989, 24.79837388, 40.1246118]
gaps = np.diff(V)
print(f"  V: {V}")
print(f"  間距: {gaps}")
print(f"  e^間距: {np.exp(gaps)}")
print(f"  (gen 比? u: gen3/gen1 = 8e4, d: 895, lepton: 3478)")

# ============ 3. 每組 fit ============
print("\n[3] 每組獨立 fit (2 個間距 × 1 基線)")
# 每組 3 個質量: m_i = M₀·e^{-a·i}? 定係 3 個能階?
# 用 3 個能階差: Δ12, Δ23
for name, g in groups.items():
    g_sorted = np.sort(g)
    ln_g = np.log(g_sorted)
    # fit: ln m = ln M₀ + slope·i (i=0,1,2)
    x = np.array([0, 1, 2])
    slope, intercept = np.polyfit(x, ln_g, 1)
    pred = np.exp(intercept + slope * x)
    resid = np.sum((ln_g - (intercept + slope*x))**2)
    print(f"\n  {name}:")
    print(f"    ln M₀ = {intercept:.4f}, slope = {slope:.4f}")
    print(f"    e^slope = {math.exp(slope):.2f} (每代倍數)")
    print(f"    pred: {pred}")
    print(f"    resid: {resid:.4f}")
    print(f"    resid²/ln: {resid/3:.4f}")

# ============ 4. 對比 Lucas 間距 ============
print("\n[4] Lucas 間距 vs SM 世代比")
print(f"  Lucas 間距 e^Δ:")
for i, d in enumerate(gaps):
    print(f"    e^{d:.2f} = {math.exp(d):.2e}")
print(f"\n  SM 世代比:")
for name, g in groups.items():
    g_sorted = np.sort(g)
    print(f"    {name}: gen3/gen1 = {g_sorted[2]/g_sorted[0]:.2e}")

# 最接近匹配
print(f"\n  最接近匹配 (Lucas 比 vs SM 比):")
lucas_ratios = [(i+1, j+1, math.exp(V[j]-V[i])) for i in range(5) for j in range(i+1, 5)]
sm_ratios = []
for name, g in groups.items():
    gs = np.sort(g)
    sm_ratios.append((f"{name} gen3/gen1", gs[2]/gs[0]))
    sm_ratios.append((f"{name} gen2/gen1", gs[1]/gs[0]))
    sm_ratios.append((f"{name} gen3/gen2", gs[2]/gs[1]))

best = []
for li, lj, lr in lucas_ratios:
    for sname, sr in sm_ratios:
        d = abs(math.log(lr) - math.log(sr))
        best.append((d, f"V{li+1}-V{lj+1}", sname, lr, sr))
best.sort()
print(f"  {'Lucas 比':>12s} {'SM 比':>18s} {'Δln':>8s} {'Lucas':>10s} {'SM':>10s}")
for d, lname, sname, lr, sr in best[:8]:
    print(f"  {lname:>12s} {sname:>18s} {d:8.3f} {lr:10.2e} {sr:10.2e}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("八期 58 總結:")
print("=" * 72)
print(f"""
  3 代 × 3 組結構:
  ─────────────────────────────────
  1. 每組世代比: 睇上面
  2. Lucas 間距 vs SM: 睇上面
  3. 最佳匹配: {best[0] if best else 'NA'}

  {'✅ 有結構匹配!' if best and best[0][0] < 0.5 else '❌ 未有強匹配'}
""")

results = {
    "test": "O57 八期 58: 3×3 結構",
    "best_match": [best[0][1], best[0][2], float(best[0][0])] if best else None,
    "passed": passed, "failed": failed
}
with open("data/58_3x3_structure.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 八期 58 完成!")
