#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 41: 音階結構 vs 最小缺口 (用戶 insight 審計)
================================================================
日期: 2026-10-18
觸發: 用戶「如果是節拍階梯，這個最小缺口就是音階本身吧」
      — 最小缺口 M₀·t_site/ħ 應該由音階結構產生 (唔係要 fit 嘅孤立數)
音階結構量 (44-tone chain 譜):
  γ_n = 4sin²(πn/88), n=1..44
  ★ Πγ_n = 176 = 2×88 = 2N   (音階全乘積, 精確! 本輪驗證)
  ★ Π√γ_n = 4√11             (音階頻率乘積, 精確)
  ★ Σγ_n = 90                 (音階總和, 已閉合)
  1/sin(π/88) ≈ 88/π           (音階跨度 vs R_world/r_d, dev 2.1e−4)
本輪:
  A. 音階核心恆等式確認 (Πγ/Π√γ/Σγ/1sin)
  B. 最小缺口 M₀·t_site/ħ = 4.0951856e38 對音階量組合 check
     (單冪 176^k/(4√11)^k/90^m/88^n/44^p + 二元組合 + E 閘)
  C. 判決: 「音階本身」= Πγ=176=2N 已閉合; 最小缺口身份 = ?
用法: /usr/bin/python3 scripts/41_musical_scale_audit.py
"""
import mpmath as mp
mp.mp.dps = 50

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

pi = mp.pi
phi = (1 + mp.sqrt(5)) / 2
Mts = mp.mpf('4.0951856e38')   # 最小缺口 M₀·t_site/ħ

print("=" * 76)
print("A. 音階核心恆等式確認 (44-tone)")
print("=" * 76)
P = mp.mpf(1)
for n in range(1, 45):
    P *= 4*mp.sin(mp.mpf(n)*pi/88)**2
P2 = mp.mpf(1)
for n in range(1, 45):
    P2 *= 2*mp.sin(mp.mpf(n)*pi/88)
Sg = sum(mp.mpf(4)*mp.sin(mp.mpf(n)*pi/88)**2 for n in range(1,45))
print(f"  Πγ_n (n=1..44) = {mp.nstr(P,10)}")
chk("A1 Πγ = 176 = 2×88 = 2N (音階全乘積)", abs(P - 176) < mp.mpf('1e-20'))
print(f"  Π√γ_n = {mp.nstr(P2,10)}")
chk("A2 Π√γ = 4√11", abs(P2 - 4*mp.sqrt(11)) < mp.mpf('1e-20'))
print(f"  Σγ_n = {mp.nstr(Sg,8)}")
chk("A3 Σγ = 90", abs(Sg - 90) < mp.mpf('1e-20'))
inv = 1/mp.sin(pi/88)
r88 = 88/pi
print(f"  1/sin(π/88) = {mp.nstr(inv,8)}  vs  88/π = {mp.nstr(r88,8)}  dev = {mp.nstr(abs(inv/r88-1),5)}")
chk("A4 1/sin(π/88) ≈ 88/π (音階跨度≈R_world/r_d)", abs(inv/r88-1) < mp.mpf('3e-4'), f"(dev {mp.nstr(abs(inv/r88-1),5)} 唔過 1e−3, 線索)")

print()
print("=" * 76)
print("B. 最小缺口 M₀·t_site/ħ 對音階量組合 check")
print("=" * 76)
print(f"  M₀·t_site/ħ = {mp.nstr(Mts,8)}  (log₁₀ {mp.nstr(mp.log10(Mts),6)})")
# 單冪族
for base, name in [(176, "176^k (Πγ)"), (4*mp.sqrt(11), "(4√11)^k (Π√γ)"),
                   (90, "90^k (Σγ)"), (88, "88^k (N)"), (44, "44^k (N_d)"),
                   (28.01127, "(88/π)^k")]:
    k = mp.log(Mts)/mp.log(base)
    frac = abs(k - mp.floor(k+mp.mpf('0.5')))
    print(f"  log_{name.split('^')[0].strip('()')} = {mp.nstr(k,6)}  (最近整數距離 {mp.nstr(frac,5)})")
# 二元組合: 176^a × (4√11)^b
print("  二元組合 176^a × (4√11)^b (a=10..25, b=0..20):")
best = (1e9, 0, 0)
for a in range(10, 26):
    for b in range(0, 21):
        v = mp.mpf(176)**a * (4*mp.sqrt(11))**b
        d = abs(v/Mts - 1)
        if d < best[0]: best = (d, a, b)
print(f"  最佳: 176^{best[1]} × (4√11)^{best[2]} dev = {mp.nstr(best[0],4)}")
chk("B1 二元組合冇 <1e−3 命中", best[0] > mp.mpf('1e-3'), f"(best dev {mp.nstr(best[0],4)})")
# 音階跨度冪: (88/π)^k × (Πγ)^m
best2 = (1e9, 0, 0)
for a in range(5, 30):
    for b in range(0, 15):
        v = (88/pi)**a * mp.mpf(176)**b
        d = abs(v/Mts - 1)
        if d < best2[0]: best2 = (d, a, b)
print(f"  88/π^a × 176^b 最佳: dev = {mp.nstr(best2[0],4)}")
chk("B2 音階跨度組合冇 <1e−3 命中", best2[0] > mp.mpf('1e-3'), f"(best dev {mp.nstr(best2[0],4)})")

print()
print("=" * 76)
print("C. 判決 — 「音階本身」結構化")
print("=" * 76)
print("  1. ★ 音階核心結構已閉合: Πγ = 176 = 2N (全乘積), Π√γ = 4√11,")
print("     Σγ = 90, 1/sin(π/88) ≈ 88/π (dev 2.1e−4)")
print("  2. 用戶 insight: 最小缺口 = 音階本身")
print("     ⟹ N_O38 = 44·(M₀·t_site/ħ), 44 = N_d 係音階半譜維度")
print("     ⟹ M₀·t_site/ħ 係『音階總跨度』(每節拍內 M₀ 振盪次數)")
print("  3. 🔴 但最小缺口對音階量單冪/二元組合全零命中 (B1/B2)")
print("     ⟹ M₀·t_site/ħ 未有音階冪結構 — 『音階本身』係命名, 唔係證明")
print("  4. O38 缺口維持 🔴; 新閉合 = Πγ = 176 = 2N (音階全乘積)")
print("     — 呢個係『音階本身』嘅真實結構核心")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)