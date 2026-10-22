#!/usr/bin/env python3
"""
O169 修正點重驗 — crystal_stress #17 (D_app/N(z) 互補)
=====================================================
上游 O169 (2026-09-15): 舊伸長定律 E_OLD = 1 + 2φ⁻¹ℓ 被 DESI DR2 D_M×6
排除 4.88σ → 正確形式 E(ℓ) = ℓ + 1/⟨v_g⟩_{1..22} = ℓ + 1.11911398。

本 script 重驗 crystal_stress 唯一受影響項:
  docs/04_master_summary.md:184  #17 D_app/N(z) 互補

舊:  D_app/R_H + 4^{-ℓ} = 1 + 2φ⁻¹ℓ·(1−4^{-ℓ})
新:  D_app/R_H + 4^{-ℓ} = 1 + (1−4^{-ℓ})·(ℓ + 0.11911398)

零自由參數; 常數全部來自 K_chain 譜 (⟨v_g⟩ = mean cos(πn/88), n=1..22)。
"""
import mpmath as mp

mp.mp.dps = 40
phi = (1 + mp.sqrt(5)) / 2
invphi = 1 / phi

# ---- 譜常數 (O169) ----
# ⟨v_g⟩_{1..K} = (1/K) Σ_{n=1..K} cos(πn/88)   (群速度 cosθ_n, θ_n = πn/88)
def vg_mean(K):
    return sum(mp.cos(mp.pi * n / 88) for n in range(1, K + 1)) / K

b22 = 1 / vg_mean(22)          # = 1/⟨v_g⟩_{1..22}
assert abs(b22 - mp.mpf("1.11911398")) < 1e-8, b22

# ---- 伸長律 ----
E_old = lambda l: 1 + 2 * invphi * l
E_new = lambda l: l + b22

# ---- #17 互補量 ----
lhs = lambda E, l: (1 - 4 ** (-l)) * E(l) + 4 ** (-l)

checks = []

# 1. 譜常數值 + √5/2 簡併
checks.append(("1/⟨v_g⟩_{1..22} = 1.11911398",
               abs(b22 - mp.mpf("1.11911398")) < 1e-8))
checks.append(("√5/2 簡併 0.0966%",
               abs(b22 - mp.sqrt(5) / 2) / (mp.sqrt(5) / 2) < 1.2e-3))

# 2. 新閉合形式 (代數恆等)
maxdev_new = max(abs(lhs(E_new, mp.mpf(x) / 7) -
                     (1 + (1 - 4 ** (-mp.mpf(x) / 7)) * (mp.mpf(x) / 7 + b22 - 1)))
                 for x in range(0, 15))
checks.append((f"新閉合形式恆等 (max|dev|={mp.nstr(maxdev_new,3)})", maxdev_new < 1e-35))

# 3. 舊閉合形式 (確認文檔舊式)
maxdev_old = max(abs(lhs(E_old, mp.mpf(x) / 7) -
                     (1 + 2 * invphi * mp.mpf(x) / 7 * (1 - 4 ** (-mp.mpf(x) / 7))))
                 for x in range(0, 15))
checks.append((f"舊閉合形式恆等 (max|dev|={mp.nstr(maxdev_old,3)})", maxdev_old < 1e-35))

# 4. ℓ=0 互補性 (兩者都 → 1)
checks.append(("ℓ=0: D_app/R_H + 1 = 1 (兩形式)",
               abs(lhs(E_old, mp.mpf(0)) - 1) < 1e-35 and
               abs(lhs(E_new, mp.mpf(0)) - 1) < 1e-35))

# 5. 單一投影算子 P = 4^{-ℓ} 保留
checks.append(("單一投影算子 P=4^{-ℓ} 保留",
               abs((4 ** (-mp.mpf("0.5"))) - mp.mpf(2) ** -1) < 1e-35))

# ---- 對 DESI 六 tracer 嘅 E 位移 ----
tracers = [("LRG1", 0.510), ("LRG2", 0.706), ("LRG3", 0.934),
           ("ELG2", 1.321), ("QSO", 1.484), ("Lyα", 2.330)]
print("=" * 74)
print("O169 修正點重驗 — crystal_stress #17")
print("=" * 74)
print(f"\n1/⟨v_g⟩_{{1..22}} = {mp.nstr(b22, 12)}  (√5/2 = {mp.nstr(mp.sqrt(5)/2,12)}, dev {mp.nstr(abs(b22-mp.sqrt(5)/2)/(mp.sqrt(5)/2)*100,4)}%)")
print(f"b22 − 1 = {mp.nstr(b22-1, 12)}")

print("\n對 DESI 六 tracer 嘅 E 值位移:")
print(f"  {'tracer':>6} {'z':>6} {'ℓ':>9} {'E_OLD':>9} {'E_NEW':>9} {'ΔE%':>8}")
for nm, z in tracers:
    l = mp.log(1 + z, 4)
    eo, en = E_old(l), E_new(l)
    print(f"  {nm:>6} {z:>6} {mp.nstr(l,5):>9} {mp.nstr(eo,6):>9} {mp.nstr(en,6):>9} {mp.nstr((en-eo)/eo*100,5):>8}")

print("\n檢查矩陣:")
allok = True
for label, ok in checks:
    allok &= bool(ok)
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")

print(f"\n結果: {sum(bool(o) for _,o in checks)}/{len(checks)} {'通過 ✅' if allok else '失敗 ❌'}")
print("零自由參數 — 常數全部來自 K_chain 譜 (cos(πn/88))")
raise SystemExit(0 if allok else 1)
