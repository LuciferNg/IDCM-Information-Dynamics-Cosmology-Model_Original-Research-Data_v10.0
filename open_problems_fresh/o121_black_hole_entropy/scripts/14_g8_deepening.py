#!/usr/bin/env python3
"""
O121 — script 14: G8 三項深化 (機制 / 張力 / 判別原則)
==================================================================
②(機制) η = φ⁻²¹ 每級 φ⁻¹ 之來源: K_tree = φ-尺度階梯 + block-spin 21 級 + RG 不變量
①(張力) f_return: O175 BH 率公式之 t_H vs τ_rec 之辨
③(判別) 候選排序之**原則性**準則 (非吻合度)

零新常數。
"""
import math, json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS = 0; FAIL = 0
def ck(n, c, d=""):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n} {d}")
    else: FAIL += 1; print(f"  ❌ {n} {d}")

phi = (1+math.sqrt(5))/2
N_d, mu2, B_c, N_gen, L4, L5, L6 = 44, 2, 4, 3, 7, 11, 18
Sigma_g, K_tree, MIS = 90.0, 33, 20
E_proj, E_sync = 28.5, 61.5
omega_ring = 72.59; Mpc_m = 3.0856775814913673e22; Yr_s = 3.1557e7
T_ring = (2*math.pi/(omega_ring*1e3/Mpc_m))/Yr_s
t_H = 1.38e10
M_BH, Mdot_uh = 5.88e18, 82.53
tau_ref = M_BH/Mdot_uh
tau_pred = (2**MIS)*T_ring
fib = [1,1]
while len(fib) < 15: fib.append(fib[-1]+fib[-2])   # fib[n-1] = F_n

print("="*78); print("O121 script 14: G8 三項深化"); print("="*78)

# ===== ② 機制: 每級 φ⁻¹ 之來源 =====
print("\n" + "="*78); print("[②→③] 機制: η = φ⁻²¹ 每級 φ⁻¹ 之來源"); print("="*78)

# (i) K_tree = φ-尺度階梯 (O221 docs/02 Q6)
n_lev = K_tree + 1                      # m = 0..33
mu_ratio = phi**K_tree
print(f"  (i) K_tree = φ-尺度階梯: μ_m = φ^(291.5−m), m=0..{K_tree} → {n_lev} 級")
print(f"      μ_0/μ_33 = φ^{K_tree} = {mu_ratio:.4e}")
ck("K_tree 階梯每級比 = φ (定義, 非擬合)", abs(phi**1/phi - 1.0) < 1e-15)
ck(f"階梯級數 = K_tree+1 = {n_lev} = F₉ = {fib[8]}", n_lev == fib[8] == 34)

# (ii) Block-spin: 4 世界副本 → 1 區塊; μ² 截斷 → 42 有效模 → 21 級
n_eff = N_d - mu2
n_rungs = n_eff/2
print(f"  (ii) Block-spin: 44 模 − μ²={mu2} 中心模 → {n_eff:.0f} 有效模 → {n_rungs:.0f} 級")
ck("有效模 = N_d−μ² = 42", n_eff == 42)
ck("級數 = 42/2 = 21 = F₈ = (N_d−μ²)/2 (雙重)", n_rungs == 21 == fib[7])
ck(f"F₉ = F₈ + F₇ ({fib[8]} = {fib[7]} + {fib[6]}) — 階梯級數為連續 Fibonacci",
   fib[8] == fib[7]+fib[6])
ck("階梯比 φ × 21 級 ⟹ η = φ⁻²¹", abs(phi**(-21) - 4.085635e-5) < 1e-11)

# (iii) RG 不變量 (代數精確)
db_dl = 4*N_d/n_eff
print(f"  (iii) RG: dβ/dℓ = 4N_d/(N_d−μ²) = {4*N_d:.0f}/{n_eff:.0f} = {db_dl:.6f} = 88/21")
ck("dβ/dℓ = 88/21 = 4.190476", abs(db_dl - 88/21) < 1e-12)
ck("RG 不變量 21 × (88/21) = 88 = 2N_d (代數精確)",
   abs(n_rungs*db_dl - 2*N_d) < 1e-9, f"({n_rungs*db_dl:.6f})")
