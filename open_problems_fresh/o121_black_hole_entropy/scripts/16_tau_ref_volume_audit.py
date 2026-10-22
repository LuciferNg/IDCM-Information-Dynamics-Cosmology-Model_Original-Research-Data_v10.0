#!/usr/bin/env python3
"""
O121 — script 16: ★ τ_ref 體積一致性審計 (G8 root-cause)
==================================================================
發現: G8 之 τ_ref = M_BH(5.88e18, V_comov=1.2e13)/Ṁ_UHECR(82.53, V_world=2.95e11)
      **混用兩個體積** — 而 O175 script 08 早已診斷同款錯誤 (factor 40.7)。
影響: τ_ref 修正 → G8 「+24.56% 吻合」係假象。

零新常數。
"""
import math, json, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS = 0; FAIL = 0
def ck(n, c, d=""):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n} {d}")
    else: FAIL += 1; print(f"  ❌ {n} {d}")

c_l, M_sun = 2.99792458e8, 1.989e30
V_comov = 1.2e13      # Mpc³ — 可觀測宇宙 comoving (粒子視界, H₀=67.4) [O173 s07, O175 s08]
V_world = 2.95e11     # Mpc³ — W-world (Hubble 半徑, R_world=c/H₀) [O173 s01]
rho_lo, rho_hi = 2.5e5, 4.9e5                    # M☉/Mpc³ (K&H / Elvis)
L_uhecr = 1e45        # erg Mpc⁻³ yr⁻¹ (正典, O175)
L_uhecr_v1 = 5e44     # erg Mpc⁻³ yr⁻¹ (O173 s01)
omega_ring = 72.59; Mpc_m = 3.0856775814913673e22; Yr_s = 3.1557e7
T_ring = (2*math.pi/(omega_ring*1e3/Mpc_m))/Yr_s
MIS = 20
tau_pred = (2**MIS)*T_ring

print("="*78); print("O121 script 16: τ_ref 體積一致性審計"); print("="*78)
print(f"\n  V_comov = {V_comov:.2e} Mpc³ (粒子視界)  |  V_world = {V_world:.2e} Mpc³ (Hubble)")
print(f"  V_comov/V_world = {V_comov/V_world:.3f}")

# ---- A. 重現 G8 之 τ_ref 及其構成 ----
print("\n"+"="*78); print("[A] 重現 G8 τ_ref 之構成 (找混用)"); print("="*78)
M_BH = rho_hi*V_comov
print(f"  M_BH = ρ_BH(Elvis {rho_hi:.1e}) × V_comov({V_comov:.1e}) = {M_BH:.3e} M☉")
ck("M_BH = 5.88e18 (重現, 用 **正確** V_comov)", abs(M_BH-5.88e18)/5.88e18 < 0.01, f"({M_BH:.3e})")
# O173 s01 之 M_uhecr
ERG_TO_J = 1e-7
rho_dot_v1 = L_uhecr_v1*ERG_TO_J/(M_sun*c_l**2)           # M☉/yr/Mpc³
Mdot_v1 = rho_dot_v1*V_world
print(f"  Ṁ_UHECR(O173 s01) = {L_uhecr_v1:.0e}/(M☉c²) × V_world({V_world:.1e}) = {Mdot_v1:.2f} M☉/yr")
ck("Ṁ_UHECR(O173) = 82.53 (重現, 但用 **錯** V_world)", abs(Mdot_v1-82.53)/82.53 < 0.01, f"({Mdot_v1:.2f})")
tau_ref_G8 = M_BH/Mdot_v1
print(f"  ⟹ τ_ref(G8) = M_BH/Ṁ_UHECR = {tau_ref_G8:.4e} yr")
ck("τ_ref(G8) = 7.1247e16 (重現)", abs(tau_ref_G8-7.1247e16)/7.1247e16 < 0.01, f"({tau_ref_G8:.3e})")
print(f"  ⚠️ **混用確認**: 分子 V_comov={V_comov:.1e}, 分母 V_world={V_world:.1e}")

# ---- B. 修正: 兩者同用 V_comov ----
print("\n"+"="*78); print("[B] 修正: 兩者同用 V_comov"); print("="*78)
Mdot_c_1e45 = (L_uhecr*ERG_TO_J/(M_sun*c_l**2))*V_comov
Mdot_c_5e44 = (L_uhecr_v1*ERG_TO_J/(M_sun*c_l**2))*V_comov
print(f"  Ṁ_UHECR(修正, ℒ=1e45) = {Mdot_c_1e45:.1f} M☉/yr")
print(f"  Ṁ_UHECR(修正, ℒ=5e44) = {Mdot_c_5e44:.1f} M☉/yr")
ck("修正後 ℒ=1e45 之率 ≈ R_rel = 6730.86 (O175 主通道)",
   abs(Mdot_c_1e45-6730.86)/6730.86 < 0.01, f"({Mdot_c_1e45:.1f})")
tau_ref_c_1e45 = M_BH/Mdot_c_1e45
tau_ref_c_5e44 = M_BH/Mdot_c_5e44
print(f"  ⟹ τ_ref(修正, 1e45) = {tau_ref_c_1e45:.4e} yr")
print(f"      τ_ref(修正, 5e44) = {tau_ref_c_5e44:.4e} yr")
r1 = tau_ref_G8/tau_ref_c_1e45
print(f"  τ_ref(G8)/τ_ref(修正,1e45) = {r1:.2f}  (= 2×40.68)")
ck("G8 τ_ref 過大 ~81× (1e45) / ~41× (5e44)", 70 < r1 < 90, f"({r1:.2f})")

