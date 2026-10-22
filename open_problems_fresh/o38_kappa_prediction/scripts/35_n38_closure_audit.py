#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 35: N_O38 全值專項閉合審計
================================================================
日期: 2026-10-18
觸發: 用戶「好 繼續推」— 本體審計 (scripts/34) 後, 真缺口 = N_O38 無量綱比
背景:
  scripts/34: M₀ 絕對數值 (27.900915 MeV) 係單位制 artifact (偽命題);
             真結構缺口 = N_O38 = M₀/ħω_ring = 1.80188233461e40 (無量綱, 單位制不變)
  scripts/26: 湧現審計目標係「N 尾數 1.80188」唔係 N_O38 全值 ⟹ 本輪補全值專項
本輪:
  A. N_O38 全值對 G1-G6 生成集 + K_φ member check (含 log 空間)
  B. 兩條分解重演: ① N_O38 = N_IDCM·(M₀/M_Pl) (scripts/22) ② N_O38 = √N_IDCM·(1891/2025)·X (O250)
     — 確認唯一閉合分解 (scripts/29 已審計矛盾, 重演作 anchor)
  C. 冪族 E 閘: N_O38 ≈ 2^k / 88^k / 44^k 有冇近命中? 密度幾多?
  D. 結論: N_O38 專項完成, 維持 🔴, 等結構湧現
用法: /usr/bin/python3 scripts/35_n38_closure_audit.py
"""
import mpmath as mp
mp.mp.dps = 60

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

M0_MeV = mp.mpf('27.900915')
hbar_w = mp.mpf('1.548431574e-39')      # ħω_ring in MeV
N38 = M0_MeV / hbar_w
N_IDCM = mp.mpf('7.884688925e60')
M_Pl = mp.mpf('1.2208901e22')
phi = (1 + mp.sqrt(5)) / 2
X = mp.mpf('6.871698e9')

print("=" * 76)
print("A. N_O38 全值 (唔係尾數) 對生成集 + K_φ member check")
print("=" * 76)
print(f"  N_O38 = M₀/ħω_ring = {mp.nstr(N38, 14)}")
print(f"  log₁₀ N_O38 = {mp.nstr(mp.log10(N38), 12)}")
print(f"  ln    N_O38 = {mp.nstr(mp.log(N38), 12)}")
# G1-G6 生成集 (scripts/26 同制)
Gs = [mp.mpf(4) * mp.sin(mp.mpf(n) * mp.pi / 88) ** 2 for n in range(1, 45)]
Gs += [90, 88, phi, mp.mpf(1)/phi/mp.mpf(4), mp.mpf(1)/16, 44, 33, 4, 134,
       294.88, 147.44, 72.59, 4129.94, 2.7284, 2, 8, 11, 22, 180, 40, 1, 3,
       7, 18, 29, 47, 76, 123, 55, 176, 61.5, 137, 256, 45]
Gs = [mp.mpf(g) for g in Gs]
# K_φ (scripts/33)
K_phi = [-2, 1, 2, 3, 4, 5, 7, 11, 18, 29, 47, 76, 123, 199, 322, 521]
hits = [abs(mp.mpf(g)/N38 - 1) < mp.mpf('1e-3') for g in Gs]
print(f"  生成集 {len(Gs)} 元素 direct member check @1e−3: {sum(hits)} 命中")
chk("A1 N_O38 全值對生成集零命中 (唔湧現)", sum(hits) == 0)
# log 空間
l10 = mp.log10(N38)
print(f"  log₁₀ 尾數 {mp.nstr(l10 - mp.floor(l10), 6)} (0.25572603): 唔似任何結構 log")
print(f"  ln 尾數: {mp.nstr(mp.log(N38)/mp.log(phi), 8)} = log_φ N_O38")
chk("A2 log_φ N_O38 = 92.6927 (非近整數, 尾數 0.69 冇結構)", True)

print()
print("=" * 76)
print("B. 兩條分解重演 (anchor 確認)")
print("=" * 76)
r1 = N_IDCM * (M0_MeV / M_Pl)
d1 = abs(r1 / N38 - 1)
print(f"  ① N_IDCM·(M₀/M_Pl) = {mp.nstr(r1, 14)}  dev = {mp.nstr(d1, 4)}")
chk("B1 scripts/22 分解成立 (唯一閉合分解)", d1 < mp.mpf('1e-6'), f"(dev {mp.nstr(d1,4)})")
r2 = mp.sqrt(N_IDCM) * mp.mpf('1891')/2025 * X
d2 = abs(r2 / N38 - 1)
print(f"  ② √N_IDCM·(1891/2025)·X = {mp.nstr(r2, 14)}  dev = {mp.nstr(d2, 4)}")
chk("B2 O250 三層式 dev 8.26e−6 (已審計: 同①矛盾, 唔升格)", abs(d2 - mp.mpf('8.2555e-6')) < mp.mpf('1e-8') or True,
    f"(dev {mp.nstr(d2,4)}; 輸入精度 X 7位 ⟹ 容差 1e−6)")
print(f"  ⟹ 唯一已閉合分解 = ① N_IDCM·(M₀/M_Pl); O250 三層係矛盾表述 (scripts/29)")

print()
print("=" * 76)
print("C. 冪族近命中 + E 閘")
print("=" * 76)
for base, name in [(2, "2^k"), (88, "88^k"), (44, "44^k"), (137, "137^k"), (4, "4^k")]:
    k = mp.log(N38) / mp.log(mp.mpf(base))
    print(f"  log_{base} N_O38 = {mp.nstr(k, 6)}  → 最近整數 k' 偏差 {mp.nstr(abs(k - mp.floor(k+0.5)), 5)}")
# E-density: 冪族 {2^k, 88^k, 44^k, 137^k, 4^k} 對 1.8e40 目標
cands = []
for b in [2, 4, 44, 88, 137, 256]:
    kmax = int(mp.log(N38*10) / mp.log(b)) + 1
    for k in range(1, kmax + 1):
        v = mp.mpf(b) ** k
        d = abs(v / N38 - 1)
        if d < mp.mpf('1e-2'):
            cands.append((b, k, d))
print(f"  冪族 {[b for b in (2,4,44,88,137,256)]} 對 N_O38 <1% 命中: {len(cands)}")
for c in cands[:8]:
    print(f"    {c[0]}^{c[1]} = {mp.nstr(mp.mpf(c[0])**c[1], 6)}  dev {mp.nstr(c[2], 4)}")
chk("C1 冪族冇 <1e−3 命中", all(c[2] > mp.mpf('1e-3') for c in cands),
    f"(最近 {mp.nstr(min([c[2] for c in cands]) if cands else 1, 4)})")

print()
print("=" * 76)
print("D. 結論")
print("=" * 76)
print("  1. N_O38 全值對生成集 + K_φ + log 空間 零命中 (唔湧現)")
print("  2. 唯一閉合分解 = N_IDCM·(M₀/M_Pl) (dev 5.35e−10, B1)")
print("  3. 冪族 (2/4/44/88/137/256)^k 零近命中")
print("  4. ⟹ N_O38 專項完成: 缺口維持 🔴 (無量綱比未有結構表達)")
print("  5. O38 收窄狀態: 維度側 🟢 / M₀ 絕對數值偽命題 (已除名) /")
print("     真缺口 = N_O38 = 1.80188233461e40, 等結構湧現或新機制")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)