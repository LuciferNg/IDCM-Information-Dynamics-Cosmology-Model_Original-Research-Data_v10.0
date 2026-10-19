# -*- coding: utf-8 -*-
"""
O142 scripts/24 — Λ 尺度機制裁決 (v16 閉合確認 + O38 獨立 pin 可行性審計)
=========================================================================
觸發: 用戶 2026-10-19「處理 O38 的 Λ 尺度機制問題」
性質: 獨立重算 (由零起, 唔 re-run 原 scripts/10/13) + 裁決
背景: O38 記錄 (row 46 / docs/27 §2·§4 / final_result §238) 標「O142 Λ_IDCM (QCD Λ 尺度)
      機制仍開放」, 引用 O142 docs/13 §4 (v14)。O142 docs/16 (v16) 已將機制⑥ 🟡→🟢。
      本腳本 (A) 獨立重算 v16 閉合, (B) 審計 Λ 可否做 N_O38 嘅 independent pin。
判準: 結構強逼 ≫ 數值吻合; 禁看到目標凑算子; σ 用輸入精度傳播
運行: /usr/bin/python3 (mpmath 高精度).  PYTHONDONTWRITEBYTECODE=1
"""
import mpmath as mp

mp.mp.dps = 50
PASS = 0; FAIL = 0
def chk(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  [PASS] {name}  {detail}")
    else:    FAIL += 1; print(f"  [FAIL] {name}  {detail}")

# ── 結構常數 (K_chain ⊗ K_tree; 零自由參數) ──────────────────────────────
B     = mp.mpf(4)      # 規範分支 / 4-simplex
N_gen = mp.mpf(3)      # 世代
L5    = mp.mpf(11)     # L₅ = N_d/B
N_d   = mp.mpf(44)     # 半鏈站點
L4    = mp.mpf(7)      # L₄ = Tr(T̂⁴)
M0    = mp.mpf("27.900915")     # MeV  (K_chain 基底標度; O38/O142)
MZ    = mp.mpf("91.1876")       # GeV  (M_Z)
hbar_w_ring = mp.mpf("1.548431574e-39")   # MeV (O38 維度錨)
N_O38 = mp.mpf("1.80188233461e40")

print("="*78)
print("A. Λ_IDCM 機制獨立重算 (O142 v16, docs/16)")
print("="*78)

# ρ = N_gen/L₅ = B·N_gen/N_d
rho = N_gen/L5
chk("ρ = N_gen/L₅ = B·N_gen/N_d",
    abs(N_gen/L5 - B*N_gen/N_d) < mp.mpf("1e-40"),
    f"= {mp.nstr(rho,20)}")

# 補角恆等: 20/88 = 1/2 − 3/11  (mode-20 = 全世代模式 m=24 之補角 partner)
Ngen_v = mp.mpf(3)
m_mode = 2*B*N_gen            # = 24 = 2B·N_gen
chk("m = 2B·N_gen = 24, m/(2N_d) = ρ", abs(m_mode/(2*N_d) - rho) < mp.mpf("1e-40"), f"= {mp.nstr(m_mode/(2*N_d),20)}")
chk("補角: 20/88 = 1/2 − 3/11 (⟹ γ₂₀ = 4cos²(ρπ))",
    abs(mp.mpf(20)/88 - (mp.mpf(1)/2 - mp.mpf(3)/11)) < mp.mpf("1e-45"), "")

# γ₂₀ 兩徑一致
g20_sin = 4*mp.sin(20*mp.pi/88)**2
g20_cos = 4*mp.cos(Ngen_v*mp.pi/11)**2
print(f"  γ₂₀ (4sin²(20π/88)) = {mp.nstr(g20_sin,25)}")
print(f"  γ₂₀ (4cos²(3π/11))  = {mp.nstr(g20_cos,25)}")
chk("γ₂₀ 兩徑 EXACT 一致", abs(g20_sin-g20_cos) < mp.mpf("1e-40"))

# λ_max = B·N_gen² − 1/γ₂₀
lmax = B*N_gen**2 - 1/g20_cos
chk("λ_max = B·N_gen² − 1/γ₂₀", abs(lmax - (mp.mpf(36) - 1/g20_cos)) < mp.mpf("1e-40"),
    f"= {mp.nstr(lmax,25)}")

# Λ_IDCM = ρ√λ_max·M₀
Lam = rho*mp.sqrt(lmax)*M0
print(f"  Λ_IDCM = ρ·√λ_max·M₀ = {mp.nstr(Lam,15)} MeV   (定點 45.2849)")
chk("Λ_IDCM ≈ 45.2849 MeV (定點)", abs(Lam-mp.mpf("45.2849")) < mp.mpf("1e-3"), f"dev {mp.nstr((Lam-mp.mpf('45.2849'))/mp.mpf('45.2849')*100,5)}%")
# 舊式等價
chk("等價舊式 √λ_max·M₀·N_gen/L₅", abs(rho*mp.sqrt(lmax)*M0 - mp.sqrt(lmax)*M0*N_gen/L5) < mp.mpf("1e-40"))
chk("√λ_max·M₀ = 166.0445 (docs/16 §6)", abs(mp.sqrt(lmax)*M0 - mp.mpf("166.0445")) < mp.mpf("1e-3"), f"= {mp.nstr(mp.sqrt(lmax)*M0,10)}")

print()
print("="*78)
print("B. α_s(M_Z) 閉合 (1-loop RGE, Nf=6)")
print("="*78)
ainv = (L4/(2*mp.pi))*mp.log(MZ*1000/Lam)
as_pred = 1/ainv
print(f"  α_s⁻¹(M_Z) = (L₄/2π)·ln(M_Z/Λ) = {mp.nstr(ainv,15)}")
print(f"  α_s(M_Z)   = {mp.nstr(as_pred,15)}")
for w, s in [("0.1180","0.0009"), ("0.1179","0.0009"), ("0.1181","0.0011")]:
    aw = mp.mpf(w); sw = mp.mpf(s)
    print(f"    vs PDG {w}±{s}: dev {mp.nstr((as_pred-aw)/aw*100,6)}%  σ={mp.nstr((as_pred-aw)/sw,4)}")
print("  (O142 docs/11 §3.1 定點: α_s⁻¹=8.47562 vs PDG 8.47458 → +0.012%, 0.016σ)")

print()
print("="*78)
print("C. ★ Λ 作 N_O38 independent pin — 可行性審計")
print("="*78)
print("  pin 邏輯: M₀ = Λ_req/(ρ√λ_max), Λ_req 由 α_s 經 1-loop RGE 反推")
for w in ["0.1179","0.1180"]:
    aw = mp.mpf(w); ainv_w = 1/aw
    Lam_req = MZ*1000*mp.exp(-2*mp.pi*ainv_w/L4)
    M0_pin  = Lam_req/(rho*mp.sqrt(lmax))
    print(f"    α_s={w}: Λ_req={mp.nstr(Lam_req,10)} MeV → M₀={mp.nstr(M0_pin,10)} MeV (dev {mp.nstr((M0_pin-M0)/M0*100,5)}%)")

# 精度傳播 (核心阻斷): δα_s 經指數關係放大
das = mp.mpf("0.0009"); as0 = mp.mpf("0.1179")
d_ainv = das/as0**2
dlnM   = (2*mp.pi/L4)*d_ainv
print(f"\n  ★ 精度傳播: δα_s = {das}")
print(f"     δα_s⁻¹ = δα_s/α_s² = {mp.nstr(d_ainv,6)}")
print(f"     δlnΛ = δln M₀ = (2π/L₄)·δα_s⁻¹ = (2π/7)·{mp.nstr(d_ainv,5)} = {mp.nstr(dlnM,6)}")
print(f"     ⟹ δM₀/M₀ = {mp.nstr(dlnM*100,4)} %   (即 M₀ = 27.9009 ± {mp.nstr(dlnM*100,3)}% = ±{mp.nstr(dlnM*M0,4)} MeV)")
print(f"     ⟹ δN/N  = {mp.nstr(dlnM*100,4)} %  (N_O38 CD 直傳)")
chk("★ Λ-pin 精度 > 1% (唔足以閉合 N_O38, 需 ~0.1%)", dlnM > mp.mpf("0.01"),
    f"δM₀/M₀ = {mp.nstr(dlnM*100,3)}%")
# 同源論證
chk("★ Λ_IDCM ∝ M₀ (同源: 公式自帶 M₀, 零獨立資訊)",
    abs(Lam/M0 - rho*mp.sqrt(lmax)) < mp.mpf("1e-30"), "Λ/M₀ = ρ√λ_max = 常數")

print()
print("="*78)
print("D. 循環性審計 — 3/11 (ρ) 係唔係由 α_s 反選?")
print("="*78)
# v13 density scan: ratio_target = strong_scale/Λ_1loop(world α_s)
strong_scale = mp.sqrt(lmax)*M0         # = 166.0445 (docs/11 §3.3: strong_scale)
Lam_world    = MZ*1000*mp.exp(-2*mp.pi*(1/mp.mpf("0.1180"))/L4)
ratio_target = strong_scale/Lam_world
ratio_115    = L5/N_gen                  # 11/3
print(f"  strong_scale = √λ_max·M₀ = {mp.nstr(strong_scale,10)} MeV")
print(f"  Λ_world(α_s) = {mp.nstr(Lam_world,10)} MeV")
print(f"  ratio_target = strong_scale/Λ_world = {mp.nstr(ratio_target,10)}")
print(f"  L₅/N_gen = 11/3 = {mp.nstr(ratio_115,10)}   dev {mp.nstr((ratio_115-ratio_target)/ratio_target*100,6)}%")
chk("★ ρ = N_gen/L₅ 與 α_s-反選值一致 ⟹ α_s-as-anchor 局部循環 (不可作獨立證據)",
    abs((ratio_115-ratio_target)/ratio_target) < mp.mpf("0.02"),
    f"dev {mp.nstr((ratio_115-ratio_target)/ratio_target*100,4)}%")

print()
print("="*78)
print("E. 判決")
print("="*78)
verdict = [
 ("A  機制⑥ 閉合 (v16)", "🟢", "Λ = ρ√λ_max·M₀ 單參數 ρ 函數, 六判據全綠 (docs/16 §5)"),
 ("B  α_s 閉合", "🟢", f"α_s(M_Z) = {mp.nstr(as_pred,8)} vs PDG 0.1179-0.1180 (0.016σ)"),
 ("C  Λ 作獨立 pin", "🔴", f"δM₀/M₀ = {mp.nstr(dlnM*100,3)}% (精度不足) + ∝M₀ 同源"),
 ("D  α_s 錨循環性", "🔴", "ρ=N_gen/L₅ 由 α_s 反選 (v13 density scan)"),
 ("E  → N_O38 閉合", "🔴", "冇 independent pin 改動; 缺口維持 (O38/m0-scale open)"),
]
for name, st, note in verdict:
    print(f"  {st}  {name:22s} {note}")

print()
print(f"檢查: {PASS} PASS / {FAIL} FAIL")
import sys
sys.exit(0 if FAIL == 0 else 1)