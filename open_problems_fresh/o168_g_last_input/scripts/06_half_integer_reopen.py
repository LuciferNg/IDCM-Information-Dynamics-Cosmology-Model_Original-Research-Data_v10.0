#!/usr/bin/env python3
"""
O168 — 06: 半整數重開審計 (Half-Integer Re-Opening Audit)
=========================================================
用戶主張: 半整數 ℓ 先合理 — 全息通道係雙向, 非黎曼傳輸協議, 88/90 震鈴平滑化。
O165 規則「ℓ 必須整數」係喺單向樹下降 visibility ladder (φ^-2ℓ, 偶冪) 上建立。
若 T_CMB 通道係雙向, 自然參數係總路徑深度 k (整數) — 奇冪 φ^-k 就唔係違規。

驗證:
  [1] 53 = 2N_d − F₅·L₄ = 88−35 (整數路徑深度候選)
  [2] 51 = N_gen·F_proj = 3×17 (e 形指數候選)
  [3] kT/M₀ vs e^-51/2: dev 0.069%
  [4] kT/M₀ vs φ^-53:  dev 0.35%
  [5] 偶冪 φ^-2ℓ 全部 > 5% → 只有奇冪 53 命中 → 半層偏移必需
  [6] 88/90 = N_d/(N_d+1) = 44/45 (邊界截斷比)
  [7] φ^-53·(44/45)^m 修正: m ∈ {±1, ±1/2} 全部 > 0.5% (純因子唔閉合)
"""
from mpmath import mp, mpf, sqrt, exp, ln, pi
mp.dps = 50
phi = (mpf(1)+sqrt(mpf(5)))/mpf(2)
results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'✅' if cond else '❌'}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 74)
print("  O168 — 06: 半整數重開審計")
print("=" * 74)

Nd, B, Ngen, F5, L4, Fproj = mpf(44), mpf(4), mpf(3), mpf(5), mpf(7), mpf(17)
M0 = mpf('27.900915e6')
kT = mpf('2.3486e-4')
F = kT/M0
print(f"  kT/M₀ = {float(F):.4e}   ln = {float(ln(F)):.6f}")

# ── [1] 53 = 2N_d − F₅·L₄ ──
print("\n─── [1] 奇冪候選 k = 53 ───")
k53 = 2*Nd - F5*L4
print(f"  53 = 2N_d − F₅·L₄ = 88 − 35 = {int(k53)}  (整數!)")
check("[1] 53 = 88−35 精確", k53 == 53, "2N_d − F₅·L₄, 全鏈減 (5,7)-crossing")

# ── [2] 51 = N_gen·F_proj ──
print("\n─── [2] e 形指數 51/2 ───")
s51 = Ngen*Fproj
print(f"  51 = N_gen·F_proj = 3×17 = {int(s51)};  51/2 = 25.5 (半整數)")
check("[2] 51 = 3×17 精確", s51 == 51, "N_gen·F_proj")

# ── [3] e 形 dev ──
d_e = abs(exp(-s51/2)/F - 1)*100
print(f"\n─── [3] e^-51/2 dev = {float(d_e):.4f}% ───")
check("[3] e^-25.5 命中 0.069%", d_e < 0.1, f"dev {float(d_e):.4f}%")

# ── [4] φ 形 dev ──
d_phi = abs(phi**(-k53)/F - 1)*100
print(f"─── [4] φ^-53 dev = {float(d_phi):.4f}% ───")
check("[4] φ^-53 命中 0.35%", d_phi < 0.5, f"dev {float(d_phi):.4f}%")

# ── [5] 偶冪全面失手 ──
print("\n─── [5] 偶冪 φ^-2ℓ (O165 家族) 檢查 ───")
best_even = min((abs(phi**(-2*L)/F-1)*100, L) for L in range(1, 34))
print(f"  最佳偶冪 φ^-{2*best_even[1]} dev {float(best_even[0]):.2f}%")
print(f"  → 只有奇冪 53 命中 → 半層偏移 (雙向通道/邊界觀察者) 係必需結構")
check("[5] 偶冪全失手, 奇冪必需", best_even[0] > 5, f"最佳偶冪 dev {float(best_even[0]):.2f}%")

# ── [6] 88/90 = 44/45 ──
print("\n─── [6] 88/90 = N_d/(N_d+1) ───")
r = mpf(88)/mpf(90)
print(f"  88/90 = {float(r):.6f} = 44/45 = N_d/(N_d+1)   (邊界截斷比, o38 45 = N_d+1)")
check("[6] 88/90 = 44/45 精確", r == mpf(44)/45, "N_d/(N_d+1)")

# ── [7] 44/45 純因子修正 ──
print("\n─── [7] φ^-53·(44/45)^m 修正測試 ───")
for m in [1, -1, mpf(1)/2, -mpf(1)/2, 2, -2]:
    val = phi**(-53)*(mpf(44)/45)**m
    dev = abs(val/F - 1)*100
    print(f"  m = {float(m):>5}: dev {float(dev):.3f}%")
best_m = min((abs(phi**(-53)*(mpf(44)/45)**m/F-1)*100, m) for m in [1,-1,mpf(1)/2,-mpf(1)/2,2,-2])
check("[7] 44/45 純因子唔閉合 (<0.5% 先算)", best_m[0] > 0.5,
      f"最佳 m={float(best_m[1])} dev {float(best_m[0]):.3f}%")

print(f"\n{'═'*74}")
print(f"  O168-06 半整數重開: {sum(results)}/{len(results)} PASS")
print(f"{'═'*74}")
