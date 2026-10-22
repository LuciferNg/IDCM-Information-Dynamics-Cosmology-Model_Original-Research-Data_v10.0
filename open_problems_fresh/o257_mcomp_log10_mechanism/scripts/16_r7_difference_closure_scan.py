#!/usr/bin/env python3
"""
O257/差值閉合 — R7: 質量比譜結構事前掃描協議 (numpy 向量化版) (2026-10-21)
==============================================================================
調律者 framing: 質量 = 駐波態之間交互嘅同步邊界譜讀數差值。
⟹ m 嘅結構形式 = 差值/比, 唔係 M_pl·10^… 絕對標度 fit。

實驗 anchor (差譜本性):
  Δm²₂₁ = 7.53e-5 eV², Δm²₃₁ = 2.434e-3 eV²
  ratio = 32.3 ≈ 2B² = 32 (O57 已確立)
  兩個 Δm² 方程, 三個未知 ⟹ 需要第三方程 = 譜結構比 (m₃/m₂)

協議 (事前定義):
  [A] m3/m2 ~ γ_a/γ_b          (直接 γ 比)
  [B] m3/m2 ~ 1/γ_a − 1/γ_b    (倒數差, 讀數差值 spirit)
  [C] m3/m2 ~ 1 + k(γ_a−γ_b)   (線性譜差修正)
  [D] m3/m2 ~ (pγ_a+qγ_b)/(rγ_c+sγ_d) 抽樣 (線性組合比)
  [E] m3/m2 ~ c·γ_a/γ_b + d 等 hmm 只做 A-D 已夠

目標 (只做命中報告, 唔用嚟揀算子):
  m3/m2 = 0.053586/0.022645 = 2.366389...
  m2/m1 = 0.022645/0.020908 = 1.083072...
"""
import numpy as np
import random

# ── γ 譜 (float64 夠 — 命中檢驗到 0.01%) ──
N = 88
n = np.arange(1, 45, dtype=float)
gamma = 4*np.sin(n*np.pi/N)**2          # γ₁..γ₄₄
inv_g = 1/gamma

# targets
m3_m2 = 0.053586/0.022645
m2_m1 = 0.022645/0.020908
m3_m1 = 0.053586/0.020908
print("="*70)
print("差值閉合 R7: 質量比譜結構事前掃描 (numpy)")
print("="*70)
print(f"targets: m3/m2 = {m3_m2:.9f}  m2/m1 = {m2_m1:.9f}  m3/m1 = {m3_m1:.9f}")

# ── [A] γ_a/γ_b ──
ga = gamma[:, None]      # (44,1)
gb = gamma[None, :]      # (1,44)
rat = ga/gb              # (44,44)
print(f"\n[A] 直接 γ 比: 44×44 = {rat.size} 候選")
best_A = np.unravel_index(np.argmin(np.abs(rat/m3_m2 - 1)), rat.shape)
print(f"  最優: γ{best_A[0]+1}/γ{best_A[1]+1} = {rat[best_A]:.9f}  dev {abs(rat[best_A]/m3_m2-1)*100:.6f}%")
hA01 = np.sum(np.abs(rat/m3_m2 - 1)*100 < 0.1)
hA001 = np.sum(np.abs(rat/m3_m2 - 1)*100 < 0.01)
print(f"  |dev|<0.1%: {hA01}  |dev|<0.01%: {hA001}")

# ── [B] 1/γ_a − 1/γ_b (b>a 保證正) ──
iag = inv_g[:, None] - inv_g[None, :]   # 全 44×44, 取正
diff = iag[iag > 0]
print(f"\n[B] 倒數差: {(iag>0).sum()} 正候選")
if diff.size:
    bd = np.abs(diff/m3_m2 - 1)
    ib = np.argmin(bd)
    best_B = diff[ib]
    # 搵返 (a,b)
    cand_arr = iag
    idx = np.argwhere(np.abs(cand_arr - best_B) < 1e-14)
    print(f"  最優: {best_B:.9f} dev {bd[ib]*100:.6f}%  (a,b)={idx[0][0]+1},{idx[0][1]+1}")
    print(f"  |dev|<0.1%: {np.sum(bd*100<0.1)}  |dev|<0.01%: {np.sum(bd*100<0.01)}")

