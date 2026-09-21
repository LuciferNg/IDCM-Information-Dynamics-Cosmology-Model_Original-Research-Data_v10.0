#!/usr/bin/env python3
"""
O57 二十期 100: CKM 湧現 — γ 譜候選探索
===========================================
PMNS 已閉合 (十九期): sin²θ₁₂=γ₂/(γ₂+γ₃), sin²θ₂₃=γ₇/(γ₇+γ₆), sin²θ₁₃=γ₆/(2B)

CKM (夸克, 小角):
  λ = |V_us| = 0.22500 ± 0.00067 (Cabibbo)
  |V_cb| = 0.0412 (θ₂₃)
  |V_ub| = 0.0037 (θ₁₃)
  δ_CKM = 66.40° (IDCM 已閉合!)

探索:
  1. λ = sinθ_C 有冇 γ 結構?
  2. |V_cb|, |V_ub| 有冇 γ 結構?
  3. Wolfenstein 參數 (λ, A, ρ, η)
"""
import sys, os, math
import json
import numpy as np

print("=" * 72)
print("O57 二十期 100: CKM γ 譜候選")
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

phi = (1 + math.sqrt(5)) / 2
g = {n: 4*math.sin(n*math.pi/88)**2 for n in range(1, 45)}

# ============ 1. 實驗 CKM ============
print("\n[1] CKM 實驗值 (PDG 2024)")
lam = 0.22500   # |V_us| Cabibbo
Vcb = 0.0412    # |V_cb|
Vub = 0.0037    # |V_ub|
print(f"  λ = |V_us| = {lam} (Cabibbo)")
print(f"  |V_cb| = {Vcb}")
print(f"  |V_ub| = {Vub}")
print(f"  δ_CKM = 66.40° (IDCM 已閉合)")

# ============ 2. λ 候選 ============
print("\n[2] λ = 0.225 候選")
cands = {
    "γ₆/γ₇×0.304": g[6]/g[7]*0.304,
    "γ₆/2×2.49": g[6]/2*2.49,
    "√γ₆/2": math.sqrt(g[6])/2,
    "γ₆/φ²": g[6]/phi**2,
    "γ₂/γ₃×2.5": g[2]/g[3]*2.5,
    "γ₆×φ/1.3": g[6]*phi/1.3,
    "γ₇/γ₆×0.304": g[7]/g[6]*0.304,
    "γ₃/γ₆×0.89": g[3]/g[6]*0.89,
    "√γ₆×0.529": math.sqrt(g[6])*0.529,
    "γ₆/8×10": g[6]/8*10,
    "φ⁻³": phi**-3,
    "1/√(2B²)": 1/math.sqrt(32),
    "√(1/44)": math.sqrt(1/44),
    "1/φ³×2.4": phi**-3*2.4,
    "γ₂/γ₆×2": g[2]/g[6]*2,
}
best = []
for name, val in cands.items():
    err = abs(val - lam)/lam*100
    best.append((err, name, val))
    print(f"  {name} = {val:.5f} (誤差 {err:.1f}%)")
best.sort()
print(f"\n  最佳: {best[0][1]} = {best[0][2]:.5f} (誤差 {best[0][0]:.1f}%)")

# ============ 3. 系統搜索 λ = γ_a×φ^b ============
print("\n[3] 系統搜索 λ = γ_a × φ^b")
best_lam = []
for a in range(1, 45):
    for b in range(-8, 9):
        val = g[a] * phi**b
        err = abs(val - lam)/lam*100
        if err < 5:
            best_lam.append((err, a, b, val))
best_lam.sort()
print(f"  <5% 命中: {len(best_lam)}")
for err, a, b, val in best_lam[:10]:
    print(f"    γ_{a}×φ^{b:+d} = {val:.5f} (誤差 {err:.1f}%)")

