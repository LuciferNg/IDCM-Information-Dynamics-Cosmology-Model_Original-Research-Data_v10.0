#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O204 scripts/17_c5_hierarchy_mechanism.py — C5 大數階層機制攻關
目標: R_world/ℓ_P = φ^e, e ≈ 291.4 — 需要結構推導 (v6.0 已標 OBSERVED not derived)
"""
import mpmath as mp
mp.mp.dps = 50
phi = (1+mp.sqrt(5))/2
Nd, B, Ngen, L4, L5, F5, F7 = 44, 4, 3, 7, 11, 5, 13
M_tree = 33
Sigma_gamma = 90

results = []
def chk(cid, ok, detail):
    results.append((cid, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid}: {detail}")

print("="*72)
print("C5: 大數階層 e ≈ 291.4 機制攻關")
print("="*72)

# ─────────────────────────────────────────────────────
print("\n## 1. 目標值精確定義")
Rw_m = mp.mpf('4129.98764888')*mp.mpf('3.0856775814913673e22')
lP_m = mp.mpf('1.616255e-35')
ratio = Rw_m/lP_m
L_ratio = mp.log10(ratio)
e_target = L_ratio/mp.log10(phi)
print(f"  R_world/ℓ_P = {mp.nstr(ratio, 8)} = 10^{mp.nstr(L_ratio, 8)}")
print(f"  e_target = ln(R_world/ℓ_P)/ln φ = {mp.nstr(e_target, 12)}")

# ─────────────────────────────────────────────────────
print("\n## 2. 結構候選搜索 (e_target ≈ 291.39)")
# 候選 A: 291 = 3×97? 97 = ? 唔結構
# 候選 B: 292 = 4×73? 73 = ? 唔結構
# 候選 C: 290.5 = 581/2? 
# 候選 D: N_d·L₅ + δ? 44×11 = 484 太大
# 候選 E: Σγ·F₅ + δ? 90×3.236?
# 候選 F: 2N_d·B·Ngen − δ? 528·2? 太大
# 候選 G: e = 528/φ? 528×0.618 = 326.3 唔啱
# 候選 H: e = N_d·φ⁴? 44×6.854 = 301.6 近!
phi4 = phi**4   # 6.8541
cand_H = Nd*phi4
dev_H = abs(cand_H - e_target)/e_target
chk("H", dev_H < 0.01,
    f"N_d·φ⁴ = 44×{mp.nstr(phi4,6)} = {mp.nstr(cand_H,6)} vs {mp.nstr(e_target,6)} (dev {mp.nstr(dev_H*100,3)}%)")
# 候選 I: e = (N_d+L₄)·φ³? (44+7)=51 × 4.236 = 216
# 候選 J: e = 88·φ + 88? 88×2.618 = 230.4+88 = 318
# 候選 K: e = B·Ngen·φ⁴·... ?
# 候選 L: e = 2F₅·φ⁴·B? 10×6.854×4 = 274
# 候選 M: e = N_gen·(Σγ+μ²)·φ? 3×92×1.618 = 446
# 候選 N: e = 291.39 ≈ 291.5 = 583/2? 583 = 11×53? 唔結構
# 候選 O: e = 2N_d·F₅ − δ? 440−? = 291 ⟹ δ = 149? 唔結構
# 候選 P: e = Σγ·L₅/φ? 90×11/1.618 = 611.9 太大
# 候選 Q: e = M_tree·φ⁴? 33×6.854 = 226.2 唔啱
# 候選 R: e = 528−236.6? 236.6 唔結構
# ★ 候選 S: e = 88·φ⁴/2? 88×6.854/2 = 301.6 唔啱
# ★ 候選 T: e = 4·φ⁴·F₅·... ?
# ★ 候選 U: e = 291.39 — 試 φ 階梯: ln(e)/ln(φ) = ?
ln_e = mp.log(e_target)/mp.log(phi)
chk("U1", False, f"e_target 嘅 φ-對數 = {mp.nstr(ln_e, 6)} (唔係整數, 冇 φ 階梯)")
# 候選 V: e = 292 − 0.61? 292−φ⁻¹ = 291.382? φ⁻¹ = 0.618 ⟹ 292−φ⁻¹ = 291.382 (dev 0.003%!)
cand_V = 292 - 1/phi
dev_V = abs(cand_V - e_target)/e_target
chk("V", dev_V < 0.0001,
    f"292−φ⁻¹ = {mp.nstr(cand_V, 8)} vs {mp.nstr(e_target, 8)} (dev {mp.nstr(dev_V*100, 6)}%)")
# 候選 W: e = 291 + φ⁻²? 291+0.382 = 291.382 一樣
cand_W = 291 + 1/phi**2
dev_W = abs(cand_W - e_target)/e_target
chk("W", dev_W < 0.0001,
    f"291+φ⁻² = {mp.nstr(cand_W, 8)} vs {mp.nstr(e_target, 8)} (dev {mp.nstr(dev_W*100, 6)}%)")
# 候選 X: e = N_d·L₅·(1−φ⁻³)? 484×0.764 = 369.7 唔啱
# 候選 Y: e = 528·φ⁻¹·...? 528×0.618 = 326.3 唔啱
# 候選 Z: e = (Σγ+M_tree)·φ·L₅/F₇? 123×1.618×11/13 = 168.4 唔啱

# ─────────────────────────────────────────────────────
print("\n## 3. ★ 新候選: 由 v6.0 291.52 出發 — 291.52 ≈ 583/2?")
# 583/2 = 291.5; 583 = 11×53 = L₅×53? 53 = 2×33−13 = 2M_tree−F₇?
cand_Z = mp.mpf(583)/2
dev_Z = abs(cand_Z - e_target)/e_target
chk("Z", dev_Z < 0.001,
    f"583/2 = {mp.nstr(cand_Z, 6)} vs {mp.nstr(e_target, 6)} (dev {mp.nstr(dev_Z*100, 4)}%); 583 = L₅×53, 53 = 2M_tree−F₇ = 66−13")
# 候選 AA: e = 291.52 (v6.0 用值) — 291.52 = ?
# 291.52 × φ = 471.7 唔啱; 291.52/φ = 180.2 唔啱
# ★ 候選 AB: e = 4·φ⁴·N_d − φ⁻¹·... ?
# ★ 候選 AC: 291.39 = 3·97.13? 97 = 2N_d+N_gen²−?  88+9 = 97! 3×97 = 291!
cand_AC = 3*(2*Nd + Ngen**2)   # 3×97 = 291
dev_AC = abs(cand_AC - e_target)/e_target
chk("AC", dev_AC < 0.005,
    f"★ N_gen(2N_d+N_gen²) = 3×97 = {cand_AC} vs {mp.nstr(e_target,6)} (dev {mp.nstr(dev_AC*100,4)}%) — 97 = 2N_d+N_gen² = 88+9 EXACT 結構!")

# 候選 AD: 291.39 更精確 — 292−φ⁻¹ = 291.382 vs 3×97 = 291 (dev 0.134%)
# 邊個好? 292−φ⁻¹ dev 0.0028%; 3×97 dev 0.134%
# ★ 候選 AE: e = 292 − φ⁻¹ = 291.381966 vs target 291.389?? — 差 0.0073 (dev 2.5e-5)
# 真正 target: 用 R_world = 4129.98764888, ℓ_P = 1.616255e-35
# e_target = 291.389... 而 292−φ⁻¹ = 291.382 — 差 0.0075 = 2.6e-5 rel
# 呢個係「好接近但唔 EXACT」— 需要 null test

print("\n## 4. ★ 關鍵洞察: e 唔需要係 φ 階梯 — 可以係複合指數")
# R_world/ℓ_P = φ^e; 但 ℓ_P = √(ħG/c³) 本身含 ħ, G, c
# 若 IDCM 能導出 R_world 同 ℓ_P 各自嘅結構形式, 比值自然結構
# ★ O34: E_kchain = √(M_P·ħ·H₀)·(1−CY₃/(N_d+1)²) — M_P 同 H₀ 都喺入面
# ★ O73: R_world = c/ω_ring, c = R_world·ω_ring (自洽)
# ⟹ 真正問題: R_world/ℓ_P 嘅結構 = (c/ω_ring)/√(ħG/c³) = c^{5/2}/(ω_ring·√(ħG))
# 呢個含 c, ħ, G — 全部要結構
chk("K1", True,
    "R_world/ℓ_P = (c/ω_ring)/√(ħG/c³) = c^{5/2}/(ω_ring√(ħG)) — 結構化需要 c, ħ, G 三樣都結構")
chk("K2", False,
    "c 已結構 (O73: c = R_world·ω_ring, N_d 相消); 但 ħ 同 G 未有結構出處 (O38: 剩 M_P 輸入; unified_constants: ħ, G TAUTOLOGY)")

# ─────────────────────────────────────────────────────
print("\n## 5. 誠實裁決")
print(f"  e_target = {mp.nstr(e_target, 10)}")
print(f"  最佳結構候選: 3(2N_d+N_gen²) = 291 (dev 0.134%) 或 292−φ⁻¹ = 291.382 (dev 0.0028%)")
print(f"  292−φ⁻¹ 嘅 dev 0.0028% 但係『2 參數候選』(292 + φ⁻¹ 修正) — 需 null test")
n_pass = sum(1 for r in results if r[1])
print(f"\n攻關: {n_pass}/{len(results)} PASS")
print("判決: e ≈ 291.39 有『接近候選』但冇 EXACT 結構命中 ⟹ C5 大數階層維持 🔴")
print("     但閉合路徑收窄: 需先結構化 ħ 或 G (O38 剩 M_P 輸入), 之後 e 自然結構")
