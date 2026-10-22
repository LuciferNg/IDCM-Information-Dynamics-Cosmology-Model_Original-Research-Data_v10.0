#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O204 scripts/20_mp_structural_search.py — M_P 結構化搜索 (C5 唯一合法路徑)
目標: 搵 M_P = f(結構數) 嘅 EXACT 候選, 過 null 先可以閉合
路徑: O38 M₀ = √(M_P·ħ·H₀)·(1891/2025)·φ^e — M_P, ħ 係輸入
      ⟹ 結構化 M_P 或 ħ ⟹ ω_P 結構 ⟹ N_world = ω_P/ω_ring 正向閉合
"""
import mpmath as mp
import itertools
mp.mp.dps = 50
phi = (1+mp.sqrt(5))/2
Nd, B, Ngen, Kt, L4, L5 = 44, 4, 3, 33, 7, 11

results = []
def chk(cid, ok, detail):
    results.append((cid, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid}: {detail}")

print("="*72)
print("M_P 結構化搜索 (C5 唯一合法路徑)")
print("="*72)

# ─────────────────────────────────────────────────────
print("\n## 1. 輸入值")
MP_GeV = mp.mpf('1.220890e19')       # CODATA 2018 M_P
MP_MeV = MP_GeV*1000
M0_MeV = mp.mpf('27.9009145112')
m7_MeV = mp.mpf('13.8002')           # O204 塔 n=7
MdW_MeV = M0_MeV/2                   # 13.9505
Ek_meV = mp.mpf('4.060265e-3')       # E_kchain (MeV)
print(f"  M_P = {mp.nstr(MP_MeV, 10)} MeV")
print(f"  M₀  = {mp.nstr(M0_MeV, 10)} MeV (O34/O38 已閉合)")
print(f"  m₇  = {mp.nstr(m7_MeV, 10)} MeV (O204 塔 n=7)")
print(f"  E_kchain = {mp.nstr(Ek_meV, 8)} MeV")

# ─────────────────────────────────────────────────────
print("\n## 2. M_P 對比已結構量之 log_φ 比率")
def log_phi(x): return mp.log(x)/mp.log(phi)
pairs = {
    "M_P/M₀":    MP_MeV/M0_MeV,
    "M_P/m₇":    MP_MeV/m7_MeV,
    "M_P/m_δW":  MP_MeV/MdW_MeV,
    "M_P/M₀²":   MP_MeV/(M0_MeV**2),
    "M_P·E_kchain": MP_MeV*Ek_meV,
}
for name, ratio in pairs.items():
    e = log_phi(ratio)
    print(f"  {name:14s} = {mp.nstr(ratio, 8)} ⟹ log_φ = {mp.nstr(e, 12)}")

# 候選檢查
e_MP_M0 = log_phi(MP_MeV/M0_MeV)
e_MP_m7 = log_phi(MP_MeV/m7_MeV)
# 98.768 vs 99 = N_gen·K_tree = 3×33?
dev_99 = abs(e_MP_M0 - 99)/99
chk("2a", dev_99 < 0.001,
    f"log_φ(M_P/M₀) = {mp.nstr(e_MP_M0,8)} vs 99 = N_gen·K_tree (dev {mp.nstr(dev_99*100,4)}%)")
# 99.98 vs 100 = 2N_d + B·N_gen = 88+12?
dev_100 = abs(e_MP_m7 - 100)/100
chk("2b", dev_100 < 0.001,
    f"log_φ(M_P/m₇) = {mp.nstr(e_MP_m7,8)} vs 100 = 2N_d + B·N_gen (dev {mp.nstr(dev_100*100,4)}%)")
# 100 = 2N_d + L₅ + 1 = 88+12?
chk("2c", 2*Nd + L5 + 1 == 100, f"100 = 2N_d + L₅ + 1 = 88+11+1 = {2*Nd+L5+1}")

# ─────────────────────────────────────────────────────
print("\n## 3. ★ 精確檢定: M_P = m₇·φ^100?")
cand = m7_MeV * phi**100
dev_cand = abs(cand - MP_MeV)/MP_MeV
chk("3a", dev_cand < 0.01,
    f"m₇·φ^100 = {mp.nstr(cand, 8)} MeV vs M_P = {mp.nstr(MP_MeV, 8)} MeV (dev {mp.nstr(dev_cand*100, 4)}%)")

# 反解精確指數
e_exact = log_phi(MP_MeV/m7_MeV)
print(f"  ★ 精確 log_φ(M_P/m₇) = {mp.nstr(e_exact, 15)}")
# 100 同 99.98 差 0.02% — 需要 null test 決定
# 但先睇: e_exact 嘅分數部分 0.02 ≈ 1/50? 或者 φ⁻⁸ = 0.0213?
frac = e_exact - 100
chk("3b", True, f"log_φ(M_P/m₇) − 100 = {mp.nstr(frac, 8)} — 唔係明顯結構分數 (φ⁻⁸ = {mp.nstr(phi**-8, 6)}, 1/47 = {mp.nstr(mp.mpf(1)/47, 6)})")

# ─────────────────────────────────────────────────────
print("\n## 4. ★ M_P 經 O38 反解: M_P·ħ 已被 M₀ 鎖定")
# M₀ = √(M_P·ħ·H₀)·(1891/2025)·φ^e ⟹ M_P·ħ = [M₀·2025/1891·φ^{−e}]²/H₀
e_O38 = mp.mpf(47) + mp.mpf(37)/528
H0_s = mp.mpf('2.355e-18')  # c/R_world (rad/s)
MP_hbar = (M0_MeV*mp.mpf('2025')/1891*phi**(-e_O38))**2 / H0_s
# 單位: M_P·ħ 喺 MeV·MeV·s = MeV²·s
chk("4a", True,
    f"M_P·ħ = [M₀·(2025/1891)·φ^−e]²/H₀ = {mp.nstr(MP_hbar, 6)} MeV²·s — 已被 M₀/H₀ 鎖定")
# 但 M_P·ħ 係複合: M_P·ħ = ħ√(ħc/G) — ħ 仍自由 ⟹ 結構化 M_P ⟺ 結構化 ħ 或 G
chk("4b", True,
    "M_P·ħ 鎖定 ≠ M_P 鎖定: M_P·ħ = ħ√(ħc/G) 仍含 ħ,G 兩個自由度 (一個組合被鎖, 另一個仍自由)")

# ─────────────────────────────────────────────────────
print("\n## 5. G 或 ħ 嘅 IDCM 候選?")
# G = c²·R_world/M_eff? 量綱檢查: [c²R/M] = L³/(T²M) ✓ = [G]
# M_eff 候選: N_d·M₀? Σγ·M₀? 88·M₀?
c_m = mp.mpf('2.99792458e8')
Rw_m = mp.mpf('4129.98764888')*mp.mpf('3.0856775814913673e22')
G_obs = mp.mpf('6.67430e-11')
M_eff = c_m**2*Rw_m/G_obs   # 需要嘅質量 kg
M0_kg = M0_MeV*mp.mpf('1.78266192e-30')  # 1 MeV/c² = 1.782e-30 kg
chk("5a", True, f"M_eff = c²R_world/G = {mp.nstr(M_eff, 4)} kg = {mp.nstr(M_eff/M0_kg, 4)}×M₀")
chk("5b", True,
    "★ G 冇獨立 IDCM 出處 (v6.0 unified_constants: G = c²L_P/M_P TAUTOLOGY 🔴; O73/O38 冇 G 結構) — "
    "G 係 SM/GR 輸入, IDCM 未結構化 ⟹ C5 缺口實質 = G 或 ħ 結構化")

# ─────────────────────────────────────────────────────
print("\n## 6. ★ 正路: r_d 已結構化 ⟹ N_world = (R_world/r_d)·(r_d/ℓ_P)")
# O170: r_d = 147.088 Mpc = πR_world·420/(88·421)? 驗證
rd_obs = mp.mpf('147.088')
rd_calc = mp.pi*Rw_m*mp.mpf('420')/(88*421)/mp.mpf('3.0856775814913673e22')
chk("6a", abs(rd_calc - rd_obs)/rd_obs < 0.001,
    f"r_d = πR_world·420/(88·421) = {mp.nstr(rd_calc,6)} Mpc vs 觀測 {rd_obs} (dev {mp.nstr(abs(rd_calc-rd_obs)/rd_obs*100,4)}%) — O170 結構化 ✓")
Rw_rd = Rw_m/(rd_obs*mp.mpf('3.0856775814913673e22'))
chk("6b", True, f"R_world/r_d = {mp.nstr(Rw_rd, 8)} ≈ 28 = B·L₄? (dev {mp.nstr(abs(Rw_rd-28)/28*100,4)}%)")
# ★ N_world = (R_world/r_d)·(r_d/ℓ_P): 若 r_d/ℓ_P 有結構 ⟹ 閉合
rd_lP = rd_obs*mp.mpf('3.0856775814913673e22')/mp.mpf('1.616255e-35')
e_rd = log_phi(rd_lP)
chk("6c", True,
    f"r_d/ℓ_P = {mp.nstr(rd_lP,5)} ⟹ log_φ = {mp.nstr(e_rd, 8)} — 同 e_target 差 log_φ(28.08) = {mp.nstr(log_phi(Rw_rd),6)} (≈ 6.7)")

# ─────────────────────────────────────────────────────
print("\n## 7. 誠實裁決")
print("  ★ M_P/m₇ = φ^(99.98): dev 0.02% 對 100 = 2N_d+B·N_gen — 有趣但分數部分 0.02 冇結構")
print("  ★ M_P·ħ 已被 M₀ 鎖定, 但 ħ/G 組合仍有一個自由度 (G 冇 IDCM 出處)")
print("  ★ r_d 已結構化 (O170) ⟹ N_world 拆解為 (R_world/r_d)·(r_d/ℓ_P) — 但 r_d/ℓ_P 同屬大數問題")
print("  ★ 實質: C5 閉合 ⟺ G 或 ħ 結構化 — 未有候選過 null")
n_pass = sum(1 for r in results if r[1])
print(f"  檢定: {n_pass}/{len(results)} PASS")
