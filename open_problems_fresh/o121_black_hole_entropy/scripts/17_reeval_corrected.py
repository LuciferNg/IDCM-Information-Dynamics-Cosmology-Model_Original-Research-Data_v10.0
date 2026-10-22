#!/usr/bin/env python3
"""
O121 — script 17: 修正後重評 (R 路線 + null test + 判別力)
============================================================
承 script 16 (τ_ref 體積修正)。三項待辦:
  ② R1a/R1b/R2a/R2b/R2c/R3 用修正 τ_ref 重評
  ③ null test 用校正 F 重算
  ① 「gap ×101」之正確定位 (下界 vs 目標)

零新常數。
"""
import math, json, os, random
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS = 0; FAIL = 0
def ck(n, c, d=""):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n} {d}")
    else: FAIL += 1; print(f"  ❌ {n} {d}")

phi = (1+math.sqrt(5))/2
N_d, mu2, K_tree, MIS, L6 = 44, 2, 33, 20, 18
dim_ker = 17
omega_ring = 72.59; Mpc_m = 3.0856775814913673e22; Yr_s = 3.1557e7
T_ring = (2*math.pi/(omega_ring*1e3/Mpc_m))/Yr_s
V_comov = 1.2e13; rho_BH = 4.9e5
M_BH = rho_BH*V_comov
L_uhecr = 1e45; ERG_TO_J = 1e-7; c_l = 2.99792458e8; M_sun = 1.989e30
Mdot_c = L_uhecr*ERG_TO_J/(M_sun*c_l**2)*V_comov
tau_ref = M_BH/Mdot_c                      # 修正後 (comoving 一致)
tau_pred = (2**MIS)*T_ring

print("="*78); print("O121 script 17: 修正後重評"); print("="*78)
print(f"\n  修正 τ_ref = {tau_ref:.5e} yr (comoving 一致)  |  T_ring = {T_ring:.5e}")
print(f"  F = τ_ref/T_ring = {tau_ref/T_ring:.5f}")

# ===== ② R 路線重評 =====
print("\n"+"="*78); print("[②] R 路線重評 (對修正 τ_ref)"); print("="*78)
routes = [
 ("R1b (主) 構型復現",  (2**MIS)*T_ring,        "Poincaré 2^20 ⊗ docs/07"),
 ("R1a 相位滑移對偶",   (dim_ker/N_d)*(2**MIS)*T_ring, "σ 反轉 × 17/44"),
 ("R2a η 階梯",         T_ring/phi**(-21),      "T_ring/η = φ²¹·T_ring"),
 ("R2b η 階梯 ×N_d",    N_d*T_ring/phi**(-21),  "44·φ²¹·T_ring"),
 ("R2c η 階梯 ×dim_ker",dim_ker*T_ring/phi**(-21),"17·φ²¹·T_ring"),
 ("R3 主通道反推",      M_BH/(V_comov*0+6730.86), "M_BH/R_rel"),
]
print(f"  {'路線':22s} {'值 (yr)':>13s} {'vs 舊 τ_ref':>12s} {'vs 修正 τ_ref':>14s}")
rows = []
for name, val, note in routes:
    d_old = val/7.1247e16 - 1; d_new = val/tau_ref - 1
    rows.append({"route": name, "value": val, "dev_old": d_old, "dev_new": d_new, "note": note})
    print(f"  {name:22s} {val:13.5e} {d_old:+12.2%} {d_new:+14.2%}")
ck("R1b..R2c 全部滿足下界 τ ≥ τ_ref (修正)", all(r["value"] >= tau_ref for r in rows[:5]))
best = min(rows, key=lambda r: abs(r["dev_new"]))
print(f"  ★ 修正後最近 = {best['route']} (dev_new {best['dev_new']:+.1%})")
ck("R1b 由 +24.56% 變為 ≫100% (吻合消失)", rows[0]["dev_new"] > 100, f"(x{1+rows[0]['dev_new']:.0f})")
ck("R3 ≈ τ_ref (恆等: 用 R_rel=6730.86 vs 重算 6712.8, 差 0.27%)", abs(rows[5]["value"]/tau_ref - 1) < 0.005, f"({rows[5]['value']/tau_ref-1:+.4%})")
print("  ★ 關鍵: 所有路線皆在**下界之上** ⟹ 觀測界**無法判別**路線")

# ===== ③ null test 重算 =====
print("\n"+"="*78); print("[③] Numerology null test 重算 (F 校正)"); print("="*78)
VOCAB = [2,3,4,5,7,8,9,11,13,17,18,19,20,21,22,26,29,33,36,41,42,44,45,46,55,57,61,88,90,98,123,176,264,421]
def hits(t, tol):
    return [(X,Y) for X in VOCAB for Y in range(1,51) if abs(X**Y/t - 1) <= tol]
