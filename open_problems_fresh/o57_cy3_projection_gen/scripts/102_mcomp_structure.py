#!/usr/bin/env python3
"""
O57 二十一期 102: M_comp 第一性原理 — 系統結構搜索
=====================================================
M_comp = 3.69e13 GeV（ν Seesaw 壓抑尺度）
已知: log10(M_pl/M_comp) = 5.5197 ≈ 1/γ₆ = 5.5329 (0.24%)
       M_comp = M_pl × 10^(-1/γ₆) = 3.58e13 (誤差 2.96%)

零參數原則: 搜索出嚟嘅候選只算 🟡, 要有第一性原理動機先算 🟢

探索:
  1. log10(M_pl/M_comp) 候選 (γ 譜, Lucas, 結構數)
  2. ln(M_pl/M_comp) 候選
  3. M_comp 直接候選 (M_pl × γ^a × φ^b)
  4. M_comp 同 CY₃ 幾何 (κ, K, h11, h12) 關係
"""
import sys, os, math
import json
import numpy as np

print("=" * 72)
print("O57 二十一期 102: M_comp 結構搜索")
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
B = 4
Nd = 44
g = {n: 4*math.sin(n*math.pi/88)**2 for n in range(1, 45)}

M_pl = 1.2209e19
M_comp = 3.69e13
ratio = M_pl / M_comp
log10_r = math.log10(ratio)
ln_r = math.log(ratio)
print(f"[0] 基礎")
print(f"  M_pl = {M_pl:.4e}, M_comp = {M_comp:.4e}")
print(f"  M_pl/M_comp = {ratio:.4e}")
print(f"  log10(M_pl/M_comp) = {log10_r:.6f}")
print(f"  ln(M_pl/M_comp) = {ln_r:.6f}")
print(f"  1/γ₆ = {1/g[6]:.6f} (誤差 {abs(1/g[6]-log10_r)/log10_r*100:.2f}%)")

# ============ 1. log10 候選 ============
print("\n[1] log10(M_pl/M_comp) = 5.5197 候選")
cands_log = {
    "1/γ₆": 1/g[6],
    "44/8 (2B)": Nd/(2*B),
    "11/2 (L₅/2)": 11/2,
    "33/6": 33/6,
    "F₈/4": 21/4,
    "L₆/γ₆²": 18/g[6]**2,
    "γ₁+γ₂+γ₃+γ₄+γ₅": sum(g[n] for n in range(1,6)),
    "946/171": 946/171,
    "66/12": 66/12,
    "98/18": 98/18,
    "36/γ₆×0.0273": 36/g[6]*0.0273,
    "Σγ_odd/16": 88/16,
    "90/16": 90/16,
}
best_log = []
for name, val in cands_log.items():
    err = abs(val - log10_r)/log10_r*100
    best_log.append((err, name, val))
    print(f"  {name} = {val:.5f} (誤差 {err:.2f}%)")
best_log.sort()
print(f"\n  最佳: {best_log[0][1]} = {best_log[0][2]:.5f} (誤差 {best_log[0][0]:.2f}%)")

# ============ 2. ln 候選 ============
print("\n[2] ln(M_pl/M_comp) = 12.709 候選")
cands_ln = {
    "2π²": 2*math.pi**2,
    "1/γ₆×2.297": 1/g[6]*2.297,
    "44×γ₆×1.6": Nd*g[6]*1.6,
    "φ⁵×1.146": phi**5*1.146,
    "L₅×1.155": 11*1.155,
    "F₇/2.75": 13/2.75,
    "2L₄+ln(2)": 2*7+math.log(2),
    "B×π": 4*math.pi,
    "π²+3": math.pi**2+3,
    "φ⁵+1.62": phi**5+1.62,
    "L₆+L₄-2.29": 18+7-2.29,
    "h11×γ₆×2": 36*g[6]*2,
}
best_ln = []
for name, val in cands_ln.items():
    err = abs(val - ln_r)/ln_r*100
    best_ln.append((err, name, val))
    print(f"  {name} = {val:.4f} (誤差 {err:.2f}%)")
best_ln.sort()
print(f"\n  最佳: {best_ln[0][1]} = {best_ln[0][2]:.4f} (誤差 {best_ln[0][0]:.2f}%)")

