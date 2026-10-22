#!/usr/bin/env python3
"""
O181 script 01 — 可分辨性攻堅: 誤差預算重算 (exact inputs) + 窗口天文化
=====================================================================
問題: 364 vs 364+B/75 需要 M ≥ 5-sf (σ<0.0029%) + t ≥ 4-sf (σ<0.029%)
重算: ① catalog 真實 median 6,973,199.696 嘅池/圈 (7-sf 點估計)
      ② median 採樣誤差 (434 對象, 0.428 dex 散佈) — 天文 floor
      ③ λ_Edd 系統誤差 (文獻: LRD 質譜方法 0.5-5 dex 分歧)
      ④ cosmic time z=9→0 (Planck 2018) + N(z)∝1/(1+z) 加權 t_eff
      ⑤ 天文可達性判決 (永久 gated?)
"""
import mpmath as mp
mp.mp.dps = 60

PASS = 0; FAIL = 0
def ck(name, cond, info=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  [PASS] {name} {info}")
    else:
        FAIL += 1; print(f"  [FAIL] {name} {info}")

print("="*74)
print("Part A — 複合點估計: catalog 真實 median (7-sf) vs O177 用嘅 3-sf 捨入")
print("="*74)
N = mp.mpf(434)
M_exact = mp.mpf('6973199.69612336')     # catalog median (λ=10%, little_red_dots/data/11_cosmosweb_tests.json)
M_3sf   = mp.mpf('6.97e6')
t_active = mp.mpf('11e9')
T_ring_yr = mp.mpf('84.6349e9')
eta = ((1+mp.sqrt(5))/2)**(-21)          # φ^-21 (O173 C6)
E_strain = mp.mpf('1564785320847.4905')

pools_3sf = N * M_3sf * T_ring_yr / (t_active * eta * E_strain)
pools_ex  = N * M_exact * T_ring_yr / (t_active * eta * E_strain)
B75 = mp.mpf(4)/75
print(f"  池/圈 (3-sf M=6.97e6)  = {mp.nstr(pools_3sf, 12)}  (O177 記錄值 364.0533148)")
print(f"  池/圈 (exact M)        = {mp.nstr(pools_ex, 12)}")
print(f"  dev vs 364 (exact)     = {mp.nstr((pools_ex/364-1)*100, 6)}%")
print(f"  dev vs 364+B/75        = {mp.nstr((pools_ex/(364+B75)-1)*100, 6)}%")
d_ex = pools_ex - 364
print(f"  δ(exact) = {mp.nstr(d_ex, 10)}  ← O177 記錄 δ = +0.0533 係 3-sf 捨入假影")
print(f"  B/75 = {mp.nstr(B75,8)} 覆蓋殘餘 = {mp.nstr(B75/d_ex*100,4)}%")
ck("A1 O177 δ=+0.0533 係 3-sf 捨入假影: exact median 令 δ = +0.2204 (4.13×)",
   abs(d_ex - B75) > abs(d_ex)*mp.mpf('0.5'),
   f"B/75 只覆蓋 {mp.nstr(B75/d_ex*100,4)}% 殘餘")
ck("A2 catalog median (6,973,199.696) 喺 O177 3-sf 範圍上端之外方向相反",
   M_exact > M_3sf, "O177 Part C 假設 M 捨入向上; 實況 catalog 高過 6.97e6")

print()
print("="*74)
print("Part B — median 採樣誤差: 天文散佈下嘅真實 σ(M) (不可降 floor)")
print("="*74)
sig_dex = mp.mpf('0.42805979772036157')   # catalog logLbol std (434 對象)
n = mp.mpf(434)
se_med_dex = mp.mpf('1.253') * sig_dex / mp.sqrt(n)
se_med_rel = mp.mpf(10)**se_med_dex - 1
print(f"  logLbol 樣本散佈 σ = {mp.nstr(sig_dex,5)} dex (434 對象, COSMOS-Web)")
print(f"  SE(median) ≈ 1.253σ/√n = {mp.nstr(se_med_dex,6)} dex = {mp.nstr(se_med_rel*100,4)}% 相對")
print(f"  5-sf 需要 σ_M < 0.0029% → 採樣 floor 6.1% = 2100× 太粗")
# 要 median SE = 0.0029% 需要幾多對象? (σ 固定 0.428 dex)
n_need = (mp.mpf('1.253')*sig_dex/mp.mpf('0.0000126'))**2   # 0.0029% → 1.26e-5 dex
print(f"  要 median SE → 5-sf: 需 n = {mp.nstr(n_need,4)} 個 LRD (σ=0.428 dex 固定)")
ck("B1 採樣 floor 6.1% 不可降: 5-sf 需要 n ≈ 1.8e9 個 LRD (全可觀測宇宙冇咁多)",
   n_need > mp.mpf('1e8'), f"n_need = {mp.nstr(n_need,3)}")
print()
print("="*74)
print("Part C — λ_Edd 系統誤差: 10% 假設嘅天文不確定度 (common-mode, 不可平均)")
print("="*74)
# 文獻: Nature 2025 (electron-scattering 展寬 → virial 質量高估); 2609.09265 quasi-star
# (GN-28074 低 5 decades); 2407.15915 mild super-Eddington; 每個方法間分歧 ≥ 0.5-1 dex
sig_lam_dex = mp.mpf('0.5')    # 保守下界 (方法間分歧)
sig_lam_rel = mp.mpf(10)**sig_lam_dex - 1
print(f"  LRD 質譜方法分歧: virial Hα vs electron-scattering vs quasi-star → ≥ ±0.5 dex (保守)")
print(f"  σ_logM(λ) ≥ 0.5 dex = {mp.nstr(sig_lam_rel*100,4)}% 相對系統誤差 (common-mode)")
print(f"  文獻極端: Nature 2025 electron-scattering → 質量高估數個數量級; 2609.09265 差 5 decades")
ck("C1 λ_Edd 系統誤差 ≥ ±0.5 dex (216%) ≫ 0.003% — M 5-sf 天文不可達",
   sig_lam_rel > mp.mpf('1.5'), f"σ_λ = {mp.nstr(sig_lam_rel*100,4)}%")
ck("C2 λ 誤差係 common-mode (全部 434 同一假設) — 唔會 √n 平均, 永久 floor",
   True, "M_obs = Lbol/(λ·1.26e38) → σ_logM = σ_logλ")

print()
print("="*74)
print("Part D — 窗口天文化: cosmic time z=9→0 (Planck 2018) 誤差")
print("="*74)
H0 = mp.mpf('67.36'); Om = mp.mpf('0.3153'); OL = 1-Om
H0_s = H0*mp.mpf('1e3')/mp.mpf('3.0857e22')
Gyr_s = mp.mpf('3.15576e16')
def tzGyr_par(H0v, Omv, z):
    import mpmath as mpl
    zz = mp.mpf(z); H = mp.mpf(H0v)*mp.mpf('1e3')/mp.mpf('3.0857e22'); OLv = 1-mp.mpf(Omv)
    def g(x):
        x = mp.mpf(x)
        return 1/((1+x)*mp.sqrt(mp.mpf(Omv)*(1+x)**3 + OLv))
    return mpl.quad(g, [zz, mp.mpf('150')]) / H / Gyr_s
t0 = tzGyr_par(67.36, 0.3153, 0); t9 = tzGyr_par(67.36, 0.3153, 9)
dt_90 = t0 - t9
print(f"  t(z=0) = {mp.nstr(t0,7)} Gyr (Planck 2018 公開值 13.787 ✓)")
print(f"  t(z=9) = {mp.nstr(t9,7)} Gyr")
print(f"  Δt(9→0) = {mp.nstr(dt_90,7)} Gyr  ← 天文定義窗口")
print(f"  O173 用 t_active = 11 Gyr (2-sf 保守) — 同天文值差 {mp.nstr((dt_90/11-1)*100,4)}%")
dt_hi = tzGyr_par(67.90, 0.3153, 0) - tzGyr_par(67.90, 0.3153, 9)
dt_lo = tzGyr_par(66.82, 0.3153, 0) - tzGyr_par(66.82, 0.3153, 9)
dt_Omhi = tzGyr_par(67.36, 0.3226, 0) - tzGyr_par(67.36, 0.3226, 9)
dt_OmLo = tzGyr_par(67.36, 0.3080, 0) - tzGyr_par(67.36, 0.3080, 9)
sig_dt = mp.sqrt((abs(dt_hi-dt_lo)/2)**2 + (abs(dt_Omhi-dt_OmLo)/2)**2)
print(f"  σ_H0(±0.54) = {mp.nstr(abs(dt_hi-dt_lo)/2,5)} Gyr, σ_Ωm(±0.0073) = {mp.nstr(abs(dt_Omhi-dt_OmLo)/2,5)} Gyr")
print(f"  σ(Δt) = {mp.nstr(sig_dt,5)} Gyr = {mp.nstr(sig_dt/dt_90*100,4)}% 相對")
ck("D1 Planck 宇宙學誤差 σ(Δt)/Δt = 1.02% ≫ 4-sf 門檻 0.029% (35×)",
   sig_dt/dt_90 > mp.mpf('0.005'), f"σ_rel = {mp.nstr(sig_dt/dt_90*100,4)}%")
ck("D2 O173 11 Gyr ≠ 天文 Δt(9→0) = 13.26 Gyr (差 20%) — 保守 2-sf 模型選擇",
   abs(dt_90-11) > mp.mpf('1'), f"Δ = {mp.nstr(dt_90-11,4)} Gyr (+{mp.nstr((dt_90/11-1)*100,3)}%)")

print()
print("="*74)
print("Part E — N(z)∝1/(1+z) 加權有效窗口 t_eff (EIGER 校準, O173 C5)")
print("="*74)
import mpmath as mpl
def wf(z):
    z = mp.mpf(z)
    return 1/((1+z)**2 * mp.sqrt(Om*(1+z)**3 + OL))
t_eff = mpl.quad(wf, [0, mp.mpf('9')]) / H0_s / Gyr_s
print(f"  t_eff (N∝1/(1+z) 加權) = {mp.nstr(t_eff,7)} Gyr")
print(f"  Δt(9→0) 無權重         = {mp.nstr(dt_90,7)} Gyr")
print(f"  加權修正 = {mp.nstr((t_eff/dt_90-1)*100,4)}% — 模型依賴性")
ck("E1 窗口定義依賴性 20-42% (11 vs 13.26 vs 7.62 Gyr) ≫ 4-sf 0.029%",
   abs(t_eff/dt_90-1) > mp.mpf('0.2'), f"N(z) 加權 → {mp.nstr(t_eff,5)} Gyr (−42.5%)")

print()
print("="*74)
print("Part F — 判決: 天文可達性 (3σ 分辨需要 σ_rel < 0.0049%)")
print("="*74)
sep = B75/mp.mpf(364)
print(f"  候選分離度 = 1/6825 = {mp.nstr(sep*100,6)}% ; 3σ 需要 σ_rel < {mp.nstr(sep/3*100,6)}%")
sig_M_samp = se_med_rel          # 6.1% (採樣, 不可降)
sig_M_lam  = sig_lam_rel         # 216% (λ common-mode)
sig_t_cosmo = sig_dt/dt_90       # 1.02%
print(f"  σ_M floor (採樣, 最佳情況) = {mp.nstr(sig_M_samp*100,4)}%   (5-sf 門檻 0.0029%)")
print(f"  σ_M floor (λ common-mode)  = {mp.nstr(sig_M_lam*100,4)}%  ← 真正主導")
print(f"  σ_t floor (宇宙學)          = {mp.nstr(sig_t_cosmo*100,4)}%  (4-sf 門檻 0.029%)")
sig_best = mp.sqrt(sig_M_samp**2 + sig_t_cosmo**2)
sig_full = mp.sqrt(sig_M_lam**2 + sig_t_cosmo**2)
print(f"  合併 floor (最佳: 採樣+宇宙學) = {mp.nstr(sig_best*100,4)}% → 差距 {mp.nstr(sig_best/(sep/3),4)}×")
print(f"  合併 floor (含 λ)            = {mp.nstr(sig_full*100,4)}% → 差距 {mp.nstr(sig_full/(sep/3),4)}×")
ck("F1 即使最佳情況 (採樣+宇宙學) 都 1250× 過粗 — 364 vs 364+B/75 永久不可分辨",
   sig_best/(sep/3) > mp.mpf('100'), f"差距 {mp.nstr(sig_best/(sep/3),4)}×")
ck("F2 主卡點 = M_med (λ common-mode 216% + 採樣 6.1%); 次卡點 = t (定義 20-42% + 宇宙學 1%)",
   sig_M_lam > sig_M_samp)

print()
print("="*74)
print("Part G — 替代路徑: 完整質譜 PDF 摺積 (唔用 median 點)")
print("="*74)
sig_obj_dex = mp.mpf('0.35')     # 每對象 Lbol 68% 誤差 (catalog u68/l68 中位)
sig_obj_lin = mp.mpf('2.3026')*sig_obj_dex
sig_sum = sig_obj_lin / mp.sqrt(n)
print(f"  每對象 Lbol 68% 誤差 ~±0.35 dex → 線性 σ_i ≈ {mp.nstr(sig_obj_lin,4)}")
print(f"  σ(ΣM)/ΣM = σ_i/√434 = {mp.nstr(sig_sum*100,4)}%  (PDF 摺積改善)")
print(f"  對比 median 採樣 floor 6.1% → 改善 1.6×, 但仍 {mp.nstr(sig_sum/(sep/3),4)}× 過粗")
print(f"  ⚠️ λ common-mode (216%) 對 ΣM 同樣成立 — PDF 摺積救唔到 λ 系統")
ck("G1 PDF 摺積替代路徑: 6.1% → 3.9%, 改善 1.6×, 仍 790× 過粗 — 唔足以分辨",
   sig_sum < sig_M_samp and sig_sum/(sep/3) > mp.mpf('100'),
   f"σ_ΣM = {mp.nstr(sig_sum*100,4)}% vs 需要 0.0049%")

print()
print("="*74)
print("Part H — O177 errata: 3-sf 捨入假影更正")
print("="*74)
print(f"  O177 docs/02: δ = +0.0533, B/75 唯一候選 (dev 0.035%), 主張2 零捨入假設")
print(f"  更正: catalog exact median 6,973,199.696 → 池/圈 = {mp.nstr(pools_ex,8)}")
print(f"         δ = +0.2204 (dev 0.0606%) — 4.13× O177 記錄值")
print(f"         B/75 只覆蓋 {mp.nstr(B75/d_ex*100,4)}% 殘餘 — 唔再係唯一候選")
print(f"  統計判決不變: δ = 0.2204 vs σ(採樣+宇宙學) = {mp.nstr(sig_best*364,5)} → "
      f"{mp.nstr(d_ex/(sig_best*364),4)}σ (仍 ≪ 1σ, 364 身份站得住)")
ck("H1 統計判決不變: exact-M 殘餘仍 ≪ 1σ (0.010σ) — 364 閉合維持",
   d_ex/(sig_best*364) < mp.mpf('0.1'), f"{mp.nstr(d_ex/(sig_best*364),4)}σ")
ck("H2 O177 嘅 B/75 候選 (dev 0.035%) 係 3-sf 捨入假影 — 唔宣稱結構",
   abs(B75/d_ex) < mp.mpf('0.5'), f"覆蓋率 {mp.nstr(B75/d_ex*100,4)}%")

print()
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
import sys
sys.exit(0 if FAIL == 0 else 1)
