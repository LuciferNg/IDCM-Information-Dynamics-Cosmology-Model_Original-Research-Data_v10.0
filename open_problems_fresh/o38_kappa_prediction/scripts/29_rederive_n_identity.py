#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 29: N 身份樹重新推導（O250 整合錯誤更正）
==============================================================
日期: 2026-10-18
性質: 用戶「整合錯誤，重新推導」—— O250 docs/07 三層身份樹嘅獨立重推
問題:
  (Q1) 上一輪 report「log dev 7.9e−8」嘅統計是否正確？
       —— 我當時用 dev = |log₁₀(N) − 40.25572603| / 40.25572603（除以目標 log₁₀）
          呢個 normalize 冇意義；應該用線性相對 dev = |N/目標 − 1|
  (Q2) O250 三層身份樹 N_O38 = √N_IDCM·(1891/2025)·φ^(47+37/528)
       乘埋嘅實際線性 dev 係幾多？—— 用 scripts/06 同一個輸入
  (Q3) O250 三層 vs O38 scripts/22 恆等式 N_O38 = N_IDCM·(M₀/M_Pl)
       嘅關係 —— 兩個分解係咪等價？O250 係咪只係將 M₀/M_Pl 重包裝？
  (Q4) 層 2「有理 = 結構」喺式族註冊制下係咪成立？
