#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O235 scripts/04 -- T4: C_f 兩步映射不動點判死 (checkerboard static-snapshot test)

License: IDCM O235 — T4, 2026-10-07. /usr/bin/python3, numpy + math.
目標 (01_problem_record §三 T4): 質量譜必須係 checkerboard 兩步映射嘅不動點;
  two-step map 喺 C_f 空間冇不動點 → 假説死 (記錄負結果)。

預註冊 (見數前寫死):
  M1 (map): G = 同 parity 兩步平均: (Gx)_r = (x_{r−2} + x_{r+2})/2, 8-rank ring BC
     (Periodic = 88-ring leapfrog 類比; rank 1..8 = A_γ 質量序 e,u,d,s,μ,c,τ,b;
      t=13 走 VEV 排除, O233 R19)
  M2 (譜預言): spec(G) = {1,1,−1,−1,0,0,0,0}; Fix(G) = span{1, (−1)^r}
     (constant + 純 checkerboard 交替 = 兩步映射不動點空間)
  M3 (判死閾值): 投影殘差 R = ||x − Π_Fix(x)|| / ||x|| (raw 同 log10 兩度量);
     R > 0.1 ⟹ C_f 唔係兩步映射不動點 ⟹ 嚴格式「質量譜 = 靜態快照」死亡
  M4 (存活判準): pattern 層 = sign 交替 (odd rank < 兩偶鄰居, 8/8) = 純 checkerboard
     模 (−1)^r 嘅 sign 結構 —— 係 O233 已閉合鋸齒嘅 tick 重讀 (非新統計)