# ============ 3. M_comp 直接候選 ============
print("\n[3] M_comp = M_pl × γ^a × φ^b 直接搜索")
best_direct = []
for a in range(1, 8):
    for b in range(-10, 11):
        val = M_pl * g[6]**a * phi**b
        err = abs(val - M_comp)/M_comp*100
        if err < 10:
            best_direct.append((err, a, b, val))
best_direct.sort()
print(f"  <10% 命中: {len(best_direct)}")
for err, a, b, val in best_direct[:12]:
    print(f"    M_pl×γ₆^{a}×φ^{b:+d} = {val:.3e} (誤差 {err:.2f}%)")

# ============ 4. 幾何關係 ============
print("\n[4] M_comp 同 CY₃ 幾何")
print(f"  h11 = 36, h12 = 98, χ = -124, B = 4")
print(f"  M_comp/M_pl = {1/ratio:.3e}")
print(f"  γ₆×M_comp/M_pl×1e6 = {g[6]/ratio*1e6:.3f}")
print(f"  M_comp/(M_pl×γ₆⁴) = {M_comp/(M_pl*g[6]**4):.3e}")
print(f"  M_comp×γ₆²/M_pl = {M_comp*g[6]**2/M_pl:.3e}")
print(f"  log10(M_comp/M_pl) = {-log10_r:.4f}")
print(f"  -log10_r/γ₆ = {-log10_r/g[6]:.3f} (≈ -30.54?)")
print(f"  -log10_r×γ₆ = {-log10_r*g[6]:.4f} (≈ -0.9977 ≈ -1!)")
check("-log10_r×γ₆ ≈ -1", abs(-log10_r*g[6] + 1) < 0.01, f"({-log10_r*g[6]:.4f} vs -1)")

# ============ 5. 深層: M_comp = M_pl^(γ₆?) 或 M_comp = M_pl × 10^(-1/γ₆) ============
print("\n[5] 指數結構")
print(f"  log10(M_comp/M_pl) = -{log10_r:.6f}")
print(f"  1/γ₆ = {1/g[6]:.6f} (誤差 {abs(1/g[6]-log10_r)/log10_r*100:.2f}%)")
print(f"  44/8 = {Nd/8:.6f} (誤差 {abs(Nd/8-log10_r)/log10_r*100:.2f}%)")
print(f"  1/γ₆ vs 44/8: 1/γ₆ - 44/8 = {1/g[6]-Nd/8:.5f}")
print(f"  → γ₆ ≈ 8/44 = 2/11 = 0.1818? γ₆ 真值 = {g[6]:.6f}")
print(f"  γ₆ vs 2/11 誤差: {abs(g[6]-2/11)/(2/11)*100:.2f}%")
print(f"  sin(3π/44) ≈ 3π/44 = {3*math.pi/44:.5f} (小角近似)")
print(f"  4×(3π/44)² = {4*(3*math.pi/44)**2:.6f} vs γ₆ = {g[6]:.6f}")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("二十一期 102 總結:")
print("=" * 72)
print(f"""
  M_comp 結構搜索:
  ─────────────────────────────────
  log10 最佳: {best_log[0][1]} = {best_log[0][2]:.5f} (誤差 {best_log[0][0]:.2f}%)
  ln 最佳: {best_ln[0][1]} = {best_ln[0][2]:.4f} (誤差 {best_ln[0][0]:.2f}%)
  直接: {len(best_direct)} 個 M_pl×γ₆^a×φ^b <10%

  ★ 重要發現: -log10(M_comp/M_pl)×γ₆ ≈ 1!
    → log10(M_pl/M_comp) ≈ 1/γ₆
    → M_comp ≈ M_pl × 10^(-1/γ₆)

  但 1/γ₆ 喺指數冇第一性原理動機
  → 全部候選 🟡 (搜索 fit)
  → 需要更深入機制鏈 (O59/O60 推導)
""")

results = {
    "test": "O57 二十一期 102: M_comp 結構",
    "log10_best": [best_log[0][1], float(best_log[0][2]), float(best_log[0][0])],
    "ln_best": [best_ln[0][1], float(best_ln[0][2]), float(best_ln[0][0])],
    "direct_hits": len(best_direct),
    "gamma6_times_log10": float(-log10_r*g[6]),
    "passed": passed, "failed": failed
}
with open("data/102_mcomp_structure.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
exit(0)
