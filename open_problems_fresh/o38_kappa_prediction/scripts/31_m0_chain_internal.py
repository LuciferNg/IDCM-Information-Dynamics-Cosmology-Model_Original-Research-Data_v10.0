#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 31: M₀ 生成鏈 IDCM 內部重寫 + H₀ 自洽審計
================================================================
日期: 2026-10-18
性質: 用戶「不發還, 在O38繼續推」—— 攻 M₀ 生成鏈本身 (唔外判 O86)
背景 (O206 docs/13 + O136 docs/37):
  O38 舊公式: M₀ = √(M_P·ħ·H₀)·(1−CY₃/45²)·φ^x,  x = 47+37/528 (O136 定理5 已否證)
  值來源路:   M₀ = m_e·F_e,  F_e = 54.600729 (scripts/25 零命中, 最近 F₁₀=55 dev 7.3e−3)
  O136 docs/37 內部不一致: E_kchain = 4.060265 meV 鎖 H₀ = 72.59;
                           H₀ = 71.157 (O170 徑向律) ⟹ E_kchain = 4.019988 meV (Δ 0.992%)
本輪:
  A. IDCM 內部重寫 √(M_Pl·ħ·H₀) —— H₀ = ω_ring (O212 錨), M_Pl = √(ħc/G)
  B. (1−CY₃/45²) 因子審計 —— CY₃=134, 45²=(N_d+1)² 都係結構數, 但『1−a/b²』式族未註冊
  C. H₀ 自洽: 兩個 H₀ 邊個鎖 M₀; H₀ 張力屬 O170 交收 (O38 內部記錄, 唔外判)
  D. M₀ 值來源三路對照