# ── [C] 1 + k(γ_a−γ_b), k ∈ 結構數 {1,2,3,4,5,8,10,12,44} ──
ks = [1,2,3,4,5,8,10,12,44]
print(f"\n[C] 線性譜差 1+kΔγ: {len(ks)}×44×44 候選")
best_C = None
for k in ks:
    v = 1 + k*(ga - gb)
    m = v > 0
    dev = np.abs(v[m]/m3_m2 - 1)*100
    if dev.size:
        im = np.argmin(dev)
        if best_C is None or dev[im] < best_C[0]:
            coords = np.argwhere(m)[im]
            best_C = (dev[im], k, coords[0]+1, coords[1]+1, v[m][im])
print(f"  最優: k={best_C[1]} γ{best_C[2]}−γ{best_C[3]} = {best_C[4]:.9f} dev {best_C[0]:.6f}%")

# ── [D] 線性組合比抽樣 500k ──
rng = random.Random(25717)
ps = [-2,-1,1,2]
M = 500000
D_vals = np.empty(M); D_names = []
cnt = 0
while cnt < M:
    p,q,r,s = (rng.choice(ps) for _ in range(4))
    a,b,c,d = (rng.randint(1,44) for _ in range(4))
    num = p*gamma[a-1]+q*gamma[b-1]
    den = r*gamma[c-1]+s*gamma[d-1]
    if den != 0:
        v = num/den
        if v > 0:
            D_vals[cnt] = v
            cnt += 1
print(f"\n[D] 線性組合比抽樣: {M} 候選")
dd = np.abs(D_vals/m3_m2 - 1)*100
print(f"  最優 dev: {dd.min():.6f}%")
print(f"  |dev|<0.1%: {np.sum(dd<0.1)}  |dev|<0.01%: {np.sum(dd<0.01)}")

# ── [E] m2/m1 交叉檢查 ──
print(f"\n[交叉] m2/m1 = {m2_m1:.9f} 命中檢查 (全 A 池):")
ea = np.abs(rat/m2_m1 - 1)*100
print(f"  最優 A: {rat[np.unravel_index(np.argmin(ea), rat.shape)]:.9f} dev {ea.min():.6f}%")
print(f"  |dev|<0.1%: {np.sum(ea<0.1)}  |dev|<0.01%: {np.sum(ea<0.01)}")

# ── [F] MC null: 隨機目標 T∈[1.5,3.2] hit 率 (A+B 池 50k 抽樣) ──
print("\n[F] MC null: 隨機目標 T∈[1.5,3.2], 池 = A∪B 抽樣計 density")
rng2 = random.Random(25718)
# 預抽池: A 全 1936 + B 全 946
pool = rat.flatten().tolist() + diff.flatten().tolist()
print(f"  (pool size = {len(pool)})")
NMC = 2000
hitsA = 0; hitsB = 0
for _ in range(NMC):
    T = rng2.uniform(1.5, 3.2)
    # 全池掃描 (2882 個, 快)
    bd = min(abs(s/T - 1)*100 for s in pool)
    if bd < 0.1: hitsA += 1
    if bd < 0.01: hitsB += 1
print(f"  隨機目標 |dev|<0.1% 命中率(3000抽樣池): {hitsA/NMC*100:.2f}%")
print(f"  隨機目標 |dev|<0.01% 命中率: {hitsB/NMC*100:.2f}%")

# ── [G] 若 R 命中, 解 Δm² 差譜 (盲測, 唔用 M_comp) ──
print("\n[G] 用命中 R 解差譜 (若能搵到 0.1% 命中):")
d21 = 7.53e-5; d31 = 2.434e-3
for R, name in [(m3_m2, "m3/m2 target"), (rat[best_A], f"A 最優 γ{best_A[0]+1}/γ{best_A[1]+1}")]:
    m2sq = (d31 - d21)/(R**2 - 1)
    if m2sq > 0:
        m2v = np.sqrt(m2sq); m1v = np.sqrt(m2sq - d21); m3v = R*m2v
        print(f"  R={R:.9f} ({name}): m1={m1v:.6f} m2={m2v:.6f} m3={m3v:.6f} Σm={m1v+m2v+m3v:.5f}")
print(f"  (vs P6: m1=0.020908 m2=0.022645 m3=0.053586 Σm=0.09714)")

print("\n" + "="*40)
print("R7 判定見上")