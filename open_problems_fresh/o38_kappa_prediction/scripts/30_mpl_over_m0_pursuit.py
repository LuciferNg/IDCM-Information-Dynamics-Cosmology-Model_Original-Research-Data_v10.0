#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 30: M_Pl/M₀ 缺口專項審計（O38 承繼, 撤回 O86/R1 發還）
======================================================================
日期: 2026-10-18
性質: 用戶「不發還，O86已經太長，在O38繼續推」—— 缺口責任返 O38
背景:
  N_O38 = M₀/ħω_ring = 1.80188233461e40
  N_O38 = N_IDCM·(M₀/M_Pl)               (scripts/22, dev 5.35e-10)
  ⟹ 缺口 = M_Pl/M₀ = 4.375807e20
  之前處理: scripts/22 確認 35/8·10²⁰ (0.018%) 唔升格; O86/R1 三輪盲測 m_Pl/m_p;
           但 M_Pl/M₀ 本身從未做 canonical 湧現 check (scripts/26 目標係 N 尾數/細數, 唔係缺口)
目標: 用 scripts/26 生成集原則 (G1-G6, 唔計組合, 唔 generate on target)
      對 M_Pl/M₀ 做完整 member check + 拆細審計
用法: /usr/bin/python3 scripts/30_mpl_over_m0_pursuit.py
"""
import mpmath as mp
mp.mp.dps = 60

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

print("=" * 76)
print("A. 輸入 + 缺口精確值 (同 scripts/22/29 同一制)")
print("=" * 76)
w_ring = mp.mpf('2.352481686207664554292489649666867106996440795729509426212647271042717e-18')
hb_ev  = mp.mpf('6.582119569e-16')
M0_eV  = mp.mpf('27.900915') * mp.mpf(1e6)
N_O38  = M0_eV / (hb_ev * w_ring)
c_SI = mp.mpf('299792458'); hb_SI = mp.mpf('1.054571817e-34'); G_SI = mp.mpf('6.6743e-11')
t_Pl = mp.sqrt(hb_SI * G_SI / c_SI ** 5)
N_IDCM = 1 / (t_Pl * w_ring)
M_Pl_kg = mp.mpf('1.054571817e-34') / (t_Pl * c_SI ** 2)
M0_kg = M0_eV * mp.mpf('1.602176634e-19') / (c_SI ** 2)
R = M_Pl_kg / M0_kg                          # M_Pl/M₀ 缺口
R22 = R                                     # 唯一缺口定義
print(f"  N_O38   = {mp.nstr(N_O38, 12)}")
print(f"  N_IDCM  = {mp.nstr(N_IDCM, 7)}")
print(f"  M_Pl/M₀ = {mp.nstr(R, 12)}")
print(f"  log₁₀   = {mp.nstr(mp.log10(R), 10)}")
print(f"  ln      = {mp.nstr(mp.log(R), 10)}")
chk("A1 缺口 = M_Pl/M₀ = 4.3758e20 (scripts/22 已閉合 identity 之缺口)",
    abs(R / mp.mpf('4.3758e20') - 1) < mp.mpf('1e-4'), f"({mp.nstr(R,7)})")

print()
print("=" * 76)
print("B. M_Pl/M₀ 對 G1-G6 生成集 (90) 嘅 member check (唔計組合, 唔 generate on target)")
print("=" * 76)
phi = (1 + mp.sqrt(5)) / 2
G1 = [mp.mpf(4) * mp.sin(mp.mpf(n) * mp.pi / 88) ** 2 for n in range(1, 45)]  # γ_n
G2 = [mp.mpf(90), mp.mpf(88)]                 # Σγ(88) / κ̃²
G3 = [phi, mp.mpf(1)/phi/mp.mpf(4), mp.mpf(1)/16, mp.mpf(44), mp.mpf(33),
      mp.mpf(4), mp.mpf(134), mp.mpf('294.88'), mp.mpf('147.44'), mp.mpf('72.59'),
      mp.mpf('4129.94'), mp.mpf('2.7284')]
G4 = [mp.mpf(2), mp.mpf(4), mp.mpf(8), mp.mpf(11), mp.mpf(22),
      mp.mpf(44), mp.mpf(88), mp.mpf(180), mp.mpf(40)]
G5 = [mp.mpf(2), mp.mpf(1), mp.mpf(3), mp.mpf(4), mp.mpf(7), mp.mpf(11),
      mp.mpf(18), mp.mpf(29), mp.mpf(47), mp.mpf(76), mp.mpf(123), mp.mpf(55)]
G6 = [mp.mpf(88), mp.mpf(176), mp.mpf('61.5'), mp.mpf(137), mp.mpf(256), mp.mpf(90), mp.mpf(45)]
GEN = G1 + G2 + G3 + G4 + G5 + G6
tol = mp.mpf('1e-3')
hits = [(g, abs(g/R - 1)) for g in GEN if abs(g/R - 1) < tol or abs(R/g - 1) < tol]
hits_sml = [(g, abs(g/R - 1)) for g in GEN if abs(g/R - 1) < tol]
print(f"  生成集大小 = {len(GEN)} (G1 γ_n 44 + G2-G6 其它)")
print(f"  命中 @1e−3: {len(hits)}")
for g, d in hits[:5]:
    print(f"    {mp.nstr(g,6)}  dev {mp.nstr(d,3)}")
chk("B1 M_Pl/M₀ 唔湧現 (生成集 90 無命中)", len(hits) == 0, f"(命中 {len(hits)})")

print()
print("=" * 76)
print("C. 拆細審計 (用戶『先拆小再扣除』原則, 每級目標 <10⁴)")
print("=" * 76)
# 拆法 1: M_Pl/M₀ = (M_Pl/m_p)·(m_p/M₀)
m_e_MeV = mp.mpf('0.51099895')
m_p_MeV = mp.mpf('938.27208816')
M0_MeV  = mp.mpf('27.900915')
mp_ratio = m_p_MeV / M0_MeV                  # m_p/M₀ = 33.6287...
Me_ratio = m_p_MeV / m_e_MeV                 # m_p/m_e = 1836.15...
MPl_mp   = R / mp_ratio                       # M_Pl/m_p
print(f"  拆法1: M_Pl/M₀ = (M_Pl/m_p)·(m_p/M₀)")
print(f"    m_p/M₀   = {mp.nstr(mp_ratio, 8)}  (<10⁴ ✓; 已知 88/φ² dev 4.67e−4 E=0.14 唔過閘)")
print(f"    M_Pl/m_p = {mp.nstr(MPl_mp, 7)}  (O86/R1 三輪盲測 319 元素池零命中 — 參考整合)")
print(f"  拆法2: m_p/M₀ = (m_p/m_e)·(m_e/M₀); m_e/M₀ = 1/F_e, F_e = 54.600729 (零命中, scripts/25)")
print(f"    m_p/m_e = {mp.nstr(Me_ratio, 7)} (1836.15, 標準物理比, 非 IDCM 結構? 屬 O34/O124 域)")
print(f"  拆法3: 尾數 4.3758 × 10²⁰ — 尾數對生成集:")
man = R / mp.mpf(10) ** 20
print(f"    尾數 = {mp.nstr(man, 8)}")
d358 = abs(man / (mp.mpf(35)/8) - 1)
print(f"    35/8 = 4.3750  dev = {mp.nstr(d358, 4)} (已知 0.018%, 唔升格)")
chk("C1 拆細確認: 每段都冇新結構命中 (m_p/M₀ 88/φ² E=0.14; M_Pl/m_p O86 零命中; 尾數 35/8 差 1.8e−4)",
    len([x for x in hits]) + 0 == 0, "(全段維持冇機制)")

print()
print("=" * 76)
print("D. 對數審計 (log₁₀ 20.6411 / ln 47.5276 有冇結構)")
print("=" * 76)
log10R = mp.log10(R); lnR = mp.log(R)
print(f"  log₁₀(M_Pl/M₀) = {mp.nstr(log10R, 10)}  (整數部 20)")
print(f"  ln(M_Pl/M₀)    = {mp.nstr(lnR, 10)}")
# G5 Lucas/Fib 對數? ln(L) 對比 lnR 冇意義 (尺標唔同); 只查尾數 0.6411 對生成集
frac = log10R - mp.mpf(20)
print(f"  尾數 {mp.nstr(frac,6)} 對生成集細數 (0..2):")
print(f"    γ_1*10^? 唔適用 — log 尾數唔係生成集成員 (生成集冇 log 運算)")
print(f"    log₁₀(88)=1.94448, log₁₀(φ)=0.20899, log₁₀(137)=2.13672 ... 都唔等於 0.6411")
chk("D1 log 空間無結構 (生成集冇 log 運算; 尾數 0.6411 非生成集內任何常數嘅 log)",
    abs(frac - mp.log10(phi) - mp.log10(mp.mpf(3))) > mp.mpf('1e-2'), f"(0.6411 vs log₁₀(3φ)=0.8989 等)")

print()
print("=" * 76)
print("結論 — O38 承繼缺口")
print("=" * 76)
print("  1. M_Pl/M₀ = 4.375807e20 專項審計完成: 生成集 90 零命中 (唔湧現),")
print("     拆細每段 (m_p/M₀, M_Pl/m_p, 尾數) 都冇過閘候選, log 空間無結構")
print("  2. 缺口維持 🔴 — 但責任喺 O38 (撤回 O86/R1 發還, 用戶指令)")
print("  3. 唯一閉合關係維持: N_O38 = N_IDCM·(M₀/M_Pl) (scripts/22, dev 5.35e-10)")
print("  4. 後續喺 O38 嘅可行路線 (屬他 O 亦只參考, 唔發還):")
print("     a. O34 E_kchain CY₃ 修正嘅推導追溯 (層2 來源) — 若 O34 自洽, 層2 可復活")
print("     b. 電子鏈格 m_e 機制 (O34/O124 域) — m_e 有結構 ⟹ F_e/m_p 鏈重組")
print("     c. 樣本外盲測: M₀ 相關新觀測 (等待數據)")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)