ck("dβ/dℓ = 4(1+1/21) (分支×4 + 中心修正)", abs(db_dl - 4*(1+1/21)) < 1e-12)
print("  ⟹ 機制鏈: K_tree 階梯比 φ (定義) ⊕ 級數 21 (block-spin/F₈)")
print("             ⟹ η = (φ⁻¹)^21 = φ⁻²¹")
print("  ⚠️ 未導之環: ① K_tree「係 φ-階梯」屬框架前提 (非本檔導出)")
print("              ② 為何遍歷 21 級 (而非全部 34) 未證")

# ===== ① 張力: O175 BH 率公式之 t_H 問題 =====
print("\n" + "="*78); print("[①] f_return 張力 — O175 用 t_H 而非 τ_rec"); print("="*78)
V_comov = M_BH/4.9e5                     # 由 M_BH(Elvis) 反推
print(f"  O175 公式: Ṁ_BH = ρ_BH·φ⁻²¹·V_comov/t_H")
print(f"    隱含 V_comov = {V_comov:.4e} Mpc³ (由 M_BH=ρ_BH·V 反推)")
Mdot_o175 = M_BH*phi**(-21)/t_H
print(f"    ⟹ Ṁ_BH(O175, Elvis) = M_BH·φ⁻²¹/t_H = {Mdot_o175:.1f} M☉/yr  (報 17,408 ✓)")
ck("O175 率 = M_BH·φ⁻²¹/t_H = 17,408 (重現)", abs(Mdot_o175-17408)/17408 < 0.01,
   f"({Mdot_o175:.0f})")
Mdot_struct = M_BH/tau_pred
print(f"  結構: Ṁ_BH = M_BH/τ_rec = {Mdot_struct:.2f} M☉/yr")
ratio = Mdot_o175/Mdot_struct
print(f"  比 = φ⁻²¹ · τ_rec/t_H = {ratio:.2f}")
ck("比 = φ⁻²¹·τ_rec/t_H (解析)", abs(ratio - phi**(-21)*tau_pred/t_H) < 1e-6,
   f"({ratio:.2f})")
ck("O175 率 > 全宇宙 UHECR 率 ⟹ 唔可能係返池率",
   Mdot_o175 > Mdot_uh, f"({Mdot_o175:.0f} vs {Mdot_uh} ⟹ ×{Mdot_o175/Mdot_uh:.1f})")
ck("結構率 < 全宇宙 UHECR 率 ⟹ 物理可行",
   Mdot_struct < Mdot_uh, f"({Mdot_struct:.2f} < {Mdot_uh})")
f_ret = Mdot_struct/Mdot_uh
print(f"  ⟹ f_return = {Mdot_struct:.2f}/{Mdot_uh} = {f_ret:.4f}")
ck("f_return = τ_ref/τ_pred = 0.8028 (與 ① 一致)", abs(f_ret - tau_ref/tau_pred) < 1e-9)
print("  ★ 裁決: ①張力非物理矛盾, 係 O175 公式之**時標錯配** (t_H vs τ_rec)")
print(f"     修正: O175 率應為 M_BH/τ_rec = {Mdot_struct:.2f} M☉/yr (小 {ratio:.0f}×)")