# ---- C. 重新評估 G8 主路線 ----
print("\n"+"="*78); print("[C] 重新評估 G8 主路線 (τ_pred = 2²⁰·T_ring)"); print("="*78)
print(f"  τ_pred = 2²⁰·T_ring = {tau_pred:.4e} yr")
for lbl, tr in (("G8 原用 (混用)", tau_ref_G8), ("修正 ℒ=1e45", tau_ref_c_1e45),
                ("修正 ℒ=5e44", tau_ref_c_5e44)):
    print(f"    vs {lbl:16s} ({tr:.3e}): dev = x{tau_pred/tr:.1f}  (+{(tau_pred/tr-1)*100:.4g}%)")
ck("修正後 dev ≫ 1% (「+24.56% 吻合」不成立)", abs(tau_pred/tau_ref_c_1e45 - 1) > 1,
   f"(x{tau_pred/tau_ref_c_1e45:.1f})")
ck("下界一致性仍成立 (τ_pred ≥ τ_ref 修正)", tau_pred >= tau_ref_c_1e45)
print("  ★ 裁決: 觀測**下界**仍滿足 (冇矛盾), 但**冇吻合** — 「+24.56%」係體積假象")

# ---- D. f_return 更正 ----
print("\n"+"="*78); print("[D] f_return 更正"); print("="*78)
t_H = 1.38e10
Mdot_o175 = M_BH*(1/( (1+math.sqrt(5))/2 )**21)/t_H
Mdot_struct = M_BH/tau_pred
print(f"  Ṁ_struct = M_BH/τ_rec = {Mdot_struct:.2f} M☉/yr")
print(f"  O175 率 = M_BH·φ⁻²¹/t_H = {Mdot_o175:.0f} M☉/yr")
for lbl, mu in (("錯誤 V_world", Mdot_v1), ("修正 ℒ=5e44", Mdot_c_5e44), ("修正 ℒ=1e45", Mdot_c_1e45)):
    print(f"    f_return vs Ṁ_UHECR({lbl:12s} {mu:8.1f}) = {Mdot_struct/mu:.4f}")
ck("f_return 由 0.80 修正為 ~0.01 (ℒ=1e45)", abs(Mdot_struct/Mdot_c_1e45-0.01) < 0.005,
   f"({Mdot_struct/Mdot_c_1e45:.4f})")
print(f"  O175 率/Ṁ_UHECR(修正 1e45) = {Mdot_o175/Mdot_c_1e45:.2f} (vs docs/15 用錯值之 210.9×)")
ck("docs/15 之「210.9×」需更正為 ~2.6×", abs(Mdot_o175/Mdot_c_1e45 - 2.59) < 0.1,
   f"({Mdot_o175/Mdot_c_1e45:.2f})")

# ---- E. 總結 ----
print("\n"+"="*78); print("總結"); print("="*78)
print(f"  ★ Root cause: O173 s01 用 V_world=2.95e11 算 Ṁ_UHECR; M_BH 用 V_comov=1.2e13")
print(f"     (同款錯誤 O175 s08 已診斷過: 'factor 40.7')")
print(f"  ★ τ_ref: 7.1247e16 → **{tau_ref_c_1e45:.3e} yr** (修正)")
print(f"  ★ G8 dev: +24.56% → **x{tau_pred/tau_ref_c_1e45:.1f}** (吻合消失)")
print(f"  ✓ 下界一致性 τ_pred ≥ τ_ref 仍成立 (冇證偽)")
print(f"  ★ f_return: 0.8028 → **{Mdot_struct/Mdot_c_1e45:.4f}**")
print(f"  ★ 需更正: docs/14 (§①), docs/15 (§①「210.9×」), 01_problem_record, final_result, register")

out = {
 "problem": "O121/G8 τ_ref 體積一致性審計",
 "volumes": {"V_comov_Mpc3": V_comov, "V_world_Mpc3": V_world, "ratio": V_comov/V_world},
 "A_G8_reproduction": {"M_BH_Msun": M_BH, "Mdot_uhecr_used": Mdot_v1,
                        "tau_ref_used_yr": tau_ref_G8,
                        "V_used_MBH_Mpc3": V_comov, "V_used_Mdot_Mpc3": V_world,
                        "mixed_volumes": (V_comov != V_world)},
 "B_corrected": {"Mdot_uhecr_1e45": Mdot_c_1e45, "Mdot_uhecr_5e44": Mdot_c_5e44,
                  "tau_ref_1e45_yr": tau_ref_c_1e45, "tau_ref_5e44_yr": tau_ref_c_5e44,
                  "overestimate_factor": r1},
 "C_reeval": {"tau_pred_yr": tau_pred,
               "dev_vs_1e45": tau_pred/tau_ref_c_1e45 - 1,
               "dev_vs_5e44": tau_pred/tau_ref_c_5e44 - 1,
               "lower_bound_satisfied": tau_pred >= tau_ref_c_1e45,
               "verdict": "+24.56% 吻合係體積假象; 下界仍滿足, 無吻合"},
 "D_f_return": {"Mdot_structural": Mdot_struct, "Mdot_o175": Mdot_o175,
                 "f_return_corrected_1e45": Mdot_struct/Mdot_c_1e45,
                 "f_return_G8_used": Mdot_struct/Mdot_v1,
                 "o175_over_uhecr_corrected": Mdot_o175/Mdot_c_1e45},
 "verdict": "G8 root-cause: τ_ref 混用體積; +24.56% 假象; 修正 gap ~100×",
}
with open(os.path.join(BASE,"data","16_tau_ref_volume_audit.json"),"w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nRESULT: {PASS} PASS, {FAIL} FAIL  {'🟢' if FAIL==0 else '🔴'}")
if FAIL: exit(1)
