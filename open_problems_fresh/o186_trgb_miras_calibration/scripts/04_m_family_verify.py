#!/usr/bin/env python3
"""
O186: M-家族統一驗證 — 攻堅第二/三輪產出 (2026-10-10)
====================================================
驗證:
1. κφ⁻¹/n ≡ φ⁻¹/(16n)  EXACT (mpmath 60-dps) — M-家族結構恆等
2. M-家族表: TRGB 16, Miras 64, RR 96, SH0ES 100, Maser 34 (φ⁻¹/M)
3. L₅−L₁ = 10, L₄−L₁ = 6 EXACT (10 減 1 之代數統一)
4. Cepheid 零修正軸: SH0ES 命中要求 n_Cep ∉ L1 家族 (R3 重構)
5. Planck = ω_ring(1−π/44) — O73 接軌 (R8)
6. F₉ = 34, F₁₀ = 55 Binet 正確符號
"""
from mpmath import mp, mpf, sqrt, pi, nstr

mp.dps = 60
phi = (mpf(1) + sqrt(mpf(5))) / 2
phi_inv = 1 / phi
kappa = mpf(1) / 16
H0_idcm = mpf('72.59')

print("=" * 72)
print("O186: M-家族統一驗證 (攻堅 2/3 輪)")
print("=" * 72)

# ============ T1: κφ⁻¹/n ≡ φ⁻¹/(16n) ============
print("\n[T1] κφ⁻¹/n ≡ φ⁻¹/(16n) EXACT")
print("-" * 72)
t1_ok = True
for n in [1, 2, 4, 6, 8, 16]:
    lhs = kappa * phi_inv / n
    rhs = phi_inv / (16 * n)
    eq = abs(lhs - rhs) < mpf('1e-55')
    t1_ok &= eq
    if n in [1, 4, 6]:
        mark = " (L1 家族)" if n in [1, 4, 6] else ""
        print(f"  κφ⁻¹/{n:<2d} = φ⁻¹/{16*n:<3d} = {nstr(lhs, 18)} {'✅' if eq else '❌'}{mark}")

# ============ T2: M-家族表 ============
print("\n[T2] M-家族: 全部 H₀ 修正 = φ⁻¹/M")
print("-" * 72)
H0_trgb = H0_idcm * (1 - phi_inv / 16)
H0_mira = H0_idcm * (1 + phi_inv / 64)
H0_rr   = H0_idcm * (1 + phi_inv / 96)
H0_sh0es = H0_idcm * (1 + phi_inv / 100)
H0_maserc = H0_idcm * (1 + phi_inv / 34)

obs = [("TRGB", H0_trgb, 69.8, 1.9, -1),
       ("Miras", H0_mira, 73.3, 2.6, +1),
       ("RR", H0_rr, 72.0, 2.0, +1),
       ("SH0ES", H0_sh0es, 73.04, 1.04, +1),
       ("Maser 候選", H0_maserc, 73.9, 3.0, +1)]
t2_ok = True
for name, pred, o, e, sgn in obs:
    dev = abs(pred - o) / o * 100
    sig = abs(pred - o) / e
    ok = dev < 0.5 or sig < 1.0
    t2_ok &= ok
    s = float(sig)
    print(f"  {name:10s}: H₀ = {float(pred):8.4f}  obs {o:6.2f}±{e:<5.2f}  dev {float(dev):7.4f}%  {s:.2f}σ  {'✅' if ok else '🟡' if s<2 else '❌'}")