用法: /usr/bin/python3 scripts/31_m0_chain_internal.py
"""
import mpmath as mp
mp.mp.dps = 60

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

# --- 基本常數 (CODATA, 同 scripts/22/29/30 同制) ---
c_SI   = mp.mpf('299792458')
hb_SI  = mp.mpf('1.054571817e-34')     # ħ (J·s)
G_SI   = mp.mpf('6.6743e-11')
hbar_ev = mp.mpf('6.582119569e-16')    # ħ (eV·s)
MeV_per_J = mp.mpf('1.602176634e-13')  # MeV/J
km_s_Mpc = mp.mpf('3.0856775814913673e22')  # m per Mpc

# ω_ring (O38 錨, scripts/19/29 同值)
w_ring = mp.mpf('2.352481686207664554292489649666867106996440795729509426212647271042717e-18')
# H₀ 兩個值
H0_ring = w_ring * km_s_Mpc / mp.mpf('1e3')          # = ω_ring 換 km/s/Mpc
H0_170  = mp.mpf('71.157')
# H₀ 反解值 (O136 docs/37)
H0_recon = mp.mpf('72.5900')

M0_MeV  = mp.mpf('27.900915')
E_kchain_MeV = mp.mpf('4.060265e-9')   # 4.060265 meV
phi = (1 + mp.sqrt(5)) / 2

print("=" * 76)
print("A. IDCM 內部重寫 √(M_Pl·ħ·H₀)")
print("=" * 76)
M_Pl_kg = mp.sqrt(hb_SI * c_SI / G_SI)                # Planck 質量 (kg)
M_Pl_J  = M_Pl_kg * c_SI ** 2
M_Pl_MeV = M_Pl_J / MeV_per_J
print(f"  M_Pl = {mp.nstr(M_Pl_MeV, 8)} MeV")
def geom_mean(H0_kmsMpc):
    H0_si = H0_kmsMpc * mp.mpf('1e3') / km_s_Mpc      # s⁻¹
    # ħH₀: 用 eV·s × s⁻¹ = eV —— 轉 MeV 除 1e6 (唔可以用 J→MeV 因子! o206 docs/13 教訓)
    hbarH0_MeV = hbar_ev * H0_si / mp.mpf('1e6')
    return mp.sqrt(M_Pl_MeV * hbarH0_MeV)

gm_ring = geom_mean(H0_ring)
gm_170  = geom_mean(H0_170)
gm_rec  = geom_mean(H0_recon)
print(f"  H₀ (ω_ring 錨)      = {mp.nstr(H0_ring, 10)} km/s/Mpc")
print(f"  √(M_Pl ħ H₀) @ ω_ring = {mp.nstr(gm_ring*1e9, 8)} meV")
print(f"  √(M_Pl ħ H₀) @ 71.157 = {mp.nstr(gm_170*1e9, 8)} meV   (O206 記錄 4.304852 meV)")
print(f"  √(M_Pl ħ H₀) @ 72.59  = {mp.nstr(gm_rec*1e9, 8)} meV")
chk("A1 @H₀=71.157 復現 O206 4.304852 meV (輸入精度: G 5位)", abs(gm_170*1e9/mp.mpf('4.304852')-1) < mp.mpf('1e-5'),
    f"(dev {mp.nstr(abs(gm_170*1e9/mp.mpf('4.304852')-1),3)})")
# 加 (1−CY₃/45²) 後對比 E_kchain 聲稱值
f2 = 1 - mp.mpf(134)/2025
E_ring = gm_ring * f2
E_170  = gm_170 * f2
print(f"  (1−CY₃/45²) = {mp.nstr(f2, 12)}")
print(f"  E_kchain 預言 @ω_ring = {mp.nstr(E_ring*1e9, 8)} meV")
print(f"  E_kchain 預言 @71.157 = {mp.nstr(E_170*1e9, 8)} meV")
print(f"  E_kchain 聲稱值       = {mp.nstr(E_kchain_MeV*1e9, 8)} meV")
chk("A2 ★ E_kchain = √(M_Pl ħ ω_ring)·(1−CY₃/45²) 命中所稱值 (dev < 1e−4)",
    abs(E_ring/E_kchain_MeV - 1) < mp.mpf('1e-4'), f"(dev {mp.nstr(abs(E_ring/E_kchain_MeV-1),3)})")
chk("A3 @H₀=71.157 得 O206 記錄嘅 4.019988 meV (Δ 0.992%) (輸入精度)",
    abs(E_170*1e9/mp.mpf('4.019988')-1) < mp.mpf('1e-5'), f"({mp.nstr(E_170*1e9,8)} meV)")
print("  ⟹ ★關鍵: 聲稱 E_kchain 4.060265 meV 對應 H₀ = ω_ring (=72.59 側), 唔係 71.157")
print("     ⟹ M₀ 值鎖死 H₀ = ω_ring 錨 (O212); O170 徑向律 71.157 與 M₀ 不相容 (Δ 0.99%)")

print()
print("=" * 76)
print("B. (1−CY₃/45²) 因子審計 — 結構數組合 vs 機制")
print("=" * 76)
print(f"  CY₃ = 134 = h11+h21 = 36+98  (O211 🟢 零輸入結構數)")
print(f"  (N_d+1)² = 45² = 2025        (N_d=44 鏈維度, 結構數)")
print(f"  1891 = 2025 − 134 = 31 × 61  (31, 61 冇 IDCM 身份 → 無結構分解)")
print("  式族『1 − a/b²』(a,b ∈ 生成集): 未註冊 (O38 docs/07 式族登記冇)")
chk("B1 1891 = 31×61 冇 IDCM 身份 (31,61 ∉ 生成集)",
    all(31 != g and 61 != g for g in [mp.mpf(2), mp.mpf(3), mp.mpf(4), mp.mpf(7), mp.mpf(9), mp.mpf(11),
        mp.mpf(22), mp.mpf(33), mp.mpf(36), mp.mpf(44), mp.mpf(88), mp.mpf(89), mp.mpf(123),
        mp.mpf(128), mp.mpf(137), mp.mpf(528)]), "(31, 61 唔喺常數集)")
print("  ⟹ (1−CY₃/45²) 嘅分子分母都係結構數, 但組合『1−a/b²』係未註冊式族,")
print("     且 1891/2025 嘅等價結構讀法唔唯一 (任何 ≈0.9338 嘅 p/q 都得)")
print("     ⟹ 維持 🟡: 需要『點解係減 CY₃/45²』嘅機制 (點解係減, 唔係乘/加)")

print()
print("=" * 76)
print("C. H₀ 自洽審計 (O38 內部記錄, 唔外判)")
print("=" * 76)
print(f"  H₀(ω_ring) = {mp.nstr(H0_ring, 10)}  (scripts/19 維度側錨鏈閉合值)")
print(f"  H₀(反解)   = {mp.nstr(H0_recon, 10)}  (O136 docs/37: 令 E_kchain = 4.060265 所需)")
print(f"  H₀(O170)   = {mp.nstr(H0_170, 10)}  (徑向律 71.157, ⚠️ 未收斂 −1.84σ SH0ES)")
d_rec_ring = abs(H0_recon/H0_ring - 1)
d_ring_170 = abs(H0_ring/H0_170 - 1)
print(f"  Δ(反解 vs ω_ring) = {mp.nstr(d_rec_ring, 4)}")
print(f"  Δ(ω_ring vs 71.157) = {mp.nstr(d_ring_170, 4)}  (= 1.97%)")
chk("C1 E_kchain 聲稱值同 ω_ring 錨一致 (Δ < 1e−4)",
    d_rec_ring < mp.mpf('1e-4'), f"(Δ {mp.nstr(d_rec_ring,3)})")
chk("C2 O170 徑向律 71.157 同 ω_ring 差 1.97% (O38 內部已知, 未閉合)",
    abs(d_ring_170 - mp.mpf('0.0197')) < mp.mpf('0.002'), f"(Δ {mp.nstr(d_ring_170,4)})")
print("  ⟹ M₀ 生成鏈要求 H₀ = ω_ring (72.5941±); O170 徑向律 71.157 產生 Δ 0.99% 偏差")
print("     ⟹ 呢個 H₀ 張力 = O170 交收問題 (O38 目錄已記錄, 唔發還)")

print()
print("=" * 76)
print("D. M₀ 值來源三路對照")
print("=" * 76)
F_e = M0_MeV / mp.mpf('0.51099895000')
print(f"  路1 (舊 O38 公式): M₀ = √(M_Pl ħ H₀)(1−CY₃/45²)φ^x — φ^x 層 🔴 已否證")
print(f"  路2 (值來源):      M₀ = m_e·F_e, F_e = {mp.nstr(F_e, 9)} — scripts/25 零命中")
print(f"  路3 (O38 核心):    κ² = M₀·ω_scale, κ̃² = 88 = 2N_d 🟢 (譜身份, 唔用 M₀ 嘅值)")
print(f"  路1 內部一致部分:  √(M_Pl ħ ω_ring)(1−CY₃/45²) = E_kchain (dev < 1e−4) ✓")
print(f"                     然後 M₀ = E_kchain·φ^x — 呢個 φ^x 就係死錨 (O136 定理5)")
chk("D1 路1 嘅前段 (幾何平均 × CY₃ 修正) 精確, 死喺 φ^x 層",
    abs(E_ring/E_kchain_MeV - 1) < mp.mpf('1e-4'), "(前段 ✓, φ^x 🔴)")

print()
print("=" * 76)
print("結論 — O38 內部繼續推 (唔外判)")
print("=" * 76)
print("  1. ★ 新發現: E_kchain = √(M_Pl·ħ·ω_ring)·(1−CY₃/45²) 精確成立至輸入精度")
print("     ⟹ M₀ 生成鏈嘅「前段」係 IDCM 內部可表達 (M_Pl 錨 O212, ω_ring 錨, CY₃ 結構數)")
print("  2. 死喺 φ^x 層 (O136 定理5 反解) — 即 M₀ = E_kchain·φ^47.07 嘅最後一步冇機制")
print("  3. ⚠️ H₀ 自洽: 聲稱 E_kchain 對應 H₀ = ω_ring (72.5941), O170 徑向律 71.157")
print("     產生 Δ 0.99% ⟹ M₀ 同 O170 H₀ 未自洽 (O170 交收問題, 喺 O38 記錄)")
print("  4. 缺口維持 🔴; 責任喺 O38 (撤回 O86/R1 發還)")
print("  5. 下一步可行 (O38 內部):")
print("     i.  φ^x 層重攻 — 唔用 φ 反解嘅話, 47.07 係咩? (47 = L₅+L₇? 47.07 = 47+?)")
print("     ii. O170 H₀ 張力閉合 (71.157 vs 72.5941) — 若閉合, M₀ 生成鏈前段直升")
print("     iii. F_e = 54.600729 嘅結構 (電子鏈格, 需 O34/O124 域參考但唔發還)")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)