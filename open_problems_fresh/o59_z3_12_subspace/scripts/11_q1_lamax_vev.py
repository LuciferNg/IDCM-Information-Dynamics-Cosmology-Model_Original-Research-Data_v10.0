#!/usr/bin/env python3
"""
O59 攻堅 Q1: 1+11 譜結構 — λ_max 係咪 Higgs VEV 幾何源頭?
=========================================================
代數現狀:
  12D Yukawa 譜: λ_max = 51.56, λ₂ = 10.0002 (近整數!), λ_max/mean = 28.1
  對應 Cartan(1) + rank(11)

測試:
  1. v_max 方向結構 (特徵向量)
  2. λ_max × M₀ (M₀ = 27.900915 MeV) 數量級
  3. v_geom ≈ √λ_max × M₀ × F_proj → 246 GeV? F_proj 有冇結構?
  4. λ₂ = 10.0002 近整數 — 有冇更深意義?
  5. λ_max 嘅代數身份 (51.56 ≈ ?)
"""
import os, json, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")
phi = (1 + math.sqrt(5)) / 2
M0 = 27.900915  # MeV (O34/O38)
v_ew = 246.22e3  # MeV (電弱標度 246.22 GeV)

print("=" * 72)
print("O59 攻堅 Q1: λ_max = Higgs VEV 幾何源頭?")
print("=" * 72)

passed, failed = 0, 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 載入 d_tensor + 譜 ============
d12 = np.load(os.path.join(DATA, "d_tensor_final.npy"))
v = phi ** (-np.arange(12) / 12)
Y12 = np.einsum("ijk,k->ij", d12, v)
Y12 = (Y12 + Y12.T) / 2
ev, evec = np.linalg.eigh(Y12)
idx = np.argsort(ev)[::-1]
ev, evec = ev[idx], evec[:, idx]

print("\n[1] 12D Yukawa 譜")
for i in range(12):
    print(f"  λ_{i}: {ev[i]:10.4f}")
lam_max = ev[0]
lam2 = ev[1]
print(f"\n  λ_max = {lam_max:.4f}")
print(f"  λ₂ = {lam2:.4f} ← 近整數 {lam2:.6f}!")

# ============ 2. v_max 方向結構 ============
print("\n[2] v_max 特徵向量結構")
vmax = evec[:, 0]
print(f"  v_max = {np.round(vmax, 4)}")
w = vmax**2
print(f"  |v_max|² 分量: {np.round(w, 4)}")
# 有冇主導分量? 有冇 Z₃ 結構 (3 組 × 4)?
print(f"  top-3 分量: {np.argsort(w)[::-1][:3]}")
print(f"  top-3 權重: {np.sort(w)[::-1][:3]}")
# 3 組 × 4 結構?
g1, g2, g3 = w[:4].sum(), w[4:8].sum(), w[8:].sum()
print(f"  3×4 分組權重: [{g1:.3f}, {g2:.3f}, {g3:.3f}]")
check("v_max 大致均勻分佈 (冇單一主導)", max(w) < 0.3, f"(max={max(w):.3f})")

# ============ 3. λ_max × M₀ 數量級 ============
print("\n[3] λ_max × M₀ 數量級")
lamM0 = lam_max * M0
print(f"  λ_max × M₀ = {lamM0:.3f} MeV = {lamM0/1e3:.4f} GeV")
sqrt_lamM0 = math.sqrt(lam_max) * M0
print(f"  √λ_max × M₀ = {sqrt_lamM0:.3f} MeV = {sqrt_lamM0/1e3:.4f} GeV")
# 比較: 電弱標度
print(f"  v_ew = {v_ew/1e3:.2f} GeV = {v_ew:.0f} MeV")
print(f"  v_ew / (√λ_max × M₀) = {v_ew/sqrt_lamM0:.1f}")
print(f"  v_ew / (λ_max × M₀) = {v_ew/lamM0:.1f}")

# 需要嘅放大因子
F_needed = v_ew / sqrt_lamM0
print(f"\n  ★ 需要放大因子 F = {F_needed:.1f}")
# 有冇結構?
print(f"  F ≈ ?")
print(f"  88×14 = {88*14}, 44×28 = {44*28}, 4×7×44 = {4*7*44}")
print(f"  F₈×L₅ = {21*11}, F₈×L₆ = {21*18}, F₇×L₅ = {13*11}")
print(f"  φ^15 = {phi**15:.1f}, φ^14 = {phi**14:.1f}")
print(f"  L₆×F₇ = {18*13}, L₆×L₅ = {18*11}, 2^11 = {2**11}")

