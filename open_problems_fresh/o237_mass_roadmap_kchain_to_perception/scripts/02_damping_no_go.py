#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O237 U6 — 「質量 = 相位同步嘅時序阻尼」假說: Γ 算子構造檢驗 + 結構 no-go
================================================================================
docs/01 §五 三分裁定: 偏差層 ✅ (γ=|1-U|^2) / 時序層 🟡 (頻率=beat) / 阻尼層 🔴 (冇機制)
本 script 執行 U6 升格條件檢驗 (docs/01 §五「升格條件」①-④):
  §1 條件①: damping 率算子 Γ(γ_n) 必須係 𝒯 內 operator identity (O210: 七運算無禁令算子)
     -> 檢查 𝒯 算子目錄係咪冇 dissipative 元素
  §2 條件②: 同一 Γ 一致推出 m = M0 γ F (或 m = M0 sqrt γ) —— 唔可以只 fit 一個粒子
     -> 測試 γ^p 冪律 (𝒯 唯一可由 γ̂ 生成嘅候選族) 喺 A5 C_f 上嘅一致性
  §3 條件④: 獨立預言 (mass decay / decoherence 時標) vs 觀測 (電子壽命 PDG)
  §4 收口裁定: 維持「相位同步偏差」命名, 阻尼 = 🔴 未定義
"""
import mpmath as mp
mp.mp.dps = 50

PASS, FAIL = [], []
def ck(name, got, exp, tol=None):
    if tol is not None:
        ok = abs(mp.mpf(got) - mp.mpf(exp)) < mp.mpf(tol)
    else:
        ok = bool(got == exp)
    (PASS if ok else FAIL).append(name)
    print(f"  {'OK ' if ok else 'FAIL'} {name} = {got}" + ("" if ok else f"  [exp {exp}]"))

print("="*88)
print("O237 U6 — 阻尼假說 no-go: Γ(γ) 升格條件檢驗")
print("="*88)

N_HALF = 44
TICK_YR = 8.463654e10/88.0            # tick = T_ring/88 (O235 T1 EXACT)
TAU_ELEC_PDG = 6.6e28                 # 電子壽命下界 (yr, PDG)

def gam(n): return 4*mp.sin(mp.mpf(n)*mp.pi/88)**2

print(f"\n[*] tick = T_ring/88 = {TICK_YR:.6e} yr  (O235 T1)")
print(f"[*] 電子壽命下界 = {TAU_ELEC_PDG:.1e} yr (PDG)")

# ================================================================ §1 條件①
print("\n" + "="*88)
print("§1 條件①: Γ 算子必須係 𝒯 內 operator identity (O210 型別層, 零新常數)")
print("="*88)
print("""𝒯 七運算: ⊗, ⊕, Tr, Spec, Proj, †, Contr — codomain ∈ {Op, Sc, Sc×Op} (O210-T2)。
Operator 目錄 (O210 Four Types): T̂, K_chain, K_tree, Ω̂, v̂_g, U, γ̂, P_world, P_CY,
T_pipe, J². 全部 = 么正 / 投影 / 正算子, 冇 dissipative channel:
  - 么正 (U, T̂, Ŝ): 譜喺單位圓 |λ|=1, 冇衰減
  - 投影 (P_world, P_CY, T_pipe): 譜 ∈ {0,1}, 冇率
  - 正算子 (γ̂, K_tree): 譜 ∈ ℝ⁺, 冇時間演化