# ============ 4. 系統搜索 λ = γ_a/γ_b ============
print("\n[4] 系統搜索 λ = γ_a/γ_b")
best_ratio = []
for a in range(1, 45):
    for b in range(1, 45):
        if a == b: continue
        val = g[a]/g[b]
        err = abs(val - lam)/lam*100
        if err < 5:
            best_ratio.append((err, a, b, val))
best_ratio.sort()
print(f"  <5% 命中: {len(best_ratio)}")
for err, a, b, val in best_ratio[:10]:
    print(f"    γ_{a}/γ_{b} = {val:.5f} (誤差 {err:.1f}%)")

# ============ 5. |V_cb| = 0.0412 候選 ============
print("\n[5] |V_cb| = 0.0412 候選")
best_cb = []
for a in range(1, 45):
    for b in range(-8, 9):
        val = g[a] * phi**b
        err = abs(val - Vcb)/Vcb*100
        if err < 5:
            best_cb.append((err, a, b, val))
best_cb.sort()
print(f"  γ_a×φ^b <5%: {len(best_cb)}")
for err, a, b, val in best_cb[:8]:
    print(f"    γ_{a}×φ^{b:+d} = {val:.5f} (誤差 {err:.1f}%)")

# ============ 6. |V_ub| = 0.0037 候選 ============
print("\n[6] |V_ub| = 0.0037 候選")
best_ub = []
for a in range(1, 45):
    for b in range(-8, 9):
        val = g[a] * phi**b
        err = abs(val - Vub)/Vub*100
        if err < 5:
            best_ub.append((err, a, b, val))
best_ub.sort()
print(f"  γ_a×φ^b <5%: {len(best_ub)}")
for err, a, b, val in best_ub[:8]:
    print(f"    γ_{a}×φ^{b:+d} = {val:.5f} (誤差 {err:.1f}%)")

# ============ 7. Wolfenstein 結構 ============
print("\n[7] Wolfenstein 參數")
# λ² = 0.0506, λ³ = 0.0114, λ⁴ = 0.00256
print(f"  λ² = {lam**2:.5f} (γ₆/8×2.24 = {g[6]/8*2.24:.5f})")
print(f"  λ³ = {lam**3:.5f} (γ₆/16 = {g[6]/16:.5f}?)")
print(f"  γ₆/16 = {g[6]/16:.5f} vs λ³ = {lam**3:.5f}")
print(f"  |V_cb|/λ² = {Vcb/lam**2:.4f} (A 參數, 預期 ~0.8)")
print(f"  |V_ub|/λ³ = {Vub/lam**3:.4f} (√(ρ²+η²), 預期 ~0.3)")
A = Vcb/lam**2
print(f"  A = {A:.4f}")

# ============ 8. 總結 ============
print("\n" + "=" * 72)
print("二十期 100 總結:")
print("=" * 72)
print(f"""
  CKM γ 譜候選:
  ─────────────────────────────────
  λ 最佳: {best[0][1]} = {best[0][2]:.5f} (誤差 {best[0][0]:.1f}%)
  λ 系統: {len(best_lam)} 個 γ_a×φ^b <5%, {len(best_ratio)} 個 γ_a/γ_b <5%
  |V_cb|: {len(best_cb)} 個 <5% {'→ '+f'γ_{best_cb[0][1]}×φ^{best_cb[0][2]:+d}' if best_cb else ''}
  |V_ub|: {len(best_ub)} 個 <5% {'→ '+f'γ_{best_ub[0][1]}×φ^{best_ub[0][2]:+d}' if best_ub else ''}

  Wolfenstein: A = {A:.4f}, λ² = {lam**2:.5f}
""")

results = {
    "test": "O57 二十期 100: CKM 候選",
    "lam_best": [best[0][1], float(best[0][2]), float(best[0][0])],
    "lam_hits": len(best_lam), "ratio_hits": len(best_ratio),
    "vcb_hits": len(best_cb), "vub_hits": len(best_ub),
    "wolfenstein_A": float(A),
    "passed": passed, "failed": failed
}
with open("data/100_ckm_candidates.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
exit(0)
