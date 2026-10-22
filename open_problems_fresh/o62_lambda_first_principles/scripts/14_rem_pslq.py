#!/usr/bin/env python3
"""
O62 五期 14: rem 高精度 PSLQ 搜索
==================================
rem = F(γ) − 264 = 0.082129232580257

線索: 1/12.176 = 0.0821288 (0.0006%)
  → rem ≈ 1/12.176
  → 12.176 = ?

策略:
  1. mpmath PSLQ: rem = Σ c_i γ_i, c_i 細整數
  2. 1/rem 嘅結構身份
  3. rem × N 有冇整數結構
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O62 五期 14: rem PSLQ 高精度")
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

try:
    import mpmath as mp
    mp.mp.dps = 50
    HAS_MP = True
    print(f"  mpmath {mp.__version__} (dps=50)")
except ImportError:
    HAS_MP = False
    print("  ⚠️ 冇 mpmath — 用 float")

# ============ 1. 高精度 rem ============
print("\n[1] 高精度 rem")
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])  # 整數, 精確
if HAS_MP:
    # 高精度重算 F(γ)
    gamma36_mp = [4*mp.sin(mp.pi*i/88)**2 for i in range(1, 37)]
    F_mp = mp.mpf(0)
    for i in range(36):
        for j in range(36):
            for k in range(36):
                kk = int(kappa[i,j,k])
                if kk != 0:
                    F_mp += kk * gamma36_mp[i]*gamma36_mp[j]*gamma36_mp[k]
    F_mp /= 6
    rem_mp = F_mp - 264
    print(f"  F(γ) 高精度 = {mp.nstr(F_mp, 40)}")
    print(f"  rem 高精度 = {mp.nstr(rem_mp, 40)}")
else:
    gamma36 = 4*np.sin(np.pi*np.arange(1,37)/88)**2
    F_mp = np.einsum("ijk,i,j,k", kappa, gamma36, gamma36, gamma36)/6.0
    rem_mp = F_mp - 264

# ============ 2. 1/rem ============
print("\n[2] 1/rem 結構")
inv_rem = 1.0/rem_mp if not HAS_MP else mp.mpf(1)/rem_mp
print(f"  1/rem = {mp.nstr(inv_rem, 20) if HAS_MP else f'{inv_rem:.15f}'}")
inv_f = float(inv_rem)
print(f"  12.176? {inv_f:.8f}")
print(f"  inv_rem − 12 = {inv_f - 12:.10f}")
print(f"  inv_rem − 12.18 = {inv_f - 12.18:.10f}")
print(f"  inv_rem × 44 = {inv_f*44:.6f}")
print(f"  inv_rem × 88 = {inv_f*88:.6f}")
print(f"  inv_rem × 90 = {inv_f*90:.6f}")
print(f"  inv_rem × 36 = {inv_f*36:.6f}")
print(f"  inv_rem × 134 = {inv_f*134:.6f}")
print(f"  inv_rem × 946 = {inv_f*946:.6f}")

# 12.1759 ≈ ?
print(f"\n  12.1759 分解:")
print(f"  44/12.1759 = {44/inv_f:.6f}")
print(f"  90/12.1759 = {90/inv_f:.6f}")
print(f"  134/12.1759 = {134/inv_f:.6f}")
print(f"  946/12.1759 = {946/inv_f:.6f}")
print(f"  12.1759/4 = {inv_f/4:.6f}")
print(f"  12.1759/φ = {inv_f/phi:.6f}")
print(f"  12.1759×φ = {inv_f*phi:.6f}")
print(f"  12.1759×φ² = {inv_f*phi**2:.6f}")

# ============ 3. PSLQ: rem = Σ c_i γ_i ============
print("\n[3] PSLQ: rem = Σ c_i γ_i")
if HAS_MP:
    gamma44_mp = [4*mp.sin(mp.pi*i/88)**2 for i in range(1, 45)]
    # 用 mp.pslq: 搵整數關係
    # 目標: c₀·rem + Σ c_i γ_i = 0, c 細
    # 直接用線性組合嘗試 (冇 pslq 都做到小範圍)
    best = []
    # 3 項組合
    for i in range(1, 45):
        gi = float(gamma44_mp[i-1])
        for j in range(i, 45):
            gj = float(gamma44_mp[j-1])
            for ci in range(-4, 5):
                for cj in range(-4, 5):
                    if ci == 0 and cj == 0:
                        continue
                    val = ci*gi + cj*gj
                    err = abs(val - float(rem_mp))/abs(float(rem_mp))
                    if err < 0.0005:
                        best.append((err, f"{ci}γ_{i}+{cj}γ_{j}", val))
    best.sort()
    print(f"  3 項組合 top 5 (誤差<0.05%):")
    for err, name, val in best[:5]:
        print(f"    {name:18s} = {val:.12f} (誤差 {err*100:.5f}%)")

    # 4 項
    best4 = []
    for i in range(1, 45):
        gi = float(gamma44_mp[i-1])
        for j in range(i+1, 45):
            gj = float(gamma44_mp[j-1])
            for k in range(j+1, 45):
                gk = float(gamma44_mp[k-1])
                for ci in range(-2, 3):
                    for cj in range(-2, 3):
                        for ck in range(-2, 3):
                            val = ci*gi + cj*gj + ck*gk
                            err = abs(val - float(rem_mp))/abs(float(rem_mp))
                            if err < 0.0001:
                                best4.append((err, f"{ci}γ_{i}+{cj}γ_{j}+{ck}γ_{k}", val))
    best4.sort()
    print(f"\n  4 項組合 top 5 (誤差<0.01%):")
    for err, name, val in best4[:5]:
        print(f"    {name:24s} = {val:.12f} (誤差 {err*100:.5f}%)")

# ============ 4. 1/12.176 身份 ============
print("\n[4] 12.1759 身份搜索")
# 12.1759 ≈ ?
# 試: 12 + 44/250 = 12.176?
print(f"  12 + 44/250 = {12 + 44/250:.6f} (誤差 {abs(12+44/250-inv_f)/inv_f*100:.4f}%)")
# 12 + γ₆/1.028
print(f"  12 + γ₆/1.028 = {12 + 0.180736/1.028:.6f}")
# 12 + γ₄×2.173
print(f"  12 + γ₄×2.173 = {12 + 0.081014*2.173:.6f}")
# 12.176 ≈ 12 + 0.176
# 0.176 = 44/250 = 22/125
# 12.176 = 12 + 22/125 = (1500+22)/125 = 1522/125
print(f"  1522/125 = {1522/125:.6f} (誤差 {abs(1522/125-inv_f)/inv_f*100:.4f}%)")
# 12.176 = ?
# 90/7.3916, 唔似
# 44×0.2767
# 試 12.176 ≈ 2×6.088, 6.088 ≈ ?
# 6.088 ≈ 2φ²+0.852
# 試 12.176 ≈ 11×1.1069, 1.1069 ≈ ?
# 1.1069 ≈ 1+0.1069, 0.1069 ≈ γ₆×0.59
# 直接: 12.1759 可能冇簡單身份

# 更可能: rem 本身 = γ 組合
# 最佳 2 項: 4γ_2 = 0.08143 (0.85%), γ_4 = 0.08101 (1.36%)
# 兩項: ci*γ_i + cj*γ_j 最接近?
print(f"\n  rem 線性組合 (細係數):")
g = [4*math.sin(math.pi*i/88)**2 for i in range(1, 45)]
for i in range(1, 45):
    for j in range(1, 45):
        for ci in range(-3, 4):
            for cj in range(-3, 4):
                val = ci*g[i-1] + cj*g[j-1]
                if abs(val) < 1e-10:
                    continue
                err = abs(val - rem_mp)/abs(rem_mp)
                if err < 0.001:
                    print(f"    {ci}γ_{i}+{cj}γ_{j} = {val:.10f} (誤差 {err*100:.4f}%)")

# ============ 5. rem × 整數 ============
print("\n[5] rem × N 整數結構")
rem_f = float(rem_mp)
for N in [44, 88, 90, 134, 946, 36, 66, 198, 484, 462, 124, 178]:
    val = rem_f * N
    print(f"  rem×{N:4d} = {val:.8f} (近整數? {abs(val-round(val)):.6f})")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("五期 14 總結:")
print("=" * 72)
print(f"""
  rem 高精度 = {mp.nstr(rem_mp, 30) if HAS_MP else f'{rem_f:.15f}'}
  1/rem = {inv_f:.10f} ≈ 12.176

  {('1/12.176 = 0.0006%' if abs(1/12.176-rem_f)/rem_f < 0.001 else '1/12.176 唔夠準')}
  12.176 身份: 12 + 22/125 = 1522/125 ({abs(1522/125-inv_f)/inv_f*100:.4f}%)
  = 12 + 0.176 = h¹¹/3 + 22/125
""")
out = {
    "test": "O62 五期 14: rem PSLQ",
    "rem_high": mp.nstr(rem_mp, 30) if HAS_MP else rem_f,
    "inv_rem": inv_f,
    "inv_rem_44": inv_f*44, "inv_rem_90": inv_f*90,
    "best_3term": [{"name": n, "val": float(v), "err": float(e)} for e, n, v in best[:5]] if HAS_MP else [],
    "best_4term": [{"name": n, "val": float(v), "err": float(e)} for e, n, v in best4[:5]] if HAS_MP else [],
    "rem_x_N": {str(N): float(rem_f*N) for N in [44,88,90,134,946,36,66,198,484,462]},
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "14_rem_pslq.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 五期 14 完成!")