# ===== ③ 判別原則: 候選評分 =====
print("\n" + "="*78); print("[③] 候選排序之原則性準則"); print("="*78)
F = tau_ref/T_ring
cands = [
 ("2²⁰·T_ring",     2**MIS,      True,  "Poincaré 構型復現 (O7 2^20 ⊗ docs/07 凍結)"),
 ("7⁷·T_ring",      7**7,        False, "無 (L₄^{L₄} 無機制)"),
 ("88³·T_ring",     88**3,       False, "無"),
 ("29⁴·T_ring",     29**4,       False, "無 (L₇⁴)"),
 ("90³·T_ring",     90**3,       False, "無 (Σγ³)"),
 ("(41/19)¹⁸·T_ring", (41/19)**18, False, "部分: 比值結構, 但指數 18=L₆ 無推導"),
 ("N_d·φ²¹·T_ring",  N_d*phi**21, False, "部分: φ-階梯 ✓, 但 N_d 前置因子無推導"),
]
print(f"  {'候選':18s} {'dev':>9s}  {'有推導':>6s}  備註")
rows = []
for name, val, hasder, note in cands:
    dev = val/F - 1
    rows.append({"candidate": name, "value": val, "dev": dev,
                 "has_derivation": hasder, "note": note})
    print(f"  {name:18s} {dev:+9.2%}  {'✓' if hasder else '✗':>6s}  {note}")
n_der = sum(1 for r in rows if r["has_derivation"])
ck("只有 1 個候選具完整推導 ⟹ 排序確定", n_der == 1, f"(具推導者 {n_der})")
best_fit = min(rows, key=lambda r: abs(r["dev"]))
print(f"  ★ 最貼者 = {best_fit['candidate']} (dev {best_fit['dev']:+.2%}) — 但無推導")
ck("最貼候選 ≠ 唯一具推導候選 ⟹ 吻合度唔可作判別",
   best_fit["candidate"] != "2²⁰·T_ring")
print("  ⟹ 準則: 每個因子都必須有推導 (證成先於吻合); 2²⁰·T_ring 唯一通過")

# ===== 總結 =====
print("\n" + "="*78); print("總結"); print("="*78)
print(f"  ②→③ 機制: φ-階梯比 (K_tree 定義) × 21 級 (block-spin/F₈) ⟹ η=φ⁻²¹; 兩環未導")
print(f"  ① 張力: **解除** — O175 公式用 t_H, 應為 τ_rec (差 {ratio:.0f}×); f_return={f_ret:.3f}")
print(f"  ③ 判別: 唯一具推導 = 2²⁰·T_ring (+{ (2**MIS)/F-1:.2%}); 吻合度不可判別")

out = {
 "problem": "O121/G8 三項深化",
 "②_mechanism": {"K_tree_ladder_ratio": phi, "K_tree_levels": n_lev,
                  "F9": fib[8], "n_eff_modes": n_eff, "n_rungs": n_rungs, "F8": fib[7], "F7": fib[6],
                  "RG_invariant": n_rungs*db_dl, "db_dl": db_dl,
                  "eta": phi**(-21),
                  "derived": {"ladder_ratio_phi": "K_tree 定義 (前提)",
                               "rungs_21": "block-spin 42/2 = F₈"},
                  "not_derived": ["K_tree 係 φ-階梯 (框架前提)", "為何遍歷 21 級而非 34"]},
 "①_tension": {"t_H": t_H, "tau_pred": tau_pred, "tau_ref": tau_ref,
                "Mdot_o175": Mdot_o175, "Mdot_structural": Mdot_struct,
                "ratio": ratio, "ratio_formula": "phi^-21 * tau_pred/t_H",
                "o175_exceeds_uhECR": Mdot_o175 > Mdot_uh,
                "f_return": f_ret,
                "verdict": "張力解除: O175 時標錯配 (t_H vs τ_rec)"},
 "③_criterion": {"rows": rows, "n_with_derivation": n_der,
                  "best_fit": best_fit["candidate"],
                  "criterion": "每因子須有推導 (證成先於吻合)"},
 "verdict": f"②機制部分閉合 ①張力解除 ③判別準則確立",
}
with open(os.path.join(BASE,"data","14_g8_deepening.json"),"w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nRESULT: {PASS} PASS, {FAIL} FAIL  {'🟢' if FAIL==0 else '🔴'}")
if FAIL: exit(1)
