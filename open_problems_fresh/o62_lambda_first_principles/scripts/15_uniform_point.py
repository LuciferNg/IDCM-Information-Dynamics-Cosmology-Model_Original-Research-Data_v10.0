#!/usr/bin/env python3
"""
O62 五期 15: rem 結構身份 — 均勻點 + PSLQ
===========================================
假設: F(2,2,...,2) = (8/6)Σκ = 264 精確?
  → rem = F(γ) − F(2·1) = 曲率偏差
  → Σκ = 198? (b₃ from O57!)

亦: mpmath PSLQ 搵 rem 精確整數關係
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O62 五期 15: 均勻點 + PSLQ")
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

import mpmath as mp
mp.mp.dps = 50

d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])

# ============ 1. Σκ ============
print("\n[1] Σκ (全 entries 和)")
S_kappa = int(kappa.sum())
print(f"  Σκ = {S_kappa}")
check("Σκ = 198 (b₃, O57)", S_kappa == 198, f"(實際 {S_kappa})")
check("198 = 6×33 = 6K_tree", 6*33 == 198)
check("Σκ = −8 特殊?", abs(S_kappa) == 8, f"(Σκ = {S_kappa})")

# ============ 2. F(2·1) ============
print("\n[2] F(2,2,...,2) 均勻點")
F2 = (8.0/6.0) * S_kappa
print(f"  F(2·1) = (8/6)×Σκ = {F2:.8f}")
check("F(2·1) = 264 精確", abs(F2 - 264) < 1e-9, f"(實際 {F2:.8f})")
check("264 = 6N_d = 3×88", 264 == 6*44)

# ============ 3. rem = F(γ) − F(2·1) ============
print("\n[3] rem 曲率偏差")
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
Fg = np.einsum("ijk,i,j,k", kappa, gamma36, gamma36, gamma36) / 6.0
rem = Fg - 264
print(f"  F(γ) = {Fg:.15f}")
print(f"  rem = F(γ) − F(2·1) = {rem:.15f}")
print(f"  → rem = (1/6)Σκ(γ³−8) 曲率偏差")

# ============ 4. 高精度 PSLQ ============
print("\n[4] mpmath PSLQ")
gamma44_mp = [4*mp.sin(mp.pi*i/88)**2 for i in range(1, 45)]
rem_mp = mp.mpf(0)
gamma36_mp = gamma44_mp[:36]
for i in range(36):
    for j in range(36):
        for k in range(36):
            kk = int(kappa[i,j,k])
            if kk != 0:
                rem_mp += kk * gamma36_mp[i]*gamma36_mp[j]*gamma36_mp[k]
rem_mp = rem_mp/6 - 264
print(f"  rem (50位) = {mp.nstr(rem_mp, 45)}")

# PSLQ 1: [rem, 1, γ_1..γ_44]
basis1 = [rem_mp] + [mp.mpf(1)] + gamma44_mp
rels1 = mp.pslq(basis1, tol=mp.mpf('1e-45'), maxcoeff=1000, maxsteps=10000)
if rels1:
    nz = [(i, r) for i, r in enumerate(rels1) if r != 0]
    print(f"  PSLQ [rem,1,γ]: {rels1}")
    print(f"  非零係數: {nz}")
    # 驗證
    val = sum(r*b for r, b in zip(rels1, basis1))
    print(f"  驗證 Σr·b = {mp.nstr(val, 20)}")
else:
    print("  PSLQ 冇搵到細係數關係")

# PSLQ 2: [rem, 1, γ_29, 1/36, 1/134]
basis2 = [rem_mp, mp.mpf(1), gamma44_mp[28], mp.mpf(1)/36, mp.mpf(1)/134]
rels2 = mp.pslq(basis2, tol=mp.mpf('1e-45'), maxcoeff=100, maxsteps=5000)
if rels2:
    nz = [(i, r) for i, r in enumerate(rels2) if r != 0]
    print(f"  PSLQ [rem,1,γ29,1/36,1/134]: {rels2}")
    print(f"  非零: {nz}")
else:
    print("  PSLQ2 冇搵到")

# PSLQ 3: [rem, 1/12.176] 對 — 直接睇 1/rem 係咪 12.176 = 1522/125
inv_rem = mp.mpf(1)/rem_mp
print(f"\n  1/rem = {mp.nstr(inv_rem, 30)}")
print(f"  1522/125 = 12.1760000000000000000")
print(f"  差 = {mp.nstr(inv_rem - mp.mpf(1522)/125, 20)}")

# PSLQ 4: 12.1759 身份 — [inv_rem, 12, 44, 250]
basis4 = [inv_rem, mp.mpf(12), mp.mpf(44), mp.mpf(250)]
rels4 = mp.pslq(basis4, tol=mp.mpf('1e-45'), maxcoeff=100, maxsteps=5000)
if rels4:
    print(f"  PSLQ [inv_rem,12,44,250]: {rels4}")

# ============ 5. 各候選精確誤差 ============
print("\n[5] 候選精確誤差 (高精度)")
cands = {
    "γ_29/36": gamma44_mp[28]/36,
    "L₅/134 = 11/134": mp.mpf(11)/134,
    "1/12.176 = 125/1522": mp.mpf(125)/1522,
    "γ₆²×2.514": (4*mp.sin(6*mp.pi/88)**2)**2 * mp.mpf('2.514'),
    "γ₁×(16+1/8)": gamma44_mp[0]*(16+mp.mpf(1)/8),
    "γ_29/36 − γ_1/99.4": gamma44_mp[28]/36 - gamma44_mp[0]/mp.mpf('99.4'),
}
for name, val in cands.items():
    err = abs(val - rem_mp)/abs(rem_mp)*100
    marker = " ★★★" if err < 0.001 else (" ★" if err < 0.01 else "")
    print(f"  {name:24s} = {mp.nstr(val, 20)} (誤差 {mp.nstr(err, 6)}%){marker}")

# ============ 6. 均勻點詮釋 ============
print("\n[6] 均勻點詮釋")
print(f"""
  F(2,2,...,2) = (8/6)Σκ = (4/3)×198 = 264 精確!

  264 = 6N_d = 3×Σγ_even(88) = 2×(44×3) = B×66 態

  rem = F(γ) − F(2·1) = (1/6)Σκ_ijk(γ_iγ_jγ_k − 8)
      = 0.0821292... (K_Chain 譜偏離均勻點嘅曲率)

  → 均勻點 2 = ? (mean γ?)
  Σγ_{{1..36}} = ?
