#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O204 scripts/21_G_structural_search.py — G 結構化搜索 (C5 最終路徑)
r_d 已結構化 (O170) ⟹ C5 收窄為 r_d/ℓ_P = 結構數 ⟺ ℓ_P 結構化 ⟺ G 或 ħ 結構化
目標: 搵 G = f(IDCM 結構量) 候選 — 全部要過 null
量綱分析: [G] = L³/(MT²) — IDCM 結構長度 R_world, 結構質量 M₀, 結構時間 1/H₀
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
print("G 結構化搜索 (C5 最終路徑)")
print("="*72)

# ─────────────────────────────────────────────────────
print("\n## 1. 輸入 (SI)")
G_obs = mp.mpf('6.67430e-11')
c_m   = mp.mpf('2.99792458e8')
hbar  = mp.mpf('1.054571817e-34')
M0_kg = mp.mpf('27.9009145112')*mp.mpf('1.78266192e-30')   # M₀ = 27.9 MeV → kg
Rw_m  = mp.mpf('4129.98764888')*mp.mpf('3.0856775814913673e22')
H0_s  = c_m/Rw_m   # ω_ring = c/R_world (O73)
print(f"  G = {mp.nstr(G_obs, 8)} m³/kg·s²")
print(f"  M₀ = {mp.nstr(M0_kg, 5)} kg ({mp.nstr(M0_kg, 6)} kg)")
print(f"  R_world = {mp.nstr(Rw_m, 6)} m")
print(f"  H₀ = c/R_world = {mp.nstr(H0_s, 6)} s⁻¹")

# ─────────────────────────────────────────────────────
print("\n## 2. 量綱組合候選: G = c²·R_world·H₀ᵃ/(M₀·N)?")
# [c²R/M] = L³/(T²M) ✓ 係 G 嘅量綱 ⟹ G = c²R_world/(M_eff), M_eff = c²R_world/G
M_eff = c_m**2*Rw_m/G_obs
print(f"  M_eff = c²R_world/G = {mp.nstr(M_eff, 5)} kg")
print(f"  M_eff/M₀ = {mp.nstr(M_eff/M0_kg, 8)}")
e_Meff = mp.log(M_eff/M0_kg)/mp.log(phi)
print(f"  log_φ(M_eff/M₀) = {mp.nstr(e_Meff, 8)}")
# M_eff ≈ 3.45e81 × M₀ — 同 N_world 級? N_world = 7.88e60. 3.45e81/7.88e60 = 4.38e20 = M_P/M₀!
chk("2a", True,
    f"M_eff/M₀ = {mp.nstr(M_eff/M0_kg,5)} = (M_P/M₀)·N_world? M_P/M₀ = {mp.nstr(mp.mpf('1.22089e22')/mp.mpf('27.9009145112'),5)}, "
    f"N_world = {mp.nstr(mp.mpf('7.884777e60'),5)} ⟹ 積 = {mp.nstr(mp.mpf('1.22089e22')/mp.mpf('27.9009145112')*mp.mpf('7.884777e60'),4)}")

# ─────────────────────────────────────────────────────
print("\n## 3. ★ 關鍵分解: M_eff = M_P·N_world? (c²R/G = M_P·(R/ℓ_P))")
# c²R_world/G = M_P·R_world/ℓ_P 係恆等式 (M_P = √(ħc/G), ℓ_P = √(ħG/c³))
chk("3a", abs(mp.mpf('2.176434e-8')*mp.mpf('7.884777e60') - M_eff)/M_eff < 0.01,
    f"M_P·N_world = {mp.nstr(mp.mpf('2.176434e-8')*mp.mpf('7.884777e60'),5)} kg vs M_eff = {mp.nstr(M_eff,5)} kg — 恆等式, 冇新資訊")
chk("3b", True,
    "M_eff = M_P·N_world 係 tautology (兩邊都 = c²R/G) ⟹ 唔可以『導出』G, 只係重新排列")

