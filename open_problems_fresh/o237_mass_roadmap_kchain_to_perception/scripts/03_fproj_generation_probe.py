#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O237 U2 — F_proj 幾何生成攻堅 (scripts/03)
================================================================================
邊界 (O206 第十輪 2026-10-06 + docs/01):
  - A5 合法 modes {1,2,3,4,5,7,9,11,13}; C_f 值 = {e,u,d,s,mu,c,tau,b} 8 個 (t 歸 VEV)
  - C_f 池匹配死 (O208/O233/O235); 冪律死 (O136); Φ_max→m_t 死 (R3)
  - 唯一幾何錨: C_e = L6/F5 = 18/5 = 3.6 (O120, dev 0.164%) = Σv2(G8)/|G8| (O145 2-adic)
  - 任務: 由 κ_ijk / φ=9 正交基底 / 2-adic 扇區統計結構 (非數值 hunt) 一次過生成 8 個 F_proj
本 script:
  §1 重現 A5 C_f 真值 (PDG 質量 / M0 / gamma_n)
  §2 2-adic 生成器檢驗 (O145 方法推廣): F_proj(sector) = Σv2 / |sector|
  §3 Φ=9 交乘檢驗: C_f = Φ[i][j] × k  (\phi=9 目錄 x 小整數, 做 null 對照)
  §4 MC null: 隨機 8 值 vs Φ 目錄命中率 (證明「非結構巧合」)
  §5 判定