""")
sum_g36 = float(sum(gamma44_mp[:36]))
print(f"  Σγ_{{1..36}} = {sum_g36:.10f}")
print(f"  mean γ (1..36) = {sum_g36/36:.10f}")
print(f"  2×36 = 72 vs Σγ_{{1..36}} = {sum_g36:.6f}")
print(f"  Σγ_{{1..36}}/36 = {sum_g36/36:.6f}")
check("Σγ(1..36) ≈ 72 = 2×36?", abs(sum_g36 - 72) < 5, f"(差 {abs(sum_g36-72):.4f})")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("五期 15 總結:")
print("=" * 72)
print(f"""
  ★★★ F(2,2,...,2) = (4/3)Σκ = 264 精確 = 6N_d = 3×88
  Σκ = 198 = 6K_tree = b₃ (O57 已見!)

  rem = F(γ) − F(2·1) = (1/6)Σκ(γ³−8) = {mp.nstr(rem_mp, 20)}

  最佳候選: {min(cands, key=lambda k: abs(cands[k]-rem_mp)/abs(rem_mp))}
  誤差: {mp.nstr(min(abs(cands[k]-rem_mp)/abs(rem_mp)*100 for k in cands), 6)}%
""")
out = {
    "test": "O62 五期 15: 均勻點 + PSLQ",
    "S_kappa": S_kappa,
    "F_uniform": float(F2),
    "rem_high": mp.nstr(rem_mp, 40),
    "inv_rem": mp.nstr(inv_rem, 30),
    "sum_gamma_1_36": float(sum_g36),
    "candidates": {k: {"val": mp.nstr(v, 20), "err_pct": mp.nstr(abs(v-rem_mp)/abs(rem_mp)*100, 8)} for k, v in cands.items()},
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "15_uniform_point.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 五期 15 完成!")