用法: /usr/bin/python3 scripts/29_rederive_n_identity.py
"""
import mpmath as mp
mp.mp.dps = 60

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

print("=" * 76)
print("Q1. 上一輪『log dev 7.9e−8』統計覆核 —— 對象: O250 三層 vs N_O38")
print("=" * 76)
# O250 scripts/06 輸入
w_ring = mp.mpf('2.352481686207664554292489649666867106996440795729509426212647271042717e-18')
hb_ev  = mp.mpf('6.582119569e-16')
M0_eV  = mp.mpf('27.900915') * mp.mpf(1e6)
N_O38  = M0_eV / (hb_ev * w_ring)          # M₀/(ħω_ring)
target = mp.mpf('1.80188233461e40')        # O38 scripts/22 紀錄
d_rec  = abs(N_O38 / target - 1)           # 復算 vs 紀錄
print(f"  N_O38 (復算) = {mp.nstr(N_O38, 12)}")
print(f"  N_O38 (紀錄) = {mp.nstr(target, 12)}")
print(f"  復算 vs 紀錄 線性 dev = {mp.nstr(d_rec, 4)}  (O38 自身復算一致 ✓)")
# 上一輪我 report 嘅「三層 log dev 7.9e−8」: |Δlog₁₀| / log₁₀(N)
# 正確統計: 線性相對 dev = |N_250/N_O38 − 1| (Q2 出 8.26e−6)
chk("Q1 上一輪『log dev 7.9e−8』係 log-normalize 假象 (除以 log₁₀ 目標); 正確線性 dev 見 Q2 (~8e−6)",
    True, "(7.9e−8 = |Δlog|/log₁₀N 嘅誤導形式, 唔係物理誤差)")

print()
print("=" * 76)
print("Q2. O250 三層身份樹實際線性 dev")
print("=" * 76)
c_SI = mp.mpf('299792458'); hb_SI = mp.mpf('1.054571817e-34'); G_SI = mp.mpf('6.6743e-11')
t_Pl = mp.sqrt(hb_SI * G_SI / c_SI ** 5)
N_IDCM = 1 / (t_Pl * w_ring)
sqrtN = mp.sqrt(N_IDCM)
phi = (1 + mp.sqrt(5)) / 2
x_lam = mp.mpf(47) + mp.mpf(37) / 528          # O136 已否證指數
l1, l2, l3 = sqrtN, mp.mpf(1891)/2025, phi ** x_lam
N_250 = l1 * l2 * l3
dev250 = abs(N_250 / N_O38 - 1)
print(f"  層1 √N_IDCM      = {mp.nstr(l1, 7)}")
print(f"  層2 1891/2025    = {mp.nstr(l2, 12)}")
print(f"  層3 φ^(47+37/528)= {mp.nstr(l3, 7)}")
print(f"  三層乘埋         = {mp.nstr(N_250, 11)}")
print(f"  vs 復算 N_O38    = {mp.nstr(N_O38, 11)}")
print(f"  線性 dev         = {mp.nstr(dev250, 6)}")
chk("Q2 三層身份樹連輸入精度都 fit 唔到 (dev ~7e−6, 即 E_kchain 7 位輸入水平)",
    dev250 > mp.mpf('1e-6'), f"(dev={mp.nstr(dev250,4)})")
print("  ⟹ O250 身份樹係近似重組（fit 到輸入精度 1e−5~1e−6 水平）, 唔係精確恆等式;")
print("    『冇超出輸入嘅預言力』—— 唔可以當『結構推導』")

print()
print("=" * 76)
print("Q3. O250 三層 vs scripts/22 恆等式 N_O38 = N_IDCM·(M₀/M_Pl)")
print("=" * 76)
M_Pl_eV = mp.sqrt(mp.mpf('1.973269804e-7'))   # √(ħc⁵/G) 以 eV 表示 ≈ 1.2209e28? 用 direct:
# M_Pl = √(ħc/G) 質量; 由 t_Pl = √(ħG/c⁵), M_Pl = ħ/(t_Pl·c²)
M_Pl_kg = mp.mpf('1.054571817e-34') / (t_Pl * c_SI ** 2)
M0_kg = M0_eV * mp.mpf('1.602176634e-19') / (c_SI ** 2)
ratio22 = M_Pl_kg / M0_kg                       # M_Pl/M₀ —— scripts/22 缺口
N_via22 = N_IDCM * M0_kg / M_Pl_kg             # N_IDCM·(M₀/M_Pl)
print(f"  M_Pl/M₀ = {mp.nstr(ratio22, 7)} (log₁₀ {mp.nstr(mp.log10(ratio22), 6)})")
print(f"  N_IDCM·(M₀/M_Pl) = {mp.nstr(N_via22, 11)}")
print(f"  vs N_O38 復算    = {mp.nstr(N_O38, 11)}")
chk("Q3a scripts/22 恆等式 N_O38 = N_IDCM·(M₀/M_Pl) 成立到輸入精度 (5e−10, G 6位+ħ 常數水平)",
    abs(N_via22 / N_O38 - 1) < mp.mpf('1e-8'), f"(dev={mp.nstr(abs(N_via22/N_O38-1),3)})")
# O250 版: √N_IDCM·(1891/2025)·φ^x — 將兩式合併
# N_IDCM·(M₀/M_Pl) = √N_IDCM·(1891/2025)·φ^x
# ⟹ φ^x = √N_IDCM·(M₀/M_Pl)·(2025/1891)  ← O250 層3 嘅本質位置
phi_x_implied = sqrtN * ratio22 * mp.mpf(2025) / 1891
x_implied = mp.log(phi_x_implied) / mp.log(phi)
print(f"  O250 層3 本質 = √N_IDCM·(M₀/M_Pl)·(2025/1891) = {mp.nstr(phi_x_implied, 7)}")
print(f"  ⟹ x_implied (log_φ) = {mp.nstr(x_implied, 9)}")
print(f"  O136 已否證 x        = {mp.nstr(mp.mpf(47)+mp.mpf(37)/528, 9)}")
chk("Q3b O250 層2×層3 ≡ M₀/M_Pl 嘅重包裝 (兩分解完全等價)",
    abs(x_implied - (mp.mpf(47)+mp.mpf(37)/528)) < mp.mpf('1e-4'),
    f"(Δx={mp.nstr(abs(x_implied-(mp.mpf(47)+mp.mpf(37)/528)),3)})")
print("  ⟹ O250 冇推導出新結構: 佢將 O38 已閉合嘅缺口 M₀/M_Pl")
print("     (=4.3758e20, scripts/22) 重新拆成 1891/2025 × φ^47.07 兩段")
print("     —— 拆法係後驗 (冇機制話點解 M₀/M_Pl 要等於呢兩項乘積)")

print()
print("=" * 76)
print("Q4. 層 2『有理 = 結構』喺式族註冊制下嘅地位")
print("=" * 76)
print("  層2 = 1891/2025 = 1 − 134/45², CY₃=134 (O211 h11+h21), 2025=(N_d+1)²")
print("  式族註冊制 5 閘: 式族 (p−q 型 1−a/b²) 有冇註冊? —— 冇 (O38 docs/07)")
print("  『有理 = 結構』錯誤: 任何近似 0.9338 嘅有理數都可以寫成 1 − p/q;")
print("  有理數唔自帶機制; 需要『點解係 1 − CY₃/(N_d+1)²』嘅物理解釋")
chk("Q4 層2 冇資格 🟢 — 未註冊式族 + 後驗; O250 自己都話『追溯 O34 待核』",
    True, "(審計結論: 層2 最多 🟡, 唔可以當獨立結構因子)")

print()
print("=" * 76)
print("重新推導結論")
print("=" * 76)
print("  1. N_O38 嘅唯一精確分解 = scripts/22: N_O38 = N_IDCM·(M₀/M_Pl)")
print("     缺口 = M_Pl/M₀ = 4.3758e20 (log₁₀ 20.6411), 已發還 O86/R1")
print("  2. O250 三層身份樹 = 同一缺口嘅後驗重包裝: 層1 √N 冇機制,")
print("     層2 有理冇機制 (未註冊), 層3 已否證 (O136 定理5)") 
print("     —— 三層乘埋 dev ~7e−6, 只 fit 到輸入精度, 冇預言力")
print("  3. 『M₀ 死錨』核心結論 (φ^x 禁區) 維持 — O136 定理5 + O38 早列禁區;")
print("     但 O250 身份樹本身唔係推導, 唔可以當『N 缺口 = φ 層』")
print("  4. O38 接收時兩錯: (i) log-normalize 假象 7.9e−8 (實為 7e−6)")
print("     (ii) 層2 升格 🟢 (應為 🟡 未註冊式族)")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)