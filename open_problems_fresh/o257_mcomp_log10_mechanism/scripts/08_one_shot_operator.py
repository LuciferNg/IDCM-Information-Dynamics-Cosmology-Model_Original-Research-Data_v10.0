#!/usr/bin/env python3
"""
O257 scripts/08 — 一次性算子盲掃: r = M_pl/M_comp 無 loop 表示 (2026-10-21)
=============================================================================
調律者 steers:
  「邏輯上好像不應該有log, 對數不像是天然產物」
  「大數是否存在天然機制約化」
  「套用ISA級別的microcode, 沒有for while等高級指令, 應該怎樣歷遍?」

核心論證:
  - ISA 冇 for/while ⟹ 冇「重複 N 次」⟹ 冪/指數/log 唔可以係歷遍
  - IDCM 算子喺譜空間對角 (γ_n 分解), 一次算子作用完成全譜 —
    唔使「歷遍 88 site」就得到 Σγ/Πγ/det (O126: 44 reads = 44 模投影一次完成)
  - log 只係人類計數壓縮; 大數 = 計數(序數)非尺度 (10-19 穹頂假說)
  - 所以 M_pl/M_comp = r = 330959 應該有「一次性乘除算式」表示 (無 pow/log 循環)

本 script: 盲掃已註冊結構量嘅乘除組合, 搵 |組合 − r|/r < 0.1% 命中
  判據: 名義一致 (非閉合!) — 只報命中, 唔升格
  禁: φ-power fit、O49 後驗凑合、超過 3 項組合 (look-elsewhere 控制)
"""
import mpmath as mp
import itertools
import random
mp.mp.dps = 50

phi = (mp.mpf(1) + mp.sqrt(5)) / 2
B, Nd, N, Ngen = 4, 44, 88, 3

def gamma(n, NN=N):
    return 4 * mp.sin(n * mp.pi / NN) ** 2

print("=" * 72)
print("O257 scripts/08 — 一次性算子盲掃 (無 loop 表示)")
print("=" * 72)

g6 = gamma(6)
target_log10 = 1/g6 - 1/mp.mpf(76)
M_pl = mp.mpf("1.2209e19")
M_comp_formula = M_pl * mp.power(10, -target_log10)
r = M_pl / M_comp_formula
print(f"r = M_pl/M_comp = {mp.nstr(r, 12)}")
print()

# ── 結構量池 (一次性, 全部已註冊) ──
pool = {}
# γ 系列
pool["γ6"] = g6
pool["1/γ6"] = 1/g6
pool["γ5"] = gamma(5); pool["γ7"] = gamma(7); pool["γ4"] = gamma(4)
pool["γ12_176"] = gamma(12, 176)
# 譜和
pool["Σγ(1..44)"] = mp.mpf(90)
pool["Σγ_odd"] = mp.mpf(88)
pool["Σγ_even"] = mp.mpf(90)
pool["Σ1/γ_all"] = mp.mpf("322.75")
# 譜積 (scripts/07 新恆等)
pool["Πγ(1..87)"] = mp.mpf(7744)
pool["Πγ(1..44)"] = mp.mpf(176)
pool["Πγ_odd"] = mp.mpf(4)
pool["Πγ_even"] = mp.mpf(1936)     # 7744/4 = 44²
pool["Πγ(45..87)"] = mp.mpf(44)
# 基礎
pool["88"] = 88; pool["44"] = 44; pool["90"] = 90; pool["60"] = 60; pool["96"] = 96
pool["176"] = 176; pool["7744"] = 7744; pool["88²"] = 7744; pool["44²"] = 1936
pool["80"] = 80; pool["100"] = 100; pool["123"] = 123; pool["76"] = 76; pool["29"] = 29
pool["45"] = 45; pool["19"] = 19; pool["37"] = 37; pool["33"] = 33; pool["34"] = 34
pool["21"] = 21; pool["55"] = 55; pool["89"] = 89; pool["144"] = 144; pool["11"] = 11
# Lucas/Fib
L = {1:1,2:3,3:4,4:7,5:11,6:18,7:29,8:47,9:76,10:123,11:199,12:322,13:521,14:843}
Ff = {3:2,4:3,5:5,6:8,7:13,8:21,9:34,10:55,11:89,12:144,13:233,14:377,15:610}
for k, v in L.items(): pool[f"L{k}"] = v
for k, v in Ff.items(): pool[f"F{k}"] = v
# hop 家族
pool["hop_sum"] = 60; pool["hop_max"] = 12; pool["hop_big"] = 88-12
# det ratio 家族
pool["1/γ4"] = 1/gamma(4); pool["1/γ5"] = 1/gamma(5); pool["1/γ7"] = 1/gamma(7)
pool["1/γ6×88"] = (1/g6)*88
pool["88/γ6"] = 88/g6
pool["1/γ6×44"] = (1/g6)*44