⟹ 𝒯 內【唔存在】「衰減率」類型算子; 任何 Γ(γ_n) 只可以由 γ̂ 嘅譜泛函構造。""")
# 唯一候選族: Γ_p = γ^p / tick (有 rate 因次; 由 Spec∘γ̂ 生成, zero new constant)
print("唯一零新常數候選族: Γ_p = γ^p / tick   (p>0, 由 Spec∘γ̂ 生成)")
g1 = gam(1)
print(f"  γ₁ = {mp.nstr(g1,10)}")

# 質量衰變時標 τ_n = 1/Γ_p = tick / γ_n^p; 最穩定粒子 n=1 必須 τ₁ > PDG 下界
def tau1(p):
    return TICK_YR / (g1**p)
print("\n  電子穩定性檢驗 (質量若係 damped, τ₁ 必須 > 6.6e28 yr):")
all_unstable = True
for p in [mp.mpf(1)/2, 1, 2, 3, 4, 6, 8, 9, 10]:
    t1 = tau1(p)
    stable = t1 > TAU_ELEC_PDG
    if p <= 8 and stable:
        all_unstable = False
    print(f"    p = {mp.nstr(p,3):>5}: τ₁ = {mp.nstr(t1,6):>12} yr  {'✅ 穩' if stable else '❌ 過快衰變'}")
# p=9 開始穩 (log 條件 p > ln(tick/τ_PDG)/ln γ₁)
p_crit = mp.log(TICK_YR/TAU_ELEC_PDG)/mp.log(g1)
print(f"    ★ 穩定性要求 p > {mp.nstr(p_crit,5)}  (p≤8 全軍覆沒)")
ck("候選族 Γ_p: p≤8 被電子穩定性排除 (no-go 成立)", all_unstable, True)

# ================================================================ §2 條件②
print("\n" + "="*88)
print("§2 條件②: 同一 Γ 一致推出質量 (O206 第十輪 A5 C_f)")
print("="*88)
# O206 第十輪 (2026-10-06): A5 合法 modes {1,2,3,4,5,7,9,11,13}; C_f = m/(M0 γ_n)
# C_f 實測 (O206 docs/01 §D, 8 費米子, t 已歸 VEV):
CF_OBS = {1:3.5941, 2:3.8029, 3:3.6620, 4:41.3207, 5:30.0309, 7:186.0605, 9:159.6437, 11:255.7517}
MODES = list(CF_OBS)
print("A5 C_f 實測 (O206 第十輪):")
for n in sorted(CF_OBS): print(f"    n={n:>2}: C_f = {CF_OBS[n]:.4f}")
print("""
若 Γ_p 係「質量格」之來源, 質量公式係 m = M0 γ F ∝ γ^p 形:
C_f(p; n) = (γ_n)^p × const.  ⟹ 全部比為 γ 冪比: C(n)/C(1) = (γ_n/γ_1)^p。
單一 p 必須一次過 fit 7 個比 (n=2,3,4,5,7,9,11)。""")
best_p, best_dev = None, None
for pk in range(1, 80):
    p = pk/mp.mpf(40)
    devs = [abs((gam(n)/g1)**p - CF_OBS[n]/CF_OBS[1])/(CF_OBS[n]/CF_OBS[1]) for n in MODES if n != 1]
    md = max(devs)
    if best_dev is None or md < best_dev:
        best_dev, best_p = md, p
print(f"  ★ 最佳單一 p = {mp.nstr(best_p,5)}: max dev = {mp.nstr(best_dev*100,4)}%")
ck("單一 Γ_p 唔可以一致 fit 全部 A5 C_f (no-go 成立)", best_dev > 0.01, True)
print("  (O206 第十輪已定案: C_f 生成器開放, 非 γ 冪律; 此處重現該結論)")

# ================================================================ §3 條件④
print("\n" + "="*88)
print("§3 條件④: 獨立預言 (decoherence 幅度) vs 觀測")
print("="*88)
# 質量衰變/decay 觀測: 電子最穩定 (PDG τ > 6.6e28 yr); 質子 τ_p = ∞ (O88 no-go)
# 質量 ∝ damped 相 -> 每個粒子都有特徵衰變; e 喺 p≤8 已死 (時間尺 1e9-1e12 yr)
print("  若存在 Γ: 每粒子有質量衰變時標 τ_n = tick/γ_n^p, 階層 τ_e ≫ τ_t (γ₁≪γ₁₃)。")
print("  觀測: 電子穩定到 6.6e28 yr; 質子無衰變 (O88 τ_p=∞ no-go) ⟹ 冇質量衰變通道。")
# 對照: τ_rec (O121) 係返池時標唔係阻尼; L7 (O213) 係細化流唔係耗散流
# 結構聲稱 (O208): 質量衰變通道不存在 = O88 no-go / O210-T2 文檔化; 非本 script 可數值化
print("  ├ 質量衰變通道不存在: O88 no-go / O210-T2 (文檔化結構聲稱, 🟡 唔入 PASS 計數)")
print("  └ (τ_rec = 2^20·T_ring 係 Poincaré 構型復現時標, 非阻尼——O121 docs/13 附錄)")

# ================================================================ §4 收口
print("\n" + "="*88)
print("§4 收口裁定 (docs/01 §五 維持)")
print("="*88)
print(f"""  ① Γ identity: 唯一候選族 Γ_p = γ^p/tick, p≤8 被電子穩定性排除; p≥9 冇 𝒯 身份
     (γ̂⁹ 唔係結構量) ⟹ 無合法 Γ.  {'' if all_unstable else 'TODO'}
  ② Γ 一致推質量: γ 冪律 max dev {mp.nstr(best_dev*100,4)}% ≫ 1% ⟹ 唔成立.
  ③ 凍結層比對: 冇 Γ 冇得比 (N/A).
  ④ 獨立預言: 冇觀測載體 (質量衰變通道不存在; τ_rec/L7 皆非阻尼).
  ⟹ 升格條件全數未達. 維持「相位同步偏差」命名; 阻尼 = 🔴 未定義假說.
  三分裁定定案: 偏差層 ✅ / 時序層 🟡 / 阻尼層 🔴 (docs/01 §五 + 本 U6 收口).""")

print("\n" + "="*88)
print(f"U6 checks: {len(PASS)} PASS / {len(FAIL)} FAIL")
print("="*88)
print("PASS" if not FAIL else "FAIL")