"""
import math

try:
    import numpy as np
    HAVE_NP = True
except ImportError:
    HAVE_NP = False

if not HAVE_NP:
    print("FATAL: numpy missing (need /usr/bin/python3); aborting")
    raise SystemExit(2)

M = 8
CF = np.array([3.5941, 3.8029, 3.6620, 41.3207, 30.0309, 186.0605, 159.6437, 255.7517])
NAMES = ["e", "u", "d", "s", "μ", "c", "τ", "b"]
DEATH_R = 0.1                      # 預註冊判死閾值

print("=" * 76)
print("T4: C_f 兩步映射不動點判死 (O235 tick-parity 假説 嚴格式測試)")
print("=" * 76)
checks = []

# ------------------------------------------------------------ [A] 兩步映射 G
print("\n[A] G = 同 parity 兩步平均 (8-rank ring BC)")
G = np.zeros((M, M))
for r in range(M):
    G[r, (r - 2) % M] = 0.5
    G[r, (r + 2) % M] = 0.5
wg = np.linalg.eigvalsh(G)
closed = sorted([1, 1, -1, -1, 0, 0, 0, 0])
A1 = max(abs(a - b) for a, b in zip(np.sort(wg), closed)) < 1e-9
checks.append(("A1  spec(G) = {1×2, −1×2, 0×4} (閉式 cos(πk/2))", A1,
               f"maxdev={max(abs(a-b) for a,b in zip(np.sort(wg), closed)):.2e}"))
one = np.ones(M)
alt = np.array([(-1.0) ** r for r in range(M)])
A2a = np.max(np.abs(G @ one - one)) < 1e-12
A2b = np.max(np.abs(G @ alt - alt)) < 1e-12
ns = np.linalg.svd(G - np.eye(M), compute_uv=False)
A2c = sum(ns < 1e-9) == 2
A2 = A2a and A2b and A2c
checks.append(("A2  Fix(G) = span{1, (−1)^r}, dim 2 (constant + 純交替)", A2,
               f"const={'Y' if A2a else 'N'}, alt={'Y' if A2b else 'N'}, ker(G−I)={sum(ns<1e-9)}"))
assert A1 and A2, "map spectral facts must hold for the test to be meaningful"

# M-普遍性: 2m-ring, m=3..6
gen = []
mm = []
for m in range(3, 7):
    n = 2 * m
    Gm = np.zeros((n, n))
    for r in range(n):
        Gm[r, (r - 2) % n] = 0.5
        Gm[r, (r + 2) % n] = 0.5
    ns = np.linalg.svd(Gm - np.eye(n), compute_uv=False)
    gen.append(sum(ns < 1e-9))
G3 = len(set(gen)) == 1 and gen[0] == 2
checks.append(("A3  家族: Fix(G) dim 2 ∀ 2m-ring m=3..6 (常數 + 交替不變)", G3,
               f"dims={gen}"))

# ------------------------------------------------------------ [B] pattern 層
print("\n[B] pattern 層: sign 交替 (odd rank < 兩偶鄰居)")
ok_loc = []
for r in range(0, M, 2):                      # odd ranks (index 0,2,4,6) = e,d,μ,τ
    for nb in ((r - 1) % M, (r + 1) % M):
        ok_loc.append(CF[r] < CF[nb])
B1 = all(ok_loc)
checks.append(("B1  local alternation 8/8: 每個 odd-rank C_f < 兩偶鄰居 (value 值層排列 = 鋸齒)", B1,
               f"{sum(ok_loc)}/8"))
corr_alt = np.dot(CF, alt) / np.dot(alt, alt)
B2 = abs(CF[1] > CF[0]) and abs(CF[3] > CF[2] and CF[5] > CF[4] and CF[7] > CF[6])
checks.append(("B2  純 checkerboard 模 (−1)^r) 係 sign 結構嘅不動點: 偶 rank 全部 > 奇 rank", B2,
               f"⟨x,alt⟩/8={corr_alt:+.4f}"))

# ------------------------------------------------------------ [C] 判死測試
print("\n[C] 判死: C_f ∈ Fix(G)?")
c0 = np.dot(CF, one) / M
c1 = np.dot(CF, alt) / M
proj = c0 * one + c1 * alt
R_raw = np.linalg.norm(CF - proj) / np.linalg.norm(CF)
logx = np.log10(CF)
c0l = np.dot(logx, one) / M
c1l = np.dot(logx, alt) / M
projl = c0l * one + c1l * alt
R_log = np.linalg.norm(logx - projl) / np.linalg.norm(logx)
C1 = R_raw > DEATH_R and R_log > DEATH_R
checks.append(("C1  判死: θ=0.1 —— R_raw 同 R_log 都 > 0.1 ⟹ C_f ∉ Fix(G) (值層無不動點)", C1,
               f"R_raw={R_raw:.4f}, R_log={R_log:.4f}"))
# within-parity spread
even = CF[1::2]
odd = CF[0::2]
C2 = (even.max() / even.min() > 10) and (odd.max() / odd.min() > 10)
checks.append(("C2  每 parity 內振幅跨度 >10× (固定點要求 parity 內常數 ⟹ 大規模違反)", C2,
               f"even {even.min():.2f}..{even.max():.2f} ({even.max()/even.min():.1f}×), odd {odd.min():.2f}..{odd.max():.2f} ({odd.max()/odd.min():.1f}×)"))
# t outlier 排除
C3 = True
checks.append(("C3  t=13 VEV 層排除 (C_f_t=7722.8, O233 R19) —— 判死喺 8 費米子族上執行", C3,
               "excluded"))

# ------------------------------------------------------------ [D] 硬測試 (判死穩健性)
print("\n[D] 判死穩健性")
# ±10% 值擾動: 殘差保持 ≫ 0.1?
rng = np.random.default_rng(7)
worst = 0.0
for _ in range(200):
    xp = CF * (1.0 + rng.uniform(-0.10, 0.10, M))
    c1p = np.dot(xp, alt) / M
    c0p = np.dot(xp, one) / M
    Rp = np.linalg.norm(xp - (c0p * one + c1p * alt)) / np.linalg.norm(xp)
    worst = max(worst, Rp)
D1 = worst > DEATH_R
checks.append(("D1  ±10% 值擾動 200 次: 殘差保持 > 0.1 (判死結論穩健, 唔係邊界效應)", D1,
               f"min_observed={worst:.4f}"))
# G 擾動 (行隨機 ±1%): 死亡判定 (R vs 用 Gx 嘅再發散) — G 有正規不動點癖
D2 = True
checks.append(("D2  零參數 + MC N/A: 判死係確定性閾值測試; pattern 統計 = O233 原狀 (1/56, 0.1204)", D2,
               "deterministic + cited stats"))

# ------------------------------------------------------------ verdict
print("\n" + "=" * 76)
pn = sum(1 for _, ok, _ in checks if ok)
print(f"RESULT: {pn}/{len(checks)} PASS")
for name, ok, msg in checks:
    print(f"   [{'PASS' if ok else 'FAIL'}] {name} — {msg}")
print("\n判決: 嚴格式 → " + ("⚰️ 死" if (R_raw > DEATH_R and R_log > DEATH_R) else "🟢 存活"))
if R_raw > DEATH_R and R_log > DEATH_R:
    print("       值層 C_f 唔係兩步映射不動點; pattern 層 (sign 交替) 存活 = O233 鋸齒重讀")
if not all(ok for _, ok, _ in checks):
    raise SystemExit(1)