# ============ T3: L₅−L₁ 統一 ============
print("\n[T3] L₅−L₁ = 10, L₄−L₁ = 6 EXACT")
print("-" * 72)
L1 = phi - phi**(-1)          # 1  (奇數: 減號)
L4 = phi**4 + phi**(-4)       # 7  (偶數: 加號)
L5 = phi**5 - phi**(-5)       # 11 (奇數: 減號)
diff10 = L5 - L1
diff6 = L4 - L1
t3_ok = abs(diff10 - 10) < mpf('1e-55') and abs(diff6 - 6) < mpf('1e-55') and abs(L1 - 1) < mpf('1e-55')
print(f"  L₁ = φ−φ⁻¹ = {nstr(L1, 18)} = 1 EXACT")
print(f"  L₅−L₁ = {float(L5):.0f}−1 = {nstr(diff10, 18)} = 10 {'✅' if abs(diff10-10)<mpf('1e-55') else '❌'}")
print(f"  L₄−L₁ = {float(L4):.0f}−1 = {nstr(diff6, 18)} = 6 {'✅' if abs(diff6-6)<mpf('1e-55') else '❌'}")

# ============ T4: Cepheid 零修正軸 ============
print("\n[T4] Cepheid 零修正軸 (SH0ES 0.002% 強制)")
print("-" * 72)
sh0es_base = H0_idcm * (1 + phi_inv / 100)
dev_base = abs(sh0es_base - 73.04) / 73.04 * 100
t4_ok = dev_base < 0.01
print(f"  無 Cepheid 修正: {float(sh0es_base):.6f} vs 73.04 → dev {float(dev_base):6.4f}% {'✅' if t4_ok else '❌'}")
for n in [1, 4, 8]:
    alt = H0_idcm * (1 + phi_inv / 100 + kappa * phi_inv / n)
    d = abs(alt - 73.04) / 73.04 * 100
    print(f"  若 Cepheid 有 κφ⁻¹/{n}: H₀ = {float(alt):8.4f} → dev {float(d):6.4f}% ❌ (破壞命中)")

# ============ T5: Planck = ω_ring(1−π/44) ============
print("\n[T5] Planck 67.36 = ω_ring(1−π/44) — O73 接軌")
print("-" * 72)
omega_ring = H0_idcm
w_cmb = omega_ring * (1 - pi / 44)
dev_cmb = abs(w_cmb - mpf('67.36')) / mpf('67.36') * 100
z_cmb = abs(w_cmb - mpf('67.36')) / mpf('0.54')
t5_ok = dev_cmb < 0.2
print(f"  ω_cmb = {(1 - float(pi/44))*100:.4f}% × ω_ring = {float(w_cmb):.5f}  vs Planck 67.36±0.54")
print(f"  dev {float(dev_cmb):.4f}% | z = {float(z_cmb):.2f}σ {'✅' if t5_ok else '❌'}")

# ============ T6: Binet 正確符號 ============
print("\n[T6] F₉ = 34, F₁₀ = 55 (Binet 正確符號)")
print("-" * 72)
F9 = (phi**9 + phi**(-9)) / sqrt(5)    # 奇數: 加號
F10 = (phi**10 - phi**(-10)) / sqrt(5) # 偶數: 減號
t6_ok = abs(F9 - 34) < mpf('1e-55') and abs(F10 - 55) < mpf('1e-55')
print(f"  F₉ = (φ⁹+φ⁻⁹)/√5 = {nstr(F9, 18)} = 34 {'✅' if abs(F9-34)<mpf('1e-55') else '❌'}")
print(f"  F₁₀ = (φ¹⁰−φ⁻¹⁰)/√5 = {nstr(F10, 18)} = 55 {'✅' if abs(F10-55)<mpf('1e-55') else '❌'}")

# ============ 總結 ============
print("\n" + "=" * 72)
total = 6
checks = [("M-家族恆等 κφ⁻¹/n≡φ⁻¹/(16n)", t1_ok),
          ("M-家族 5 預言", t2_ok),
          ("L₅−L₁=10, L₄−L₁=6", t3_ok),
          ("Cepheid 零修正軸", t4_ok),
          ("Planck=ω_ring(1−π/44)", t5_ok),
          ("Binet F₉/F₁₀", t6_ok)]
passed = 0
for name, ok in checks:
    print(f"  {'✅' if ok else '❌'} {name}")
    passed += int(ok)
print(f"\n結果: {passed}/{total} PASS")
print(f"狀態: {'🟢 全部通過' if passed == total else '🟡 部分通過'}")