F_old, F_new = 7.1247e16/T_ring, tau_ref/T_ring
print(f"  F_old = {F_old:.4e}   F_new = {F_new:.4e}")
print(f"  {'窗':>5s} {'觀察 (新 F)':>12s} {'形式':>26s} {'隨機期望':>9s}")
random.seed(20261002)
res = {}
for tol in (0.25, 0.10, 0.03):
    h = hits(F_new, tol)
    arr = [len(hits(math.exp(random.uniform(math.log(1e3), math.log(1e6))), tol)) for _ in range(3000)]
    exp = sum(arr)/len(arr)
    res[f"tol_{tol}"] = {"observed": len(h), "forms": h, "expected": exp}
    print(f"  ±{tol*100:4.0f}% {len(h):12d} {str(h)[:26]:>26s} {exp:9.2f}")
ck("±25% 匹配仍唔稀有 (觀察 ≈ 期望)", res["tol_0.25"]["observed"] <= max(2, math.ceil(res["tol_0.25"]["expected"]*2)),
   f"({res['tol_0.25']['observed']} vs {res['tol_0.25']['expected']:.2f})")
best_fit = min(hits(F_new, 0.25), key=lambda xy: abs(xy[0]**xy[1]/F_new-1))
print(f"  ★ 最貼形式 (新 F) = {best_fit[0]}^{best_fit[1]} = {best_fit[0]**best_fit[1]:.0f} "
      f"(dev {best_fit[0]**best_fit[1]/F_new-1:+.2%})")
ck("最貼形式 ≠ 2^20 (pd)", not (best_fit[0] == 2 and best_fit[1] == MIS))
print("  ⟹ 方法學結論不變: 數值匹配證據權重低 (且 R1b 現為 x101, 連 ±25% 都唔入)")

# ===== ① gap 之正確定位 =====
print("\n"+"="*78); print("[①] 「gap ×101」之正確定位"); print("="*78)
slack = tau_pred/tau_ref
print(f"  τ_ref = M_BH/Ṁ_UHECR 係**下界** ('全 UHECR 當 BH 流失' 之最寬鬆假設)")
print(f"  ⟹ 冇『gap』可言 — 只需要 τ_pred ≥ τ_ref; 現 slack = x{slack:.1f}")
print(f"     (即觀測只排除 τ_rec < {tau_ref:.3e} yr)")
ck("τ_pred ≥ τ_ref ⟹ 冇證偽", tau_pred >= tau_ref)
print(f"  ★ 真問題: 下界太鬆 (slack x{slack:.0f}) ⟹ **無法判別路線**")
print(f"  ★ 要判別, 需要**獨立**觀測量 (非 M_BH/Ṁ_UHECR), 例如:")
print(f"     (i) BH 源 UHECR 佔比 f = Ṁ_struct/Ṁ_UHECR = {M_BH/tau_pred/Mdot_c:.4f} (~1%)")
print(f"     (ii) σ_n 譜之 n↔E 映射 (P-G8f; 需導出)")
print(f"     (iii) 黑洞質量函數低端 (P-G8c)")
print(f"     (iv) 最小黑洞質量 M_crit = 7.9e4 kg (P-G8d)")

# ===== 總結 =====
print("\n"+"="*78); print("總結"); print("="*78)
print(f"  ② R 路線: 全部 ≥ 修正 τ_ref ⟹ 觀測界無法判別; R1b 由 +24.56% → x{1+rows[0]['dev_new']:.0f}")
print(f"  ③ null test: F {F_old:.3e} → {F_new:.3e}; 匹配仍唔稀有 ⟹ 結論不變")
print(f"  ① 「gap」定位更正: τ_ref 係下界, 非目標 ⟹ 冇 gap; 真問題 = 下界太鬆 (x{slack:.0f})")
out = {
 "problem": "O121/G8 修正後重評",
 "tau_ref_corrected_yr": tau_ref, "tau_pred_yr": tau_pred, "F_new": F_new, "F_old": F_old,
 "②_routes": rows, "best_route_new": best["route"], "all_above_bound": all(r["value"]>=tau_ref for r in rows),
 "③_null": res, "③_best_form": list(best_fit),
 "①_framing": {"lower_bound_satisfied": tau_pred >= tau_ref, "slack": slack,
                "verdict": "τ_ref 係下界非目標 ⟹ 冇 gap; 真問題 = 下界太鬆 (x%.0f) ⟹ 無法判別" % slack},
 "discriminating_observables": ["BH 源 UHECR 佔比 f~1%", "σ_n 之 n↔E 映射", "黑洞質量函數低端", "M_crit = 7.9e4 kg"],
}
with open(os.path.join(BASE,"data","17_reeval_corrected.json"),"w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nRESULT: {PASS} PASS, {FAIL} FAIL  {'🟢' if FAIL==0 else '🔴'}")
if FAIL: exit(1)
