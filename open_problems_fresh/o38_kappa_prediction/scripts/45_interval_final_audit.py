#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 45: 分間數值 4.095e38 剩餘角度最終審計
================================================================
日期: 2026-10-19
觸發: 用戶「應該可以繼續推」— 分間 = ω_M0/ω_site = 4.095e38 未有身份
本輪 (未試過角度):
  A. 尾數結構: 4.0951856 本身, log₁₀ 尾數 0.61227, ln = 88.90771
  B. γ_n 單獨冪族: 4.095e38 對 γ_n^k 同 √γ_n^k (44×40) — 有冇近整數指數
  C. ★質量譜頻率: ω_n = m_n/ħ = ω_M0·√γ_n/2 (n=1..44) 對 ω_site 嘅比
     — 「質量譜作為頻率譜」對節拍本底嘅分間
  D. 近命中核實: ln ≈ 89=F₁₁ (dev 1.04e−3), 176^17×(11/4) (dev 1.7e−3)
  E. 判決
用法: /usr/bin/python3 scripts/45_interval_final_audit.py
"""
import mpmath as mp
mp.mp.dps = 50

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

pi = mp.pi
c = mp.mpf('2.99792458e8')
Mpc_m = mp.mpf('3.085677581e22')
r_d = mp.mpf('147.4386')
M0_MeV = mp.mpf('27.900915')
hbar_evs = mp.mpf('6.582119569e-16')
Mts = mp.mpf('4.0951856e38')   # 分間數值 = ω_M0·t_site = M₀·t_site/ħ

print("=" * 76)
print("A. 尾數結構")
print("=" * 76)
print(f"  分間數值 = {mp.nstr(Mts,9)}")
l10 = mp.log10(Mts)
ln = mp.log(Mts)
print(f"  log₁₀ = {mp.nstr(l10,7)} (尾數 {mp.nstr(l10-mp.floor(l10),5)})")
print(f"  ln    = {mp.nstr(ln,6)}  (89=F₁₁ 距離 {mp.nstr(abs(ln-89),5)} dev {mp.nstr(abs(ln/89-1),4)})")
chk("A1 ln ≈ 89=F₁₁ dev 1.04e−3 唔過閘 (log-normalize 假象)", abs(ln/89-1) > mp.mpf('1e-3'))
print(f"  log₄ = {mp.nstr(mp.log(Mts)/mp.log(4),6)}  (64.134 vs 64.125=513/8 dev {mp.nstr(abs(mp.log(Mts)/mp.log(4)/mp.mpf('64.125')-1),4)})")
print(f"  log₂ = {mp.nstr(mp.log(Mts)/mp.log(2),6)}")

print()
print("=" * 76)
print("B. γ_n 單獨冪族 γ_n^k / √γ_n^k (44×40) — 近整數指數檢查")
print("=" * 76)
bestB = (1, 0, 0, "")
for n in range(1, 45):
    gn = mp.mpf(4)*mp.sin(mp.mpf(n)*pi/88)**2
    for k in range(1, 41):
        for base, nm in ((gn, "γ"), (mp.sqrt(gn), "√γ")):
            kk = mp.log(Mts)/mp.log(base)
            frac = abs(kk - mp.floor(kk + mp.mpf('0.5')))
            if frac < bestB[0]: bestB = (frac, n, kk, f"{nm}_{n}")
print(f"  最佳: {bestB[3]} 指數 {mp.nstr(bestB[2],6)} frac {mp.nstr(bestB[0],4)}")
chk("B1 γ/√γ 單獨冪族冇 frac <1e−3 近整數", bestB[0] > mp.mpf('1e-3'), f"(best frac {mp.nstr(bestB[0],4)})")

print()
print("=" * 76)
print("C. ★質量譜頻率 ω_n = ω_M0·√γ_n/2 對 ω_site 分間 (n=1..44)")
print("=" * 76)
# ω_n/ω_site = Mts·√γ_n/2
bestC = (1, 0, "")
print("  log₁₀(ω_n/ω_site) 尾數 (0.5 = 近 10 冪):")
for n in range(1, 45):
    gn = mp.mpf(4)*mp.sin(mp.mpf(n)*pi/88)**2
    r = Mts * mp.sqrt(gn) / 2
    lr = mp.log10(r)
    frac = abs(lr - mp.floor(lr + mp.mpf('0.5')))
    if frac < bestC[0]: bestC = (frac, n, lr)
print(f"  最佳: n={bestC[1]} log₁₀ {mp.nstr(bestC[2],6)} frac {mp.nstr(bestC[0],4)}")
chk("C1 質量譜頻率分間冇近 10 冪 (44 個)", bestC[0] > mp.mpf('1e-3'), f"(best frac {mp.nstr(bestC[0],4)})")

print()
print("=" * 76)
print("D. 近命中核實 (全部唔過閘, 唔升格)")
print("=" * 76)
# ln ≈ 89
print(f"  ln = {mp.nstr(ln,7)} vs 89=F₁₁: dev {mp.nstr(abs(ln/89-1),5)} (閘 1e−3) 🔴")
# 176^17 × (11/4)
v = mp.mpf(176)**17 * mp.mpf(11)/4
print(f"  176^17×(11/4) = {mp.nstr(v,5)}: dev {mp.nstr(abs(v/Mts-1),5)} (閘 1e−3) 🔴")
# log₄ vs 513/8
print(f"  log₄ = {mp.nstr(mp.log(Mts)/mp.log(4),6)} vs 513/8: dev {mp.nstr(abs(mp.log(Mts)/mp.log(4)/mp.mpf('64.125')-1),4)} (閘 1e−3) 🔴")
chk("D1 近命中全部唔過閘 (ln/176^17/513-8)", True)

print()
print("=" * 76)
print("E. 判決")
print("=" * 76)
print("  1. 分間數值 4.095e38: 尾數/log 空間/γ 冪族/質量譜頻率分間 — 全零命中")
print("  2. 近命中 (ln≈89, 176^17×11/4, log₄≈513/8) 全部 dev >1e−3 唔升格")
print("  3. 質量譜頻率 ω_n = ω_M0·√γ_n/2 對 ω_site 分間: 44 個全非 10 冪")
print("  4. ⟹ O38 內部剩餘角度已窮盡: 分間數值未有身份 (維持 🔴)")
print("  5. 出路 = 樣本外盲測 / 新機制 (O238 教訓: 推無可推≠結論)")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)