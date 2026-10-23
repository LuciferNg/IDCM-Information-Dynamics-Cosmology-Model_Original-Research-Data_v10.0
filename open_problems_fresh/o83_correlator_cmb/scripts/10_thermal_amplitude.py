#!/usr/bin/env python3
"""
O83 — Script 10: A4 攻堅 — 熱態 ↔ C_ℓ 振幅絕對耦合
=====================================================
問題: docs/02 §5 有熱 propagator ⟨φφ⟩_T = G(0)(1 + 2/(e^{βω}−1))，
      但 T_CMB 用外來式子、β 從未由 Z_0(β) 決定 ⟹ 「熱態未接振幅」(A4)。

本輪: 由 M₀ / T_CMB 階層直接計算佔據因子，判定振幅是否需要熱修正。
      高精度 (mpmath 50 位)，唔用浮點近似。

輸入 (corpus 已註冊):
  M₀ = 27.900915 MeV   (O38 譜標度)
  T_CMB = 2.72548 K    (COBE/FIRAS)
  ω_n = 2 sin(nπ/88)   (K_chain 無量綱本徵值)
  γ_n = ω_n²
"""
import os, sys
import mpmath as mp

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'✅ PASS' if cond else '❌ FAIL'}] {name} {detail}")
def note(name, detail=""):
    print(f"  [📝 註記] {name} {detail}")
def rec(kind, name, detail=""):
    print(f"  [{kind}] {name} {detail}")

mp.mp.dps = 50

print("=" * 78)
print("  O83 — Script 10: A4 — 熱態 ↔ C_ℓ 振幅")
print("=" * 78)

# ──────────────────────────────────────────────
# §1 單位與階層
# ──────────────────────────────────────────────
M0_MeV = mp.mpf("27.900915")
T_CMB  = mp.mpf("2.72548")
kB_eV  = mp.mpf("8.617333262e-5")          # CODATA 2018
kB_MeV = kB_eV / 1e6
E0_MeV = M0_MeV * 1                          # 譜標度 (每單位 γ/ω)
kBT_MeV = kB_MeV * T_CMB

print(f"\n─── [1] 能量階層 (mpmath dps={mp.mp.dps}) ───")
print(f"  M₀        = {mp.nstr(M0_MeV, 12)} MeV")
print(f"  k_B·T_CMB = {mp.nstr(kBT_MeV, 12)} MeV")
ratio = M0_MeV / kBT_MeV
print(f"  M₀/k_BT   = {mp.nstr(ratio, 12)}")
check("M₀ ≫ k_B T_CMB (階層恆定)", ratio > mp.mpf('1e6'),
      f"ratio = {mp.nstr(ratio,8)}")

# ──────────────────────────────────────────────
# §2 每個模式嘅佔據因子
# ──────────────────────────────────────────────
print(f"\n─── [2] 玻色佔據 n_B(ω_n) = 1/(e^{{x}}−1),  x = ω_n·M₀/(k_B T) ───")
print(f"  {'n':>3} {'ω_n':>14} {'x':>20} {'n_B':>14} {'2n_B (修正)':>14}")
rows = []
for n in (1, 7, 22, 44):
    w = 2 * mp.sin(mp.pi * n / 88)
    x = w * ratio
    nb = 1 / (mp.e ** x - 1)
    rows.append((n, w, x, nb))
    print(f"  {n:>3} {mp.nstr(w,10):>14} {mp.nstr(x,10):>20} {mp.nstr(nb,6):>14} {mp.nstr(2*nb,6):>14}")

all_negligible = all(r[3] < mp.mpf('1e-100') for r in rows)
check("全部 n_B < 1e-100 (熱佔據為零)", all_negligible,
      f"max n_B = {mp.nstr(max(r[3] for r in rows), 6)}")

# ──────────────────────────────────────────────
# §3 熱 propagator 相對修正
# ──────────────────────────────────────────────
print(f"\n─── [3] ⟨φφ⟩_T / G(0) − 1 = 2n_B ───")
for n, w, x, nb in rows:
    rel = 2 * nb
    print(f"  n={n:>2}: 相對修正 = {mp.nstr(rel, 6)}")
max_rel = max(2 * r[3] for r in rows)
check("熱修正 < 1e-100 (機器級零)", max_rel < mp.mpf('1e-100'),
      f"max = {mp.nstr(max_rel,6)}")
rec("🟢", "熱修正可忽略", "⟹ C_ℓ 振幅 = 真空 propagator G_n(0)，熱態不貢獻")

# ──────────────────────────────────────────────
# §4 交叉核: 要幾高溫才有效?
# ──────────────────────────────────────────────
print(f"\n─── [4] 臨界溫度 (熱修正 = 1% 所需) ───")
print(f"  ⟨φφ⟩_T/G(0) − 1 = 2/(e^{{βω}}−1) = 0.01  ⟹  e^{{βω}} = 201 ⟹ x = ln(201)")
x_crit = mp.log(201)
T_crit = M0_MeV * 2 * mp.sin(mp.pi / 88) / (kB_MeV * x_crit)
print(f"  x_crit = ln(201) = {mp.nstr(x_crit, 10)}")
print(f"  ω₁ = {mp.nstr(2*mp.sin(mp.pi/88), 10)}")
print(f"  T_crit = ω₁·M₀/(k_B·x_crit) = {mp.nstr(T_crit, 8)} MeV = {mp.nstr(T_crit*1e6/kB_eV, 8)} K")
print(f"  vs T_CMB = {mp.nstr(T_CMB, 8)} K  ⟹ 差 {mp.nstr(T_crit*1e6/kB_eV/T_CMB, 6)} 倍")
check("T_crit ≫ T_CMB (熱態遠離 CMB)", T_crit * 1e6 / kB_eV > 1e6 * T_CMB,
      f"T_crit/T_CMB ≈ {mp.nstr(T_crit*1e6/kB_eV/T_CMB, 4)}")
note("⟹ CMB 溫度遠低於 K_chain 熱激發閾值 ⟹ 振幅必須用 T=0 propagator")

# ──────────────────────────────────────────────
# §5 結論 + 剩餘缺口
# ──────────────────────────────────────────────
print("\n" + "=" * 78)
passed, total = sum(results), len(results)
print(f"  RESULT: {passed}/{total} PASS")
print("=" * 78)
print(f"""
  A4 裁決 (2026-10-23):
  🟢 已閉合 (耦合已計算): 熱佔據 n_B < 1e-100 ∀n ∈ 1..44
     ⟹ ⟨φ_nφ_n⟩_T = G_n(0) 至機器精度
     ⟹ C_ℓ 振幅 = A_m = w_m² G_m(0) **真空形式即最終形式**
  🟢 已量化: 熱修正要達 1% 需 T = {mp.nstr(T_crit*1e6/kB_eV, 4)} K ≈ {mp.nstr(T_crit*1e6/kB_eV/T_CMB, 3)}× T_CMB
  🔴 仍屬缺口 (轉 A5): T_CMB **本身**為何係 2.7255 K —— 屬 P3 (H1 後驗式 0.104%), 非 O83
  ⟹ A4 由「未耦合」降級為「已耦合且貢獻為 0」— 形式完整, 剩 T_CMB 來源跨 O
""")
sys.exit(0 if passed == total else 1)