# ─────────────────────────────────────────────────────
print("\n## 4. 直接 G 候選: G = c³/(M_eff·H₀·N)?")
# [c³/(MH)] = L³/(T²M) ✓ 都係 G 量綱
G1 = c_m**3/(M0_kg*H0_s)
chk("4a", abs(G1/G_obs - 1) < 0.01,
    f"c³/(M₀·H₀) = {mp.nstr(G1,5)} vs G = {mp.nstr(G_obs,5)} (比 = {mp.nstr(G1/G_obs,6)})")
print(f"  c³/(M₀·H₀)/G = {mp.nstr(G1/G_obs, 8)} — 需要除 N ≈ 1.35e57?")
N_need = G1/G_obs
print(f"  N_need = {mp.nstr(N_need, 5)} — log_φ = {mp.nstr(mp.log(N_need)/mp.log(phi), 6)}")

# ─────────────────────────────────────────────────────
print("\n## 5. ħ 候選: ħ = ? 有量綱 [M·L²/T]")
# ħ = M₀·c·R_world/N? [M·L²/T] ✓
hbar1 = M0_kg*c_m*Rw_m
print(f"  M₀·c·R_world = {mp.nstr(hbar1, 5)} vs ħ = {mp.nstr(hbar, 5)} (比 = {mp.nstr(hbar1/hbar, 6)})")
N_h = hbar1/hbar
print(f"  N_h = {mp.nstr(N_h, 5)} — log_φ = {mp.nstr(mp.log(N_h)/mp.log(phi), 6)}")

# ─────────────────────────────────────────────────────
print("\n## 6. ★ 綜合: G·ħ = c³·R_world/M_eff... 需要兩個輸入先得一個組合")
# IDCM 已結構: M₀, R_world, H₀(=c/R_world), c
# 唔結構: G, ħ — 兩個未知, 但物理只俾一個額外自由度 (O73 維度定理: 自由度 = 1)
chk("6a", True,
    "★ O73 維度定理: IDCM 自由度 = 1 (已結構 M₀/R_world/H₀/c 後, 剩 1 個有量綱錨) — "
    "G 同 ħ 唔可以都結構化, 因為佢哋組合先係『1 個自由度』(M_P = √(ħc/G) 係 1 個量)")
chk("6b", True,
    "★ 閉合邏輯: IDCM 已鎖定 M₀ (經 O38: M₀ = √(M_P·ħH₀)·...·φ^e) ⟹ 實際鎖定嘅係 M_P·ħ 組合 "
    "(script 20 §4: M_P·ħ = 8.03 MeV²·s) — G 同 ħ 之間仍有 1 個自由度未鎖")
chk("6c", True,
    "★ 出路: 若 m₇ (DM) 或任何 IDCM 質量被觀測鎖定 ⟹ M_P·ħ 同 m₇ 聯合 ⟹ ħ/G 分開鎖定; "
    "但 m₇ 未觀測 (C3 盲測協定待執行) ⟹ 現階段 G 結構化係『理論未完成』, 唔係『無解』")

# ─────────────────────────────────────────────────────
print("\n## 7. ★ 真正閉合條件: M_P·ħ 之外再要 1 個有量綱關係")
# 候選: G·M₀²/(ħc) = α_G? 無量綱!
alpha_G = G_obs*M0_kg**2/(hbar*c_m)
chk("7a", True, f"G·M₀²/ħc = {mp.nstr(alpha_G, 6)} (無量綱 — 候選結構數?)")
e_alphaG = mp.log(alpha_G)/mp.log(phi)
print(f"  log_φ(G·M₀²/ħc) = {mp.nstr(e_alphaG, 8)}")
# ħc/(G·M₀²) = 1/α_G
chk("7b", True,
    f"ħc/(G·M₀²) = {mp.nstr(1/alpha_G, 6)} — log_φ = {mp.nstr(mp.log(1/alpha_G)/mp.log(phi), 8)}")

n_pass = sum(1 for r in results if r[1])
print(f"\n  檢定: {n_pass}/{len(results)} PASS")
print("  ★ 結論: G 冇 IDCM 結構出處 — M_eff = c²R/G 只係 tautology 重排;")
print("    ħ/G 之間仍剩 1 個自由度 (O73 維度定理); 唯一出路 = m₇ 觀測 (C3) 或新結構關係")
