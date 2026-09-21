#!/usr/bin/env python3
"""
O57 四期 32: 質量譜質量指標 — 誠實評估 φ Kähler 參數
=====================================================
四期 31 教訓: 候選 B range 2.65e8 但 166 個 curves 中只有 6 個有質量
→ range 大 ≠ 質量譜好!

正確指標:
  1. 有質量 curves 數 (m > 1e-30, 唔 underflow)
  2. 質量譜寬度 (log 範圍, 排除 underflow)
  3. 有幾多個「合理」質量 (0.01~1 之間)
  4. 質量譜同 SM 15 粒子嘅匹配
  5. 3 代結構 (3 個 cluster?)

物理: 真正嘅 Kähler 參數應該產生
      - 唔係全部 curve 有質量 (有啲係 zero-volume)
      - 有質量嘅 curve 數量合理 (~15-52?)
      - 質量譜連續覆蓋 10^8 範圍
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 四期 32: 質量譜質量指標")
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

kappa = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])

def mass_spectrum(t):
    """完整質量譜分析"""
    v = np.einsum('i,ijk->jk', t, kappa)
    v = (v + v.T) / 2
    np.fill_diagonal(v, 0)
    pos = v[v > 1e-10]
    masses = np.exp(-pos)
    # 唔 underflow 嘅 (m > 1e-30)
    finite = masses[masses > 1e-30]
    return {
        "n_pos": len(pos),
        "n_finite": len(finite),
        "range": pos.max()/pos.min() if len(pos) > 1 else 1,
        "finite_range": finite.max()/finite.min() if len(finite) > 1 else 1,
        "finite_masses": np.sort(finite)[::-1],
        "n_zero": len(masses) - len(finite),
    }

def quality_score(ms):
    """質量譜質量: 加權分數"""
    # 1. 有質量數 (目標 ~15-30)
    n = ms["n_finite"]
    score = 0
    if 10 <= n <= 60:
        score += 2
    elif n >= 5:
        score += 1
    # 2. 質量範圍 (目標 10^5-10^8)
    r = ms["finite_range"] if ms["n_finite"] > 1 else 1
    if 1e5 <= r <= 1e10:
        score += 2
    elif 1e3 <= r < 1e5:
        score += 1
    # 3. 唔太多 underflow (零質量唔應該超過一半)
    if ms["n_zero"] <= ms["n_pos"] * 0.5:
        score += 2
    elif ms["n_zero"] <= ms["n_pos"] * 0.8:
        score += 1
    return score

# ============ 1. 全部候選 ============
print("\n[1] 候選質量譜分析")
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199]
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

candidates = {}
# φ 冪
candidates["A: φ^(i-1)"] = phi ** np.arange(36)
candidates["B: φ^(35-i)"] = phi ** (35 - np.arange(36))
candidates["C: φ^(i mod 12)"] = phi ** (np.arange(36) % 12)
candidates["D: 3×12 代遞增"] = phi ** ((np.arange(36) % 12) + 12 * (np.arange(36) // 12))
# Lucas
candidates["F: L mod 12"] = np.array([L[i % 12] for i in range(36)])
candidates["G: F mod 12"] = np.array([F[(i % 12) + 1] if (i % 12) + 1 < 12 else F[11] for i in range(36)])
# J*
jd = json.load(open(os.path.join(O53, "Jstar_36D.json")))
Jstar = np.array(jd.get("Jstar_36D", jd))
candidates["J*"] = Jstar

scores = {}
for name, t in candidates.items():
    ms = mass_spectrum(t)
    s = quality_score(ms)
    scores[name] = s
    print(f"  {name}: n_pos={ms['n_pos']:3d}, n_finite={ms['n_finite']:3d}, "
          f"range={ms['range']:.2e}, finite_range={ms['finite_range']:.2e}, "
          f"zero={ms['n_zero']:3d} → score={s}")

# ============ 2. 最佳候選嘅質量譜 ============
print("\n[2] 最佳候選質量譜")
best = max(scores, key=scores.get)
print(f"  最佳: {best} (score={scores[best]})")
ms = mass_spectrum(candidates[best])
print(f"  有限質量數: {ms['n_finite']}")
if ms["n_finite"] > 0:
    print(f"  質量譜:")
    for i, m in enumerate(ms["finite_masses"][:20]):
        print(f"    m{i+1:2d}: {m:.4e}")

# ============ 3. 對比 SM ============
print("\n[3] 對比 SM")
sm_masses = np.array([0.001, 0.511, 2.16, 4.67, 93.4, 105.66, 1270, 1776.86,
                      4180, 80377, 91187.6, 125250, 172760])
print(f"  SM: {len(sm_masses)} 粒子, range {sm_masses.max()/sm_masses.min():.1e}")

if ms["n_finite"] > 0:
    fm = ms["finite_masses"]
    print(f"  Best 候選有限質量數: {len(fm)} (SM 需要 ~15)")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("四期 32 總結:")
print("=" * 72)
print(f"""
  質量譜質量指標 (誠實):
  ─────────────────────────────────
  1. 候選 B (φ^(35-i)) range 大但 160 個 underflow → 假達標
  2. 正確指標: n_finite + range + zero 比例
  3. 分數:
{chr(10).join(f'     {k}: {v}' for k, v in sorted(scores.items(), key=lambda x: -x[1]))}
  4. 最佳: {best} (score={scores[best]}/6)

  {'✅ 有合格候選' if max(scores.values()) >= 4 else '❌ 冇合格候選 — 質量階層仍需開放'}
""")

results = {
    "test": "O57 四期 32: 質量譜指標",
    "scores": scores,
    "best": best,
    "best_score": int(scores[best]),
    "sm_count": len(sm_masses),
    "passed": passed, "failed": failed
}
with open("data/32_mass_quality.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 四期 32 完成!")
