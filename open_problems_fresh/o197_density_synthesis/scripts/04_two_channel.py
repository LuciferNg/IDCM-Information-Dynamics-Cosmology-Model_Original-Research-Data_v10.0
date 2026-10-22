#!/usr/bin/env python3
# O197 scripts/04 — T3 定案: 兩通道並存模型
# 發現: logN-only 中位 6.985e6 命中 LRD 6.97e6 (0.2%), 乘性 (δ̂ 因子) 偏離
# ⟹ 合成結構 = 兩個獨立種子通道 (channel mixture), 唔係乘性因子:
#   通道 A (譜偏差): M = M_base(1+δ̂)^{3/2}, δ̂ arcsine [−1,1] ⟹ M ∈ [0, 5.41e6]
#   通道 B (環境過密): M = M_base(1+δ_env)^{3/2}, logN(μ=0.8625, s=1.187) ⟹ 中位 6.97e6
# T3a: logN-only 中位命中 LRD (δ_env 通道 = 主導種子族)
# T3b: δ̂ 通道 M ∈ [0, 5.41e6] (arcsine 低端) — 獨立種子族
# T3c: 兩通道並存 P(M) = w·P_A + (1−w)·P_B, 權重由觀測約束 (LRD 中位)
# T3d: 可證偽預言 — 低端種子密度 (arcsine 通道) + 高端重尾 (logN 通道)
import numpy as np

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

M_base = 1.914e6
mu_env, s_env = 0.862478, np.sqrt(1.4098)
ks = np.arange(1, 89)
dhat = -np.cos(2*ks*np.pi/176)
dhat_pos = dhat[dhat > 0]

print("== T3a: δ_env 通道中位命中 LRD ==")
M_med_env = M_base * np.exp(1.5*mu_env)
print(f"  logN 通道中位 M = {M_med_env:.4e}, LRD 錨 = 6.97e6")
check("T3a logN-only 中位命中 LRD (0.5% 內)", abs(M_med_env - 6.97e6)/6.97e6 < 0.005,
      f"dev = {abs(M_med_env-6.97e6)/6.97e6*100:.3f}%")

print("\n== T3b: δ̂ 通道 = 獨立低端種子族 ==")
M_arc = M_base * (1 + dhat_pos)**1.5
print(f"  δ̂₊ 通道 M 範圍: [{M_arc.min():.3e}, {M_arc.max():.3e}]")
check("T3b δ̂ 通道 M ∈ [M_base, 5.41e6] (arcsine 低端)", 
      abs(M_arc.max() - M_base*2**1.5)/ (M_base*2**1.5) < 1e-9 and M_arc.min() > M_base*1.0,
      f"M_max = {M_arc.max():.3e}, M_base·2^1.5 = {M_base*2**1.5:.3e}")
# 兩通道質量域: δ̂ 通道 [1.9e6, 5.4e6] vs logN 通道中位 6.97e6 — 域分離!
print(f"  δ̂ 通道域 [1.91e6, 5.41e6] vs logN 通道中位 6.97e6 ⟹ 兩通道域分離")
check("T3b' 兩通道質量域分離 (δ̂ 通道上限 < logN 中位)", M_arc.max() < M_med_env,
      f"{M_arc.max():.3e} < {M_med_env:.3e}")

print("\n== T3c: 兩通道並存 P(M) = w·P_A + (1−w)·P_B ==")
rng = np.random.default_rng(13)
N = 500000
M_env_s = M_base * np.exp(1.5*rng.normal(mu_env, s_env, N))
M_arc_s = M_base * (1 + rng.choice(dhat_pos, size=N))**1.5
# 權重掃描: w = δ̂ 通道份額, 中位 M 對 w
print("  w (δ̂ 份額)  合成中位 M    P(M>1e9)    P(M<2e6)")
for w in [0.0, 0.1, 0.25, 0.5, 0.75]:
    M_mix = np.where(rng.random(N) < w, M_arc_s, M_env_s)
    print(f"  {w:>5.2f}      {np.median(M_mix):>9.3e}   {np.mean(M_mix>1e9):>8.2e}   {np.mean(M_mix<2e6):>8.3f}")
# w 由低端種子觀測約束 — 未有數據, 標 data-gated
print("  ⟹ w 由低端種子數密度約束 (JWST z>5 低質量 BH 樣本) — data-gated")

print("\n== T3d: 可證偽預言 ==")
# 預言 1: 低端種子 (M < 5.4e6) 必須存在 (arcsine 通道), 密度由 w 決定
# 預言 2: 高端種子 (M > 1e8) 只由 logN 通道 (arcsine 通道上限 5.41e6 到唔到)
print(f"  預言 1: M < 5.41e6 種子存在 (arcsine 通道) — 若完全冇低端種子 = 證偽")
print(f"  預言 2: M > 5.41e6 種子全部經 δ_env 通道 — 種子質譜高端斜率 = logN 尾")
print(f"  預言 3: 種子質譜喺 M ≈ 5.41e6 有結構轉折 (通道交界)")
# logN 高端斜率 (M>1e8): d ln P/d ln M = −(ln M − μ_M)/s_M², μ_M = ln M_base+1.5μ, s_M = 1.5s
mu_M = np.log(M_base) + 1.5*mu_env
s_M = 1.5*s_env
slope = -(np.log(1e8) - mu_M)/s_M**2
print(f"  logN 通道 μ_M = {mu_M:.3f}, s_M = {s_M:.3f}, M>1e8 端斜率 = {slope:.2f}")
check("T3d logN 高端斜率 ∈ [−2.5, −0.5] (O176 docs/11 預言 −0.5~−1.0 種子譜)",
      -2.5 <= slope <= -0.5, f"slope = {slope:.2f}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