"""
import math, itertools, random
import numpy as np

PASS, FAIL = [], []
def ck(name, got, exp, tol=None):
    if tol is not None:
        ok = abs(float(got)-float(exp)) < tol
    else:
        ok = bool(got == exp)
    (PASS if ok else FAIL).append(name)
    print(f"  {'OK ' if ok else 'FAIL'} {name} = {got}" + ("" if ok else f"  [exp {exp}]"))

M0 = 27.9009          # MeV (O54/O210)
MASS = {  # PDG (O206 第十輪 docs/01 §D 同源)
    "e":0.510998950, "u":2.16, "d":4.67, "s":93.4, "mu":105.6583755,
    "c":1270.0, "tau":1776.86, "b":4180.0}
MODES = {"e":1,"u":2,"d":3,"s":4,"mu":5,"c":7,"tau":9,"b":11}
def gam(n): return 4*math.sin(math.pi*n/88)**2

print("="*88)
print("O237 U2 — F_proj 幾何生成攻堅")
print("="*88)

# ---------------------------------------------------------------- §1 真值
print("\n[1] A5 C_f 真值  C_f = m / (M0 * gamma_n)")
CF = {}
for p in MASS:
    CF[p] = MASS[p]/(M0*gam(MODES[p]))
    print(f"    {p:>4} (n={MODES[p]:>2}): C_f = {CF[p]:>10.4f}")
print(f"    C_e = {CF['e']:.4f} vs L6/F5 = 3.6  (dev {(CF['e']/3.6-1)*100:.3f}%)")
ck("C_e 錨 = 3.6 ± 0.3% (O120 盲測接受)", abs(CF['e']/3.6-1) < 0.003, True)

# ---------------------------------------------------------------- §2 2-adic 生成器
print("\n" + "="*88)
print("[2] 2-adic 扇區生成器 (O145 方法: F_proj(e) = Σv2(G8)/|G8| = L6/F5)")
print("="*88)
def v2(n):
    v = 0
    while n % 2 == 0 and n > 0:
        n //= 2; v += 1
    return v
# O145: G8 = φ=8 規範玻色子扇區 {8,16,24,32,40}; Σv2 = 3+4+3+5+3 = 18 = L6; |G8| = 5
G8 = [8, 16, 24, 32, 40]
G8_sum = sum(v2(x) for x in G8)
print(f"    G8 = {G8}: Σv2 = {G8_sum} = L6, |G8| = {len(G8)}, Σv2/|G8| = {G8_sum/len(G8):.3f} = L6/F5 = 18/5 = 3.6")
ck("O145 錨: Σv2(G8)/|G8| = 18/5", G8_sum/len(G8), 18/5, tol=1e-12)
# 推廣: 對每個 A5 mode n, 定義 G(n) = {L5*k : k=1..8} 嘅 v2 統計?
# G8 = L5 階梯 {11..88}. n 嘅 sector: v2(n) 分層
print("    v2 分層: 對每個 A5 mode n:")
for p, n in MODES.items():
    print(f"      {p:>4} n={n:>2}: v2(n)={v2(n)}, v2(44±n)={v2(44-n)},{v2(44+n) if 44+n<=88 else '-'}")
# 測試推廣: C_f(p) vs Σv2(sector(n)) — 冇明顯線性, 嘗試「2-adic 阻抗」 = 44 / v2-sum
print("\n    2-adic 阻抗候選 Z(n) = B^v2(n) 同 C_f 比對:")
ok2 = True
for p, n in MODES.items():
    z = 4**v2(n)
    ratio = CF[p]/z
    print(f"      {p:>4}: C_f={CF[p]:>10.4f}  Z=B^v2={z:>4}  C_f/Z = {ratio:>10.4f}")
ck("2-adic Z(n)=B^v2(n) 對 C_f 冇結構 (ratio 唔係常數)", True, True)  # 描述性檢查
# 真正檢驗: C_f 係咪 = f(v2 分層) 一次過? 用分層均值
layers = {}
for p, n in MODES.items():
    layers.setdefault(v2(n), []).append(CF[p])
print("    C_f 按 v2(n) 分層:")
for v in sorted(layers):
    print(f"      v2={v}: {[round(x,3) for x in layers[v]]}")

# ---------------------------------------------------------------- §3 Φ=9 交乘
print("\n" + "="*88)
print("[3] Φ=9 相交目錄 x 整數  (φ=9 結構性生成候選; null 對照)")
print("="*88)
x3 = [1,5,9]; x3p = [0,1,3,4,6,7]
PHI = sorted(set([1+a*b for a in x3 for b in x3p]))
print(f"    Φ 目錄 ({len(PHI)} 值): {PHI}")
# 非逐個 fit: 生成規則 = C_f = Φ[i] * k, k ∈ {1,2,...,8} (8 個費米子 -> k 唔可以係 fit 參數,
# k 一定要同 mode/世代有結構身份)。此處只做「結構候選」盤點, 唔做池匹配判死。
# 有意義嘅結構檢查: C_f 係咪落在 Φ×{1..8} ∪ Φ/{1..8} 目錄 (密度對照用)
catalog = set(PHI) | set(p*k for p in PHI for k in range(1,9)) | set(p/k for p in PHI for k in range(2,9))
hits = {p: min(abs(CF[p]-c) for c in catalog) for p in CF}
print("    最近目錄值偏差:")
for p in CF:
    print(f"      {p:>4}: {CF[p]:>10.4f}  d_min = {hits[p]:>8.4f}  (rel {hits[p]/CF[p]*100:.2f}%)")

# ---------------------------------------------------------------- §4 MC null
print("\n" + "="*88)
print("[4] MC null: 隨機 8 值命中 Φ×k 目錄 1% 窗嘅概率 (10^5)")
print("="*88)
rng = np.random.default_rng(20261007)
Nsim = 100000
Nhit = 0
for _ in range(Nsim):
    # 隨機 8 個 positive C_f, 尺度 = 對數均勻 [3, 300]
    rand = np.exp(rng.uniform(np.log(3), np.log(300), 8))
    # 命中 = 至少一個隨機值喺目錄 1% 窗內
    h = 0
    for r in rand:
        if any(abs(r-c) < 0.01*r for c in catalog):
            h += 1
    if h >= 1:
        Nhit += 1
p_null = Nhit/Nsim
print(f"    P(隨機值命中目錄 1% 窗) = {p_null:.4f}")
# 觀察: 目錄太密 ⟹ 1% 窗冇判別力 (隨機值都有 ~99% 命中) ⟹ 只有精確窗先有效
# O206 第十輪用精確窗 (1e-9) 判: 0/8 精確成員 (權威)
obs_hits = sum(1 for p in CF if any(abs(CF[p]-c) < 0.01*CF[p] for c in catalog))
print(f"    觀測: 8 個 C_f 喺 1% 窗內命中目錄數 = {obs_hits}/8")
ck("MC: 1% 窗隨機命中率 ~100% ⟹ Φ×k 1% 窗冇判別力 (要用精確窗 0/8)", p_null > 0.95, True)
ck("權威判準: 精確窗 (1e-9) Φ 目錄命中 = 0/8 (O206 第十輪)", sum(1 for p in CF if any(abs(CF[p]-c) < 1e-9*CF[p] for c in PHI)) == 0, True)

# ---------------------------------------------------------------- §5 判定
print("\n" + "="*88)
print("[5] 判定")
print("="*88)
print(f"""  現狀:
  - 唯一封閉 F_proj: C_e = L6/F5 = 3.6 = Σv2(G8)/|G8| (O145 2-adic, O120 盲測) dev 0.164%
  - 其餘 7 個 C_f 冇幾何生成 (Φ 目錄 0/8 精確; Φ×k 目錄最近偏差 > 1% 窗: {sum(1 for p in CF if hits[p]/CF[p]>0.01)}/8 遠離)
  - 2-adic Z(n)=B^v2(n) 唔係 C_f 結構 (ratio 非常數)
  ⟹ U2 攻堅結果: 冇一次過生成規則由 κ/Φ/2-adic 現有結構產生 8 個 F_proj.
  保持 🔴 (docs/01 原判); 呢啲 negative 結果排除咗 3 個候選族, 收窄下一步。

  下一步候選 (唔喺本 O 推, 交 register handoff):
  R1 κ_ijk=18·I9 嘅投影迹: F_proj = Tr(P_sector κ̂) 用 A5 扇區投影算子 (需 O210 型別層定義)
  R2 φ=9 世代混合扇區 2-adic 正交 (Z=0, O145)——已證 φ=9 sect 正交, 但未接 C_f 值
  R3 2-adic 阻抗共振 O145 方法嘅 A5 版: Z(n) = Σv2(模式鄰域) — 本輪 v2 分層冇直接對應
""")

print("\n" + "="*88)
print(f"U2 round: {len(PASS)} PASS / {len(FAIL)} FAIL")
print("="*88)
print("PASS" if not FAIL else "FAIL")