# 除掉太細嘅數 (分母 0 風險)
items = [(k, mp.mpf(v)) for k, v in pool.items()]
print(f"結構量池: {len(items)} 項")
print()

# ── 1 項直接 ──
hits1 = []
for k, v in items:
    if v <= 0: continue
    dev = abs(v - r)/r
    if dev < 0.001:
        hits1.append((k, mp.nstr(v, 8), mp.nstr(dev*100, 4)))
print(f"[1項] 命中 ±0.1%: {len(hits1)}")
for h in hits1: print(f"    {h[0]} = {h[1]} (dev {h[2]}%)")

# ── 2 項乘除 ──
print(f"\n[2項] a×b, a/b, a×88, a×44, a×90 等 — 掃 {len(items)}×{len(items)}:")
hits2 = []
for (ka, va), (kb, vb) in itertools.product(items, repeat=2):
    if va <= 0 or vb <= 0: continue
    for op, val in [("*", va*vb), ("/", va/vb)]:
        if val <= 0: continue
        dev = abs(val - r)/r
        if dev < 0.001:
            hits2.append((f"{ka}{op}{kb}", mp.nstr(val, 8), mp.nstr(dev*100, 4)))
# 去重保留最少
seen = set(); uniq = []
for h in hits2:
    if h[1] not in seen:
        seen.add(h[1]); uniq.append(h)
print(f"  命中 ±0.1%: {len(hits2)} (去重 {len(uniq)})")
for h in uniq[:30]: print(f"    {h[0]} = {h[1]} (dev {h[2]}%)")

# ── 3 項 (限: 一個乘一個除) ──
print(f"\n[3項] a×b/c — 抽樣 (全掃 = {len(items)}³ 太大, 抽 5000 組合):")
random.seed(257)
hits3 = []
for _ in range(5000):
    ka, kb, kc = random.sample(items, 3)
    va, vb, vc = ka[1], kb[1], kc[1]
    if va <= 0 or vb <= 0 or vc <= 0: continue
    val = va*vb/vc
    if val <= 0: continue
    dev = abs(val - r)/r
    if dev < 0.001:
        hits3.append((f"{ka[0]}×{kb[0]}/{kc[0]}", mp.nstr(val, 8), mp.nstr(dev*100, 4)))
print(f"  抽樣命中 ±0.1%: {len(hits3)}")
for h in hits3[:20]: print(f"    {h[0]} = {h[1]} (dev {h[2]}%)")

# ── 重點: 有冇 88/60/90 組合直接出 r? ──
print("\n[重點檢定] 基本結構組合:")
combos = {
  "90×88×44/??": None,
  "88³/2": 88**3/2,
  "88²×43": 88*88*43,
  "88²×42.75": 88*88*42.75,
  "60³×1.53": None,
}
for name, val in combos.items():
    if val is None: continue
    dev = abs(val - r)/r*100
    print(f"    {name} = {mp.nstr(mp.mpf(val),9)} dev {mp.nstr(dev,4)}%")
# 88³/2 = 340736 dev vs 10^{1/γ₆}=341139
x = mp.power(10, 1/g6)
print(f"    10^(1/γ6) = {mp.nstr(x,9)} vs 88³/2 = {mp.nstr(mp.mpf(88**3)/2,9)} dev {mp.nstr(abs(x-88**3/2)/(88**3/2)*100,4)}%")
# r 直接除 88 系列
print(f"    r/7744  = {mp.nstr(r/7744, 6)}")
print(f"    r/7744/43 = {mp.nstr(r/7744/43, 8)}")
print(f"    r/(88×90) = {mp.nstr(r/(88*90), 8)}  ← 88×90 = 7920")
print(f"    r/(88×90)×? 76/76…")
print(f"    r×44/90 = {mp.nstr(r*44/90, 6)}")
print(f"    r/88/44/90 = {mp.nstr(r/88/44/90, 8)}")
# 一個特別組合: 176 × 44 × 43
print(f"    176×44×43 = {176*44*43}  vs r = {mp.nstr(r,6)}")
print(f"    88×90×41.8 =")
print(f"    r/88 = {mp.nstr(r/88, 6)}  (3760.9 — 有冇身份?)")
print(f"    r/88/43 = {mp.nstr(r/88/43, 8)}")
print(f"    r/88/45 = {mp.nstr(r/88/45, 6)}  (83.6 = 88×0.95? no)")
# 3760.9 身份?
q = r/88
for name, v in [("φ^8", phi**8), ("φ^9", phi**9), ("44×85.5", 44*85.5), ("34×110.6", None)]:
    if v is not None:
        print(f"    r/88 = {mp.nstr(q,8)} vs {name} = {mp.nstr(v,8)} dev {mp.nstr(abs(q-v)/v*100,4)}%")

print("\n" + "=" * 40)
print("RESULT: 名義一致只報命中, 唔升格 (look-elsewhere: 池 100+ 項, 2項組合 ~10⁴, 期望 ~10 個假命中)")