# ============ 4. λ_max 代數身份搜索 ============
print("\n[4] λ_max 代數身份")
print(f"  λ_max = {lam_max:.4f}")
candidates = {
    "44+8": 52, "44+7.56": 51.56, "φ^8": phi**8, "φ^7×3": phi**7*3,
    "L₆×3-2.44": 18*3-2.44, "F₇×4-0.44": 13*4-0.44,
    "88×0.586": 88*0.586, "44×1.172": 44*1.172,
    "10×5.156": 10*5.156, "51.56": 51.56,
    "4×12.89": 4*12.89, "33+18.56": 33+18.56,
    "φ^8.15": phi**8.15, "F₈+L₆×2": 21+36,
}
for name, val in candidates.items():
    err = abs(val - lam_max)/lam_max*100
    mark = "★" if err < 1 else ""
    print(f"    {name:15s} = {val:10.3f}  誤差 {err:6.2f}% {mark}")

# 特別: λ_max/λ₂ ratio
ratio12 = lam_max / lam2
print(f"\n  λ_max/λ₂ = {ratio12:.4f}")
print(f"  5.156 = ? 5.156 ≈ φ⁴/1.5? φ⁴ = {phi**4:.3f}")
print(f"  φ⁴ = {phi**4:.4f}, λ_max/λ₂ = {ratio12:.4f}")
print(f"  φ⁴/λ_max/λ₂ = {phi**4/ratio12:.4f}")
print(f"  λ_max/λ₂ ≈ 5.156 ≈ 5+1/6.4?")

# ============ 5. 電弱標度其他路徑 ============
print("\n[5] 電弱標度其他路徑")
# m_7 = 13.8 MeV (K_Chain mode 7) — 已知
# v_ew = 246.22 GeV
print(f"  m_7 = 13.8 MeV (memory)")
print(f"  v_ew/m_7 = {v_ew/13.8e3:.1f}")
print(f"  v_ew/m_7 ≈ 17840? 唔似")
# M₀ × 88?
print(f"  M₀×88 = {M0*88:.1f} MeV = {M0*88/1e6:.4f} TeV")
# M₀ × 44 × 2?
print(f"  M₀×44×2 = {M0*88:.1f} MeV")
# M₀ × φ^12?
print(f"  M₀×φ^12 = {M0*phi**12:.1f} MeV = {M0*phi**12/1e3:.2f} GeV")
# M₀ × φ^13?
print(f"  M₀×φ^13 = {M0*phi**13:.1f} MeV = {M0*phi**13/1e3:.2f} GeV")
# M₀ × φ^14?
print(f"  M₀×φ^14 = {M0*phi**14:.1f} MeV = {M0*phi**14/1e3:.3f} GeV")
# M₀ × φ^15?
print(f"  M₀×φ^15 = {M0*phi**15:.1f} MeV = {M0*phi**15/1e3:.3f} GeV")
# 246 GeV / M₀:
ratio_ew = v_ew / M0
print(f"\n  v_ew/M₀ = {ratio_ew:.1f} ≈ ?")
print(f"  φ^15 = {phi**15:.2f}, φ^16 = {phi**16:.2f}")
print(f"  ratio_ew/φ^15 = {ratio_ew/phi**15:.4f}")
print(f"  ratio_ew/φ^16 = {ratio_ew/phi**16:.4f}")
print(f"  8821 = ? 44×200.5? 88×100.2?")
print(f"  8821/88 = {ratio_ew/88:.1f}, 8821/44 = {ratio_ew/44:.1f}")

# ============ 6. λ_max 同 M₀ 產品 ============
print("\n[6] λ_max × M₀ 嘅物理對應")
lamM0_GeV = lamM0/1e3
print(f"  λ_max × M₀ = {lamM0_GeV:.3f} GeV")
print(f"  → 1.439 GeV ≈ ?")
print(f"  m_τ = 1.777 GeV, m_Λ = 1.116 GeV, m_Σ = 1.189 GeV")
print(f"  m_p = 0.938 GeV")
print(f"  1.439 = ? 0.938×1.534? 1.777×0.81?")
print(f"  √λ_max × M₀ = {sqrt_lamM0/1e3:.3f} GeV = 0.200 GeV")

print(f"\n{'='*72}")
print(f"Q1 初步: {passed} PASS, {failed} FAIL")
print(f"{'='*72}")
